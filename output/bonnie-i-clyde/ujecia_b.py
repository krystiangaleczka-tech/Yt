"""Ujęcia aktów 5–8 filmu „Bonnie and Clyde: The Outlaws Made of Paper”: funkcja `s_<klucz>(st, w, t, T)` na ujęcie.

Akt V — łowca (Hamer), VI — Ameryka przestaje kibicować, VII — pułapka, VIII — kto ma legendę. Rozpiska: docs/filmy/bonnie-i-clyde/ujecia/dane.py.
Śmierć i strzały pokazujemy tylko w teatrze cieni (parawan) albo przez ślady (kapelusz, czapki), nigdy ciał.
"""
import math
import sys

from scena import (CX, DROGA_Y, J, OCZY, P, STOPY, Z0, auto, back, bk, blysk, cien, ciezarowka, cmentarz, drukarnia, ease, ease_out,
                   eastham, jazda, kam, kino, lalka, las, lerp, mapa_punkt, mapa_scena, miasto, motocykl, noise, parawan, podpis, pr,
                   preria, punkt, teatr_gazet, widownia, wnetrze)
from ujecia_a import KARABIN, REV, _reflektory, auto_srodek, koniec, tab

NOC = (0.7, 0.72, 0.85)
LOWCY = (("hamer", "Frank Hamer"), ("gault", "Manny Gault"), ("alcorn", "Bob Alcorn"), ("hinton", "Ted Hinton"),
         ("jordan", "Henderson Jordan"), ("oakley", "Prentiss Oakley"))


def _bump(t, t0, d=0.15):
    return max(0.0, 1.0 - abs(t - t0) / d)


def _biuro(st, t, w, kapelusz=False, mapa=True):
    """Biuro Hamera w Austin (jak w akcie III: zielona ściana, biurko, krzesło); mapa stanów na ścianie po lewej."""
    wnetrze(st, t, w, sciana="zielen", okna=(1080,), meble=(("biurko", 560, 170, P.lalki + 0.02), ("krzeslo", 820, 200, P.lalki + 0.005)),
            zarowki=(560,))
    if kapelusz:
        st.put(J.rek("kapelusz_fedora"), 826, 520, P.lalki + 0.006, h=40, anchor=(0.5, 1.0), tint=(1.0, 0.95, 0.75))
    if mapa:
        J.hang(st, J.mapa_plansza(), 280, 60, P.miasto + 0.01, bk(w, 0.3, 0.9), t, 610, w=380, drop=500, sway=0.2, strings=(0.08, 0.92))


def _ganek(st, t, w):
    """Ganek domu Hamera w Austin: preria za domem, weranda z balustradą (podłoga ganku na linii stóp)."""
    preria(st, t, w, droga=0.0, slupy=False, wiatrak=True)
    Z0.rise(st, J.ganek(), 640, STOPY + 120, P.drzewa, bk(w, 0.35), t, 620, w=1300, wob=0.0)


# ===================== AKT V · KTO W KOŃCU RUSZYŁ ZA NIMI =====================

def s_odbicie(st, w, t, T):
    """Mgła nad Eastham; więźniowie wyciągają broń z rowu, strażnik pada; z mgły trąbi Ford, więźniowie wskakują na stopnie."""
    kam(st, t, 70, 640, 420, 1.0, 0.77, shake=2.0 * (3.2 < t < 3.6))
    eastham(st, t, w, mgla=1.0 - 0.4 * ease(pr(t, 6.0, 4.0)))
    ax = jazda(t, 5.6, 2.4, -400, 620, ease_out)[0] if t < 9.0 else jazda(t, 9.0, 3.0, 620, 1900, ease)[0]
    auto(st, t, ax, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.88, 0.88, 0.92), kurz=t > 9.0)
    for n, (key, x0, off) in enumerate((("wiezien", 280, -200), ("henry_wiezien", 450, -60), ("wiezien2", 980, 110))):
        schyl = ease(pr(t, 1.2 + 0.3 * n, 0.6)) * (1 - ease(pr(t, 2.2 + 0.3 * n, 0.5)))
        wsk = ease(pr(t, 8.0 + 0.2 * n, 0.7))
        x = ax + off if wsk >= 1 else lerp(x0, 620 + off, wsk)
        lalka(st, t, key, x, 290, flip=1 if x0 < 640 else -1, lean=30 * schyl, lift=30 * wsk + 60 * math.sin(math.pi * wsk),
              rece=(50 + 40 * schyl, 30), trzyma=REV() if t > 2.4 + 0.3 * n else None, hop=4 * (0 < wsk < 1))
    blysk(st, 940, 520, P.lalki, t, 3.2, r=220)
    pad = ease(pr(t, 3.4, 1.2))
    lalka(st, t, "crowson", 1160, 310, flip=-1, rece=(40, 0), trzyma=KARABIN(150) if pad < 0.3 else None, sink=0.9 * pad, lean=25 * pad)
    tab(w, t, "BEEP BEEP!", 220, 260, 5.4, 2.4)
    koniec(st, w, t, extra=(0.95, 0.97, 1.02))


def s_straznik(st, w, t, T):
    """Mgła rzednie; na drodze zostaje kapelusz strażnika; podpis „Major Joe Crowson”; światło przygasa."""
    kam(st, t, 71, 700, 540, 1.4, 0.8)
    st.dof = 1.3
    eastham(st, t, w, mgla=lerp(0.6, 0.2, ease(t / T)), kul=False)
    st.put(J.rek("kapelusz_fedora"), 700, 655, P.rampa - 0.01, h=64, anchor=(0.5, 1.0), rot=-12, tint=(0.95, 0.9, 0.8))
    podpis(w, t, "Major Joe Crowson", 700, 520, 1.0, T)
    koniec(st, w, t, dim=1.0 - 0.3 * ease(pr(t, 3.0, 4.0)))


def s_simmons(st, w, t, T):
    """Szef więziennictwa wali pięścią w biurko, aż podskakuje kałamarz; podpis „Lee Simmons, Texas prisons chief”."""
    kam(st, t, 72, 640, 470, 1.3, 0.8)
    wnetrze(st, t, w, sciana="deski", okna=(1050,), meble=(("biurko", 640, 170, P.lalki + 0.02),), zarowki=(640,))
    st.put(J.tag("TEXAS PRISON SYSTEM"), 640, 210, P.miasto + 0.01, h=44, anchor=(0.5, 0.5))
    b = sum(_bump(t, t0) for t0 in (1.6, 2.4, 3.2))
    lalka(st, t, "simmons", 600, 320, flip=1, sink=0.15, lean=4 * b, rece=(100 - 70 * b, 30))
    st.put(J.rek("butelka"), 730, 538 - 30 * b, P.lalki + 0.025, h=34, anchor=(0.5, 1.0), tint=(0.25, 0.25, 0.35), rot=10 * b)
    podpis(w, t, "Lee Simmons, Texas prisons chief", 600, 250, 4.0, 4.6)
    koniec(st, w, t)


def s_hamer(st, w, t, T):
    """Na ganku wysoki mężczyzna w kapeluszu wstaje powoli z bujanego fotela i sięga po karabin; podpis o Hamerze."""
    kam(st, t, 73, 640, 450, 1.1, 0.8)
    _ganek(st, t, w)
    wstaje = ease(pr(t, 1.6, 2.0))
    if bk(w, 0.6) >= 1:
        st.put(J.mebel("fotel_bujany"), 480, STOPY, P.lalki - 0.005, h=240, anchor=(0.5, 1.0), rot=4 * math.sin(t * 2) * (1 - wstaje))
    ma = t > 6.0
    if not ma and bk(w, 0.6) >= 1:
        st.put(J.rek("karabin"), 900, STOPY - 6, P.lalki - 0.004, w=210, anchor=(0.0, 0.5), rot=-80)
    hx = lerp(480, 820, ease(pr(t, 3.8, 1.8)))
    lalka(st, t, "hamer", hx, 340, flip=1, sink=0.2 * (1 - wstaje), rece=(lerp(20, 80, ease(pr(t, 5.4, 0.6))), 10), trzyma=KARABIN(180) if ma else None,
          hop=3 * (3.8 < t < 5.6))
    podpis(w, t, "Frank Hamer, retired Texas Ranger", 640, 250, 3.6, 5.0)
    koniec(st, w, t)


