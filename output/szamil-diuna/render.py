"""The Imam Who Fought Russia for 25 Years — and Ended Up in Dune: teatr papierowy rysowany kodem (1280 × 720, 24 kl./s).
Kopia renderu „Bonnie and Clyde” (27.11.2026); wzór: output/pierwszy-cesarz/render.py.

Rozpiska: docs/filmy/szamil-diuna/ujecia/dane.py (akt → scena → beat → ujęcie, z kluczem ujęcia).
Ujęcia: ujecia_a.py (akty 1–4) i ujecia_b.py (akty 5–9), funkcja `s_<klucz>(st, w, t, T)` na ujęcie.
Świat (stan sceny, lalki, scenografie): scena.py. Wycinanki: zestaw_bc.py. Silnik: output/pierwszy-cesarz/papier.py.

  python3 render.py arkusz [1,2,3] [plik]   — arkusz klatek ujęć (numery od 1) do obejrzenia
  python3 render.py klatka 12.5 [plik]      — jedna klatka filmu (czas w sekundach)
  python3 render.py kontrola [1,2,3]        — test „końca świata” (płótno w barwie pustki), równolegle
  python3 render.py klipy [1,2,3] <katalog> — klip mp4 na ujęcie
  SZKIC=1 …                                 — szkic 640 × 360, 12 kl./s (przegląd w Studio); bez tego pełna jakość
  ROZDZIELCZOSC=1080 albo 1440 …            — klatka 1920 × 1080 albo 2560 × 1440 (ta sama geometria); bez tego 1280 × 720
  NAPISY=1 …                                — z napisami wypalonymi w obraz (domyślnie bez: reżyser 24.11)
Moduł ma SCENES, DUR, FPS i frame(t) — tak jak pozostałe filmy (scripts/kontrola_ujec.py, wgrywanie do Studio).
"""
import math
import zlib
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/szamil-diuna/ujecia"))

import scena as swiat  # noqa: E402
import papier  # noqa: E402
import ujecia_a  # noqa: E402
import ujecia_b  # noqa: E402
import zestaw_kz as Z  # noqa: E402
import uklad_kz  # noqa: E402
import dane  # noqa: E402
from dane import AKTY, HAK, kwestia, okno_kwestii, ujecia  # noqa: E402
from papier import FPS, H, W, Stage, back, ease, noise  # noqa: E402

NAPISY = os.environ.get("NAPISY", "0") == "1"  # reżyser 24.11: bez wypalonych napisów (NAPISY=1 włącza je z powrotem)
SZKIC = os.environ.get("SZKIC", "0") == "1"  # szkic do przeglądu w Studio: 640 × 360, 12 kl./s
if SZKIC:
    papier.Q, FPS = 0.5, 12
elif os.environ.get("ROZDZIELCZOSC"):  # wysokość klatki, np. ROZDZIELCZOSC=1440 → 2560 × 1440 (ta sama geometria, Q = 2)
    papier.Q = int(os.environ["ROZDZIELCZOSC"]) / H

UJ = ujecia()
KOL = swiat.KOL
FNS = [getattr(ujecia_a, "s_" + k, None) or getattr(ujecia_b, "s_" + k, None) for k in KOL]  # None = ujęcie do narysowania
ODN = [f"d{a:02d}_{k:02d}" for a, k, *_ in UJ]
# ujęcia, w których dekoracja staje od nowa (pierwsze ujęcie sceny albo zmiana miejsca): elementy wjeżdżają po kolei
BUDUJ = set()  # uzupełniane niżej z GRANICE: pierwsze ujęcie każdej sceny buduje dekorację od nowa

# (start, koniec, ruch, napis, start kwestii, długość kwestii) — jak w pozostałych filmach
SCENES, _t = [], 0.0
for _akt, _k, _klucz, _kadr, _ruch, _sec, _opis, _snd in UJ:
    SCENES.append((_t, _t + _sec, _ruch, kwestia(_snd), *okno_kwestii(_snd, _klucz in HAK)))
    _t += _sec
