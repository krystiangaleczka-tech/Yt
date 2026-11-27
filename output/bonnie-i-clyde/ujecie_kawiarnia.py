"""Ujęcie 24: kawiarnia. Wersja robocza do weryfikacji renderem.

Samodzielny moduł, nie zmienia ujecia_a ani silnika. Kamera, SIGH…, gag i czasy
efektów pozostają z wersji starej. Polecenia: klip, porownanie, kontrola, dzwiek.
Kontrola sprawdza każdą klatkę renderu, dodatkowo próbę mutacji +20 px dzbanka.
"""
import math
import os
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scena as SW
import uklad as U
import zestaw_bc as J
import ujecia_a as A
from scena import P, bk, kam, lerp, pr, ease

KLUCZ = "kawiarnia"
NALANIE, KONIEC_NALEWANIA, LOMOT = 1.45, 2.30, 2.95
GAG, GAG_DL, SZELEST = 7.0, 2.6, 0.55
BONNIE_X, BONNIE_H = 595, 290
KLIENT_X, KLIENT_H = 820, 300
LADA_X, LADA_H = 640, 150
FU_DZBANEK, FU_KUBEK = 0.44, 0.65
H_DZBANEK, H_KUBEK, H_GAZETA = 60, 34, 130
# Punkty na oryginalnych arkuszach J.REKWIZYTY, nie współrzędne w kadrze.
UCHO, DZIOBEK = (18, 84), (146, 55)
USTE_KUBKA = (35, 10)
BRZEG_KUBKA = ((13, 10), (57, 10))
CHWYTY_GAZETY = {"przod": (6, 342), "tyl": (354, 342)}
RZEDY = {n: p for n, p in U.RZEDY_WNETRZA.items() if n not in ("lalki", "przod")}
RZEDY.update({"za ladą": P.lalki - 0.015, "lada": P.lalki,
              "przed ladą": P.lalki + 0.02, "przejście": P.lalki + 0.03})
CHWILE = (0.0, 0.6, 1.05, 1.25, 1.45, 1.8, 2.29, 2.55, 2.95, 3.2,
          5.2, 7.0, 7.55, 8.1, 9.55, 10.35)


def xy3(xy, p):
    return (*xy, p)


def na_plan(st, xy, zrodlo, cel):
    """Ten sam punkt ekranu na innym planie: odwrotność Cam.screen."""
    a, b = st.cam.screen(*xy, zrodlo)
    x, y = st.cam.screen(0, 0, cel)
    g = st.cam.mag(cel)
    return (a - x) / g, (b - y) / g


def miks(a, b, k):
    return tuple(lerp(x, y, k) for x, y in zip(a, b))


def wiez(u, opis, ok, wartosc):
    u.wiezy.append((opis, bool(ok), wartosc))


def dekoracja(u, w, t):
    # Ten sam wystrój i zegar budowy, tylko lada ma własny rząd.
    with u.obiekt("wnętrze", "dekoracja", p=P.miasto):
        SW.wnetrze(u.st, t, w, sciana="paski", okna=(260, 1020), meble=(), kul=False)
    # Osobny właściciel rampy: stare wnetrze() narysowało ją wewnątrz bloku.
    for idx in list(u.wl):
        if u.st.items[idx][1] == P.rampa:
            u.wl[idx] = "rampa"
            u.obiekty.setdefault("rampa", dict(rodzaj="dekoracja", p=P.rampa))
    with u.obiekt("kulisy", "dekoracja", p=0.95):
        SW.kulisy(u.st, t, w, dol=False)
    k = bk(w, 0.45)
    u.mebel("lada", "lada", LADA_X, LADA_H, rzad="lada", k=k, seed=130, wob=0.1)
    return k


def na_blacie_geo(u, ark, fu, h):
    x, y = u.powierzchnia("lada", "blat", fu)
    p = u.obiekty["lada"]["p"] + 0.002
    return U.Geo(x, y, h / ark.hs, (ark.srodek, ark.dol), p=p)