def s_poscigi(st, w, t, T):
    """Radiowóz goni Forda; Ford znika, radiowóz wylatuje z zakrętu i ląduje w rowie kołami do góry; „AGAIN?!”."""
    kam(st, t, 74, 640, 440, lerp(1.1, 0.95, ease(t / T)), 0.78, shake=6.0 * (6.1 < t < 6.5))
    preria(st, t, w, slupy=True, mesa=True)
    fx = jazda(t, 0.8, 2.6, -400, 1800)[0]
    auto(st, t, fx, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], kurz=True)
    h = 220
    if t < 5.0:
        px = jazda(t, 1.8, 3.2, -500, 900)[0]
        auto_srodek(st, t, px, DROGA_Y - h * 0.5, h, 0, kolor="czarny", napis="SHERIFF", pasazerowie=[("policjant", 1, (40, 0))])
    else:
        f = ease(pr(t, 5.0, 1.2))
        cx = lerp(900, 1060, f)
        cy = lerp(DROGA_Y - h * 0.5, DROGA_Y - h * 0.5 + 24, f) - 200 * math.sin(math.pi * f)
        auto_srodek(st, t, cx, cy, h, 180 * f, kolor="czarny", napis="SHERIFF", droga=t * 500)
    tab(w, t, "AGAIN?!", 1040, 290, 6.6, 3.0)
    koniec(st, w, t)


def s_hak_szuflada(st, w, t, T):
    """Hamer zdejmuje z biurka zabawkowy radiowóz i chowa go do szuflady; tabliczka „NO MORE CHASING”."""
    kam(st, t, 75, 580, 470, 1.45, 0.8)
    st.dof = 1.2
    _biuro(st, t, w)
    f = ease(pr(t, 1.2, 1.0))
    lalka(st, t, "hamer", 650, 330, flip=-1, sink=0.15, rece=(lerp(30, 70, ease(pr(t, 0.8, 0.4))) - 40 * f, 20))
    if f < 1 and bk(w, 0.5) >= 1:
        st.put(J.rek("zabawka"), lerp(520, 600, f), 538 + 30 * f, P.lalki + 0.025 - 0.01 * (f > 0.5), h=34, anchor=(0.5, 1.0), alpha=1 - f * f)
    tab(w, t, "NO MORE CHASING", 600, 280, 2.4, 2.8)
    koniec(st, w, t)


