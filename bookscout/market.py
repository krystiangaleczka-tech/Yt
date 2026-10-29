"""Popyt i konkurencja: odsłony Wikipedii (zawsze, za darmo) i wyniki YouTube.

YouTube ma dwie drogi, które dają ten sam surowy format filmów:
- YouTube Data API v3 z kluczem GOOGLE_API_KEY (~102 jednostki z 10 000 dziennie na temat),
- plik dla Claude Code, który uzupełnia go narzędziem TubeAlfred (bez klucza, płatne kredyty TubeAlfred).
"""
from __future__ import annotations

import datetime as dt
import math
import re
import statistics
from urllib.parse import quote

import httpx

from . import config

STOPWORDS = {"the", "and", "of", "in", "on", "a", "an", "to", "for", "how", "why", "what", "who", "was",
             "were", "is", "that", "this", "with", "from", "by", "history", "documentary", "story"}
SHORTS_MAX_SECONDS = 180
STRONG_VIEWS = 100_000


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


# ── Wikipedia ────────────────────────────────────────────────────────────────

async def _wiki_get(http: httpx.AsyncClient, params: dict) -> dict:
    r = await http.get("https://en.wikipedia.org/w/api.php", params={**params, "format": "json"})
    if r.status_code != 200:
        raise RuntimeError(f"Wikipedia odpowiedziała {r.status_code}")
    return r.json().get("query", {})


async def _resolve_article(http: httpx.AsyncClient, article: str | None, query: str) -> tuple[str | None, str]:
    """Zwraca (tytuł, sposób dopasowania): „exact” z oceny Claude albo „search” z wyszukiwarki Wikipedii."""
    if article:
        pages = (await _wiki_get(http, {"action": "query", "titles": article, "redirects": 1})).get("pages", {})
        page = next(iter(pages.values()), {})
        if page and "missing" not in page and page.get("title"):
            return page["title"], "exact"
    if not query:
        return None, "none"
    hits = (await _wiki_get(http, {"action": "query", "list": "search", "srsearch": query, "srlimit": 1}))
    hits = hits.get("search", [])
    return (hits[0]["title"], "search") if hits else (None, "none")


async def wikipedia_demand(http: httpx.AsyncClient, article: str | None, query: str) -> dict:
    """Średnie miesięczne odsłony artykułu z ostatnich 12 pełnych miesięcy."""
    title, matched = await _resolve_article(http, article, query)
    if not title:
        return {"article": None, "monthly_avg": 0, "url": None, "matched": matched}
    today = now_utc().date().replace(day=1)
    end = today - dt.timedelta(days=1)
    start = (today.replace(year=today.year - 1))
    slug = quote(title.replace(" ", "_"), safe="")
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
           f"{slug}/monthly/{start:%Y%m%d}00/{end:%Y%m%d}00")
    r = await http.get(url)
    items = r.json().get("items", []) if r.status_code == 200 else []
    total = sum(i.get("views", 0) for i in items)
    return {"article": title, "monthly_avg": round(total / max(len(items), 1)) if items else 0,
            "url": f"https://en.wikipedia.org/wiki/{slug}", "matched": matched}


# ── YouTube Data API ─────────────────────────────────────────────────────────

def iso_duration_seconds(value: str) -> int | None:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value or "")
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


async def youtube_api_videos(http: httpx.AsyncClient, key: str, query: str) -> list[dict]:
    base = "https://www.googleapis.com/youtube/v3"
    r = await http.get(f"{base}/search", params={"part": "snippet", "type": "video", "maxResults": 25, "q": query,
                                                 "relevanceLanguage": "en", "order": "relevance", "key": key})
    if r.status_code != 200:
        raise RuntimeError(f"YouTube API: {r.json().get('error', {}).get('message', r.status_code)}")
    ids = [i["id"]["videoId"] for i in r.json().get("items", []) if i.get("id", {}).get("videoId")]
    if not ids:
        return []
    r = await http.get(f"{base}/videos", params={"part": "snippet,statistics,contentDetails", "id": ",".join(ids),
                                                 "key": key})
    items = r.json().get("items", [])
    channel_ids = sorted({i["snippet"]["channelId"] for i in items})
    r = await http.get(f"{base}/channels", params={"part": "statistics", "id": ",".join(channel_ids), "key": key})
    subs = {c["id"]: int(c.get("statistics", {}).get("subscriberCount", 0) or 0) for c in r.json().get("items", [])}
    return [{
        "id": i["id"],
        "title": i["snippet"]["title"],
        "channel": i["snippet"]["channelTitle"],
        "views": int(i.get("statistics", {}).get("viewCount", 0) or 0),
        "published": i["snippet"]["publishedAt"],
        "length_seconds": iso_duration_seconds(i.get("contentDetails", {}).get("duration", "")),
        "subs": subs.get(i["snippet"]["channelId"]),
    } for i in items]