def odstawiony(u, nazwa, key, fu, h, k):
    geo = u.na(nazwa, key, "lada", "blat", fu, h)
    # W czasie wyrastania dół może być poza ekranem: więź geometryczna
    # obowiązuje również wtedy, kontrola maski wymaga widocznego dna.
    if k < 1:
        u.kontrole.pop()  # u.na zarejestrował kontrolę maski dna
        u.kontakt(xy3(geo(*geo.kotw), geo.p),
                  xy3(u.powierzchnia("lada", "blat", fu), geo.p),
                  nazwa + ": dno na rosnącym blacie")
    return geo


def dzbanek_i_bonnie(u, w, t, k, kubek, mutacja=0.0):
    ark = U.ark_rek("dzbanek")
    rest = na_blacie_geo(u, ark, FU_DZBANEK, H_DZBANEK)
    p = rest.p
    dno = rest(*rest.kotw)
    chwyt_stoi = rest(*UCHO)
    # Zanim dzbanek jest przechylony, unosi się pionowo z blatu.
    wysoko = (chwyt_stoi[0], chwyt_stoi[1] - 65)
    ust = kubek(*USTE_KUBKA)
    cel_dziobka = (ust[0], ust[1] - 25)
    # Położenie ucha wynika z celu dzióbka i obrotu arkusza.
    obrot = 45.0
    dx, dy = SW._off((DZIOBEK[0] - UCHO[0]) * rest.k,
                     (DZIOBEK[1] - UCHO[1]) * rest.k, obrot)
    lej = (cel_dziobka[0] - dx, cel_dziobka[1] - dy)
    if t < 1.10:
        uch, kat = chwyt_stoi, 0.0
    elif t < 1.27:
        uch, kat = miks(chwyt_stoi, wysoko, ease(pr(t, 1.10, 0.17))), 0.0
    elif t < NALANIE:
        f = ease(pr(t, 1.27, NALANIE - 1.27))
        uch, kat = miks(wysoko, lej, f), obrot * f
    elif t < KONIEC_NALEWANIA:
        uch, kat = lej, obrot
    elif t < 2.55:
        f = ease(pr(t, KONIEC_NALEWANIA, 2.55 - KONIEC_NALEWANIA))
        uch, kat = miks(lej, wysoko, f), obrot * (1 - f)
    elif t < LOMOT:
        f = pr(t, 2.55, LOMOT - 2.55) ** 1.6
        uch, kat = miks(wysoko, chwyt_stoi, f), 0.0
    else:
        uch, kat = chwyt_stoi, 0.0

    # Bonnie stoi wcześniej niż w starym wejściu, żeby była gotowa na 1.45 s.
    # Dłoń zaczyna sięgać dopiero po wyrośnięciu lalki.
    wej = bk(w, 0.45, 0.50)
    flip = -1.0 if 7.2 < t < 8.0 else 1.0
    def cel(s):
        if t < 0.95 or t >= 3.15:
            return 10.0
        spocz = U.Uklad.dlon_z_kata(s, 10.0)
        punkt = na_plan(u.st, uch, p, s["p"])
        if t < 1.10:
            return miks(spocz, punkt, ease(pr(t, 0.95, 0.15)))
        if t >= LOMOT:
            return miks(punkt, spocz, ease(pr(t, LOMOT, 0.20)))
        return punkt
    s = u.lalka("Bonnie", "bonnie_kelnerka", BONNIE_X, BONNIE_H,
                rzad="za ladą", k=wej, wejscie=False, flip=flip, przod=cel,
                tyl=10.0, lokiec=("dol", "dol"))
    trzyma = 1.10 <= t < LOMOT
    wiez(u, "dzbanek: stan chwytu zgodny z osią czasu", not trzyma or s is not None,
         "w dłoni" if trzyma else "na ladzie")
    if trzyma and s is not None:
        dlon = s["przod"]["dlon"]
        hx, hy = na_plan(u.st, dlon, s["p"], p)
        # Mutacja przesuwa rzeczywisty rysowany wycinek, nie cel dłoni.
        geo = u.rzecz("dzbanek", ark, hx + mutacja, hy, p, UCHO, H_DZBANEK, rot=kat, z=0.02)
        u.relacje.append(("dzbanek", "Bonnie", "w dłoni za ucho"))
        u.kontakt(xy3(geo(*UCHO), p), xy3(dlon, s["p"]),
                  "dzbanek: ucho w dłoni Bonnie", tol=2.0)
        u.dotyka("dzbanek", xy3(dlon, s["p"]), "dzbanek: papier ucha dotyka dłoni", 3.0)
        u.punkt("Bonnie", xy3(dlon, s["p"]), "Bonnie: widoczna dłoń z dzbankiem", r=9, ile=0.10)
    else:
        geo = odstawiony(u, "dzbanek", "dzbanek", FU_DZBANEK, H_DZBANEK, k) if k > 0 else rest
        if abs(t - LOMOT) < 1e-6 and s is not None:
            u.kontakt(xy3(geo(*UCHO), geo.p), xy3(s["przod"]["dlon"], s["p"]),
                      "dzbanek: zwolnienie chwytu na blacie")
    if k >= 1:
        u.widac("dzbanek", 0.93, oprocz=("Bonnie", "zielsko"))
    if s is not None and wej >= 1:
        u.widac("Bonnie", 0.94, oprocz=("lada", "rampa", "dzbanek", "kubek", "strumień", "zielsko"))
    if NALANIE <= t < KONIEC_NALEWANIA:
        start = geo(*DZIOBEK)
        koniec = kubek(*USTE_KUBKA)
        # Na tym samym planie, za papierem filiżanki (z=-0.02).
        with u.obiekt("strumień", "rzecz", p=p):
            u.st.line([start, koniec], p, width=3.0, color=(86, 54, 30), alpha=0.95, z=-0.02)
        u.relacje.append(("strumień", "dzbanek", "z dzióbka"))
        u.relacje.append(("strumień", "kubek", "do wnętrza"))
        u.dotyka("strumień", xy3(start, p), "strumień: zaczyna się przy dzióbku", 3.0)
        u.dotyka("dzbanek", xy3(start, p), "strumień: dzióbek jest papierem dzbanka", 3.0)
        u.dotyka("strumień", xy3(koniec, kubek.p), "strumień: dochodzi do otworu filiżanki", 3.0)
        u.dotyka("kubek", xy3(koniec, kubek.p), "strumień: kończy się na brzegu filiżanki", 3.0)
        x0, x1 = sorted(kubek(*q)[0] for q in BRZEG_KUBKA)
        wiez(u, "strumień: dzióbek nad otworem, przepływ w dół",
             x0 <= start[0] <= x1 and start[1] < koniec[1], f"odchylenie x={start[0]-koniec[0]:.2f} px")
        u.widac("strumień", 0.75, oprocz=("dzbanek", "kubek"))
    return s