def s_hak_teczka(st, w, t, T):
    """Hamer otwiera grubą teczkę; wycinki wyfruwają i same przypinają się do mapy; Hamer stawia kubek kawy i siada wygodnie."""
    kam(st, t, 76, 480, 430, 1.2, 0.8)
    _biuro(st, t, w)
    otw = t > 1.0
    st.put(J.rek("teczka_otwarta" if otw else "teczka"), 540, 538, P.lalki + 0.025, h=46 if otw else 60, anchor=(0.5, 1.0))
    for n in range(8):
        f = ease(pr(t, 1.8 + 0.5 * n, 1.0))
        if f <= 0:
            continue
        tx, ty = 160 + 60 * (n % 4), 120 + 90 * (n // 4)
        x, y = lerp(540, tx, f), lerp(510, ty, f) - 120 * math.sin(math.pi * f)
        st.put(J.gazeta(J.NAGLOWKI[n % len(J.NAGLOWKI)], 80 + n, 360, 300, False), x, y, P.miasto + 0.012, h=lerp(30, 54, f), anchor=(0.5, 0.5),
               rot=(1 - f) * 300 + 6 * (n % 3 - 1), shadow=(3, 4, 4, 0.3))
        if f >= 1:
            st.put(J.rek("pinezka"), x, y - 22, P.miasto + 0.013, h=10, anchor=(0.5, 0.5))
    if t > 6.6:
        st.put(J.rek("kubek"), 640, 538, P.lalki + 0.025, h=30, anchor=(0.5, 1.0))
    lalka(st, t, "hamer", 690, 330, flip=-1, sink=0.15, lean=-8 * ease(pr(t, 7.2, 0.8)), rece=(60 - 30 * ease(pr(t, 7.0, 0.5)), 20))
    koniec(st, w, t)


def s_podkreslenie(st, w, t, T):
    """W aktach jedno zdanie: czerwony ołówek podkreśla je dwa razy; zjeżdża tabliczka „HE WON'T GO BACK”."""
    kam(st, t, 77, 640, 400, 1.0, 0.8)
    st.put(J.sciana("zielen"), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    st.put(J.rek("teczka_otwarta"), 640, 420, P.drzewa, w=1400, anchor=(0.5, 0.5))
    for n, (txt, y) in enumerate((("CLYDE CHAMPION BARROW", 250), ("PAROLED FEB. 2, 1932", 320))):
        st.put(J.tag(txt), 330, y + 60, P.drzewa + 0.002, h=44, anchor=(0.5, 0.5), shadow=None)
    st.put(J.tag("\"I'LL NEVER GO BACK TO EASTHAM\""), 330, 430, P.drzewa + 0.002, h=56, anchor=(0.5, 0.5), shadow=None)
    x0, x1 = 80, 580
    for n, (a, d, dy) in enumerate(((2.0, 2.0, 0), (4.6, 1.8, 10))):
        f = ease(pr(t, a, d))
        if f > 0:
            st.line([(x0, 468 + dy), (lerp(x0, x1, f), 468 + dy + 3 * math.sin(f * 9))], P.drzewa + 0.003, width=5, color=(190, 40, 36))
        if 0 < f < 1:
            st.put(J.rek("olowek"), lerp(x0, x1, f) + 90, 430 + dy, P.drzewa + 0.01, w=200, anchor=(0.95, 0.5), rot=-35, shadow=(4, 6, 6, 0.35))
    tab(w, t, "HE WON'T GO BACK", 640, 150, 8.0, 4.0)
    koniec(st, w, t)


def s_dzien1(st, w, t, T):
    """Zawieszka „DAY 1”; Hamer jedzie starym autem przez prerię z mapą na kolanach."""
    x = lerp(200, 1100, t / T)
    kam(st, t, 78, x, 450, 1.15, 0.78, truck=1.0)
    w.zawieszki = [("DAY 1", x, 160, pr(t, 0.8, 1.0))]
    preria(st, t, w, slupy=True, mesa=True)
    auto(st, t, x, 240, kolor="czarny", pasazerowie=[("hamer", 1, (60, 30))], kurz=True)
    st.put(J.rek("mapa_zwoj"), x - 70, DROGA_Y - 150, P.auta + 0.003, h=40, anchor=(0.5, 0.5), rot=-8)
    koniec(st, w, t)


def s_hamer_motel(st, w, t, T):
    """Hamer pokazuje recepcjoniście zdjęcie Bonnie; recepcjonista kiwa głową i wskazuje drogę; na ladzie piramida puszek po fasoli."""
    kam(st, t, 79, 620, 460, 1.2, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(1050,), meble=(("lada", 700, 150, P.lalki + 0.02),), zarowki=(700,))
    for n, (x, r) in enumerate(((560, 0), (594, 0), (628, 0), (577, 1), (611, 1), (594, 2))):
        if bk(w, 0.6) >= 1:
            st.put(J.rek("puszka"), x, STOPY - 150 - 36 * r, P.lalki + 0.025, h=36, anchor=(0.5, 1.0))
    kiwa = 5 * math.sin(t * 9) * (3.0 < t < 5.0)
    lalka(st, t, "recepcjonista", 800, 300, flip=-1, sink=0.08, lean=kiwa, rece=(lerp(20, 120, ease(pr(t, 5.4, 0.5))), 0))
    lalka(st, t, "hamer", 420, 340, flip=1, rece=(lerp(20, 90, ease(pr(t, 0.8, 0.6))), 10),
          trzyma=(J.zdjecie_bonnie(), 70, (0.5, 0.8), 90, True) if t > 1.0 else None)
    koniec(st, w, t)


def s_dzien20(st, w, t, T):
    """Zawieszka „DAY 20”; tablica „STATE LINE”; Ford przemyka przez granicę, radiowóz hamuje przed nią z piskiem."""
    kam(st, t, 80, 640, 460, 1.0, 0.78)
    w.zawieszki = [("DAY 20", 640, 160, pr(t, 0.6, 1.0))]
    preria(st, t, w, slupy=True, tablice=[("STATE LINE", 760)])
    auto(st, t, jazda(t, 1.2, 2.6, -400, 1800)[0], 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], kurz=True)
    px = jazda(t, 2.4, 3.4, -500, 520, ease_out)[0]
    auto(st, t, px, 220, kolor="czarny", napis="SHERIFF", p=P.auta + 0.004, przechyl=3 * math.sin(math.pi * pr(t, 5.2, 0.6)),
         pasazerowie=[("policjant", 1, (40 + 80 * (t > 7.0), 0))])
    if 5.0 < t < 7.2:
        for n in range(4):
            f = pr(t, 5.0 + 0.2 * n, 1.4)
            st.put(J.glow(r=256, color=(200, 180, 140)), px + 200 - 80 * n, DROGA_Y - 20 - 40 * f, P.auta + 0.01, w=120 + 160 * f,
                   anchor=(0.5, 0.5), alpha=0.5 * (1 - f), shadow=None)
    tab(w, t, "SCREECH!", 520, 300, 5.0, 2.0)
    tab(w, t, "NOT MY STATE...", 520, 300, 7.4, 3.6)
    koniec(st, w, t)


def s_mapa(st, w, t, T):
    """Hamer przypina do mapy znaczniki: Teksas, Oklahoma, Missouri, Luizjana; łączy je czerwoną nicią."""
    kam(st, t, 81, 640, 400, 1.0, 0.72)
    x0, y0, sk = mapa_scena(st, t, w, sciana="zielen", wd=780, x=560)
    pkt = [mapa_punkt((x0, y0), sk, m) for m in ("Dallas", "Atoka", "Joplin", "Ruston")]
    for n, (px, py) in enumerate(pkt):
        k = pr(t, 1.4 + 1.2 * n, 0.3)
        if k > 0:
            st.put(J.rek("pinezka"), px, py, P.wzgorza + 0.02, h=18 * back(k, 1.6), anchor=(0.5, 0.5))
        if n > 0:
            f = ease(pr(t, 1.6 + 1.2 * n, 0.8))
            if f > 0:
                a = pkt[n - 1]
                st.line([a, (lerp(a[0], px, f), lerp(a[1], py, f))], P.wzgorza + 0.019, width=3, color=(190, 40, 36))
    lalka(st, t, "hamer", 1060, 340, flip=-1, rece=(110 + 20 * math.sin(t * 2), 20))
    koniec(st, w, t)


def s_petle(st, w, t, T):
    """Czerwona nić na mapie układa się w pętle wzdłuż granic stanów; każda pętla wraca do Dallas, do dwóch małych domków."""
    x0, y0, sk = mapa_scena(st, t, w, sciana="zielen", wd=900, x=640, y=20)
    dx, dy = mapa_punkt((x0, y0), sk, "Dallas")
    zb = ease(pr(t, 9.5, 4.0))
    kam(st, t, 82, lerp(640, dx, zb), lerp(360, dy, zb), lerp(1.05, 1.7, zb), 0.72)
    for n, m in enumerate(("Atoka", "Joplin", "Commerce", "Ruston", "Wellington")):
        cx, cy = mapa_punkt((x0, y0), sk, m)
        f = pr(t, 0.8 + 1.7 * n, 1.6)
        if f <= 0:
            continue
        vx, vy = cx - dx, cy - dy
        dl = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / dl, vx / dl
        pts = []
        for i in range(int(40 * f) + 1):
            s = i / 40
            a, b = math.sin(math.pi * s), 0.35 * dl * math.sin(2 * math.pi * s)
            pts.append((dx + vx * a + nx * b, dy + vy * a + ny * b))
        if len(pts) > 1:
            st.line(pts, P.wzgorza + 0.019, width=3, color=(190, 40, 36))
    for n in range(2):
        k = ease(pr(t, 9.6 + 0.3 * n, 0.6))
        if k > 0:
            st.put(J.fasada("dom"), dx - 16 + 32 * n, dy, P.wzgorza + 0.021, h=34 * back(k, 1.5), anchor=(0.5, 1.0), shadow=(2, 3, 3, 0.3))
    tab(w, t, "HOME", dx, dy - 120, 11.0, 3.4)
    koniec(st, w, t)


# ===================== AKT VI · KIEDY AMERYKA PRZESTAŁA KIBICOWAĆ =====================

def s_grapevine(st, w, t, T):
    """„DAY 50 · Easter Sunday”; wiejska droga, kwitnące drzewa, Ford na poboczu; nadjeżdżają dwaj motocykliści i zwalniają."""
    kam(st, t, 83, lerp(560, 700, ease(t / T)), 450, 1.05, 0.78)
    w.zawieszki = [("DAY 50 · Easter Sunday", 640, 160, pr(t, 0.8, 1.0))]
    preria(st, t, w, slupy=False, zielen=True)
    for n, x in enumerate((180, 1160, 620)):
        Z0.rise(st, J.drzewo(n + 3, (236, 186, 200)), x, 690, P.wzgorza + 0.02, bk(w, 0.3 + 0.05 * n), t, 630 + n, h=360 + 40 * n, wob=0.1)
    for n in range(10):
        y = (t * 30 + n * 83) % 520 + 120
        st.put(J.platek(), (n * 137) % 1280 + 30 * math.sin(t + n), y, P.drzewa + 0.02, h=10, anchor=(0.5, 0.5), rot=t * 90 + n * 40)
    auto(st, t, 920, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))])
    for n, key in enumerate(("murphy", "wheeler")):
        mx = jazda(t, 2.0 + 0.4 * n, 4.0, -300 - 200 * n, 360 - 220 * n, ease_out)[0]
        motocykl(st, t, mx, 190, jezdziec=key, p=P.auta + 0.004 * n)
    koniec(st, w, t)


def s_grapevine_cien(st, w, t, T):
    """Za parawanem dwa błyski, dwie sylwetki przy motocyklach padają; motocykl przewraca się z łoskotem (szczyt 2)."""
    kam(st, t, 84, 640, 460, 1.3, 0.79, lens=1.4, shake=5.0 * (2.4 < t < 2.8))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    sil = dict(tint=(0.08, 0.06, 0.05), alpha=1.0, blur=1.6)
    motocykl(st, t, 330, 130, y=y0 - 26, p=p0 + 0.001, **sil)
    motocykl(st, t, 560, 130, y=y0 - 26, p=p0 + 0.0012, rot=-75 * ease(pr(t, 2.4, 0.4)), **sil)
    auto(st, t, 1000, 170, y=y0 - 26, p=p0 + 0.0008, flip=-1, shadow=None, szyby=False, **sil)
    for n, (key, x) in enumerate((("murphy", 430), ("wheeler", 680))):
        pad = ease(pr(t, 1.8 + 0.3 * n, 1.2))
        cien(st, t, key, x, 250, y0 - 26, p0 + 0.002, flip=1, rece=(20, 0), sink=0.9 * pad, lean=-22 * pad)
    blysk(st, 900, y0 - 150, p0 + 0.003, t, 1.5, r=260)
    blysk(st, 920, y0 - 140, p0 + 0.003, t, 1.8, r=240)
    koniec(st, w, t, dim=0.88)


def s_tullis(st, w, t, T):
    """Przy trumnie młoda kobieta w białej sukni ślubnej; z góry powoli spadają płatki; podpis „Maree Tullis”."""
    kam(st, t, 85, 600, 470, 1.25, 0.8)
    cmentarz(st, t, w)
    if bk(w, 0.6) >= 1:
        st.put(J.rek("trumna"), 700, 676, P.lalki + 0.07, w=320, anchor=(0.5, 1.0))
        st.put(J.rek("kwiaty"), 700, 610, P.lalki + 0.075, h=70, anchor=(0.5, 1.0))
    lalka(st, t, "tullis", 460, 290, flip=1, lean=6, rece=(30, 20))
    for n in range(14):
        if t < 0.6 + 0.2 * n:
            continue
        y = (t * 36 + n * 97) % 760 - 40
        st.put(J.platek((248, 236, 240)), 200 + (n * 83) % 900 + 20 * math.sin(t + n), y, P.rekwizyty, h=12, anchor=(0.5, 0.5),
               rot=t * 70 + n * 30, sx=math.cos(t * 2 + n))
    podpis(w, t, "Maree Tullis", 460, 240, 2.5, 4.0)
    koniec(st, w, t, dim=0.92)