DUR = _t
# Render końcowy (FILM=1 → zloz.py): ujęcie kończy się na klatce najbliższej swojemu końcowi na osi, więc klipy złożone jeden
# po drugim trwają dokładnie tyle co oś w Studio i muzyka z efektami nie rozjeżdżają się z obrazem (wzór: „Syn słońca”
# i „Pierwszy cesarz” render.py). Klipy do Studio: zaokrąglone w górę, jak dotąd. CRF — jakość pliku (domyślnie 23; render
# końcowy 21).
FILM = os.environ.get("FILM", "0") == "1"
CRF = os.environ.get("CRF", "21" if FILM else "23")  # 1440p, CRF 21: ok. 16 Mbit/s przy ziarnie papieru (CRF 18: 40 Mbit/s)


def klatki_ujecia(i):
    a, b = SCENES[i][:2]
    if FILM:
        return math.floor(b * FPS + 0.5) - math.floor(a * FPS + 0.5)
    return math.ceil((b - a) * FPS - 1e-9)

# Rytm, w którym ułożono akcję ujęć (sekundy w ujecia_a/b.py, efekty.ZDARZENIA, GAG_PUENTA): długość ujęcia i kwestii z tempa
# lektora, sprzed nagrania. Prawdziwe nagranie bywa krótsze albo dłuższe (23.11.2026: „matka_obietnica” 11,5 → 9,1 s, gag
# z zawieszkami WEEK wypadał za cięciem) — czas_akcji() przekłada chwilę ujęcia na czas akcji: do oddechu bez zmian, kwestia
# do kwestii, pauza po kwestii do pauzy po kwestii. Gag na słowie lektora trafia w to słowo, puenta w pauzę po kwestii.
dane.BEZ_NAGRAN[0] = True  # dane.ujecia_szkicu() i okna kwestii z tempa lektora
try:
    SZKIC_CZAS = [(u[5], okno_kwestii(u[7], u[2] in HAK)[1]) for u in ujecia()]
finally:
    dane.BEZ_NAGRAN[0] = False
assert len(SZKIC_CZAS) == len(SCENES)


# Ujęcia o długości wpisanej ręką w rozpisce (reżyser przyciął w Studio, „Szybkie” itp.): akcja wypełnia tę długość
# niezależnie od kwestii, więc gra w swoim czasie (bez przełożenia).
STALA_DLUGOSC = {_x[0] for _n, _tyt, _o, _sceny in AKTY for _st, _pl, _beaty in _sceny for _b, _sh in _beaty for _x in _sh
                 if _x[3] is not None}


def _wezly(i):
    a, b, _, _, vs, vl = SCENES[i]
    T, (T0, vl0) = b - a, SZKIC_CZAS[i]
    x, y = [0.0], [0.0]
    if KOL[i] in STALA_DLUGOSC:
        return [0.0, T], [0.0, T]
    if vl and vl0 and vs + vl < T - 0.05 and vs + vl0 < T0 - 0.05:
        x += [vs, vs + vl]
        y += [vs, vs + vl0]
    return x + [T], y + [T0]


def czas_akcji(i, lt):
    """(czas akcji, długość akcji) ujęcia i w chwili lt ujęcia z prawdziwym nagraniem lektora."""
    x, y = _wezly(i)
    return float(np.interp(lt, x, y)), y[-1]


swiat.CZAS["akcji"] = lambda klucz, s: czas_akcji(KOL.index(klucz), s)[0]  # scena.rs: sekunda reżysera → czas akcji


def czas_ujecia(i, ta):
    """Odwrotność czas_akcji: chwila ujęcia i, w której akcja jest w chwili ta (zdarzenia dźwięku, puenty gagów)."""
    x, y = _wezly(i)
    return float(np.interp(ta, y, x))


BEZ_NAPISU = {"dzieki"}  # tekst jest w kadrze (tabliczki z podziękowaniem)