@lru_cache(None)
def ark_gazety():
    im = J._gazeta_img(360, 480, "DEPRESSION DEEPENS", J.TYTULY_GAZET[5], 5)
    return U.Ark(J.gazeta("DEPRESSION DEEPENS", 5, 360, 480), im)


def klient(u, w, t):
    ark = ark_gazety()
    k = bk(w, 0.55, 0.60)
    # Papier porusza się w takt dokładnie tych samych pięciu szelestów.
    drg = sum(math.sin(math.pi * pr(t, GAG + SZELEST * n, 0.18)) for n in range(5))
    def papier(s):
        fx, fy = s["punkt"](150, 122)
        return U.Geo(fx + 2 * drg, fy + H_GAZETA * 0.22, H_GAZETA / ark.hs,
                     (180, 240), rot=2.0 * drg, p=s["p"])
    def cel(reka):
        return lambda s: papier(s)(*CHWYTY_GAZETY[reka])
    s = u.lalka("klient", "przechodzien2", KLIENT_X, KLIENT_H, rzad="przed ladą",
                k=k, wejscie=False, flip=-1.0, przod=cel("przod"), tyl=cel("tyl"),
                lokiec=("dol", "dol"))
    if s is None:
        return
    plan = papier(s)
    # Z tyłu dłoń obejmuje brzeg od spodu, z przodu nachodzi na gazetę.
    geo = u.rzecz("gazeta", ark, plan.x, plan.y, plan.p, plan.kotw,
                  H_GAZETA, rot=plan.rot, z=0.025)
    u.relacje.append(("gazeta", "klient", "w obu dłoniach"))
    for reka, chwyt in CHWYTY_GAZETY.items():
        dlon = s[reka]["dlon"]
        u.kontakt(xy3(geo(*chwyt), geo.p), xy3(dlon, s["p"]),
                  "gazeta: chwyt " + reka, tol=2.0)
        if k >= 1:
            u.dotyka("gazeta", xy3(dlon, s["p"]), "gazeta: papier przy dłoni " + reka, 3.0)
    if k >= 1:
        u.widac("gazeta", 0.94, oprocz=("klient", "zielsko"))
        u.widac("klient", 0.95, oprocz=("gazeta", "rampa", "zielsko"))


