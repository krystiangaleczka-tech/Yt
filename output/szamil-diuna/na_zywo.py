"""Teatr papierowy „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” na żywo: Python liczy ruch ujęcia, przeglądarka rysuje go kartą graficzną — bez klipów mp4.
Wzór: output/pierwszy-cesarz/na_zywo.py (ten sam protokół, który czyta Studio: studio_api/teatr.py, apps/studio/src/teatr.ts).

Ułożenie klatki (kto gdzie stoi, jak duży, jak rozmyty, gdzie kamera i światło) liczy kod ujęć z ujecia_a.py / ujecia_b.py
przez render.uloz; rysowanie pikseli robi przeglądarka w WebGL. Render końcowy dalej robi render.py (reżyser).

Studio uruchamia ten serwer samo, kiedy ujęcia projektu mają w legacy.teatr {"film": "szamil-diuna", "jezyk": "en",
"odn": "d01_01"}. Ręcznie:
  JEZYK=en python3 -I output/szamil-diuna/na_zywo.py 6 [--port 8899]   → http://127.0.0.1:8899 (jedno ujęcie)
Po zapisaniu kodu ujęć, sceny, wycinków albo rozpiski ruch liczy się od nowa, a podgląd sam się odświeża.
"""
import argparse
import hashlib
import importlib
import io
import json
import math
import os
import re
import sys
import threading
import time
import traceback
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
DOCS = HERE.parents[1] / "docs/filmy/szamil-diuna/ujecia"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(DOCS))
DANE = HERE / "build" / ("na_zywo_" + os.environ.get("JEZYK", "en"))
WYCINKI = DANE / "wycinki"
STRONA = HERE.parent / "pierwszy-cesarz" / "na_zywo" / "podglad.html"  # ta sama strona podglądu
# kolejność przeładowania: moduł i wszystko, co z niego korzysta (wycinki w zestaw.py budują się od nowa tylko wtedy,
# gdy zmienił się zestaw.py albo papier.py — zmiana samego ujęcia liczy się w ułamek sekundy)
MODULY = ["papier", "zestaw", "zestaw_kz", "dane", "scena", "uklad", "uklad_kz", "ujecia_a", "ujecia_b", "render"]  # uklad: 28.11
SILNIK = HERE.parent / "pierwszy-cesarz"  # papier.py i zestaw.py — silnik wspólny z „Pierwszym cesarzem”
PLIKI = {m: (DOCS if m == "dane" else SILNIK if m in ("papier", "zestaw") else HERE) / f"{m}.py" for m in MODULY}

import render  # noqa: E402

# kod — wersja kodu (rośnie po każdym udanym przeładowaniu); gotowe — policzone ujęcia: odn → (kod, JSON)
STAN = {"kod": 1, "stan": "gotowe", "czas": 0.0, "blad": "", "moduly": [], "numer": 6, "podpis": ""}
# Policzone ujęcia zostają na dysku (reżyser 24.11: „118/119 statyczne, jakby się coś zepsuło”, „to ujęcie było dobrze zrobione,
# po prostu jest zacięte”): po każdym uruchomieniu Studio serwer liczył 119 ujęć od zera, po kolei od pierwszego, a ujęcie
# jeszcze niepoliczone Studio rysowało ze starej klatki zapasowej (v1 z 19.11) — stara poza, nikt się nie rusza. Teraz ujęcie
# policzone dla tej samej treści kodu, nagrań lektora i ustawień wczytuje się z pliku w ułamku sekundy.
PAMIEC = DANE / "ujecia"
LEKTOR = HERE / "lektor_en"
GOTOWE = {}
LOCK = threading.RLock()
_HASH = {}  # id(Sprite), poziom mipmapy → (plik PNG, rozmiar)


def r3(v):
    return round(float(v), 3)


def _plik_wycinka(spr, lvl):
    key = (id(spr), lvl)
    if key not in _HASH:
        mip = spr.mips[lvl]
        h = hashlib.sha1(mip.tobytes() + repr(mip.size).encode()).hexdigest()[:16]
        out = WYCINKI / f"{h}.png"
        if not out.exists():  # alfa wymnożona zostaje w pliku: przeglądarka wczytuje go bez przeliczania
            buf = io.BytesIO()
            mip.save(buf, "PNG", compress_level=1)
            tmp = out.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_bytes(buf.getvalue())
            tmp.replace(out)
        _HASH[key] = (out.name, mip.size)
    return _HASH[key]