def s_gazety_zle(st, w, t, T):
    """Nowe gazety o bezlitosnej Bonnie; ludzie zgniatają je i rzucają na ziemię; kolejka przy kiosku się rozchodzi."""
    kam(st, t, 86, 680, 430, lerp(1.1, 0.95, ease(t / T)), 0.79)
    miasto(st, t, w, fasady=(("kiosk", 380), ("apteka", 900)), tyl=(("dom", 160), ("bank", 700)))
    lalka(st, t, "gazeciarz", 380, 240, flip=1, rece=(lerp(130, 20, ease(pr(t, 5.0, 1.0))), 0))
    for n, key in enumerate(("bezrobotny", "przechodnia", "przechodzien3", "przechodzien", "przechodnia2")):
        x0 = 560 + 120 * n
        odch = ease(pr(t, 5.5 + 0.3 * n, 3.0))
        x = x0 + (1 if n % 2 else -1) * 900 * odch
        g = ease(pr(t, 2.4 + 0.4 * n, 0.5))
        out = lalka(st, t, key, x, 300 - 6 * (n % 2), flip=(-1 if n % 2 == 0 else 1) if odch > 0 else -1, rece=(lerp(80, 20, ease(pr(t, 3.0 + 0.4 * n, 0.3))), 0),
                    hop=4 * (0 < odch < 1))
        f = pr(t, 3.0 + 0.4 * n, 0.5)
        if g < 1 and out:
            st.put(J.gazeta("BONNIE LAUGHED AS HE DIED", 90 + n, 360, 300, False), out[0], out[1], P.lalki + 0.03, h=lerp(70, 26, g), anchor=(0.5, 0.6),
                   sy=lerp(1.0, 0.6, g), rot=40 * g)
        elif f > 0:
            st.put(J.gazeta("BONNIE LAUGHED AS HE DIED", 90 + n, 360, 300, False), x0 + 20, lerp(560, STOPY - 24, f * f), P.rampa - 0.01, h=22,
                   anchor=(0.5, 1.0), sy=0.6, rot=60 * n)
    koniec(st, w, t)


def s_listy_gon(st, w, t, T):
    """Na słupie wyrastają kolejne listy gończe z nagrodą; farmer z dubeltówką przystaje, czyta i odwraca się w stronę drogi."""
    kam(st, t, 87, 640, 440, 1.15, 0.8)
    preria(st, t, w, slupy=False)
    st.put(J.slup(), 600, STOPY, P.lalki - 0.01, h=620, anchor=(0.5, 1.0))
    for n, (x, y, nag) in enumerate(((556, 230, "$500"), (650, 300, "$1000"), (560, 400, "$1000"), (648, 470, "$2500"))):
        k = pr(t, 0.8 + 1.0 * n, 0.4)
        if k > 0:
            s_ = back(k, 1.6)
            st.put(J.rek("plakat"), x, y, P.lalki - 0.008 + 0.0005 * n, h=120 * s_, anchor=(0.5, 0.5), rot=-4 + 3 * n)
            st.put(J.tag("REWARD " + nag), x, y + 70 * s_, P.lalki - 0.007 + 0.0005 * n, h=24 * s_, anchor=(0.5, 0.5), shadow=None)
    fx = jazda(t, 3.4, 3.0, 1400, 800, ease_out)[0]
    lalka(st, t, "farmer", fx, 310, flip=-1 if t < 8.6 else 1, lean=-6 * (6.4 < t < 8.6), rece=(50, 20), trzyma=KARABIN(160), hop=4 * (3.4 < t < 6.4))
    koniec(st, w, t)


def s_commerce(st, w, t, T):
    """Ford ugrzązł w rowie pod Commerce; dwaj stróże prawa idą przez pole, żeby pomóc."""
    kam(st, t, 88, 680, 450, 1.05, 0.78)
    preria(st, t, w, slupy=True, plot=True)
    auto(st, t, 480, 230, y=DROGA_Y + 40, przechyl=-14, droga=t * 300, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))])
    for n, key in enumerate(("campbell", "boyd")):
        x = jazda(t, 1.0 + 0.3 * n, 6.0, 1400 + 90 * n, 900 + 120 * n)[0]
        lalka(st, t, key, x, 300 - 10 * n, flip=-1, rece=(20 + 50 * (n == 1) * (t > 6), 0), hop=4 * (1.0 < t < 7.3))
    koniec(st, w, t)


def s_commerce_cien(st, w, t, T):
    """Za parawanem błysk, starszy konstabl pada; komendant podnosi ręce i wsiada do Forda."""
    kam(st, t, 89, 640, 460, 1.3, 0.79, lens=1.4, shake=3.0 * (1.5 < t < 1.8))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    auto(st, t, 420, 170, y=y0 - 6, p=p0 + 0.0008, przechyl=-12, tint=(0.08, 0.06, 0.05), alpha=1.0, shadow=None, blur=1.6, szyby=False)
    pad = ease(pr(t, 1.8, 1.2))
    cien(st, t, "campbell", 760, 250, y0 - 26, p0 + 0.002, flip=-1, rece=(20, 0), sink=0.9 * pad, lean=22 * pad)
    bx = lerp(900, 560, ease(pr(t, 3.4, 2.0)))
    cien(st, t, "boyd", bx, 260, y0 - 26, p0 + 0.002, k=1.0 - ease(pr(t, 5.4, 0.5)), flip=-1, rece=(170 * ease(pr(t, 2.0, 0.4)),) * 2,
         hop=4 * (3.4 < t < 5.4))
    blysk(st, 540, y0 - 170, p0 + 0.003, t, 1.5, r=240)
    koniec(st, w, t, dim=0.9)


def s_boyd(st, w, t, T):
    """Komendant na tylnym siedzeniu z rękami w górze; Bonnie odwraca się do niego z uniesionym palcem; podpis."""
    kam(st, t, 90, 600, 470, 1.55, 0.79)
    st.dof = 1.3
    preria(st, t, w, slupy=True, kul=False)
    x = 640 + 6 * math.sin(t * 9)
    auto(st, t, x, 300, droga=t * 400, pasazerowie=[("boyd", (372, 128), (170, 165)),
                                                   ("bonnie", (505, 126), (lerp(0, 150, ease(pr(t, 2.4, 0.4))) + 8 * math.sin(t * 8) * (t > 3), 0), -1)])
    podpis(w, t, "Percy Boyd, police chief", 560, 250, 1.0, 3.6)
    koniec(st, w, t)


def s_boyd_tab(st, w, t, T):
    """Boyd stoi przy drodze i patrzy za odjeżdżającym Fordem; tabliczka „SHE DOESN'T SMOKE CIGARS!”."""
    kam(st, t, 91, 640, 450, 1.05, 0.79)
    preria(st, t, w, slupy=True, tablice=[("KANSAS", 1100)])
    auto(st, t, jazda(t, 1.2, 3.0, 760, 1900, ease)[0], 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], kurz=t > 1.2)
    lalka(st, t, "boyd", 460, 300, flip=1, rece=(lerp(10, 160, ease(pr(t, 5.0, 0.5))) + 10 * math.sin(t * 9) * (t > 5.5), 0))
    tab(w, t, "SHE DOESN'T SMOKE CIGARS!", 480, 230, 3.0, 5.5)
    koniec(st, w, t)


