"""Wyszukiwanie i pobieranie materiałów z Wikimedia Commons z rejestrem licencji.

    python3 fetch_commons.py search "SOSUS" [--video] [--n 10]
    python3 fetch_commons.py get "File:Nazwa.jpg" OUT_DIR [--name krotka_nazwa] [--width 1920]

Każde pobranie dopisuje wiersz do OUT_DIR/licenses.json (tytuł, autor, licencja, URL strony).
Dopuszczalne licencje: domena publiczna, CC0, CC BY, CC BY-SA (wymagają podpisu w opisie filmu).
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "DocOS/0.1 (documentary research; contact: local user)"}
OK = re.compile(r"public domain|^pd|cc0|cc[- ]by(-sa)?[- ]?\d|cc[- ]by(-sa)?$", re.I)


def fetch(req, timeout=60):
    """urlopen z odczekaniem przy 429 (Commons ogranicza tempo zapytań)."""
    for attempt in range(6):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 10 * 2 ** attempt
            print(f"  (429 — czekam {wait}s)", file=sys.stderr)
            time.sleep(wait)
        except urllib.error.URLError:
            if attempt == 5:
                raise
            print("  (błąd sieci — ponawiam)", file=sys.stderr)
            time.sleep(5 * (attempt + 1))


def call(**params):
    params |= {"format": "json", "formatversion": "2"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    with fetch(req) as r:
        return json.load(r)


def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def info(titles, width=None):
    p = dict(action="query", titles="|".join(titles), prop="imageinfo",
             iiprop="url|size|mime|extmetadata")
    if width:
        p["iiurlwidth"] = width
    pages = call(**p)["query"]["pages"]
    out = []
    for pg in pages:
        if "imageinfo" not in pg:
            continue
        ii = pg["imageinfo"][0]
        md = ii.get("extmetadata", {})
        g = lambda k: strip(md.get(k, {}).get("value", ""))  # noqa: E731
        out.append(dict(title=pg["title"], url=ii["url"], thumb=ii.get("thumburl", ii["url"]),
                        mime=ii["mime"], w=ii.get("width"), h=ii.get("height"),
                        license=g("LicenseShortName"), artist=g("Artist"), credit=g("Credit"),
                        date=g("DateTimeOriginal"), desc=g("ImageDescription")[:300],
                        page=ii.get("descriptionurl", "")))
    return out


def search(q, video=False, n=10):
    ftype = "filetype:video" if video else "filetype:bitmap"
    res = call(action="query", list="search", srsearch=f"{q} {ftype}", srnamespace=6, srlimit=n)
    titles = [r["title"] for r in res["query"]["search"]]
    return info(titles) if titles else []


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("search"); s.add_argument("q"); s.add_argument("--video", action="store_true"); s.add_argument("--n", type=int, default=10)
    g = sp.add_parser("get"); g.add_argument("title"); g.add_argument("out"); g.add_argument("--name"); g.add_argument("--width", type=int, default=1920)
    a = ap.parse_args()

    if a.cmd == "search":
        for r in search(a.q, a.video, a.n):
            flag = "OK " if OK.search(r["license"]) else "?? "
            print(f"{flag}{r['title']} | {r['w']}x{r['h']} | {r['license']} | {r['artist'][:40]} | {r['date'][:10]} | {r['desc'][:110]}")
        return

    r = info([a.title], a.width)
    if not r:
        sys.exit("nie znaleziono")
    r = r[0]
    if not OK.search(r["license"]):
        sys.exit(f"Licencja niedozwolona: {r['license']}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    src = r["url"] if r["mime"].startswith(("video", "application/ogg")) else r["thumb"]
    if src == r["url"] and (r.get("h") or 0) > 1100:  # 4K -> pochodna 1080p generowana przez Commons
        pg = call(action="query", titles=r["title"], prop="videoinfo", viprop="derivatives")["query"]["pages"][0]
        ders = [d for d in pg.get("videoinfo", [{}])[0].get("derivatives", []) if d.get("height") in (1080, 720)]
        if ders:
            src = sorted(ders, key=lambda d: -d["height"])[0]["src"]
    ext = Path(urllib.parse.urlparse(src).path).suffix
    name = (a.name or re.sub(r"\W+", "_", r["title"][5:])[:50]) + ext
    req = urllib.request.Request(src, headers=UA)
    with fetch(req, timeout=300) as resp:
        (out / name).write_bytes(resp.read())
    lic = out / "licenses.json"
    led = json.loads(lic.read_text()) if lic.exists() else []
    led = [x for x in led if x["file"] != name] + [dict(file=name, source="Wikimedia Commons", **r)]
    lic.write_text(json.dumps(led, ensure_ascii=False, indent=2))
    print(f"zapisano {out / name} ({r['license']}, {r['artist'][:40]})")


if __name__ == "__main__":
    main()