# Skróty ujęć (akt 0: zapowiedź i hak, szkic D; reżyser 18.11.2026: „na początku mini spoiler 5 s, co będzie w filmie (najlepsze
# akcje)”). Ujęcie z tego słownika rysuje inne ujęcie filmu od chwili `od` (sekundy od jego początku), ze stanem świata z jego
# miejsca w filmie i z jego długością (kamera i zdarzenia liczą się tak jak w oryginale) — to skrót, a nie nowa scena.
# Trzeci element: długość, z jaką liczy się oryginał, gdy ujęcie skraca samo siebie (teatr: od 1 s, za kurtyną zapala się
# lampa, szyld „SON OF THE SUN” widać, gdy kurtyna się rozsunie, bracia wysuwają się na polanę, kamera dojeżdża do 5 s).
WYCINEK = {"zap_akhulgo": ("armaty", 0.3), "zap_tratwa": ("tratwa", 0.9), "zap_najazd": ("jezdzcy", 0.4),
           "zap_rzeka": ("brzegi", 0.8), "zap_mundur": ("mundur", 0.9), "zap_gunib": ("flaga", 0.7), "zap_slowa": ("kanly", 1.2),
           "zap_wydma": ("pytanie", 0.6)}
# Kurtyna startu (reżyser 18.11.2026: „po spoilerze na końcu ściemnienie i kurtyna startu z pierwszym ujęciem”): ujęcie
# zaczyna się zasuniętą kurtyną bez tytułu, która się rozsuwa (zapowiedź kończy się ściemnieniem — koniec swojej sceny).
KURTYNA_START = {"tytul"}

# ---- przejścia między ujęciami (wzór: „Pierwszy cesarz” render.py; reżyser 15.11: kurtyna między aktami, ściemnienie przy
# zmianie miejsca, Podręcznik „Rytm” 7) — nachodzą na pauzę po kwestii i na początek następnego ujęcia, film nie rośnie ----
GRANICE = []  # na ujęcie: akt, tytuł aktu, czy pierwsze/ostatnie w scenie i w akcie (kolejność jak w dane.ujecia())
for _n, _tyt, _o, _sceny in AKTY:
    for _si, (_st, _pl, _beaty) in enumerate(_sceny):
        _shots = [_x for _b, _sh in _beaty for _x in _sh]
        for _ui in range(len(_shots)):
            GRANICE.append(dict(akt=_n, tytul=_tyt, pierwsze_sceny=_ui == 0, ostatnie_sceny=_ui == len(_shots) - 1,
                                pierwsze_aktu=_si == 0 and _ui == 0, ostatnie_aktu=_si == len(_sceny) - 1 and _ui == len(_shots) - 1))
assert len(GRANICE) == len(UJ)
BUDUJ |= {KOL[_i] for _i, _g in enumerate(GRANICE) if _g["pierwsze_sceny"]}
# Ta sama dekoracja co w poprzednim ujęciu (to samo miejsce, czas leci dalej): bez gaśnięcia i bez budowy od zera, zwykłe cięcie.
# Przegląd 19.11 („ujęcie po ujęciu zbytnio nie kontynuowało poprzedniego”): pole pod Waldo po śmiechu Darby'ego, rzeka po
# Dexfield, nocna droga po odejściu W.D., Kansas po jeździe z Boydem budowały się od pustego płótna jak nowa historia.
CIAGLOSC = {"dwie_wojny", "slowo_kindjal"}  # KINDJAL: góry wyrosły już w „pytanie”, słowo spada od razu
BUDUJ -= CIAGLOSC
KURTYNA = (1.5, 0.8, 0.25, 0.85)  # zamykanie 1,5 s przed końcem aktu, trwa 0,8 s; w nowym akcie po 0,25 s otwiera się 0,85 s
CIEMNO = 0.35  # ściemnienie: tyle sekund gaśnie na końcu sceny i tyle zapala się na początku następnej
# Akty bez kurtyny na wejściu (Podręcznik → Rytm, 19.11.2026: „jeden początek”): prolog przechodzi w akt I ściemnieniem, bo
# kurtyna z tytułem aktu po obietnicy wyglądała jak drugi start filmu.
BEZ_KURTYNY = {1}


# Kurtyny aktów II–IV (szkic D, reżyser 28.11: „Zatwierdzam”): mała tabliczka „Act N — SŁOWO” (słowo z Diuny), pod nią pytanie.
SLOWA_AKTOW = {2: ("KANLY", "How do you buy back a son?"), 3: ("SIRIDAR", "How does a 25-year war end?"),
               4: ("SIETCH", "What did Dune take?")}


def tytul_aktu(n):
    slowo, pytanie = SLOWA_AKTOW[n]
    return f"Act {n} — {slowo} · {pytanie}"