# ── Metryki konkurencji ──────────────────────────────────────────────────────

def query_tokens(query: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (query or "").lower()) if len(t) > 2 and t not in STOPWORDS}


def is_relevant(title: str, tokens: set[str]) -> bool:
    if not tokens:
        return True
    hits = len(tokens & set(re.findall(r"[a-z0-9]+", title.lower())))
    return hits >= max(1, math.ceil(len(tokens) / 2))


def _age_months(published: str | None, now: dt.datetime) -> float | None:
    if not published:
        return None
    try:
        when = dt.datetime.fromisoformat(published.replace("Z", "+00:00"))
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt.timezone.utc)
    return max((now - when).days / 30.44, 0.5)


def video_metrics(videos: list[dict], query: str, now: dt.datetime | None = None) -> dict:
    """Liczy konkurencję z surowej listy filmów (bez Shorts)."""
    now = now or now_utc()
    tokens = query_tokens(query)
    longs = [v for v in videos if (v.get("length_seconds") or SHORTS_MAX_SECONDS + 1) > SHORTS_MAX_SECONDS]
    relevant = [v for v in longs if is_relevant(v.get("title", ""), tokens)]
    pool = relevant if len(relevant) >= 3 else longs
    views = [int(v.get("views") or 0) for v in pool]
    first_year, outliers, subs = [], [], []
    strong = strong_recent = 0
    for v in pool:
        age = _age_months(v.get("published"), now)
        n = int(v.get("views") or 0)
        if age is not None:
            first_year.append(n * min(1.0, 12 / age))
        if n >= STRONG_VIEWS and v in relevant:
            strong += 1
            if age is not None and age <= 24:
                strong_recent += 1
        if v.get("subs"):
            subs.append(v["subs"])
            outliers.append(n / v["subs"])
    return {
        "results": len(videos),
        "long_form": len(longs),
        "relevant": len(relevant),
        "strong": strong,
        "strong_recent": strong_recent,
        "median_views": int(statistics.median(views)) if views else 0,
        "top_views": max(views) if views else 0,
        "median_first_year": int(statistics.median(first_year)) if first_year else 0,
        "median_subs": int(statistics.median(subs)) if subs else None,
        "outlier_ratio": round(statistics.median(outliers), 2) if outliers else None,
        "top_videos": sorted(({"title": v.get("title"), "views": v.get("views"), "channel": v.get("channel"),
                               "id": v.get("id"), "published": v.get("published")} for v in relevant),
                             key=lambda v: -(v["views"] or 0))[:5],
    }


async def analyze(book: dict, google_key: str) -> dict:
    """Wikipedia zawsze, YouTube tylko z kluczem. Zwraca obiekt `market` do zapisania."""
    rating = book.get("rating") or {}
    query = rating.get("youtube_query") or book["title"]
    market = dict(book.get("market") or {})
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": config.USER_AGENT}) as http:
        market["wiki"] = await wikipedia_demand(http, rating.get("wikipedia_article"), query)
        if google_key:
            videos = await youtube_api_videos(http, google_key, query)
            market["youtube"] = youtube_from_raw(query, videos, "youtube_api")
    market["analyzed_at"] = now_utc().isoformat()
    return market


def youtube_from_raw(query: str, videos: list[dict], source: str) -> dict:
    """Metryki plus surowa lista filmów — pozwala przeliczyć konkurencję po zmianie reguł."""
    return {"query": query, "source": source, "fetched_at": now_utc().isoformat(), "videos": videos,
            **video_metrics(videos, query)}


MARKET_FILE_HEADER = """<!-- Book Scout — analiza YouTube {batch_id} (tryb Claude Code + TubeAlfred)
Dla każdej pozycji poniżej wyszukaj `query` narzędziem youtube_search_query (type=video,
jedna strona wyników = 1 kredyt TubeAlfred) i zapisz do pliku {response_name} obiekt JSON:
{{"<id książki>": {{"query": "...", "videos": [{{"id": "...", "title": "...", "channel": "...",
  "views": 123, "published": "ISO-8601", "length_seconds": 600, "subs": null}}]}}}}
Przepisz wszystkie filmy z pierwszej strony wyników bez zmian (views = view_count_int,
published = published_time). Potem w Book Scout kliknij „Importuj z plików”. -->

"""
