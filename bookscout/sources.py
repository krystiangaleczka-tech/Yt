"""Losowanie książek z katalogów i sprawdzanie, czy są dostępne w sieci.

Open Library (książki anglojęzyczne) i Biblioteka Narodowa (polskie książki — arbitraż PL→EN).
Dostępność cyfrowa: Open Library / Internet Archive, HathiTrust i — z kluczem — Google Books.
"""
from __future__ import annotations

import asyncio
import random
import re
from urllib.parse import quote

import httpx

from . import config
from .config import AVAILABILITY_RANK, Category

OL_FIELDS = ("key,title,author_name,first_publish_year,subject,ebook_access,ia,isbn,"
             "language,number_of_pages_median")
OL_ACCESS = {"public": "full", "borrowable": "borrow", "printdisabled": "restricted", "no_ebook": "none"}
BN_MIN_ID, BN_MAX_ID = 1_000_000, 12_500_000
BN_SKIP = re.compile(r"powieść|opowiadani|komiks|literatura dziecięca|literatura młodzieżowa|poezja|dramat"
                     r"|łamigłówk|podręcznik|kolorowank|fantastyka|kryminał|romans|materiały pomocnicze|ściąg"
                     r"|informator|do wypełniania|katalog wystawy|bibliografia|słownik|przewodnik", re.I)
OL_EXCLUDE = ('-subject:fiction -subject:"juvenile literature" -subject:congresses -subject:"law and legislation"'
              ' -subject:textbooks -subject:"examinations, questions" -subject:bibliography')
MAX_PARALLEL = 6


def client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=30, headers={"User-Agent": config.USER_AGENT}, follow_redirects=True)


def best_availability(statuses: list[str]) -> str:
    known = [s for s in statuses if s in AVAILABILITY_RANK]
    return max(known, key=AVAILABILITY_RANK.index) if known else "unknown"


async def _gather_limited(coros):
    sem = asyncio.Semaphore(MAX_PARALLEL)

    async def run(coro):
        async with sem:
            return await coro
    return await asyncio.gather(*(run(c) for c in coros))


# ── Open Library ─────────────────────────────────────────────────────────────

def ol_query(cat: Category, only_offline: bool, year_from: int | None, year_to: int | None) -> str:
    q = f"{cat.ol} language:eng {OL_EXCLUDE}"
    if only_offline:
        q += " ebook_access:no_ebook"
    if year_from or year_to:
        q += f" first_publish_year:[{year_from or '*'} TO {year_to or '*'}]"
    return q


def ol_doc_to_book(doc: dict, cat: Category) -> dict:
    access = OL_ACCESS.get(doc.get("ebook_access", ""), "unknown")
    detail = [{"source": "Open Library", "status": access, "url": f"https://openlibrary.org{doc['key']}"}]
    if doc.get("ia") and access in ("full", "borrow", "restricted"):
        detail.append({"source": "Internet Archive", "status": access,
                       "url": f"https://archive.org/details/{doc['ia'][0]}"})
    return {
        "id": f"ol:{doc['key'].rsplit('/', 1)[-1]}",
        "source": "openlibrary",
        "category": cat.key,
        "title": doc.get("title", "").strip(),
        "author": ", ".join(doc.get("author_name", [])[:3]),
        "year": doc.get("first_publish_year"),
        "language": ",".join(doc.get("language", [])[:4]) or "eng",
        "subjects": doc.get("subject", [])[:25],
        "description": "",
        "toc": [],
        "isbn": doc.get("isbn", [])[:6],
        "url": f"https://openlibrary.org{doc['key']}",
        "availability": access,
        "availability_detail": detail,
    }


async def draw_openlibrary(http: httpx.AsyncClient, cat: Category, count: int, only_offline: bool,
                           year_from=None, year_to=None) -> list[dict]:
    params = {"q": ol_query(cat, only_offline, year_from, year_to), "limit": count,
              "sort": f"random_{random.randint(1, 10**9)}", "fields": OL_FIELDS}
    r = await http.get("https://openlibrary.org/search.json", params=params)
    r.raise_for_status()
    return [ol_doc_to_book(d, cat) for d in r.json().get("docs", []) if d.get("title")]