def _ekran(st, p):
    """Odwzorowanie kadr wzorcowy → ekran na planie p jest liniowe w każdej osi: (x0, kx, y0, ky)."""
    a0, ax, ay = st.cam.screen(0, 0, p), st.cam.screen(1, 0, p), st.cam.screen(0, 1, p)
    return a0[0], ax[0] - a0[0], a0[1], ay[1] - a0[1]


def kurtyna(st, k, tytul=None, kt=0.0, p=0.975):
    """Kurtyna przed sceną w układzie ekranu (kamera jej nie powiększa): k = 0 otwarta, 1 zasunięta; tytuł aktu na
    tabliczce zjeżdża na środek (kt = 0..1)."""
    if k <= 0.001 and kt <= 0.001:
        return
    x0, kx, y0, ky = _ekran(st, p)
    na_swiat = lambda sx, sy: ((sx - x0) / kx, (sy - y0) / ky)
    szer = 700
    for strona in (-1, 1):
        if k <= 0.001:
            break
        przes = (1 - ease(k)) * (szer + 60)
        brzeg = 640 + 30 * strona * -1 + strona * przes
        wx, wy = na_swiat(brzeg, -70)
        st.put(Z.Z0.kurtyna(strona), wx, wy, p, w=szer / kx, anchor=(1.0 if strona < 0 else 0.0, 0.0),
               rot=0.5 * noise(st.t, 300 + strona, 0.6) * (1 - k * 0.5), sx=0.86 + 0.14 * ease(k), blur=0,
               shadow=(8 * strona, 0, 14, 0.45))
    if tytul and kt > 0.001:
        # tytuł aktu jako pytanie (przegląd 18.11.2026): „Act N” na małej tabliczce, pod nią pytanie — jedna tabliczka z całym
        # zdaniem byłaby szersza niż kadr
        akt, _, pytanie = Z.tr(tytul).partition(" · ")
        spad = (1 - back(kt, 1.2)) * 520
        rzedy = [(akt, 40, 74, 268)] + ([(pytanie, 46, 86, 352)] if pytanie else [])
        for n, (txt, size, h, y) in enumerate(rzedy):
            wx, wy = na_swiat(640, y - spad)
            st.put(Z.tag(txt, size), wx, wy, p + 0.002 + 0.001 * n, h=h / ky, anchor=(0.5, 0.5),
                   rot=1.2 * noise(st.t, 333 + n, 0.5), blur=0, shadow=(4, 6, 8, 0.45))


def przejscie(st, i, lt, T):
    """Kurtyna na granicy aktów, ściemnienie na granicy scen w akcie; w pozostałych miejscach cięcie."""
    g = GRANICE[i]
    zam, dl, czekaj, otw = KURTYNA
    if KOL[i] in KURTYNA_START:
        kurtyna(st, 1 - pr_(lt, 0.1, otw))
        return
    if g["ostatnie_aktu"] and i < len(UJ) - 1 and g["akt"] + 1 not in BEZ_KURTYNY:
        kurtyna(st, pr_(lt, T - zam, dl), tytul_aktu(g["akt"] + 1), pr_(lt, T - zam + dl - 0.1, 0.45))
    elif g["pierwsze_aktu"] and i > 0 and g["akt"] not in BEZ_KURTYNY:
        kurtyna(st, 1 - pr_(lt, czekaj, otw), tytul_aktu(g["akt"]), 1 - pr_(lt, 0.0, czekaj + 0.15))
    else:
        if (g["ostatnie_sceny"] or g["ostatnie_aktu"]) and i < len(UJ) - 1 and KOL[i + 1] not in CIAGLOSC:
            st.dim *= 1 - ease(pr_(lt, T - CIEMNO, CIEMNO))
        if (g["pierwsze_sceny"] or g["pierwsze_aktu"]) and i > 0 and KOL[i] not in CIAGLOSC:
            st.dim *= ease(pr_(lt, 0.0, CIEMNO))


def pr_(t, a, d):
    return min(1.0, max(0.0, (t - a) / d))


def wrap(txt, n=60):
    out, line = [], ""
    for word in txt.split():
        if len(line) + len(word) + 1 > n and line:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    return out + [line]