def s_prasa_cygaro(st, w, t, T):
    """Maszyna wypluwa gazety „BONNIE: NO CIGARS!”; stronica gazety zasłania scenę, a za nią jedna gazeta ląduje na biurku Hamera."""
    zmiana = 7.6
    if t < zmiana:
        kam(st, t, 92, 640, 380, 1.0, 0.72, shake=1.0)
        drukarnia(st, t, w, obrot=t * 220)
        lalka(st, t, "drukarz", 1000, 310, flip=-1, rece=(70 + 15 * math.sin(t * 5), 40))
        for n in range(12):
            f = ((t * 0.6 + n / 12) % 1.0)
            if t < 0.6 + n * 0.15:
                continue
            st.put(J.gazeta("BONNIE: NO CIGARS!", n % 4, 360, 480), 820 + f * 900 + 40 * math.sin(n), 300 - f * 520 + 80 * math.sin(f * 3 + n),
                   P.drzewa + 0.02 * (n % 3), h=110, anchor=(0.5, 0.5), rot=f * 200 + n * 30, sx=math.cos(f * 6 + n), shadow=(4, 6, 6, 0.3))
    else:
        kam(st, t, 93, 520, 460, 1.3, 0.8)
        _biuro(st, t, w, kapelusz=True)
        st.put(J.rek("teczka"), 470, 538, P.lalki + 0.025, h=56, anchor=(0.5, 1.0))
        f = pr(t, zmiana + 0.5, 1.6)
        if f > 0:
            st.put(J.gazeta("BONNIE: NO CIGARS!", 7, 360, 480), lerp(760, 610, f) + 40 * math.sin(f * 9) * (1 - f), lerp(-120, 538, ease(f)),
                   P.lalki + 0.026, h=lerp(130, 70, f), anchor=(0.5, 1.0), rot=lerp(30, -8, f), sy=lerp(1.0, 0.5, ease(pr(t, zmiana + 2.0, 0.3))))
    k = ease(pr(t, zmiana - 0.6, 0.6)) * (1 - ease(pr(t, zmiana, 0.6)))  # szybkie ściemnienie: zmiana dekoracji w ciemności
    koniec(st, w, t, dim=1.0 - 0.95 * k)


# ===================== AKT VII · JAK ZASTAWIĆ PUŁAPKĘ NA DUCHA =====================

def s_methvin(st, w, t, T):
    """Hamer przy stole naprzeciw brodatego farmera, między nimi papier „PARDON”; farmer kiwa głową; podpis „Ivy Methvin”."""
    kam(st, t, 93, 640, 460, 1.2, 0.8)
    wnetrze(st, t, w, sciana="deski", okna=(1080,), meble=(("stol", 640, 130, P.lalki + 0.02),), zarowki=(640,), noc_za_oknem=True)
    lalka(st, t, "hamer", 450, 340, flip=1, sink=0.15, rece=(lerp(30, 70, ease(pr(t, 2.8, 0.4))) * (t < 4.4) + 20, 10))
    lalka(st, t, "ivy", 840, 310, flip=-1, sink=0.15, lean=5 * math.sin(t * 9) * (6.0 < t < 7.6), rece=(30, 10))
    st.put(J.rek("pardon"), lerp(560, 670, ease(pr(t, 3.0, 1.2))), STOPY - 130, P.lalki + 0.025, h=60, anchor=(0.5, 1.0))
    podpis(w, t, "Ivy Methvin", 840, 260, 2.4, 3.6)
    koniec(st, w, t)


def s_wiersz(st, w, t, T):
    """Bonnie wręcza matce zeszyt; matka czyta przy lampie, a za oknem czekają światła Forda."""
    w.noc = 1.0
    kam(st, t, 94, 680, 460, 1.2, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(1000,), meble=(("stol", 520, 130, P.lalki + 0.02),), zarowki=(520,), noc_za_oknem=True)
    for n in range(2):
        st.put(J.glow(r=128, color=(255, 240, 190)), 975 + 50 * n, 420, P.miasto + 0.03, w=70, anchor=(0.5, 0.5), mode="add", alpha=0.8,
               shadow=None)
    podala = t > 2.2
    zesz = (J.rek("zeszyt"), 40, (0.5, 0.5), 80, True)
    lalka(st, t, "matka_bonnie", 520, 290, flip=1, sink=0.12, lean=6 * podala, rece=(lerp(20, 80, ease(pr(t, 1.6, 0.6))), 60 * podala),
          trzyma=zesz if podala else None)
    lalka(st, t, "bonnie", 760, 290, flip=-1 if t < 6.0 else 1, rece=(lerp(80, 10, ease(pr(t, 2.2, 0.5))), 0), trzyma=zesz if not podala else None)
    koniec(st, w, t)


def s_pozegnanie(st, w, t, T):
    """Ford przejeżdża powoli obok dwóch domów; w oknach dwie matki machają; Ford znika za zakrętem."""
    w.noc = 0.5
    kam(st, t, 95, 640, 440, 1.0, 0.78)
    miasto(st, t, w, fasady=(("dom", 380), ("dom", 900)), tyl=(), chodnik=True, swiatlo_okien=True)
    for n, (key, x) in enumerate((("matka_bonnie", 380), ("matka_clyde", 900))):
        lalka(st, t, key, x, 250, flip=1, p=P.drzewa, rece=(120 + 30 * math.sin(t * 6 + n), 0))
    x = jazda(t, 0.4, 6.6, -300, 1700)[0]
    auto(st, t, x, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.85, 0.82, 0.9))
    _reflektory(st, x, DROGA_Y, P.auta, k=0.6)
    koniec(st, w, t)


def s_shreveport(st, w, t, T):
    """Przed kawiarnią w Shreveport chłopak wysiada z Forda i znika w tłumie; podpis „Henry Methvin”; Ford odjeżdża bez niego."""
    kam(st, t, 96, 640, 440, lerp(1.1, 0.98, ease(t / T)), 0.79)
    miasto(st, t, w, fasady=(("bank", 220), ("kawiarnia", 700), ("apteka", 1160)), chodnik=True)
    x = jazda(t, 0.4, 2.4, -300, 480, ease_out)[0] if t < 10.0 else jazda(t, 10.0, 3.0, 480, 1800, ease)[0]
    pas = [("bonnie", (330, 132), (0, 0)), ("clyde", (505, 126), (40, 0))] + ([("henry", (410, 128), (0, 0))] if t < 3.4 else [])
    auto(st, t, x, 230, pasazerowie=pas)
    if t >= 3.4:
        hx = jazda(t, 3.6, 4.0, 560, 980)[0]
        lalka(st, t, "henry", hx, 290, flip=1, hop=4 * (t < 7.6), alpha=1.0 - ease(pr(t, 6.4, 1.2)))
    for n, key in enumerate(("przechodzien", "przechodnia", "przechodzien2", "przechodnia2", "przechodzien3")):
        kier = 1 if n % 2 else -1
        px = (300 + n * 260 + kier * t * 70) % 1600 - 160
        lalka(st, t, key, px, 290 + 8 * (n % 2), flip=kier, p=P.lalki + 0.02, hop=4)
    podpis(w, t, "Henry Methvin", 700, 250, 3.8, 3.6)
    tab(w, t, "...?", 480, 330, 8.4, 2.0)
    koniec(st, w, t)


def _krzaki_lowcow(st, t, sink, tint=None, karabiny=False, xs=None):
    xs = xs or [170 + 188 * n for n in range(6)]
    for n, ((key, _), x) in enumerate(zip(LOWCY, xs)):
        lalka(st, t, key, x, 300, flip=-1 if n % 2 else 1, sink=sink, tint=tint, rece=(60, 30) if karabiny else (20, 10),
              trzyma=KARABIN(150) if karabiny else None)
        st.put(J.krzak(n), x, STOPY + 4, P.lalki + 0.02, h=130, anchor=(0.5, 1.0), tint=tint)
    return xs