def eksport(i):
    """Ułożenie każdej klatki ujęcia i (od 0; 24 kl./s) w pikselach ekranu 1280 × 720 — te same wzory co Stage._sprite."""
    papier = render.papier
    a, b = render.SCENES[i][:2]
    T = b - a
    n = max(1, math.ceil(T * render.FPS - 1e-9))
    klatki, uzycia = [], {}
    for f in range(n):
        st, napis = render.uloz(a + f / render.FPS)
        el, linie = [], []
        for kind, p, z, g, it in st.ulozone():
            if kind != "spr":
                q = [st.cam.screen(x, y, p) for x, y in it["pts"]]
                linie.append({"p": [r3(v) for xy in q for v in xy], "w": r3(max(0.8, it["width"] * g)),
                              "c": [r3(c / 255) for c in it["color"]], "a": r3(it["alpha"]), "i": len(el)})
                continue
            spr = it["spr"]
            S = st.cam.screen(it["x"], it["y"], p)
            kk = it["k"] * g
            blur = it["blur"]
            if blur is None:
                blur = min(5.0, st.dof * abs(math.log(p / st.focus)) * (st.cam.L ** 0.5))
            if blur < 0.35:
                blur = 0.0
            sh = it["shadow"]
            if sh is True:
                d = 6 + 14 * p
                sh = (d * 0.75, d, 5 + 9 * p, 0.42)
            sh = (sh[0] * g, sh[1] * g, max(0.8, sh[2] * g), sh[3]) if sh and it["mode"] == "over" else (0, 0, 0, 0)
            skala = kk * max(abs(it["sx"]), abs(it["sy"]))
            uzycia[id(spr)] = (spr, max(skala, uzycia.get(id(spr), (spr, 0))[1]))
            tint = it["tint"] if it["tint"] is not None else (1, 1, 1)
            el.append([id(spr), r3(S[0]), r3(S[1]), r3(kk * it["sx"]), r3(kk * it["sy"]), r3(it["rot"]), r3(it["anchor"][0]),
                       r3(it["anchor"][1]), r3(it["alpha"]), r3(blur), *[r3(v) for v in sh], *[r3(v) for v in tint],
                       r3(it["haze"] or 0), {"over": 0, "add": 1, "mul": 2}[it["mode"]]])
        spot = None
        if st.spot:
            sx, sy, sp, rr, dark = st.spot
            px, py = st.cam.screen(sx, sy, sp)
            spot = [r3(px), r3(py), r3(rr * st.cam.mag(sp)), r3(dark)]
        klatki.append({"t": r3(f / render.FPS), "gr": [r3(v) for v in st.grade], "dim": r3(st.dim), "spot": spot,
                       "ns": int(st.t * papier.FPS) // 3 + 101 + st.seed, "napis": napis, "e": el, "l": linie})
    # tekstura: najmniejsza mipmapa, która przy największym powiększeniu w ujęciu ma jeszcze ok. 1,25 piksela na piksel ekranu
    tex, idx = [], {}
    for sid, (spr, skala) in uzycia.items():
        lvl = min(len(spr.mips) - 1, max(0, int(math.floor(math.log2(1.0 / max(skala * 1.25, 1e-6))))))
        plik, size = _plik_wycinka(spr, lvl)
        idx[sid] = len(tex)
        tex.append({"plik": plik, "w": spr.w, "h": spr.h, "tw": size[0], "th": size[1], "nazwa": spr.name})
    for k in klatki:
        for e in k["e"]:
            e[0] = idx[e[0]]
    return {"numer": i + 1, "klucz": render.KOL[i], "odn": render.ODN[i], "kod": STAN["kod"], "T": r3(T), "fps": render.FPS,
            "w": papier.W, "h": papier.H, "wycinki": tex, "klatki": klatki}


def podpis():
    """Skrót wszystkiego, od czego zależy ruch ujęć: kod modułów (silnik, wycinki, rozpiska, scena, ujęcia, render), ten plik
    (format JSON), nagrania lektora (długości kwestii w dane.py) i ustawienia z otoczenia."""
    h = hashlib.sha1()
    for m in MODULY:
        p = PLIKI[m]
        h.update(m.encode() + (p.read_bytes() if p.exists() else b"-"))
    h.update(Path(__file__).read_bytes())
    for p in sorted(LEKTOR.glob("*.json")) if LEKTOR.exists() else ():
        h.update(p.name.encode() + p.read_bytes())
    for k in ("JEZYK", "NAPISY", "SZKIC", "ROZDZIELCZOSC"):
        h.update(f"{k}={os.environ.get(k, '')};".encode())
    return h.hexdigest()[:16]


def _z_dysku(odn):
    """JSON ujęcia z pamięci na dysku (bez pola „kod”) albo None: brak pliku, inny podpis, brak wycinka albo zepsuty plik."""
    plik = PAMIEC / f"{odn}-{STAN['podpis']}.json.z"
    if not STAN["podpis"] or not plik.exists():
        return None
    try:
        surowe = zlib.decompress(plik.read_bytes())
        if all((WYCINKI / w["plik"]).exists() for w in json.loads(surowe)["wycinki"]):
            return surowe
    except Exception:
        traceback.print_exc()
    return None


def _na_dysk(odn, surowe):
    PAMIEC.mkdir(parents=True, exist_ok=True)
    for stary in PAMIEC.glob(f"{odn}-*.json.z"):  # poprzednie wersje tego ujęcia
        stary.unlink(missing_ok=True)
    plik = PAMIEC / f"{odn}-{STAN['podpis']}.json.z"
    tmp = plik.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_bytes(zlib.compress(surowe, 1))
    tmp.replace(plik)


def ujecie(odn):
    """JSON ujęcia dla obecnej wersji kodu — z pamięci, z dysku albo policzony teraz. Po błędzie w kodzie: ostatnia dobra wersja."""
    with LOCK:
        hit = GOTOWE.get(odn)
        if hit and (hit[0] == STAN["kod"] or STAN["stan"] == "błąd"):
            return hit[1]
        if odn not in render.ODN:
            raise KeyError(odn)
        surowe = _z_dysku(odn)
        if surowe is None:
            dane = eksport(render.ODN.index(odn))
            dane.pop("kod")
            surowe = json.dumps(dane, ensure_ascii=False, separators=(",", ":")).encode()
            try:
                _na_dysk(odn, surowe)
            except OSError:
                traceback.print_exc()
        body = b'{"kod":%d,' % STAN["kod"] + surowe[1:]  # wersja kodu tej sesji serwera (Studio porównuje ją ze stanem)
        GOTOWE[odn] = (STAN["kod"], body)
        return body


def przeladuj(zmienione):
    """Przeładowuje zmienione moduły i te, które z nich korzystają; nowa wersja kodu unieważnia policzone ujęcia."""
    global render
    t0 = time.time()
    with LOCK:
        try:
            od = min(MODULY.index(m) for m in zmienione)
            for m in MODULY[od:]:
                if m in sys.modules:
                    importlib.reload(sys.modules[m])
            render = sys.modules["render"]
            if {"zestaw", "zestaw_kz", "papier"} & set(zmienione):
                _HASH.clear()
            STAN.update(kod=STAN["kod"] + 1, stan="gotowe", blad="", moduly=sorted(zmienione), podpis=podpis())
            biezace = render.ODN[STAN["numer"] - 1]
            ujecie(biezace)  # ujęcie z osobnej strony liczy się od razu, reszta na żądanie i w tle
        except Exception:
            STAN.update(stan="błąd", blad=traceback.format_exc(limit=6), moduly=sorted(zmienione))
        STAN["czas"] = round(time.time() - t0, 2)
    print(f"kod {STAN['kod']}: {STAN['stan']} w {STAN['czas']} s (zmiana: {', '.join(sorted(zmienione))})", flush=True)
    if STAN["blad"]:
        print(STAN["blad"], flush=True)


def obserwuj():
    """Co pół sekundy sprawdza daty plików kodu; po zapisie przeładowuje kod."""
    daty = {m: p.stat().st_mtime for m, p in PLIKI.items() if p.exists()}
    while True:
        time.sleep(0.5)
        zm = {m for m, p in PLIKI.items() if p.exists() and p.stat().st_mtime != daty.get(m)}
        if zm:
            time.sleep(0.2)  # edytor zapisuje plik czasem w dwóch krokach
            daty = {m: p.stat().st_mtime for m, p in PLIKI.items() if p.exists()}
            przeladuj(zm)


def w_tle():
    """Liczy w tle ujęcia, których jeszcze nie ma dla obecnej wersji kodu — przewijanie montażu nie czeka."""
    while True:
        brak = [o for o in list(render.ODN) if GOTOWE.get(o, (0,))[0] != STAN["kod"]] if STAN["stan"] != "błąd" else []
        if not brak:
            time.sleep(0.5)
            continue
        try:
            ujecie(brak[0])
        except Exception:
            traceback.print_exc()
            time.sleep(2)
        time.sleep(0.02)  # żądania ze Studio mają pierwszeństwo


def rodzic(pid):
    """Serwer uruchomiony przez Studio kończy się razem z nim."""
    while True:
        time.sleep(2)
        try:
            os.kill(pid, 0)
        except OSError:
            os._exit(0)


class Obsluga(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _wyslij(self, body, typ, kod=200, cache=False):
        self.send_response(kod)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=31536000, immutable" if cache else "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                return self._wyslij(STRONA.read_bytes(), "text/html; charset=utf-8")
            if u.path == "/wersja":
                pola = {k: STAN.get(k) for k in ("kod", "stan", "czas", "blad", "moduly", "numer")}
                pola.update(wersja=STAN["kod"], ujec=len(render.ODN), gotowe=sum(1 for v in GOTOWE.values() if v[0] == STAN["kod"]),
                            odn=render.ODN[STAN["numer"] - 1], jezyk=os.environ.get("JEZYK", "en"))
                return self._wyslij(json.dumps(pola, ensure_ascii=False).encode(), "application/json")
            m = re.fullmatch(r"/ujecie/(d\d\d_\d\d)\.json", u.path)
            if m:
                return self._wyslij(ujecie(m.group(1)), "application/json")
            if u.path == "/dane.json":  # osobna strona: bieżące ujęcie
                return self._wyslij(ujecie(render.ODN[STAN["numer"] - 1]), "application/json")
            if u.path.startswith("/wycinki/"):
                plik = WYCINKI / Path(u.path).name
                if plik.exists():
                    return self._wyslij(plik.read_bytes(), "image/png", cache=True)
                return self._wyslij(b"brak", "text/plain", 404)
            if u.path == "/klatka":  # wzorzec: ta sama klatka narysowana przez Pythona (render.py)
                t = float(q.get("t", ["0"])[0])
                odn = q.get("odn", [render.ODN[STAN["numer"] - 1]])[0]
                with LOCK:
                    a, b = render.SCENES[render.ODN.index(odn)][:2]
                    img = render.frame(min(a + t, b - 0.01))
                buf = io.BytesIO()
                img.save(buf, "PNG", compress_level=1)
                return self._wyslij(buf.getvalue(), "image/png")
            if u.path == "/ujecie":  # osobna strona: /ujecie?n=31
                STAN["numer"] = int(q["n"][0])
                ujecie(render.ODN[STAN["numer"] - 1])
                return self._wyslij(b"ok", "text/plain")
            return self._wyslij(b"brak", "text/plain", 404)
        except KeyError as e:
            return self._wyslij(f"nie ma ujęcia {e}".encode(), "text/plain; charset=utf-8", 404)
        except Exception:
            return self._wyslij(traceback.format_exc(limit=6).encode(), "text/plain; charset=utf-8", 500)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("numer", type=int, nargs="?", default=6, help="ujęcie na osobnej stronie (numer jak w Studio)")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--rodzic", type=int, default=0, help="pid Studio: serwer kończy się razem z nim")
    ap.add_argument("--bez-tla", action="store_true", help="nie licz w tle pozostałych ujęć")
    args = ap.parse_args()
    WYCINKI.mkdir(parents=True, exist_ok=True)
    STAN["numer"] = args.numer
    STAN["podpis"] = podpis()
    if args.rodzic and sys.platform != "win32":  # na Windows os.kill(pid, 0) zabiłby proces Studio
        threading.Thread(target=rodzic, args=(args.rodzic,), daemon=True).start()
    threading.Thread(target=obserwuj, daemon=True).start()
    if not args.bez_tla:
        threading.Thread(target=w_tle, daemon=True).start()
    print(f"teatr na żywo: http://127.0.0.1:{args.port}  (JEZYK={os.environ.get('JEZYK', 'pl')}, ujęć {len(render.ODN)})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Obsluga).serve_forever()