def subtitle(img, txt):
    """Napis jako pasek papieru u dołu kadru — tylko wtedy, gdy lektor mówi."""
    q = papier.Q
    w, h = img.size
    f = ImageFont.truetype(Z.FONT_PL, round(28 * q), index=Z.PL_IDX)
    lines = wrap(txt)
    d = ImageDraw.Draw(img, "RGBA")
    lh = 36 * q
    wd = max(d.textlength(ln, font=f) for ln in lines) + 40 * q
    y1 = h - 20 * q
    y0 = y1 - lh * len(lines) - 14 * q
    d.rounded_rectangle([w / 2 - wd / 2 + 3 * q, y0 + 4 * q, w / 2 + wd / 2 + 3 * q, y1 + 4 * q], 4 * q, fill=(20, 12, 8, 90))
    d.rounded_rectangle([w / 2 - wd / 2, y0, w / 2 + wd / 2, y1], 4 * q, fill=(238, 224, 192, 238))
    for n, ln in enumerate(lines):
        d.text((w / 2, y0 + 8 * q + lh * n + lh / 2 - 2 * q), ln, font=f, fill=(44, 28, 22, 255), anchor="mm")


def ziarno(i):
    """Ziarno losowania (ziarno papieru, drżenie) z klucza ujęcia — klip ujęcia nie zależy od jego miejsca w filmie."""
    return zlib.crc32(KOL[i].encode()) % 1000003


# Rzeczy stawiane wprost w ujęciu (rekwizyt, zawieszka, nitka) czekają, aż dekoracja się zbuduje — tak jak lalki i auta
# (scena.wejscie). Przegląd 19.11: teczka i kapelusz wisiały nad pustym płótnem, zanim wyrosło biurko; karabin, puszka
# i list unosiły się w powietrzu w pierwszej sekundzie budowy.
SCENOGRAFIA = {"niebo", "slonce", "ksiezyc", "chmury", "rampa", "kulisy", "pas", "ciemnosc", "parawan", "wnetrze", "dekoracja",
               "gwiazdy", "teatr_kz", "kaukaz", "gruzja", "petersburg", "sala_balowa", "miczik", "izba", "pustynia", "gory_pasmo",
               "mur_przod", "_niebo_kz"}
SAME_WCHODZA = SCENOGRAFIA | {"lalka", "auto", "motocykl", "ciezarowka", "cien", "rise"}  # mają własne wejście / wyrastanie


def po_budowie(st):
    k = swiat.wejscie(0.9, 0.4)
    if k >= 1.0:
        return

    def wprost():
        f = sys._getframe(2)
        while f is not None and f.f_code.co_name != "uloz":
            if f.f_code.co_name in SAME_WCHODZA:
                return False
            f = f.f_back
        return True
    put0, line0 = st.put, st.line

    def put(spr, x, y, p, *a, **kw):
        if 0.685 <= p < swiat.P.rampa and wprost():
            kw["alpha"] = kw.get("alpha", 1.0) * k
        return put0(spr, x, y, p, *a, **kw)

    def line(pts, p, *a, **kw):
        if 0.685 <= p < swiat.P.rampa and wprost():
            kw["alpha"] = kw.get("alpha", 0.9) * k
        return line0(pts, p, *a, **kw)
    st.put, st.line = put, line