def s_kawiarnia(st, w, t, T, mutacja=0.0):
    hk = 2.95 < t < 3.25
    kam(st, t, 15, 640, 390, 1.15, 0.8, shake=3.0 * hk)
    u = U.Uklad(st, t, rzedy=RZEDY)
    k = dekoracja(u, w, t)
    kubek = (odstawiony(u, "kubek", "kubek", FU_KUBEK, H_KUBEK, k) if k > 0
             else na_blacie_geo(u, U.ark_rek("kubek"), FU_KUBEK, H_KUBEK))
    if k >= 1:
        u.widac("kubek", 0.95, oprocz=("zielsko", "strumień"))
    dzbanek_i_bonnie(u, w, t, k, kubek, mutacja)
    klient(u, w, t)
    tz = pr(t, GAG, GAG_DL)
    if 0 < tz < 1:
        u.put("zielsko", J.rek("zielsko"), lerp(-120, 1400, tz),
              566 - 90 * abs(math.sin(tz * 9)), u.p("przejście"),
              "rzecz", h=86, anchor=(0.5, 1.0), rot=tz * 900)
    A.tab(w, t, "SIGH…", BONNIE_X, 230, 2.4, 1.8)
    A.koniec(st, w, t)


def _render():
    os.environ.setdefault("NAPISY", "0")
    import render as R
    i = SW.I[KLUCZ]
    a, b = R.SCENES[i][:2]
    if not math.isclose(b-a, 10.4, abs_tol=1e-6):
        raise ValueError(f"Rozpiska: długość {b-a:.6f}, oczekiwano 10.4 s")
    return R


def podmien(R):
    i = SW.I[KLUCZ]
    stara = R.FNS[i]
    R.FNS[i] = s_kawiarnia
    return i, stara


def porownanie(out):
    R = _render()
    i = SW.I[KLUCZ]
    a, b = R.SCENES[i][:2]
    chwile = CHWILE
    R.FNS[i] = A.s_kawiarnia
    stare = [R.frame(a + c) for c in chwile]
    podmien(R)
    nowe = [R.frame(a + c) for c in chwile]
    tw, th = 640, 360
    f = ImageFont.truetype(U.FONT, 22)
    arkusz = Image.new("RGB", (tw * 2, (th + 4) * len(chwile) + 40), (20, 18, 16))
    d = ImageDraw.Draw(arkusz)
    d.text((tw / 2, 20), "STARE (ujecia_a.s_kawiarnia)", font=f, fill=(255, 220, 120), anchor="mm")
    d.text((tw * 1.5, 20), "NOWE (uklad.py)", font=f, fill=(140, 230, 140), anchor="mm")
    for r, c in enumerate(chwile):
        for col, im in enumerate((stare[r], nowe[r])):
            arkusz.paste(im.resize((tw, th), Image.LANCZOS), (col * tw, 40 + r * (th + 4)))
        d.text((8, 44 + r * (th + 4)), f"{c:.2f} s", font=f, fill=(255, 255, 0))
    arkusz.save(out)
    return out