def _text(value) -> str:
    if isinstance(value, dict):
        value = value.get("value", "")
    return str(value or "").strip()


async def enrich_openlibrary(http: httpx.AsyncClient, book: dict) -> None:
    """Opis z rekordu dzieła i spis treści z pierwszego wydania, które go ma."""
    work = book["id"].split(":", 1)[1]
    try:
        r = await http.get(f"https://openlibrary.org/works/{work}.json")
        if r.status_code == 200:
            book["description"] = _text(r.json().get("description"))[:2000]
        r = await http.get(f"https://openlibrary.org/works/{work}/editions.json", params={"limit": 30})
        if r.status_code == 200:
            for ed in r.json().get("entries", []):
                toc = [_text(t.get("title") if isinstance(t, dict) else t) for t in ed.get("table_of_contents", [])]
                toc = [t for t in toc if t]
                if toc:
                    book["toc"] = toc[:40]
                    break
    except httpx.HTTPError:
        pass


# ── Biblioteka Narodowa ──────────────────────────────────────────────────────

def _marc_subfields(record: dict, tag: str) -> list[str]:
    out = []
    for f in (record.get("marc") or {}).get("fields", []):
        body = f.get(tag)
        if isinstance(body, dict):
            out.append(" ".join(str(v) for sf in body.get("subfields", []) for v in sf.values()))
    return out


def bn_author(raw: str) -> str:
    """Pole BN skleja wszystkich twórców i wydawcę — zostaw pierwszą osobę („Nazwisko, Imię (lata)”)."""
    person = re.match(r"[^()]+\([^)]*\)", raw)
    return (person.group() if person else raw[:80]).strip()


def bn_record_to_book(rec: dict, cat: Category) -> dict:
    year = re.search(r"\d{4}", str(rec.get("publicationYear") or ""))
    title = re.sub(r"\s*/\s*$", "", rec.get("title", "")).strip()
    toc = []
    for chunk in _marc_subfields(rec, "505"):
        toc += [t.strip(" .") for t in re.split(r"\s+--\s+|;\s", chunk) if t.strip(" .")]
    isbns = re.findall(r"\b(?:97[89])?\d{9}[\dX]\b", rec.get("isbnIssn") or "")
    subjects = [s for s in (rec.get("subject"), rec.get("subjectPlace"), rec.get("subjectTime"),
                            rec.get("domain"), rec.get("genre")) if s]
    return {
        "id": f"bn:{rec['id']}",
        "source": "bn",
        "category": cat.key,
        "title": title,
        "author": bn_author(rec.get("author") or ""),
        "year": int(year.group()) if year else None,
        "language": rec.get("language") or "polski",
        "subjects": subjects,
        "description": " ".join(_marc_subfields(rec, "520"))[:2000],
        "toc": toc[:40],
        "isbn": isbns[:6],
        "url": "https://katalogi.bn.org.pl/discovery/search?vid=48OMNIS_NLOP:48OMNIS_NLOP&query=any,contains,"
               + quote(title[:120]),
        "availability": "unknown",
        "availability_detail": [{"source": "Polona", "status": "unknown",
                                 "url": "https://polona.pl/search?query=" + quote(title[:120])}],
    }


def _bn_usable(rec: dict, year_from, year_to) -> bool:
    if rec.get("deleted") or not rec.get("title"):
        return False
    if BN_SKIP.search(" ".join(str(rec.get(k) or "") for k in ("genre", "formOfWork", "subject", "audienceGroup"))):
        return False
    original = str(rec.get("languageOfOriginal") or "").lower()
    if original and "polski" not in original:
        return False   # przekład — brak arbitrażu PL→EN
    year = re.search(r"\d{4}", str(rec.get("publicationYear") or ""))
    if year and ((year_from and int(year.group()) < year_from) or (year_to and int(year.group()) > year_to)):
        return False
    return True


