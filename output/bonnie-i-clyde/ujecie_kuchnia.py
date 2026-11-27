"""Ujęcie 25 „kuchnia” na ulepszonym silniku (uklad.py) — reżyser zatwierdził 27.11.2026; ujecia_a.s_kuchnia woła
to ujęcie, a stara wersja została jako ujecia_a.s_kuchnia_stara (do porównania).

Rozpiska: W ciasnej kuchni Bonnie miesza kakao; drzwiami wchodzi Clyde w kapeluszu i uchyla go; z nitki zjeżdżają dwa
serduszka. Gag: na „he was arrested” serduszka odjeżdżają w górę, na tej samej nitce zjeżdżają kajdanki.

Bez zmian wobec starej wersji: długość ujęcia, kamera, budowa dekoracji, okno, serca i kajdanki, chwile dźwięków
z efekty.ZDARZENIA["kuchnia"] (mieszanie 0–3 s, drzwi 1,2 s, whoosh 3,3 s; serca w górę 8,2 s, kajdanki 9,5 s).
Zmienione (każda zmiana to błąd starej wersji, który teraz liczy silnik):
- Clyde wchodzi DRZWIAMI (wytyczne 1.2): w 1,2 s, na dźwięk „drzwi”, skrzydło się otwiera; Clyde idzie korytarzem za
  ścianą (widać go tylko w otworze — ściana ma wycięty otwór, 1.1), przechodzi przez próg do kuchni (rząd korytarz →
  aktorzy), skrzydło domyka się za nim. Było: wjeżdżał zza krawędzi kadru obok zamkniętych drzwi.
- Kapelusz jest osobnym wycinkiem: dłoń (ręka z łokciem) chwyta go za główkę, unosi, przechyla do Bonnie i odkłada na
  głowę (whoosh 3,3 s). Było: ręka machała nad głową, a kapelusz stał na głowie (sztywna ręka nie sięga głowy).
- Bonnie stoi ZA kuchenką (kuchenka zasłania ją od pasa), garnek stoi na płycie, łyżka jest w garnku, za jego przednią
  ścianką (1.22); po mieszaniu Bonnie wyjmuje łyżkę i odwraca się do Clyde'a, zanim ten uchyli kapelusz (1.16, 1.21).
- Przyjaciółka stoi za stołem z dłonią na blacie; na blacie kubek. Było: stół stał za wszystkimi jak ława.
Nowe zdarzenie dźwiękowe: drzwi domykają się w DRZWI_ZAMK + DRZWI_ZAMK_DL = 2,95 s (efekty.ZDARZENIA["kuchnia"], „stuk”).

  python3 ujecie_kuchnia.py klip <plik.mp4>       — klip ujęcia (jak render.py klipy, pełna jakość, bez napisów)
  python3 ujecie_kuchnia.py porownanie <plik.png> — stare i nowe ujęcie w tych samych chwilach
  python3 ujecie_kuchnia.py kontrola <katalog>    — arkusz kontroli (klatka + rzut z góry), zbliżenia dłoni, raport
  python3 ujecie_kuchnia.py dzwiek <klip.mp4> <wynik.mp4> — próbka: klip + zdarzenia dźwiękowe ujęcia (bez muzyki)
"""
import math
import os
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import scena as SW  # noqa: E402
import uklad as U  # noqa: E402
import zestaw as Z0  # noqa: E402
import zestaw_bc as J  # noqa: E402
from papier import Sprite, ease, ease_out, settle  # noqa: E402
from scena import CX, P, bk, kam, kulisy, lerp, pr, rampa, spod  # noqa: E402
import ujecia_a as A  # noqa: E402  (A.koniec przez moduł: efekty.py podsłuchuje A.koniec)

KLUCZ = "kuchnia"

