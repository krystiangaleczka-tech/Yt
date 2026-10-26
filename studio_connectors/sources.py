from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import socket
import time
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

import httpx

from studio_core.media import PlainText
from studio_core.store import atomic_json

USER_AGENT = "DocOSStudio/0.1 (local documentary research; https://github.com/krystiangaleczka-tech/Yt)"


def public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Podaj publiczny adres HTTP lub HTTPS bez danych logowania")
    host = parsed.hostname
    try:
        addresses = [item[4][0] for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))]
    except OSError as e:
        raise ValueError("Nie można rozpoznać adresu źródła") from e
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
        raise ValueError("Pobieranie z prywatnych adresów sieciowych jest wyłączone")
    return url


def get_bytes(url: str, *, params=None, limit=15 * 1024 * 1024, headers=None) -> tuple[bytes, str, str]:
    current = public_url(url)
    # Validate each redirect and never forward credentials to another origin.
    original = urlparse(current).netloc
    with httpx.Client(timeout=35, follow_redirects=False, headers={"User-Agent": USER_AGENT}) as client:
        for _ in range(5):
            safe_headers = headers if urlparse(current).netloc == original else None
            with client.stream("GET", current, params=params, headers=safe_headers) as response:
                params = None
                if response.is_redirect:
                    current = public_url(urljoin(str(response.url), response.headers["location"]))
                    continue
                response.raise_for_status()
                chunks = bytearray()
                for chunk in response.iter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > limit:
                        raise ValueError("Źródło przekracza limit pobierania")
                return bytes(chunks), response.headers.get("content-type", ""), str(response.url)
    raise ValueError("Zbyt wiele przekierowań źródła")