def kontrola(katalog):
    start = time.monotonic()
    R = _render()
    i, _ = podmien(R)
    a, b = R.SCENES[i][:2]
    kat = Path(katalog)
    kat.mkdir(parents=True, exist_ok=True)
    f = ImageFont.truetype(U.FONT, 15)
    wiersze, zle = [], {}
    def wpis(c, wyn):
        for opis, ok, wart in wyn:
            v = zle.setdefault(opis, [0, 0, []])
            v[1] += 1
            if not ok:
                v[0] += 1
                v[2].append(f"{c:.4f} s: {wart}")
    def sprawdz(c):
        st, _ = R.uloz(a + c)
        return st, U.kontrola(st)
    for c in CHWILE:
        st, (wyn, idb, pelne, kod, widac) = sprawdz(c)
        im = st.render()
        plan = U.rzut(st, pelne, widac, wyn,
                      pokaz=("Bonnie","lada","kubek","dzbanek","klient","gazeta","strumień","zielsko"))
        row = Image.new("RGB", (1280, 390 + 20 * len(wyn)), (250, 247, 240))
        row.paste(im.resize((640, 360), Image.LANCZOS), (0, 0))
        row.paste(plan, (640, 0))
        d = ImageDraw.Draw(row)
        d.text((8, 8), f"{c:.2f} s", font=f, fill=(255, 255, 0))
        for n, (opis, ok, wart) in enumerate(wyn):
            d.text((10, 366 + 20*n), f"{'OK' if ok else 'BŁĄD'} {opis}: {wart}", font=f,
                   fill=(25, 100, 40) if ok else (190, 35, 35))
        wiersze.append(row)
    im = Image.new("RGB", (1280, sum(r.height for r in wiersze)), (250,247,240))
    y = 0
    for row in wiersze:
        im.paste(row, (0,y))
        y += row.height
    im.save(kat / "kontrola_kawiarnia.png")
    # Wszystkie klatki, nie co druga jak we wzorcu.
    n = math.ceil((b-a)*R.FPS - 1e-9)
    for fr in range(n):
        c = min(fr/R.FPS, b-a-1e-3)
        _, (wyn, *_) = sprawdz(c)
        wpis(c, wyn)
    # Dodatkowe dokładne granice zdarzeń (nie muszą wypadać na klatkę).
    for c in (1.10, NALANIE, KONIEC_NALEWANIA, LOMOT, GAG,
              *(GAG+SZELEST*j for j in range(5))):
        _, (wyn, *_) = sprawdz(c)
        wpis(c, wyn)
    probka = 1.80
    st, (przed, *_) = sprawdz(probka)
    im0 = st.render()
    try:
        R.FNS[i] = lambda st,w,t,T: s_kawiarnia(st,w,t,T,mutacja=20.0)
        st, (po, *_) = sprawdz(probka)
        im1 = st.render()
    finally:
        R.FNS[i] = s_kawiarnia
    st, (cof, *_) = sprawdz(probka)
    im2 = st.render()
    def chwyt(wyn):
        return next((ok, wart) for opis, ok, wart in wyn if opis == "dzbanek: ucho w dłoni Bonnie")
    test = chwyt(przed)[0] and not chwyt(po)[0] and chwyt(cof)[0]
    panel = Image.new("RGB", (1280, 3*380), (250,247,240))
    d = ImageDraw.Draw(panel)
    for r, (label, img, wyn) in enumerate(zip(("oryginał", "+20 px", "cofnięto"), (im0, im1, im2), (przed, po, cof))):
        panel.paste(img.resize((640,360), Image.LANCZOS), (0, r*380+20))
        d.text((8,r*380+2), label, font=f, fill=(30,30,30))
        for j, (opis, ok, wart) in enumerate(x for x in wyn if "dzbanek" in x[0] or "strumień" in x[0]):
            d.text((645,r*380+28+j*20), f"{'OK' if ok else 'BŁĄD'} {opis}: {wart}", font=f,
                   fill=(20,100,40) if ok else (190,30,30))
    panel.save(kat / "mutacja_dzbanek.png")
    import efekty as E
    evs = E.ZDARZENIA[KLUCZ]
    oczek = [(NALANIE, "nalewanie"), (LOMOT, "lomot")] + [(GAG+SZELEST*j,"papier") for j in range(5)]
    dzwiek_ok = all(any(math.isclose(a0,b0,abs_tol=1e-7) and a1==b1 for b0,b1,*_ in evs) for a0,a1 in oczek)
    suma = sum(v[0] for v in zle.values())
    with (kat / "raport_kawiarnia.md").open("w", encoding="utf-8") as fh:
        fh.write(f"# Ujęcie 24: kontrola\n\nKlatek: {n} (każda przy {R.FPS} fps) oraz granice zdarzeń.\n")
        fh.write(f"\nBłędy: {suma}; mutacja: {'OK' if test else 'BŁĄD'}; zgodność dźwięku: {dzwiek_ok}.\n")
        fh.write(f"\nPrzed: {chwyt(przed)}; +20 px kadru wzorcowego: {chwyt(po)}; po cofnięciu: {chwyt(cof)}.\n")
        fh.write(f"\nCzas kontroli: {time.monotonic()-start:.1f} s.\n\n")
        fh.write("| kontrola | błędy / sprawdzenia | pierwsze błędy |\n|---|---|---|\n")
        for opis, (nz,nk,gdzie) in zle.items():
            fh.write(f"| {opis} | {nz} / {nk} | {'; '.join(gdzie[:3])} |\n")
        fh.write("\n## Inscenizacja\n"
                 "- Bonnie za ladą, klient przed nią: lada zasłania dolną część kelnerki, nie klienta. Stary plan lada=P.drzewa był za obiema lalkami.\n"
                 "- Kubek i odstawiony dzbanek na blacie obliczanym z wycinka mebla. Stare STOPY-150 ignorowało rzeczywisty blat i jego ruch.\n"
                 "- Dzbanek ma uchwyt i dzióbek z arkusza; łokieć sięga celu. W starym kodzie kąt ręki, dzióbek i punkt odstawienia były niezależne.\n"
                 "- Klient ma dwa osobne chwyty przeciwległych brzegów gazety, zamiast jednego kąta obu rąk; nie odwraca wzroku.\n"
                 "- Wejście Bonnie i podnoszenie dzbanka dostrojone przed 1.45 s; nie zmieniono dźwięków, kamery ani gagów.\n"
                 "- Pozycja SIGH… podąża za Bonnie, napis i czas niezmienione. Łomot w 2.95 s kończy ruch na blacie, bez podskoku dna.\n"
                 "- Podczas wyrastania mebla kontrola geometryczna działa także poza kadrem; kontrola maski dna po zakończeniu wyrastania.\n"
                 "- Kontrole automatyczne nie zastępują obejrzenia klipu i arkusza przez wykonawcę.\n")
    print(f"{n} klatek, {suma} błędów, mutacja={test}, dźwięk={dzwiek_ok}")
    if suma or not test or not dzwiek_ok:
        raise SystemExit(1)
    return kat