# ---- oś czasu ujęcia (sekundy od początku; te same liczby rysuje obraz i ma mieć dźwięk) ----
MIESZA_DO = 3.0  # efekty: (0.0, "mieszanie", 3.0)
DRZWI_OTW, DRZWI_OTW_DL = 1.2, 0.35  # efekty: (1.2, "drzwi", 0.6)
DRZWI_ZAMK, DRZWI_ZAMK_DL = 2.55, 0.4  # drzwi domykają się za Clyde'em; efekty: (2.95, "stuk", 0.9)
KORYTARZ = (1.25, 0.65)  # Clyde idzie korytarzem do otworu drzwi
PROG = (1.9, 0.35)  # przez próg: rząd korytarz → aktorzy
DO_KUCHNI = (2.25, 0.65)  # od progu na swoje miejsce
CLYDE_X = (1235, 1062, 1036, 936)
BONNIE_CHWYT = (1.6, 0.15)  # dłoń Bonnie bierze łyżkę opartą w garnku
WYJMUJE = (MIESZA_DO, 0.2)  # wyjmuje łyżkę z garnka
ODWROT = (3.2, 0.35)  # Bonnie odwraca się do Clyde'a
SIEGA = (3.12, 0.18)  # dłoń Clyde'a idzie do kapelusza
CHWYT = 3.3  # dłoń chwyta kapelusz; efekty: (3.3, "whoosh", 0.25)
UNOSI = (3.3, 0.3)
OPUSZCZA = (3.95, 0.3)
PUSZCZA = 4.25
WRACA = (4.25, 0.3)

# ---- miejsca ----
DRZWI_X, DRZWI_Y, DRZWI_H = 1060, 690, 440  # jak w starej wersji (wnetrze(drzwi=(1060,)))
KUCHENKA_X, KUCHENKA_H = 380, 170
STOL_X, STOL_H = 690, 140
BONNIE_X, BONNIE_H = 405, 290  # spódnica (± 36 px) cała za kuchenką (306–454)
PRZYJ_X = 690
CLYDE_H = 320
FU_GARNEK = 0.4  # lewy palnik
FU_DLON_PRZYJ, FU_KUBEK = 0.68, 0.86
CHWYT_KAPELUSZA = (180, 66)  # przód główki fedory na arkuszu korpusu 300 × 690
CHWYT_LYZKI = (20, 148)  # koniec trzonka na arkuszu łyżki 40 × 160
CZERPAK_LYZKI = (20, 24)
KONIEC_LYZKI = (20, 2)
BRZEG_GARNKA = 22  # v brzegu (powierzchnia kakao) na arkuszu garnka 160 × 110


# ---------- dekoracja: ściana z otworem, korytarz, drzwi otwierane na zawiasie ----------

@lru_cache(None)
def drzwi_czesci(kolor=(110, 76, 52)):
    """Framuga i skrzydło drzwi z tych samych kawałków i ziaren co J.drzwi (zamknięte wyglądają jak dotąd)."""
    w, h = 200, 420
    rama = Z0.stack(w, h, [(Z0.rect(0, 0, w, h), J._shade(kolor, 0.8))], seed=151)
    a = np.asarray(rama.getchannel("A")).copy()
    a[12:, 12:w - 12] = 0
    rama.putalpha(Image.fromarray(a))
    skrzydlo = Z0.stack(w, h, [(Z0.rect(12, 12, w - 12, h), kolor, dict(edge=2)),
                               (Z0.rect(40, 40, w - 40, 170), (170, 196, 206), dict(kind="gladki", contrast=0.5)),
                               (Z0.ell(w - 34, 230, 9, 9), J.GOLD)], seed=158)
    return (Sprite(rama, "framuga", rim=2, clean=False, crop=False), Sprite(skrzydlo, "skrzydlo", rim=2, clean=False, crop=False))


def otwor_drzwi():
    """Prostokąt otworu drzwi w kadrze wzorcowym (wewnętrzna krawędź framugi): x0, y0, x1, y1."""
    k = DRZWI_H / 420
    x0 = DRZWI_X - 100 * k
    return x0 + 12 * k, DRZWI_Y - DRZWI_H + 12 * k, x0 + 188 * k, DRZWI_Y