def uloz(t, void=None):
    """Klatka w chwili t filmu, ułożona (wycinki, kamera, światło), jeszcze nie narysowana: (Stage, napis albo None).
    Z niej korzysta render i podgląd na żywo w Studio (na_zywo.py) — wzór: „Pierwszy cesarz” render.uloz."""
    i = next((k for k, s in enumerate(SCENES) if s[0] <= t < s[1]), len(SCENES) - 1)
    a, b, ruch, txt, vs, vl = SCENES[i]
    lt, T = t - a, b - a
    st = Stage(lt, seed=ziarno(i))
    uklad_kz.uk(st, lt)  # układ sceny od pierwszego wycinka: dekoracje i rampa też mają właściciela (Wytyczne 1.32)
    st.void = void
    if KOL[i] in WYCINEK:  # skrót innego ujęcia: oryginał od chwili `od`, jego świat i jego długość
        src, od, *dl = WYCINEK[KOL[i]]
        j = swiat.I[src]
        Tj = dl[0] if dl else SZKIC_CZAS[j][0]  # skrót gra akcję oryginału w jej rytmie (od jak w czas_akcji)
        st = Stage(od + lt, seed=ziarno(j))  # czas sceny jak w oryginale (mruganie, drżenie, kołysanie)
        uklad_kz.uk(st, od + lt)
        st.void = void
        w = swiat.stan(j)
        if src in BUDUJ:
            w.build = od + lt
        swiat.BUDOWA["t"] = w.build
        st.T = Tj
        po_budowie(st)
        FNS[j](st, w, od + lt, Tj)
        if not void:
            przejscie(st, i, lt, T)
    elif FNS[i] is None:  # ujęcie jeszcze nie narysowane: pusta scena z kartką
        st.put(Z.sky(), W / 2, H / 2, 0.14, w=1760, anchor=(0.5, 0.5), shadow=None)
        st.put(Z.tag(f"{ODN[i]} · do narysowania"), W / 2, H / 2, 0.8, h=60, anchor=(0.5, 0.5))
    else:
        w = swiat.stan(i)
        if KOL[i] in BUDUJ:
            w.build = lt
        swiat.BUDOWA["t"] = w.build
        ta, Ta = czas_akcji(i, lt)
        st.T = Ta
        po_budowie(st)
        FNS[i](st, w, ta, Ta)
        if not void:
            przejscie(st, i, lt, T)
    if not void:
        st.dim *= min(1.0, t / 0.2, max(0.0, (DUR - 0.1 - t) / 1.0))  # film wchodzi z czerni (szybko: zapowiedź) i w nią wychodzi
    return st, (txt if NAPISY and txt and KOL[i] not in BEZ_NAPISU and vs <= lt < min(T - 0.05, vs + vl + 0.35) else None)


def frame(t, void=None):
    st, napis = uloz(t, void)
    if void:  # kontrola „końca świata”: surowe płótno, nienarysowane miejsca zostają w barwie pustki
        return st.render(post=False)
    img = st.render()
    if napis:
        subtitle(img, napis)
    return img


def arkusz(only=None, out=None, cols=4, tw=320):
    """Arkusz klatek: kilka chwil każdego ujęcia (początek, środek, koniec)."""
    rows = [i for i in range(len(SCENES)) if not only or i + 1 in only]
    th = tw * 9 // 16
    sheet = Image.new("RGB", (tw * cols, th * len(rows)))
    for r, i in enumerate(rows):
        a, b = SCENES[i][:2]
        for c in range(cols):
            f = 0.03 + 0.94 * c / (cols - 1)
            t = a + (b - a) * f
            im = frame(t).resize((tw, th), Image.LANCZOS)
            ImageDraw.Draw(im).text((5, 3), f"{i + 1} {ODN[i]} {KOL[i]} · {t - a:.1f} s", fill=(255, 255, 0))
            sheet.paste(im, (c * tw, r * th))
    out = out or HERE / "arkusz.png"
    sheet.save(out)
    return out


def _pustka(i):
    """Ile pikseli pustki (nienarysowanego płótna) ma najgorsza klatka ujęcia i; sprawdzana co 4. klatka."""
    from papier import VOID
    a, b = SCENES[i][:2]
    worst, when = 0, a
    for f in range(0, int((b - a) * FPS), 4):
        arr = np.asarray(frame(a + f / FPS, void=VOID)).astype(np.int16)
        n = int(((arr[..., 0] > 250) & (arr[..., 1] < 6) & (arr[..., 2] > 250)).sum())
        if n > worst:
            worst, when = n, a + f / FPS
    return i, worst, when