class Connectors:
    def __init__(self, root: Path):
        self.root = root
        self.config_path = root / "connections.json"
        self.cache = root / "source-cache"
        self.cache.mkdir(parents=True, exist_ok=True)

    def config(self) -> dict:
        config = json.loads(self.config_path.read_text()) if self.config_path.exists() else {}
        for k in ("pixabay_key", "pexels_key", "ai_key", "ai_base_url", "ai_model"):
            value = os.environ.get("DOCOS_" + k.upper())
            if value:
                config[k] = value
        return config

    def save(self, values: dict) -> None:
        allowed = {"pixabay_key", "pexels_key", "ai_key", "ai_base_url", "ai_model", "custom"}
        if not set(values) <= allowed:
            raise ValueError("Nieznane ustawienia połączeń")
        config = self.config()
        for key, value in values.items():
            if value is not None:
                config[key] = value
        for item in config.get("custom", []):
            public_url(item["url"].replace("{query}", "test"))
            if not item.get("id", "").startswith("custom_"):
                raise ValueError("Identyfikator własnego źródła musi zaczynać się od custom_")
        atomic_json(self.config_path, config)
        self.config_path.chmod(0o600)

    def catalog(self) -> list[dict]:
        c = self.config()
        items = [
            {"id": "commons", "name": "Wikimedia Commons", "kinds": ["image", "video"], "configured": True, "note": "Zdjęcia i archiwalia · metadane licencji"},
            {"id": "pixabay", "name": "Pixabay", "kinds": ["image", "video"], "configured": bool(c.get("pixabay_key")), "note": "Zdjęcia i stockowe filmy · klucz API"},
            {"id": "pexels", "name": "Pexels", "kinds": ["image", "video"], "configured": bool(c.get("pexels_key")), "note": "Opcjonalny dostawca · wymagany dostęp API"},
            {"id": "openlibrary", "name": "Open Library", "kinds": ["book"], "configured": True, "note": "Katalog książek, autorzy i wydania"},
            {"id": "googlebooks", "name": "Google Books", "kinds": ["book"], "configured": True, "note": "Katalog i dostępne podglądy"},
            {"id": "crossref", "name": "Crossref", "kinds": ["information"], "configured": True, "note": "Publikacje i DOI · metadane"},
        ]
        items += [{"id": x["id"], "name": x["name"], "kinds": [x.get("kind", "information")], "configured": True,
                   "note": "Własne źródło JSON"} for x in c.get("custom", [])]
        return items

    def json(self, url, params=None, headers=None):
        raw, _, _ = get_bytes(url, params=params, headers=headers)
        return json.loads(raw)

    def search(self, provider: str, query: str, kind: str = "image", page: int = 1) -> list[dict]:
        catalog = next((c for c in self.catalog() if c["id"] == provider), None)
        if not catalog or not catalog["configured"]:
            raise ValueError("Najpierw skonfiguruj połączenie z tym dostawcą")
        if kind not in catalog["kinds"]:
            raise ValueError("Dostawca nie obsługuje tego typu treści")
        if not query.strip() or len(query) > 200 or page < 1 or page > 20:
            raise ValueError("Podaj zapytanie do dwustu znaków")
        c = self.config()
        identity = hashlib.sha256(json.dumps([provider, query, kind, page, c.get(provider + "_key", "")]).encode()).hexdigest()
        cached = self.cache / (identity + ".json")
        if cached.exists() and time.time() - cached.stat().st_mtime < 86400:
            return json.loads(cached.read_text())
        results = []
        if provider == "commons":
            params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": query + (" filetype:video" if kind == "video" else " filetype:bitmap"),
                      "gsrnamespace": 6, "gsrlimit": 18, "gsroffset": (page - 1) * 18, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 640}
            data = self.json("https://commons.wikimedia.org/w/api.php", params)
            for item in sorted(data.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 0)):
                info = (item.get("imageinfo") or [{}])[0]
                ext = info.get("extmetadata", {})
                val = lambda k: PlainText.extract(ext.get(k, {}).get("value", ""))
                if info.get("mime", "").startswith("image/svg"):
                    continue
                results.append(dict(id=str(item["pageid"]), title=item["title"].removeprefix("File:"), kind=kind,
                                    thumbnail=info.get("thumburl", ""), download_url=info.get("thumburl") if kind == "image" else info.get("url", ""),
                                    url=info.get("descriptionurl", ""), author=val("Artist"), license=val("LicenseShortName"),
                                    license_url=val("LicenseUrl"), width=info.get("width", 0), height=info.get("height", 0)))
        elif provider == "pixabay":
            data = self.json("https://pixabay.com/api/" + ("videos/" if kind == "video" else ""),
                             {"key": c["pixabay_key"], "q": query[:100], "safesearch": "true", "per_page": 18, "page": page})
            for item in data.get("hits", []):
                variant = item.get("videos", {}).get("small", {})
                results.append(dict(id=str(item["id"]), title=item.get("tags", "Pixabay"), kind=kind, thumbnail=item.get("webformatURL") or variant.get("thumbnail", ""),
                                    download_url=item.get("largeImageURL") or variant.get("url", ""), url=item.get("pageURL", ""), author=item.get("user", ""),
                                    license="Pixabay Content License", license_url="https://pixabay.com/service/license-summary/", duration=item.get("duration", 0)))
        elif provider == "pexels":
            url = "https://api.pexels.com/videos/search" if kind == "video" else "https://api.pexels.com/v1/search"
            data = self.json(url, {"query": query, "per_page": 18, "page": page}, {"Authorization": c["pexels_key"]})
            for item in data.get("videos" if kind == "video" else "photos", []):
                files = sorted([v for v in item.get("video_files", []) if v.get("file_type") == "video/mp4"], key=lambda x: abs((x.get("width") or 1280) - 1280))
                results.append(dict(id=str(item["id"]), title=item.get("alt") or "Pexels video", kind=kind,
                                    thumbnail=item.get("src", {}).get("medium") or item.get("image", ""),
                                    download_url=item.get("src", {}).get("large2x") or (files[0]["link"] if files else ""),
                                    url=item.get("url", ""), author=item.get("photographer") or item.get("user", {}).get("name", ""),
                                    license="Pexels License", license_url="https://www.pexels.com/license/", duration=item.get("duration", 0)))
        elif provider == "openlibrary":
            data = self.json("https://openlibrary.org/search.json", {"q": query, "limit": 18, "page": page, "fields": "key,title,author_name,first_publish_year,cover_i,edition_key,isbn"})
            for item in data.get("docs", []):
                results.append(dict(id=item["key"], title=item.get("title", ""), kind="book", url="https://openlibrary.org" + item["key"],
                                    author=", ".join(item.get("author_name", [])), edition=str(item.get("first_publish_year", "")),
                                    identifier=(item.get("isbn") or [""])[0], thumbnail=f"https://covers.openlibrary.org/b/id/{item['cover_i']}-M.jpg" if item.get("cover_i") else ""))
        elif provider == "googlebooks":
            data = self.json("https://www.googleapis.com/books/v1/volumes", {"q": query, "maxResults": 18, "startIndex": (page - 1) * 18})
            for item in data.get("items", []):
                v = item["volumeInfo"]
                results.append(dict(id=item["id"], title=v.get("title", ""), kind="book", url=v.get("infoLink", ""),
                                    author=", ".join(v.get("authors", [])), edition=v.get("publishedDate", ""),
                                    identifier=(v.get("industryIdentifiers") or [{}])[0].get("identifier", ""),
                                    thumbnail=v.get("imageLinks", {}).get("thumbnail", "").replace("http:", "https:"),
                                    preview_url=v.get("previewLink", ""), description=PlainText.extract(v.get("description", ""))[:1000]))
        elif provider == "crossref":
            data = self.json("https://api.crossref.org/works", {"query": query, "rows": 18, "offset": (page - 1) * 18})
            for item in data.get("message", {}).get("items", []):
                results.append(dict(id=item.get("DOI", ""), title=(item.get("title") or ["Publikacja"])[0], kind="information", url=item.get("URL", ""),
                                    author=", ".join(" ".join([a.get("given", ""), a.get("family", "")]).strip() for a in item.get("author", [])[:5]),
                                    identifier=item.get("DOI", ""), description=PlainText.extract(item.get("abstract", ""))[:1000]))
        else:
            config = next(x for x in c.get("custom", []) if x["id"] == provider)
            data = self.json(config["url"].replace("{query}", quote(query, safe="")))
            for part in config.get("results_path", "").split("."):
                if part:
                    data = data[part]
            if not isinstance(data, list):
                raise ValueError("Własne źródło musi zwracać listę wyników JSON")
            for i, item in enumerate(data[:50]):
                if not isinstance(item, dict):
                    continue
                mapped = {k: item.get(v, "") for k, v in config.get("mapping", {"title": "title", "url": "url"}).items()}
                results.append(mapped | {"id": str(item.get("id", i)), "kind": kind})
        for result in results:
            result["provider"] = provider
        atomic_json(cached, results)
        return results