@lru_cache(None)
def sciana_z_otworem(wzor="kwiaty"):
    """Ściana z wyciętym otworem drzwi: przez otwór widać korytarz i to, co w nim stoi (wytyczne 1.1)."""
    spr = J.sciana(wzor)
    img = spr.mips[0].copy()  # ściana nieprzezroczysta: barwy z alfą wymnożoną = zwykłe
    f = img.width / 2200
    ox, oy = CX - 1100, 720 - 820  # arkusz 2200 × 820 stoi kotwicą (0.5, 1) w (CX, 720), 1 px arkusza = 1 px kadru
    x0, y0, x1, y1 = otwor_drzwi()
    a = np.asarray(img.getchannel("A")).copy()
    a[int((y0 + 3 - oy) * f):int((y1 - oy) * f), int((x0 + 3 - ox) * f):int((x1 - 3 - ox) * f)] = 0
    img.putalpha(Image.fromarray(a))
    return Sprite(img, f"sciana-{wzor}-otwor", rim=0, clean=False, pad=0, crop=False)


@lru_cache(None)
def korytarz_img():
    """Ciemny korytarz za drzwiami: u góry ciemniej, od lewej trochę światła z głębi domu."""
    w, h = 130, 320  # wyższy niż otwór: nad głową wchodzącego nie może świecić pustka
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    jas = 0.55 + 0.45 * (yy / h) - 0.25 * (xx / w)
    rgb = np.stack([62 * jas, 46 * jas, 36 * jas], -1)
    im = Image.fromarray(np.dstack([rgb, np.full((h, w), 255.0)]).astype(np.uint8), "RGBA")
    return Sprite(im, "korytarz", rim=0, clean=False, pad=0, crop=False)


def kat_drzwi(t):
    """Kąt skrzydła (0 — zamknięte, 78° — otwarte do kuchni): otwiera się na dźwięk „drzwi”, domyka za Clyde'em."""
    otw = ease_out(pr(t, DRZWI_OTW, DRZWI_OTW_DL))
    zam = ease(pr(t, DRZWI_ZAMK, DRZWI_ZAMK_DL)) ** 1.6  # domyka się coraz szybciej
    k = otw * (1 - zam)
    drg = settle((t - DRZWI_ZAMK - DRZWI_ZAMK_DL) / 0.35, 2, 2.5) if t > DRZWI_ZAMK + DRZWI_ZAMK_DL else 0.0
    return max(0.0, 78 * k + drg)