def s_noc(st, w, t, T):
    """„DAY 101”; noc w lesie, sześciu mężczyzn kuli się w krzakach; nad kapeluszami krążą komary, jeden bezgłośnie klepie się w kark."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 97, 640, 500, 1.15, 0.79)
    w.zawieszki = [("DAY 101", 640, 220, pr(t, 0.8, 1.0))]
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, noc=1.0)
    xs = [170 + 188 * n for n in range(6)]
    for n, ((key, _), x) in enumerate(zip(LOWCY, xs)):
        klap = _bump(t, 7.0, 0.25) if n == 2 else 0.0
        lalka(st, t, key, x, 300, flip=-1 if n % 2 else 1, sink=0.22, tint=NOC, rece=(20 + 150 * klap, 10))
        st.put(J.krzak(n), x, STOPY + 4, P.lalki + 0.02, h=130, anchor=(0.5, 1.0), tint=NOC)
        for m in range(2):
            a = t * 7 + m * 3 + n
            st.put(J.rek("pinezka"), x + 40 * math.cos(a), 440 + 14 * math.sin(a * 1.3), P.lalki + 0.03, h=6, anchor=(0.5, 0.5),
                   tint=(0.1, 0.1, 0.1), shadow=None)
    koniec(st, w, t)


def s_posse(st, w, t, T):
    """W krzakach sześciu mężczyzn; nad każdym po kolei zjeżdża podpis; Hinton przeciera okulary."""
    w.noc, w.moon = 0.75, 0.6
    kam(st, t, 98, lerp(320, 960, ease(t / T)), 520, 1.35, 0.79)
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, noc=0.75)
    xs = [170 + 188 * n for n in range(6)]
    for n, ((key, imie), x) in enumerate(zip(LOWCY, xs)):
        okul = n == 3 and 6.5 < t < 9.0
        lalka(st, t, key, x, 300, flip=-1 if n % 2 else 1, sink=0.18, tint=(0.82, 0.82, 0.92),
              rece=((110 + 20 * math.sin(t * 10)) if okul else 60, 30), trzyma=None if okul else KARABIN(150))
        st.put(J.krzak(n), x, STOPY + 4, P.lalki + 0.02, h=130, anchor=(0.5, 1.0), tint=(0.82, 0.82, 0.92))
        podpis(w, t, imie, x, 360, 1.0 + 2.0 * n, 2.6)
    koniec(st, w, t)


def s_zasadzka_rano(st, w, t, T):
    """„DAY 102”; świt na leśnej drodze; ciężarówka Ivy'ego stoi na lewarku; w krzakach sześć kapeluszy i luf."""
    kam(st, t, 99, 640, 450, 1.0, 0.78)
    w.zawieszki = [("DAY 102", 640, 160, pr(t, 0.8, 1.0))]
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=1.0)
    ciezarowka(st, t, 640, 260, lewarek=ease(pr(t, 1.0, 1.5)))
    lalka(st, t, "ivy", 900, 300, flip=-1, rece=(20, 0), p=P.lalki + 0.03)
    _krzaki_lowcow(st, t, 0.3, karabiny=True, xs=[-20, 90, 200, 1080, 1190, 1300])
    koniec(st, w, t, extra=(1.06, 0.98, 0.9))


def s_kanapka(st, w, t, T):
    """Wnętrze Forda: Bonnie w czerwonej sukience je kanapkę z papierka; Clyde prowadzi w ciemnych okularach."""
    kam(st, t, 100, 640, 480, 1.6, 0.79)
    st.dof = 1.3
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=0.6, kul=False)
    h = 330
    x = 640 + 4 * math.sin(t * 9)
    gryz = 0.5 + 0.5 * math.sin(t * 2.2)
    auto(st, t, x, h, droga=t * 300, pasazerowie=[("bonnie_czerwona", (372, 128), (lerp(70, 110, gryz), 70)), ("clyde", (505, 126), (60, 40))])
    k = h / 360.0
    st.put(J.rek("kanapka"), x + (372 - 450) * k + 30 + 12 * gryz, DROGA_Y + (128 - 356) * k + 70 - 20 * gryz, P.auta - 0.002, h=26,
           anchor=(0.5, 0.5), rot=-10)
    dh = h * 0.92
    sx_ = x + (505 - 450) * k
    stopy = DROGA_Y + (126 - 356) * k + (676 - 128) / 614.0 * dh
    for u, v in OCZY:
        ex, ey = punkt("clyde", sx_, dh, u, v, y=stopy)
        st.put(J.listwa(30, 18, (24, 22, 24)), ex, ey, P.auta - 0.0035, h=14 * dh / 300, anchor=(0.5, 0.5), shadow=None)
    koniec(st, w, t, extra=(1.04, 0.98, 0.92))


def s_zwolnienie(st, w, t, T):
    """Ford zwalnia przy ciężarówce; Ivy macha z pobocza; Clyde wychyla się przez okno."""
    kam(st, t, 101, 700, 460, 1.1, 0.79)
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=0.8, kul=False)
    ciezarowka(st, t, 1060, 210, lewarek=1.0)
    lalka(st, t, "ivy", 860, 300, flip=-1, rece=(130 + 30 * math.sin(t * 10), 0))
    auto(st, t, jazda(t, 0.0, 1.8, 200, 560, ease_out)[0], 240, pasazerowie=[("bonnie_czerwona", 0, (0, 0)), ("clyde", 1, (40 + 60 * ease(pr(t, 1.2, 0.5)), 0))])
    koniec(st, w, t, extra=(1.04, 0.98, 0.92))


def s_zasadzka(st, w, t, T):
    """Za parawanem dziesiątki błysków jeden po drugim, papierowy Ford drży i powoli zjeżdża do rowu; spada kapelusz; cisza (szczyt 3)."""
    kam(st, t, 102, 640, 460, 1.25, 0.79, lens=1.4, shake=2.5 * (0.3 < t < 2.6))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    f = ease(pr(t, 2.6, 1.6))
    x = 640 + 6 * math.sin(t * 40) * (0.3 < t < 2.6) + 120 * f
    auto(st, t, x, 190, y=y0 - 26 + 40 * f, p=p0 + 0.001, przechyl=10 * f, tint=(0.08, 0.06, 0.05), alpha=1.0, shadow=None, blur=1.6, szyby=False)
    for n in range(28):
        bx = 150 + 40 * (n % 4) if n % 2 == 0 else 1130 - 40 * (n % 4)
        blysk(st, bx, y0 - 120 - 30 * (n % 3), p0 + 0.003, t, 0.3 + 0.075 * n, r=160)
    f2 = pr(t, 2.8, 0.9)
    if f2 > 0:
        st.put(J.rek("kapelusz_fedora"), 700 + 40 * f2, lerp(y0 - 300, y0 - 40, f2 * f2), p0 + 0.003, h=36, anchor=(0.5, 1.0), rot=200 * f2 if f2 < 1 else 20,
               tint=(0.08, 0.06, 0.05), shadow=None, blur=1.6)
    koniec(st, w, t, dim=0.88 * (1 - 0.3 * ease(pr(t, 3.6, 1.0))))


def s_dym(st, w, t, T):
    """Dym opada; mężczyźni wychodzą z krzaków z bronią; jeden zdejmuje kapelusz; nikt nic nie mówi."""
    kam(st, t, 103, 640, 450, 1.05, 0.79)
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=1.0)
    auto(st, t, 960, 230, y=DROGA_Y + 30, przechyl=8, dziury=30)
    for n, (key, _) in enumerate(LOWCY):
        x = 120 + 110 * n
        wyj = ease(pr(t, 1.5 + 0.3 * n, 1.2))
        if key == "hamer":
            x = 760
            zdj = t > 6.8
            lalka(st, t, "hamer_bez" if zdj else "hamer", x, 340, flip=1, sink=0.5 * (1 - wyj), rece=(lerp(20, 90, ease(pr(t, 6.2, 0.6))) if not zdj else 30, 0),
                  trzyma=(J.rek("kapelusz_fedora"), 36, (0.5, 0.2), 90, True) if zdj else None)
        else:
            lalka(st, t, key, x, 300, flip=1, sink=0.5 * (1 - wyj), rece=(20, 0), trzyma=KARABIN(150))
    for n in range(10):
        f = clamp_(t / 6.0 + n * 0.03)
        st.put(J.glow(r=256, color=(190, 186, 180)), 700 + 70 * math.sin(n * 2.1) + 30 * t, 560 - 30 * n % 200 - 20 * t, P.lalki + 0.03,
               w=260 + 40 * n % 160, anchor=(0.5, 0.5), alpha=0.6 * (1 - f), shadow=None)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96), dim=1.0 - 0.15 * ease(pr(t, 8.0, 3.0)))