async def draw_bn(http: httpx.AsyncClient, cat: Category, count: int, year_from=None, year_to=None) -> list[dict]:
    """Losowy fragment katalogu BN: polskie książki z danej dziedziny, bez beletrystyki."""
    found: list[dict] = []
    top = BN_MAX_ID
    for _ in range(4):
        params = {"kind": "książka", "language": "polski", "limit": 60,
                  "sinceId": random.randint(BN_MIN_ID, top), **cat.bn}
        r = await http.get("https://data.bn.org.pl/api/institutions/bibs.json", params=params)
        r.raise_for_status()
        recs = [x for x in r.json().get("bibs", []) if _bn_usable(x, year_from, year_to)]
        if not recs:
            top = max(BN_MIN_ID + 1, top // 2)   # za wysokie id albo rzadki filtr — szukaj niżej
            continue
        random.shuffle(recs)
        found += [bn_record_to_book(x, cat) for x in recs[: count - len(found)]]
        if len(found) >= count:
            break
    return found


# ── Dostępność cyfrowa ───────────────────────────────────────────────────────

async def check_hathitrust(http: httpx.AsyncClient, book: dict) -> None:
    if not book["isbn"]:
        return
    ids = "|".join(f"isbn:{i}" for i in book["isbn"][:4])
    try:
        r = await http.get(f"https://catalog.hathitrust.org/api/volumes/brief/json/{ids}")
        if r.status_code != 200:
            return
        items = [it for v in r.json().values() for it in v.get("items", [])]
    except (httpx.HTTPError, ValueError):
        return
    if not items:
        return
    full = [it for it in items if it.get("usRightsString", "").lower().startswith("full")]
    item = (full or items)[0]
    book["availability_detail"].append({"source": "HathiTrust", "status": "full" if full else "restricted",
                                        "url": item.get("itemURL", "")})


async def check_google_books(http: httpx.AsyncClient, book: dict, key: str) -> None:
    if not key:
        return
    q = f"isbn:{book['isbn'][0]}" if book["isbn"] else f'intitle:"{book["title"][:80]}"'
    try:
        r = await http.get("https://www.googleapis.com/books/v1/volumes", params={"q": q, "maxResults": 1, "key": key})
        items = r.json().get("items", []) if r.status_code == 200 else []
    except (httpx.HTTPError, ValueError):
        return
    if not items:
        return
    item = items[0]
    view = item.get("accessInfo", {}).get("viewability", "NO_PAGES")
    status = {"ALL_PAGES": "full", "PARTIAL": "partial"}.get(view, "none")
    book["availability_detail"].append({"source": "Google Books", "status": status,
                                        "url": item.get("volumeInfo", {}).get("infoLink", "")})
    if not book["description"]:
        book["description"] = (item.get("volumeInfo", {}).get("description") or "")[:2000]


async def enrich(http: httpx.AsyncClient, book: dict, google_key: str) -> dict:
    tasks = [check_hathitrust(http, book), check_google_books(http, book, google_key)]
    if book["source"] == "openlibrary":
        tasks.append(enrich_openlibrary(http, book))
    await asyncio.gather(*tasks)
    statuses = [d["status"] for d in book["availability_detail"]]
    if book["source"] == "bn" and len(statuses) > 1:
        statuses = statuses[1:]   # Polona „unknown” przestaje się liczyć, gdy inne źródło coś wie
    book["availability"] = best_availability(statuses)
    return book


async def draw(categories: list[Category], source: str, count: int, only_offline: bool,
               year_from=None, year_to=None, google_key: str = "") -> list[dict]:
    """Losuje `count` książek po równo z podanych kategorii i źródeł, potem je wzbogaca."""
    sources = ["openlibrary", "bn"] if source == "both" else [source]
    jobs = [(c, s) for c in categories for s in sources]
    per_job = max(1, -(-count // len(jobs)))
    async with client() as http:
        calls = [draw_openlibrary(http, c, per_job, only_offline, year_from, year_to) if s == "openlibrary"
                 else draw_bn(http, c, per_job, year_from, year_to) for c, s in jobs]
        results = await asyncio.gather(*calls, return_exceptions=True)
        books = [b for res in results if isinstance(res, list) for b in res][:count]
        errors = [str(res) for res in results if isinstance(res, Exception)]
        books = await _gather_limited(enrich(http, b, google_key) for b in books)
    if only_offline:
        books = [b for b in books if b["availability"] not in ("full", "borrow")]
    if not books and errors:
        raise RuntimeError("; ".join(errors[:3]))
    return books
