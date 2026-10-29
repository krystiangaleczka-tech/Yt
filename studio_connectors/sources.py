from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import socket
import time
import re
import xml.etree.ElementTree as ET
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
    original = (urlparse(current).scheme,urlparse(current).netloc)
    with httpx.Client(timeout=35, follow_redirects=False, headers={"User-Agent": USER_AGENT}) as client:
        for _ in range(5):
            safe_headers = headers if (urlparse(current).scheme,urlparse(current).netloc) == original else None
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
        for k in ("pixabay_key", "pexels_key", "ai_key", "ai_base_url", "ai_model", "paper_image_key", "paper_image_model"):
            value = os.environ.get("DOCOS_" + k.upper())
            if value:
                config[k] = value
        price = os.environ.get("DOCOS_PAPER_IMAGE_REQUEST_COST")
        if price is not None:
            config["paper_image_request_cost"] = float(price)
        return config

    def save(self, values: dict) -> None:
        allowed = {"pixabay_key", "pexels_key", "ai_key", "ai_base_url", "ai_model", "ai_request_cost", "paper_image_key", "paper_image_model", "paper_image_request_cost", "custom"}
        if not set(values) <= allowed:
            raise ValueError("Nieznane ustawienia połączeń")
        config = self.config()
        from studio_core.paper_theatre_cutouts import MODELS
        if "paper_image_model" in values and values["paper_image_model"] not in MODELS:
            raise ValueError("Wybierz obsługiwany model transparent PNG")
        if "paper_image_request_cost" in values and (
            isinstance(values["paper_image_request_cost"], bool) or
            not isinstance(values["paper_image_request_cost"], (int, float)) or
            not 0 <= values["paper_image_request_cost"] <= 1000
        ):
            raise ValueError("Niepoprawny szacowany koszt generatora PNG")
        if "ai_request_cost" in values and (not isinstance(values["ai_request_cost"],(int,float)) or not 0<=values["ai_request_cost"]<=10000):
            raise ValueError("Niepoprawny szacowany koszt wywołania")
        for key, value in values.items():
            if value is not None:
                config[key] = value
        for item in config.get("custom", []):
            public_url(item["url"].replace("{query}", "test").replace("{page}", "1"))
            if not item.get("id", "").startswith("custom_"):
                raise ValueError("Identyfikator własnego źródła musi zaczynać się od custom_")
            if any(not re.fullmatch(r"[A-Za-z0-9-]+",k) or "\n" in str(v) or "\r" in str(v) for k,v in item.get("headers",{}).items()):
                raise ValueError("Niepoprawne nagłówki API")
            old=next((x for x in self.config().get("custom",[]) if x["id"]==item["id"]),{})
            if "headers" not in item and old.get("headers"): item["headers"]=old["headers"]
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
        for item in items:
            item["capabilities"]={"search":True,"pagination":True,"download":bool(set(item["kinds"])&{"image","video"}),"editions":item["id"]=="openlibrary","preview":item["id"]=="googlebooks","fulltext":item["id"]=="googlebooks"}
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
        identity = hashlib.sha256(json.dumps([provider, query, kind, page, c.get(provider + "_key", ""),c.get("custom",[])],sort_keys=True).encode()).hexdigest()
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
                results[-1]["variants"]=[{"name":"Podgląd","url":info.get("thumburl",""),"width":640},{"name":"Oryginał","url":info.get("url",""),"width":info.get("width",0),"height":info.get("height",0)}]
        elif provider == "pixabay":
            data = self.json("https://pixabay.com/api/" + ("videos/" if kind == "video" else ""),
                             {"key": c["pixabay_key"], "q": query[:100], "safesearch": "true", "per_page": 18, "page": page})
            for item in data.get("hits", []):
                variant = item.get("videos", {}).get("small", {})
                results.append(dict(id=str(item["id"]), title=item.get("tags", "Pixabay"), kind=kind, thumbnail=item.get("webformatURL") or variant.get("thumbnail", ""),
                                    download_url=item.get("largeImageURL") or variant.get("url", ""), url=item.get("pageURL", ""), author=item.get("user", ""),
                                    license="Pixabay Content License", license_url="https://pixabay.com/service/license-summary/", duration=item.get("duration", 0)))
                results[-1]["variants"]=[{"name":name,"url":v.get("url",""),"width":v.get("width",0),"height":v.get("height",0)} for name,v in item.get("videos",{}).items()] if kind=="video" else [{"name":"Duży obraz","url":item.get("largeImageURL","")}]
                results[-1].update(width=variant.get("width",0) if kind=="video" else item.get("imageWidth",0),height=variant.get("height",0) if kind=="video" else item.get("imageHeight",0))
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
                results[-1]["variants"]=[{"name":str(v.get("quality","mp4")),"url":v["link"],"width":v.get("width",0),"height":v.get("height",0)} for v in files] if kind=="video" else [{"name":name,"url":value} for name,value in item.get("src",{}).items()]
                results[-1].update(width=item.get("width",0),height=item.get("height",0))
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
                access=item.get("accessInfo",{})
                results[-1]["access"]="fulltext" if access.get("viewability")=="ALL_PAGES" else "preview" if access.get("viewability")=="PARTIAL" else "catalog"
                results[-1]["language"]=v.get("language","")
                results[-1]["edition"]=" · ".join(filter(None,[v.get("publishedDate",""),v.get("publisher","")]))
                if access.get("publicDomain"):
                    download=access.get("pdf",{}).get("downloadLink") or access.get("epub",{}).get("downloadLink")
                    if download: results[-1]["download_url"]=download
        elif provider == "crossref":
            data = self.json("https://api.crossref.org/works", {"query": query, "rows": 18, "offset": (page - 1) * 18})
            for item in data.get("message", {}).get("items", []):
                results.append(dict(id=item.get("DOI", ""), title=(item.get("title") or ["Publikacja"])[0], kind="information", url=item.get("URL", ""),
                                    author=", ".join(" ".join([a.get("given", ""), a.get("family", "")]).strip() for a in item.get("author", [])[:5]),
                                    identifier=item.get("DOI", ""), description=PlainText.extract(item.get("abstract", ""))[:1000]))
        else:
            config = next(x for x in c.get("custom", []) if x["id"] == provider)
            data = self.json(config["url"].replace("{query}", quote(query, safe="")).replace("{page}",str(page)),headers=config.get("headers"))
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

    def editions(self,work,page=1):
        if not re.fullmatch(r"/works/OL\d+W",work) or not 1<=page<=100: raise ValueError("Niepoprawny identyfikator dzieła")
        data=self.json("https://openlibrary.org"+work+"/editions.json",{"limit":20,"offset":(page-1)*20})
        results=[]
        for entry in data.get("entries",[]):
            key=entry.get("key","")
            results.append({"id":key,"title":entry.get("title",""),"provider":"openlibrary","kind":"book","url":"https://openlibrary.org"+key,
                            "edition":" · ".join(filter(None,[entry.get("publish_date",""),", ".join(entry.get("publishers",[]))])),"identifier":(entry.get("isbn_13") or entry.get("isbn_10") or [""])[0],
                            "language":", ".join(x.get("key","").split("/")[-1] for x in entry.get("languages",[])),"pages":entry.get("number_of_pages"),"access":"catalog","description":"Konkretne wydanie. Pełny tekst wymaga osobnego, legalnie dostępnego pliku."})
        return results

    def feed(self,url):
        raw,_,final=get_bytes(url,limit=4*1024*1024)
        try:root=ET.fromstring(raw)
        except ET.ParseError as error:raise ValueError("Adres nie zwrócił poprawnego kanału RSS/Atom") from error
        if root.tag=="rss": entries=root.findall("./channel/item")
        else: entries=root.findall("{http://www.w3.org/2005/Atom}entry")
        result=[]
        for entry in entries[:100]:
            def field(name):
                node=next((x for x in entry if x.tag.split("}")[-1]==name),None)
                return "".join(node.itertext()) if node is not None else ""
            link=next((x.attrib.get("href","") or x.text or "" for x in entry if x.tag.split("}")[-1]=="link"),"")
            link=urljoin(final,link)
            result.append({"id":hashlib.sha256(link.encode()).hexdigest()[:16],"title":field("title"),"description":PlainText.extract(field("description") or field("summary")),"url":link,"published_at":field("pubDate") or field("published") or field("updated"),"provider":"rss","kind":"information"})
        return result