def clamp_(v):
    return max(0.0, min(1.0, v))


# ===================== AKT VIII · DO KOGO NALEŻY LEGENDA =====================

def s_pamiatki(st, w, t, T):
    """Tłum otacza podziurawionego Forda w Arcadii; ktoś odchodzi ze skrawkiem sukienki, ktoś z puklem włosów; szeryf odgania ludzi."""
    kam(st, t, 104, 640, 440, lerp(1.15, 0.95, ease(t / T)), 0.79)
    miasto(st, t, w, fasady=(("meble", 300), ("zaklad", 960)), tyl=(("dom", 640),), chodnik=True)
    auto(st, t, 640, 230, dziury=30)
    for n, (key, x0) in enumerate((("przechodzien", 250), ("przechodnia", 430), ("przechodzien2", 540), ("farmer", 660), ("przechodnia2", 780),
                                   ("przechodzien3", 990), ("farmer2", 1080))):
        x = x0 + 10 * math.sin(t * 3 + n)
        za_autem = 400 < x0 < 880  # tłum za autem: widać go nad dachem, auto zostaje widoczne
        lalka(st, t, key, x, 300 + 10 * (n % 3), flip=1 if x < 640 else -1, p=(P.auta - 0.006 - 0.001 * (n % 3)) if za_autem else P.lalki + 0.01,
              lean=(8 if x < 640 else -8) * (0.5 + 0.5 * math.sin(t * 2 + n)), rece=(60 + 30 * math.sin(t * 4 + n), 20), hop=3)
    for n, (key, x0, x1, spr, tint) in enumerate((("przechodnia", 560, 120, J.rek("pranie"), (0.9, 0.3, 0.3)), ("przechodzien", 760, 1200, J.platek((240, 210, 120)), None))):
        f = ease(pr(t, 5.6 + 0.6 * n, 3.0))
        if f > 0:
            out = lalka(st, t, key, lerp(x0, x1, f), 290, flip=1 if x1 > x0 else -1, p=P.lalki + 0.03, rece=(100, 0), hop=4)
            if out:
                st.put(spr, out[0], out[1], P.lalki + 0.035, h=20, anchor=(0.5, 0.3), tint=tint)
    lalka(st, t, "szeryf", 1120, 320, flip=-1, rece=(90 + 50 * math.sin(t * 8) * (t > 7.0), 60 * (t > 7.0)))
    tab(w, t, "BACK OFF!", 1100, 260, 7.4, 3.0)
    koniec(st, w, t)


def s_darby_zaklad(st, w, t, T):
    """W zakładzie pogrzebowym młody mężczyzna w fartuchu zakłada rękawice; zjeżdża jego stary podpis."""
    kam(st, t, 105, 600, 460, 1.25, 0.8)
    wnetrze(st, t, w, sciana="paski", okna=(1050,), meble=(("stol_obrus", 800, 120, P.lalki + 0.02),), zarowki=(640,), tint=(0.85, 0.88, 0.9))
    lalka(st, t, "darby_fartuch", 520, 300, flip=1, rece=(80 + 12 * math.sin(t * 7) * (1.0 < t < 3.6), 70))
    podpis(w, t, "Dillard Darby, undertaker", 520, 230, 2.0, 5.0)
    koniec(st, w, t, extra=(0.94, 0.97, 1.02))


def s_pogrzeby(st, w, t, T):
    """Dwa osobne pogrzeby na dwóch cmentarzach, między nimi droga; tłumy przy obu; matka Bonnie odwraca się plecami."""
    kam(st, t, 106, 640, 440, lerp(1.1, 0.95, ease(t / T)), 0.79)
    cmentarz(st, t, w)
    for n, (txt, x) in enumerate((("FISHTRAP CEMETERY", 150), ("WESTERN HEIGHTS", 1130))):
        Z0.rise(st, J.tablica(txt), x, STOPY, P.wzgorza + 0.03, bk(w, 0.4 + 0.1 * n), t, 640 + n, h=170, wob=0.0)
    for x in (330, 980):
        if bk(w, 0.6) >= 1:
            st.put(J.rek("trumna"), x, 676, P.lalki + 0.07, w=240, anchor=(0.5, 1.0))
    for n, (key, x) in enumerate((("przechodnia", 230), ("przechodzien", 300), ("matka_bonnie", 440), ("przechodnia2", 510),
                                  ("przechodzien2", 860), ("matka_clyde", 930), ("przechodzien3", 1060), ("farmer", 1130))):
        fl = 1 if x < 640 else -1
        if key == "matka_bonnie":
            fl = 1 - 2 * ease(pr(t, 6.0, 0.8))
        lalka(st, t, key, x, 280 + 10 * (n % 2), flip=fl, lean=5 * fl, rece=(10, 0))
    koniec(st, w, t, dim=0.95)


def s_auto_jarmark(st, w, t, T):
    """Na jarmarku pod namiotem stoi podziurawiony Ford; kolejka płaci za wejście i zagląda w dziury; obok kręci się diabelski młyn."""
    kam(st, t, 107, 640, 430, lerp(1.1, 0.95, ease(t / T)), 0.78)
    preria(st, t, w, droga=0.0, slupy=False, zielen=True)
    if bk(w, 0.3) > 0:
        st.put(J.kolo_mlynskie(), 1080, 360 + (1 - back(bk(w, 0.3), 1.2)) * 700, P.miasto, h=560, anchor=(0.5, 0.5), rot=t * 15)
    Z0.rise(st, J.namiot_jarmark(), 580, STOPY, P.wzgorza, bk(w, 0.4), t, 651, h=440, wob=0.0)
    auto(st, t, 580, 220, dziury=30)
    if bk(w, 0.6) >= 1:
        st.line([(300, 610), (860, 612)], P.auta + 0.01, width=3, color=(180, 40, 40))
    lalka(st, t, "przechodzien3", 200, 290, flip=1, rece=(60, 0))
    podpis(w, t, "10¢ A LOOK", 200, 300, 0.8, T)
    for n, key in enumerate(("przechodnia", "farmer", "dziecko1", "przechodzien", "przechodnia2")):
        x = lerp(1400 + 120 * n, 900 + 100 * n, ease(pr(t, 0.6 + 0.6 * n, 3.0)))
        lalka(st, t, key, x, 290 if "dziecko" not in key else 200, flip=-1, lean=-10 * ease(pr(t, 3.8 + 0.6 * n, 0.5)), hop=4 * (t < 3.6 + 0.6 * n))
    koniec(st, w, t)


def s_blanche_po(st, w, t, T):
    """Starsza Blanche w okularach podlewa kwiaty przed domkiem; zjeżdża zawieszka „1988”."""
    kam(st, t, 108, 680, 460, 1.2, 0.8)
    w.zawieszki = [("1988", 640, 160, pr(t, 1.0, 1.0))]
    miasto(st, t, w, fasady=(("dom", 560),), tyl=(), chodnik=False)
    for n, x in enumerate((800, 880, 960) if bk(w, 0.6) >= 1 else ()):
        st.put(J.rek("kwiaty"), x, STOPY + 4, P.lalki + 0.02, h=90, anchor=(0.5, 1.0), rot=3 * math.sin(t + n))
    out = lalka(st, t, "blanche_stara", 680, 290, flip=1, rece=(70, 10), trzyma=(J.rek("dzbanek"), 40, (0.3, 0.3), 40, True))
    if out:
        for n in range(5):
            f = (t * 1.4 + n / 5) % 1.0
            st.put(J.platek((150, 190, 230)), out[0] + 60 + 40 * f, out[1] + 10 + 140 * f * f, P.lalki + 0.03, h=8, anchor=(0.5, 0.5), shadow=None)
    koniec(st, w, t)