def _klip(arg):
    """Renderuje jedno ujęcie do pliku mp4 (klatki zaokrąglone w górę, żeby klip pokrył ujęcie na osi)."""
    import subprocess
    i, out = arg
    a, b = SCENES[i][:2]
    n = klatki_ujecia(i)
    if FILM:  # klatki na wspólnej siatce czasu filmu (klatka k filmu = k / FPS)
        a = math.floor(a * FPS + 0.5) / FPS
    ow, oh = int(round(W * papier.Q)), int(round(H * papier.Q))
    part = out.with_name(out.stem + ".part.mp4")  # plik niedokończony nie wygląda na gotowy po przerwaniu
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", CRF, "-preset", "medium", "-pix_fmt", "yuv420p",
                             str(part)],
                            stdin=subprocess.PIPE)
    for f in range(n):
        proc.stdin.write(frame(min(a + f / FPS, b - 1e-3)).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit(f"ffmpeg: {out}")
    os.replace(part, out)
    return i, n


def rozgrzej(ktore=None):
    """Buduje wycinki w procesie głównym, zanim powstaną procesy robocze — po rozwidleniu dzielą one tę samą pamięć.
    Bez tego każdy proces ładował własny komplet wycinków i komputer z 8 GB RAM wchodził w pamięć wymiany (10.11.2026)."""
    for i, (a, b, *_) in enumerate(SCENES):
        if FNS[i] is None or (ktore and i not in ktore):
            continue
        for f in (0.5, 0.93):
            FNS[i](Stage(a, seed=i), swiat.stan(i), SZKIC_CZAS[i][0] * f, SZKIC_CZAS[i][0])  # samo ułożenie sceny tworzy wycinki
    for n in range(10):
        Z.flame(n)


PROCESY = int(os.environ.get("PROCESY", "1"))  # 8 GB RAM i inne otwarte programy: kilka procesów naraz tylko się dławi


def rownolegle(fn, args, procs=None):
    """Jeden proces po kolei (domyślnie) albo kilka z rozwidlenia (PROCESY=3 na maszynie z wolną pamięcią)."""
    procs = procs or PROCESY
    if procs <= 1:
        for a in args:
            yield fn(a)
        return
    import multiprocessing as mp
    # macOS/Linux: rozwidlenie (wspólna pamięć wycinków); Windows nie ma fork — każdy proces wczytuje wycinki sam
    ctx = mp.get_context("fork" if "fork" in mp.get_all_start_methods() else "spawn")
    with ctx.Pool(procs, maxtasksperchild=6) as pool:
        yield from pool.imap_unordered(fn, args)


def klipy(out, only=None, procs=None):
    """Klipy ujęć (numery od 1) do katalogu out; zwraca {indeks: (plik, klatki)}."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    # skróty ujęć (WYCINEK: zapowiedź, tytuł) nie mają własnej funkcji, ale rysują się z oryginału — też idą do klipów
    idx = [i for i in range(len(SCENES)) if (FNS[i] is not None or KOL[i] in WYCINEK) and (not only or i + 1 in only)]
    if (procs or PROCESY) > 1 and sys.platform != "win32":
        rozgrzej(set(idx))
    idx = [i for i in idx if not (out / f"{ODN[i]}.mp4").exists() or os.environ.get("NADPISZ") == "1"]  # wznowienie: gotowe zostają
    done = {}
    for i, n in rownolegle(_klip, [(i, out / f"{ODN[i]}.mp4") for i in idx], procs):
        done[i] = (out / f"{ODN[i]}.mp4", n)
        print(f"{ODN[i]} {KOL[i]}: {n} klatek", flush=True)
    return done


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "arkusz"
    only = ({int(x) for x in sys.argv[2].split(",")} if cmd != "klatka" and len(sys.argv) > 2 and sys.argv[2][0].isdigit()
            else None)  # przy „klatka” drugi argument to czas, nie numery ujęć
    if cmd == "klatka":
        frame(float(sys.argv[2])).save(sys.argv[3] if len(sys.argv) > 3 else str(HERE / "klatka.png"))
    elif cmd == "kontrola":
        idx = [i for i in range(len(SCENES)) if FNS[i] is not None and (not only or i + 1 in only)]
        if PROCESY > 1:
            rozgrzej(set(idx))
        bad = 0
        for i, n, when in sorted(rownolegle(_pustka, idx)):
            bad += n > 0
            print(f"{ODN[i]} {KOL[i]}: {'OK' if n == 0 else f'PUSTKA {n} px w {when - SCENES[i][0]:.2f} s'}")
        sys.exit(1 if bad else 0)
    elif cmd == "klipy":
        klipy(sys.argv[-1], only)
    else:
        print(arkusz(only, sys.argv[3] if len(sys.argv) > 3 else None))