def klip(out):
    R = _render()
    i, _ = podmien(R)
    return R._klip((i, Path(out)))


def dzwiek(klip_mp4, out_mp4):
    """Próbka zgrania obrazu z dźwiękiem: zdarzenia ręczne ujęcia z efekty.py (ZDARZENIA z gagami, budowa dekoracji)
    nałożone na klip. Bez muzyki, kroków lalek i tła — te liczy efekty.py dla całego filmu."""
    import subprocess
    import efekty as E
    R = _render()
    i = SW.I[KLUCZ]
    a, b = R.SCENES[i][:2]
    sec = b - a
    n = E.N(sec)
    fx = np.zeros(n)
    evs = list(E.ZDARZENIA.get(KLUCZ, []))  # ZDARZENIA mają już dołączone GAGI_DZWIEK
    if KLUCZ in R.BUDUJ:
        evs += [(dd, "whoosh", 0.3) for dd in (0.0, 0.25, 0.45, 0.65, 0.9)] + [(dd, "knock", 0.25) for dd in (0.75, 1.05, 1.4, 1.7)]
    for at, kind, gg in evs:
        s = E.DLUGIE[kind](min(gg, sec - at)) if kind in E.DLUGIE else E.KROTKIE[kind]() * gg
        j = E.N(at)
        fx[j:j + len(s)] += s[:n - j]
    wav = Path(out_mp4).with_suffix(".wav")
    E.zapisz(wav, fx)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(klip_mp4), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "160k", str(out_mp4)], check=True)
    wav.unlink()
    return out_mp4, evs


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "porownanie"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == "klip":
        print(klip(arg or HERE / "kawiarnia_uklad.mp4"))
    elif cmd == "porownanie":
        print(porownanie(arg or HERE / "porownanie_kawiarnia.png"))
    elif cmd == "kontrola":
        print(kontrola(arg or HERE / "kontrola_kawiarnia"))
    elif cmd == "dzwiek":
        print(dzwiek(arg, sys.argv[3]))