def dekoracja(u, w, t):
    """Kuchnia jak scena.wnetrze(sciana="kwiaty", okna=(300,), drzwi=(1060,), meble=(kuchenka, stół)), tylko rzędami
    i z drzwiami, przez które da się wejść."""
    st = u.st
    kd = bk(w, 0.25)
    gotowe = kd >= 1  # ściana dostaje otwór, kiedy drzwi już stoją (wcześniej zamknięte skrzydło i tak go zasłania)
    u.put("ściana", sciana_z_otworem() if gotowe else J.sciana("kwiaty"), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    with u.obiekt("pas pod ścianą", "dekoracja", p=P.miasto - 0.002):
        spod(st)
    x0, y0, x1, y1 = otwor_drzwi()
    if gotowe:
        u.put("korytarz", korytarz_img(), (x0 + x1) / 2, y1 + 10, u.p("korytarz") - 0.004, w=x1 - x0 + 30, anchor=(0.5, 1.0),
              shadow=None)
    noc = w.noc > 0.5
    with u.obiekt("okno", "dekoracja", p=P.miasto + 0.01):
        J.hang(st, J.okno(noc), 300, 150, P.miasto + 0.01, bk(w, 0.2), t, 120, h=300, drop=500, sway=0.3, strings=(0.1, 0.9))
    rama, skrz = drzwi_czesci()
    pd = u.p("drzwi")
    with u.obiekt("drzwi", "dekoracja", p=pd):
        Z0.rise(st, rama, DRZWI_X, DRZWI_Y, pd, kd, t, 125, wob=0.0, h=DRZWI_H)
        if not gotowe:
            Z0.rise(st, skrz, DRZWI_X, DRZWI_Y, pd + 0.001, kd, t, 125, wob=0.0, h=DRZWI_H)
    if gotowe:  # skrzydło na zawiasie (lewa krawędź): obracając się do kuchni, zwęża się i wychodzi przed framugę
        th = math.radians(kat_drzwi(t))
        k = DRZWI_H / 420
        u.put("skrzydło drzwi", skrz, DRZWI_X - 88 * k, DRZWI_Y, pd + 0.001 + 0.03 * math.sin(th), h=DRZWI_H, anchor=(12 / 200, 1.0),
              sx=max(0.04, math.cos(th)), tint=(1 - 0.28 * math.sin(th),) * 3, shadow=True)
    with u.obiekt("podłoga", "dekoracja", p=P.droga):
        Z0.rise(st, J.podloga((130, 96, 66)), CX, 820, P.droga, bk(w, 0.3), t, 128, w=2200, wob=0.0, lift=220, anchor=(0.5, 1.0))
    u.mebel("kuchenka", "kuchenka", KUCHENKA_X, KUCHENKA_H, "przod", k=bk(w, 0.45), seed=130, wob=0.1)
    u.mebel("stół", "stol", STOL_X, STOL_H, "przod", k=bk(w, 0.53), seed=131, wob=0.1)
    with u.obiekt("rampa", "dekoracja", p=P.rampa):
        rampa(st, bk(w, 0.6, 0.6))
    with u.obiekt("kulisy", "dekoracja", p=0.95):
        kulisy(st, t, w, dol=False)


# ---------- aktorzy ----------

def _clyde_x_rzad(t):
    a, b, c, d = CLYDE_X
    if t < PROG[0]:
        return lerp(a, b, ease(pr(t, *KORYTARZ))), "korytarz", 0 < pr(t, *KORYTARZ) < 1
    if t < PROG[0] + PROG[1]:
        k = pr(t, *PROG)
        return lerp(b, c, k), ("korytarz", "lalki", ease(k)), True
    k = pr(t, *DO_KUCHNI)
    return lerp(c, d, ease(k)), "lalki", 0 < k < 1


def clyde(u, t):
    x, rzad, idzie = _clyde_x_rzad(t)
    flip = -1.0
    tip = ease(pr(t, CHWYT, 0.3)) * (1 - ease(pr(t, OPUSZCZA[0], 0.3)))
    lean = 4.0 * flip * tip  # skłon w przód przy uchyleniu
    w_dloni = CHWYT <= t < PUSZCZA

    def cel(s):
        chwyt_na_glowie = s["punkt"](*CHWYT_KAPELUSZA)
        spocz = U.Uklad.dlon_z_kata(s, 4.0)
        if t < SIEGA[0] or t >= WRACA[0] + WRACA[1]:
            return 4.0
        if t < CHWYT:
            k = ease(pr(t, *SIEGA))
            return lerp(spocz[0], chwyt_na_glowie[0], k), lerp(spocz[1], chwyt_na_glowie[1], k)
        if t < PUSZCZA:
            k = ease(pr(t, *UNOSI)) * (1 - ease(pr(t, *OPUSZCZA)))
            fala = 2.5 * math.sin((t - UNOSI[0]) * 9) * ease(pr(t, UNOSI[0] + 0.3, 0.1)) * (1 - pr(t, *OPUSZCZA))
            return chwyt_na_glowie[0] + 10 * flip * k, chwyt_na_glowie[1] - 20 * k + fala
        k = ease(pr(t, *WRACA))
        return lerp(chwyt_na_glowie[0], spocz[0], k), lerp(chwyt_na_glowie[1], spocz[1], k)
    przechyl = 14 * flip * ease(pr(t, *UNOSI)) * (1 - ease(pr(t, *OPUSZCZA)))
    kap = {"gdzie": "dlon", "chwyt": CHWYT_KAPELUSZA, "przechyl": przechyl} if w_dloni else {"gdzie": "glowa"}
    s = u.lalka("Clyde", "clyde", x, CLYDE_H, rzad=rzad, flip=flip, lean=lean, hop=5 * idzie, wejscie=False, przod=cel,
                tyl=2.0, lokiec=("przod", "dol"), kapelusz=dict(kap, nazwa="kapelusz"))
    # kontrole Clyde'a
    x0, y0, x1, y1 = otwor_drzwi()
    if s["p"] < P.miasto:
        u.w_otworze("Clyde", (x0, y0, x1, y1, u.p("drzwi")), "Clyde w korytarzu: widać go tylko w otworze drzwi")
    glowa = s["punkt"](152, 128)
    if x < x1 - 20:
        u.punkt("Clyde", (*glowa, s["p"]), "Clyde: głowa widoczna")
    if t >= DO_KUCHNI[0]:
        u.widac("Clyde", 0.97, "Clyde w kuchni: nic go nie zasłania (≥ 97%)", oprocz=("rampa", "kapelusz"))
    if CHWYT + 0.1 <= t < PUSZCZA - 0.1:
        u.widac("kapelusz", 0.97, "kapelusz w dłoni: zasłania go tylko dłoń Clyde'a", oprocz=("Clyde",))
    return s


def bonnie(u, t, garnek, brzeg):
    """Bonnie za kuchenką: miesza, wyjmuje łyżkę, odwraca się do Clyde'a."""
    flip = lerp(-1.0, 1.0, ease(pr(t, *ODWROT)))
    lyzka = U.ark_rek("lyzka")
    kl = 50 / lyzka.hs  # piksele kadru na piksel arkusza łyżki (wycinek 50 px jak dotąd)
    gx = (brzeg[0] + brzeg[1]) / 2
    ry = brzeg[2]
    pg = brzeg[3]
    w_garnku = pg - 0.001  # łyżka w garnku: za przednią ścianką garnka, przed kuchenką i przed Bonnie

    def czerpak_w_garnku(tt, k_mieszania):
        om = 2 * math.pi * 1.0 * (tt - BONNIE_CHWYT[0])
        bx = gx + lerp(9, 12 * math.sin(om), k_mieszania)
        by = ry + 10 + 2 * math.cos(om) * k_mieszania
        rot = 180 + lerp(24, 10 * math.cos(om), k_mieszania)  # oparta o brzeg → pionowo i chybocze się przy mieszaniu
        return bx, by, rot

    def dlon_dla(bx, by, rot):
        dx, dy = SW._off(0, (CZERPAK_LYZKI[1] - CHWYT_LYZKI[1]) * kl, rot)
        return bx - dx, by - dy

    # gdzie jest łyżka i gdzie ma być dłoń
    k_mies = ease(pr(t, BONNIE_CHWYT[0] + BONNIE_CHWYT[1], 0.3))
    bx, by, rot = czerpak_w_garnku(min(t, MIESZA_DO), k_mies)
    dlon_w_garnku = dlon_dla(bx, by, rot)
    wyj = ease(pr(t, *WYJMUJE))
    rot_l = lerp(rot, 180.0, wyj)

    nad_garnkiem = (gx + 8, ry - 52)  # łyżka wyjęta pionowo w górę: koniec czerpaka nad brzegiem

    def cel(s):
        przed_soba = (s["x"] + 62 * s["flip"], 506 + 2 * math.sin(t * 2.2))  # na wysokości pasa, przed sobą
        if t < BONNIE_CHWYT[0]:
            return 0.0
        if t < BONNIE_CHWYT[0] + BONNIE_CHWYT[1]:
            spocz = U.Uklad.dlon_z_kata(s, 0.0)
            k = ease(pr(t, *BONNIE_CHWYT))
            return lerp(spocz[0], dlon_w_garnku[0], k), lerp(spocz[1], dlon_w_garnku[1], k)
        if t < WYJMUJE[0]:
            return dlon_w_garnku
        if t < ODWROT[0]:
            return lerp(dlon_w_garnku[0], nad_garnkiem[0], wyj), lerp(dlon_w_garnku[1], nad_garnkiem[1], wyj)
        # najpierw w bok na wysokości „nad garnkiem” (łyżka nie przejeżdża przez ściankę garnka), potem w dół do pasa
        kx = ease(pr(t, ODWROT[0], ODWROT[1]))
        ky = ease(pr(t, ODWROT[0] + ODWROT[1] - 0.05, 0.3))
        return lerp(nad_garnkiem[0], przed_soba[0], kx), lerp(nad_garnkiem[1], przed_soba[1], ky)
    s = u.lalka("Bonnie", "bonnie", BONNIE_X, BONNIE_H, flip=flip, przod=cel, tyl=0.0, lokiec=("dol", "dol"))
    trzyma = s is not None and t >= BONNIE_CHWYT[0] + BONNIE_CHWYT[1]
    if trzyma:
        hx, hy = s["przod"]["dlon"]
        geo = U.Geo(hx, hy, kl, CHWYT_LYZKI, rot_l, 1.0, w_garnku)
        # wyjęta: cała łyżka nad brzegiem — od tej chwili jest w dłoni (przed dłonią), a nie w garnku, nawet gdy dłoń
        # zjedzie niżej niż brzeg (stan się nie cofa: łyżka nie „wraca” do garnka, od którego jest daleko)
        nad = t >= ODWROT[0] or (t >= WYJMUJE[0] and geo(*KONIEC_LYZKI)[1] < ry - 1)
        u.w_dloni("łyżka", lyzka, s, CHWYT_LYZKI, 50, rot_l, p=None if nad else w_garnku, z=0.08 if nad else 0.0)
        u.relacje.append(("łyżka", "Bonnie", "w dłoni"))
        if not nad:
            u.relacje.append(("łyżka", "garnek", "w garnku"))
            u.w_naczyniu("łyżka", brzeg, "łyżka w garnku: nic nie wystaje spod brzegu")
        if t >= ODWROT[0]:
            u.widac("łyżka", 0.97, "łyżka w dłoni po odwróceniu: nic jej nie zasłania", oprocz=("Bonnie",))
    else:  # łyżka oparta w garnku, zanim Bonnie ją weźmie
        dl = dlon_dla(*czerpak_w_garnku(t, 0.0))
        u.rzecz("łyżka", lyzka, dl[0], dl[1], w_garnku, CHWYT_LYZKI, 50, rot=czerpak_w_garnku(t, 0.0)[2])
        u.relacje.append(("łyżka", "garnek", "w garnku"))
        u.w_naczyniu("łyżka", brzeg, "łyżka w garnku: nic nie wystaje spod brzegu")
    if s is not None and s["h"] and t >= 1.65:
        u.punkt("Bonnie", (*s["punkt"](152, 128), s["p"]), "Bonnie: głowa widoczna")
        u.punkt("Bonnie", (*s["przod"]["dlon"], s["p"]), "Bonnie: dłoń z łyżką widoczna", r=6, ile=0.15)
        plyta = u.powierzchnia("kuchenka", "plyta", 0.5)
        u.w_naczyniu("Bonnie", (0, 0, plyta[1] + 3, u.obiekty["kuchenka"]["p"]), "Bonnie: od pasa w dół za kuchenką")
    return s


def przyjaciolka(u, t):
    """Przyjaciółka za stołem, dłoń na blacie obok kubka."""
    blat = u.powierzchnia("stół", "blat", FU_DLON_PRZYJ)
    stoi = SW.wejscie(1.0 + 0.08 * (sum(map(ord, "przyjaciolka")) % 5)) >= 1.0
    t_stoi = (1.0 + 0.08 * (sum(map(ord, "przyjaciolka")) % 5) + 0.6) if SW.BUDOWA["t"] is not None else -9.0
    k_reki = ease(pr(t, t_stoi, 0.3))  # dłoń idzie na blat dopiero, kiedy lalka stoi (nie sięga zza rampy)

    def cel(s):
        if k_reki <= 0:
            return 0.0
        spocz = U.Uklad.dlon_z_kata(s, 0.0)
        na_blacie = (blat[0], blat[1] - s["r_dloni"])  # dłoń leży NA blacie: dół dłoni na krawędzi blatu
        return lerp(spocz[0], na_blacie[0], k_reki), lerp(spocz[1], na_blacie[1], k_reki)
    s = u.lalka("przyjaciółka", "przyjaciolka", PRZYJ_X, 290, flip=1.0, przod=cel, tyl=0.0, lokiec=("dol", "dol"))
    if s is not None and stoi and k_reki >= 1:
        hx, hy = s["przod"]["dlon"]
        u.dotyka("stół", (hx, hy + s["r_dloni"], s["p"]), "przyjaciółka: dłoń leży na blacie (wycinek stołu pod dłonią)", 2.0)
        u.relacje.append(("przyjaciółka", "stół", "dłoń na blacie"))
    return s


# ---------- ujęcie ----------

def s_kuchnia(st, w, t, T):
    """W ciasnej kuchni Bonnie miesza kakao; drzwiami wchodzi Clyde w kapeluszu i uchyla go; z nitki zjeżdżają dwa
    serduszka (ulepszony silnik: rzędy, przyczepianie, ręka z łokciem, kontrola — uklad.py)."""
    kam(st, t, 16, 640, 390, 1.1, 0.8)
    u = U.Uklad(st, t)
    dekoracja(u, w, t)
    garnek = u.na("garnek", "garnek", "kuchenka", "plyta", FU_GARNEK, 50)
    kubek = u.na("kubek", "kubek", "stół", "blat", FU_KUBEK, 30)  # noqa: F841
    brzeg =(garnek(20, BRZEG_GARNKA)[0], garnek(140, BRZEG_GARNKA)[0], garnek(80, BRZEG_GARNKA)[1], garnek.p)
    bonnie(u, t, garnek, brzeg)
    przyjaciolka(u, t)
    clyde(u, t)
    for n in range(2):  # jak w starej wersji (gag 6, GAGI.md)
        with u.obiekt(f"serce {n + 1}", "rzecz", p=P.rekwizyty):
            J.hang(st, J.serce(), 620 + 90 * n, 160 + 20 * n, P.rekwizyty, pr(t, 4.4 + 0.3 * n, 1.0) * (1 - pr(t, 8.2 + 0.1 * n, 0.5)),
                   t, 460 + n, h=60, drop=420)
    with u.obiekt("kajdanki", "rzecz", p=P.rekwizyty):
        J.hang(st, J.rek("kajdanki"), 665, 170, P.rekwizyty, pr(t, 8.7, 0.9), t, 470, h=64, drop=420)
    A.koniec(st, w, t)


# ---------- uruchamianie: klip, porównanie, kontrola ----------

def _render():
    os.environ.setdefault("NAPISY", "0")
    import render as R
    return R


def podmien(R):
    i = SW.I[KLUCZ]
    stara = R.FNS[i]
    R.FNS[i] = s_kuchnia
    return i, stara


CHWILE = (0.6, 1.45, 1.75, 2.05, 2.6, 3.4, 3.7, 4.6, 6.0, 9.8)


def porownanie(out):
    R = _render()
    i = SW.I[KLUCZ]
    a, b = R.SCENES[i][:2]
    chwile = (1.45, 2.05, 2.6, 3.7, 4.6, 9.8)
    R.FNS[i] = A.s_kuchnia_stara
    stare = [R.frame(a + c) for c in chwile]
    podmien(R)
    nowe = [R.frame(a + c) for c in chwile]
    tw, th = 640, 360
    f = ImageFont.truetype(U.FONT, 22)
    arkusz = Image.new("RGB", (tw * 2, (th + 4) * len(chwile) + 40), (20, 18, 16))
    d = ImageDraw.Draw(arkusz)
    d.text((tw / 2, 20), "STARE (ujecia_a.s_kuchnia_stara)", font=f, fill=(255, 220, 120), anchor="mm")
    d.text((tw * 1.5, 20), "NOWE (uklad.py)", font=f, fill=(140, 230, 140), anchor="mm")
    for r, c in enumerate(chwile):
        for col, im in enumerate((stare[r], nowe[r])):
            arkusz.paste(im.resize((tw, th), Image.LANCZOS), (col * tw, 40 + r * (th + 4)))
        d.text((8, 44 + r * (th + 4)), f"{c:.2f} s", font=f, fill=(255, 255, 0))
    arkusz.save(out)
    return out


def kontrola(katalog):
    """Arkusz kontroli: w wybranych chwilach klatka + rzut z góry + wynik kontroli; zbliżenia dłoni z rzeczą; raport ze
    wszystkich klatek (co 2. klatka renderu)."""
    R = _render()
    i, _ = podmien(R)
    a, b = R.SCENES[i][:2]
    T = b - a
    kat = Path(katalog)
    kat.mkdir(parents=True, exist_ok=True)
    f = ImageFont.truetype(U.FONT, 15)
    wiersze, raport = [], []
    for c in CHWILE:
        st, _ = R.uloz(a + c)
        img = st.render()
        wyn, idb, pelne, kod, widac = U.kontrola(st)
        plan = U.rzut(st, pelne, widac, wyn)
        wiersz = Image.new("RGB", (1280, 360 + 18 * max(1, len(wyn)) // 2 + 30), (250, 247, 240))
        wiersz.paste(img.resize((640, 360), Image.LANCZOS), (0, 0))
        wiersz.paste(plan, (640, 0))
        d = ImageDraw.Draw(wiersz)
        d.text((8, 6), f"{c:.2f} s", font=ImageFont.truetype(U.FONT, 22), fill=(255, 255, 0))
        for n, (opis, ok, wart) in enumerate(wyn):
            x = 8 + 636 * (n % 2)
            y = 366 + 18 * (n // 2)
            d.text((x, y), f"{'OK ' if ok else 'BŁĄD '} {opis} — {wart}", font=f, fill=(20, 100, 40) if ok else (200, 40, 40))
        wiersze.append(wiersz)
        raport.append((c, wyn))
    hgt = sum(w_.height for w_ in wiersze)
    ark = Image.new("RGB", (1280, hgt), (250, 247, 240))
    y = 0
    for w_ in wiersze:
        ark.paste(w_, (0, y))
        y += w_.height
    ark.save(kat / "kontrola_kuchnia.png")
    # zbliżenia dłoni z rzeczą (wytyczne 1.28: wycinek 240 px wokół dłoni w kilku chwilach)
    dlonie = []
    for c in (1.9, 2.4, 3.1, 3.45, 3.75, 4.1, 4.8):
        st, _ = R.uloz(a + c)
        img = st.render()
        for nazwa, xy in st.uklad.dlonie.items():
            sx, sy = U._ekran(st, *xy)
            box = (int(sx - 120), int(sy - 120), int(sx + 120), int(sy + 120))
            dlonie.append((c, nazwa, img.crop(box)))
    if dlonie:
        cols = 7
        rows = math.ceil(len(dlonie) / cols)
        zb = Image.new("RGB", (240 * cols, 262 * rows), (20, 18, 16))
        d = ImageDraw.Draw(zb)
        for n, (c, nazwa, im) in enumerate(dlonie):
            x, y = 240 * (n % cols), 262 * (n // cols)
            zb.paste(im, (x, y + 22))
            d.text((x + 6, y + 3), f"{nazwa} · {c:.2f} s", font=f, fill=(255, 230, 140))
        zb.save(kat / "dlonie_kuchnia.png")
    # wszystkie klatki: które kontrole kiedykolwiek nie przeszły
    zle = {}
    n = math.ceil(T * R.FPS)
    for fr in range(0, n, 2):
        c = fr / R.FPS
        st, _ = R.uloz(a + c)
        wyn = U.kontrola(st)[0]
        for opis, ok, wart in wyn:
            zle.setdefault(opis, [0, 0, []])
            zle[opis][1] += 1
            if not ok:
                zle[opis][0] += 1
                zle[opis][2].append(f"{c:.2f} s: {wart}")
    with open(kat / "raport_kuchnia.md", "w") as fh:
        fh.write(f"# Kontrola ujęcia 25 „kuchnia” (uklad.py) — {n // 2 + n % 2} klatek co 2.\n\n")
        fh.write("| kontrola | klatek z błędem / sprawdzonych | pierwsze błędy |\n|---|---|---|\n")
        for opis, (nz, nk, gdzie) in zle.items():
            fh.write(f"| {opis} | {nz} / {nk} | {'; '.join(gdzie[:3])} |\n")
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
        print(klip(arg or HERE / "kuchnia_uklad.mp4"))
    elif cmd == "porownanie":
        print(porownanie(arg or HERE / "porownanie_kuchnia.png"))
    elif cmd == "kontrola":
        print(kontrola(arg or HERE / "kontrola_kuchnia"))
    elif cmd == "dzwiek":
        print(dzwiek(arg, sys.argv[3]))