def s_hamer_ganek(st, w, t, T):
    """Hamer na ganku odkłada gazetę o zasadzce, zakłada kapelusz i odwraca się od reporterów."""
    kam(st, t, 109, 600, 450, 1.1, 0.8)
    _ganek(st, t, w)
    odl = ease(pr(t, 2.0, 0.6))
    kap = t > 3.5
    hx = lerp(640, 960, ease(pr(t, 5.0, 2.2)))
    lalka(st, t, "hamer" if kap else "hamer_bez", hx, 340, flip=-1 if t < 4.5 else 1, rece=(lerp(80, 20, odl) + 90 * _bump(t, 3.4, 0.4), 20),
          trzyma=(J.gazeta("OUTLAWS DIE IN AMBUSH", 5, 360, 480), 80, (0.5, 0.8), 90, True) if odl < 1 else None, hop=3 * (5.0 < t < 7.2))
    if odl >= 1:
        st.put(J.gazeta("OUTLAWS DIE IN AMBUSH", 5, 360, 480), 800, STOPY - 120, P.lalki - 0.004, h=60, anchor=(0.5, 1.0), rot=-6)
    lalka(st, t, "reporter", 220, 300, flip=1, lean=6, rece=(80, 30))
    lalka(st, t, "fotograf", 360, 300, flip=1, rece=(90, 80), trzyma=(J.rek("aparat"), 50, (0.5, 0.5), 90, True))
    for t0 in (1.6, 3.0, 5.4):
        blysk(st, 420, 470, P.lalki + 0.02, t, t0, r=200, kolor=(1.0, 1.0, 1.0))
    koniec(st, w, t)


def _ekran(sx0, sy0, s):
    return sx0, sy0, 1060 * s, 520 * s


def s_film_hamer(st, w, t, T):
    """Ekran kina: piękna para z filmu z 1967 roku, potem aktor-Hamer związany, a filmowa Bonnie robi sobie z nim zdjęcie; widownia
    się śmieje; obok ekranu prawdziwy Hamer z tabliczką „THAT'S NOT ME!”."""
    kam(st, t, 110, 640, 390, 0.95, 0.78)
    ex, ey, ew, eh = _ekran(*kino(st, t, w))
    pe = P.miasto + 0.003
    film = dict(tint=(0.82, 0.82, 0.86), shadow=None, p=pe, y=ey + eh - 8)
    if t < 5.6:
        auto(st, t, ex + 0.75 * ew, 150, y=ey + eh - 8, p=pe - 0.0005, tint=(0.8, 0.8, 0.84), shadow=None)
        lalka(st, t, "aktor", ex + 0.34 * ew, 280, flip=1, rece=(60, 40), **film)
        lalka(st, t, "aktorka", ex + 0.48 * ew, 260, flip=-1, lean=-6, rece=(70, 50), **film)
    else:
        hx = ex + 0.4 * ew
        lalka(st, t, "aktor_hamer", hx, 290, flip=1, rece=(0, 0), **film)
        for n in range(3):
            yy = ey + eh - 8 - 120 - 40 * n
            st.line([(hx - 30, yy), (hx + 30, yy + 6)], pe + 0.0005, width=3, color=(200, 190, 170))
        lalka(st, t, "aktorka", ex + 0.6 * ew, 260, flip=-1, rece=(90, 70), trzyma=(J.rek("aparat"), 40, (0.5, 0.5), 90, True), **film)
        blysk(st, ex + 0.58 * ew, ey + eh - 200, pe + 0.001, t, 8.0, r=220, kolor=(1.0, 1.0, 1.0))
    if 5.4 < t < 5.8:
        st.dim = 0.3
    widownia(st, t)
    tab(w, t, "HA HA HA!", 640, 560, 8.6, 2.6)
    lalka(st, t, "hamer", 1200, 330, ease(pr(t, 9.6, 0.6)), flip=-1, rece=(20, 0))
    tab(w, t, "THAT'S NOT ME!", 1130, 240, 10.4, 4.0)
    koniec(st, w, t)


def s_gra(st, w, t, T):
    """Ekran migocze; zamiast filmu pikselowa para uciekinierów w aucie z gry wideo; widzowie w pierwszym rzędzie trzymają pady."""
    kam(st, t, 111, 640, 420, 1.0, 0.78)
    ex, ey, ew, eh = _ekran(*kino(st, t, w))
    pe = P.miasto + 0.003
    if t < 1.6:
        for n in range(40):
            r = (int(t * 24) * 7 + n * 13) % 97 / 97.0
            st.put(J.listwa(40, 12, (210, 210, 210)), ex + ew * ((n * 0.137 + r) % 1.0), ey + eh * ((n * 0.071 + r * 0.5) % 1.0), pe, w=30,
                   anchor=(0.5, 0.5), alpha=0.6, shadow=None)
    else:
        x = ex + ew * lerp(0.25, 0.7, ease(pr(t, 1.6, T - 2.0)))
        st.put(J.gra_piksele(), x, ey + eh * 0.62 + 6 * abs(math.sin(t * 6)), pe, w=0.4 * ew, anchor=(0.5, 0.5), shadow=None)
    widownia(st, t)
    for n, x in enumerate((300, 560, 820, 1020)):
        st.put(J.rek("pad"), x, 600, P.rampa - 0.005, h=46, anchor=(0.5, 0.5), rot=8 * math.sin(t * 8 + n), shadow=None)
    koniec(st, w, t)


def s_koniec(st, w, t, T):
    """Papierowa Bonnie z cygarem i Clyde kładą się płasko w stronę gazety; obok zamyka się teczka Hamera; kurtyna zasuwa się."""
    kam(st, t, 112, 640, lerp(380, 400, ease(t / T)), lerp(1.0, 0.92, ease(t / T)), 0.8, drift=0.4)
    teatr_gazet(st, t, w)
    auto(st, t, 700, 290)
    kl = ease(pr(t, 3.0, 2.5))
    lalka(st, t, "bonnie_cygaro", 470, 320, flip=1, lean=-85 * kl, sink=0.4 * kl, rece=(70 * (1 - kl), 10), trzyma=REV() if kl < 0.5 else None)
    lalka(st, t, "clyde", 980, 350, flip=-1, lean=85 * kl, sink=0.4 * kl, rece=(35 * (1 - kl), 20), trzyma=KARABIN() if kl < 0.5 else None)
    zam = t > 7.0
    st.put(J.rek("teczka" if zam else "teczka_otwarta"), 640, STOPY + 30, P.rekwizyty, h=110 if zam else 90, anchor=(0.5, 1.0),
           shadow=(5, 7, 8, 0.4))
    R = sys.modules.get("render") or sys.modules.get("__main__")
    if R is not None and hasattr(R, "kurtyna"):
        R.kurtyna(st, ease(pr(t, 10.0, 3.0)))
    koniec(st, w, t)


def s_dzieki(st, w, t, T):
    """Przed kurtyną wychodzą wszystkie lalki filmu i kłaniają się po kolei; Hamer zdejmuje kapelusz, Bonnie macha."""
    kam(st, t, 113, 640, 400, 1.0, 0.8, drift=0.4)
    for strona in (-1, 1):
        st.put(Z0.kurtyna(strona), CX, -60, P.drzewa, h=1000, anchor=(1.0 if strona < 0 else 0.0, 0.0), shadow=None)
    st.put(J.glow(), CX, 700, P.drzewa + 0.01, w=1800, anchor=(0.5, 0.5), mode="add", alpha=0.25, shadow=None, tint=(1.0, 0.85, 0.6))
    for n, key in enumerate(("buck", "blanche", "wd", "bonnie", "clyde", "hamer", "darby", "boyd")):
        x = 120 + 148 * n
        t0 = 1.2 + 0.45 * n
        uklon = ease(pr(t, t0, 0.35)) * (1 - ease(pr(t, t0 + 0.6, 0.4)))
        fl = 1 if x < CX else -1
        h = 330 if key in ("clyde", "hamer", "buck") else 300
        if key == "hamer":
            zdj = t > t0 - 0.3
            lalka(st, t, "hamer_bez" if zdj else "hamer", x, h, flip=fl, lean=25 * fl * uklon, rece=(40, 0),
                  trzyma=(J.rek("kapelusz_fedora"), 36, (0.5, 0.2), 90, True) if zdj else None)
        else:
            mach = key == "bonnie" and t > t0 + 1.0
            lalka(st, t, key, x, h, flip=fl, lean=25 * fl * uklon, rece=(130 + 30 * math.sin(t * 8) if mach else 20, 10))
    koniec(st, w, t)
