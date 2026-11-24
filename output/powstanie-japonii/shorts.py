"""Shortsy z „Son of the Sun” (EN): pion 1080 × 1920 wycięty z gotowego renderu końcowego (nic nie rysuje się od nowa).
Wzór: output/pierwszy-cesarz/shorts.py (gałąź film/pierwszy-cesarz) — ten sam układ, przestawiony na render 1080p.

  python3 -I output/powstanie-japonii/shorts.py waz               → output/powstanie-japonii/shorts/waz.mp4
  python3 -I output/powstanie-japonii/shorts.py waz --proba 3 25  → same klatki PNG w tych sekundach Shortsa
                                                                    (build/shorts_proba/, układ)

Dlaczego z renderu, a nie ze Studio: silnik teatru rysuje tylko kadr 16:9 (geometria 1280 × 720), więc pion ze Studio
dałby ten sam wycinek, tylko z nowym renderem. Tu obraz, lektor, muzyka i efekty są dokładnie takie jak w filmie.

Kurtyna (`kurtyna`): Shorts zaczyna się od zasuniętej kurtyny teatru, która się rozsuwa, i kończy jej zasunięciem,
więc w pętli YouTube widz ogląda go w kółko bez szwu. Kurtyna to ta sama połowa z filmu (zestaw.kurtyna) z tym samym
ruchem co render.kurtyna, a dźwięk to ta sama synteza (efekty.kurtyna_nowa).

Części w środku ujęcia (`czesci` jako słownik): `od_w` = sekunda pierwszego ujęcia, od której część się zaczyna,
`do_w` = sekunda ostatniego ujęcia, na której się kończy. Napisy części są przycięte do niej, a `tekst` podmienia napis
kwestii, z której w Shortsie zostaje tylko początek. `lektor` = część ma dźwięk złożony od nowa ze ścieżek filmu
(lektor_en, dzwiek_en/muzyka.wav i efekty.wav, zmiksowane jak w zloz.py), bez kurtyny aktu z efektów, a lektor wchodzi
o tyle sekund później niż w filmie. Tak jest, gdy w kadrze kurtyny już nie ma, a w miksie filmu jeszcze ją słychać.

Kurtyna aktu: Shorts, który zaczyna się pierwszym ujęciem aktu, ma w filmie pod spodem kurtynę z tabliczką aktu
(render.przejscie). Nakładka rusza wtedy dokładnie jak ona (`kurtyna_ruch`), więc wygląda jak jedna kurtyna i zasłania
tabliczkę „Act …”, a jej dźwięk jest już w miksie filmu (`dzwiek_startu=False`).

Układ: u góry zaczepka na papierowej zawieszce jak w filmie; pośrodku pas filmu: wycinek 1199 × 917 z kadru
1920 × 1080, bez paska wypalonych napisów, który przy dwóch wierszach zaczyna się na y = 921. Kadr jedzie za akcją według `kadr`
(środek wycinka jako ułamek szerokości, czas od początku ujęcia), a na cięciach filmu przeskakuje. Pod pasem
duże napisy w stylu napisów filmu, zgrane z pauzami w nagraniach lektora. Tło to ten sam kadr, rozmyty i ciemny.
Czasy ujęć i kwestii pochodzą z rozpiski (dane.py, tak samo jak w publikacja.py i w renderze końcowym FILM=1).
"""
import math
import os
import subprocess
import sys
import wave
from itertools import combinations
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

os.environ["JEZYK"] = "en"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "docs/filmy/powstanie-japonii/ujecia"))
sys.path.insert(0, str(ROOT / "output/pierwszy-cesarz"))  # silnik teatru: zestaw.py (kurtyna, papier, czcionka)
sys.path.insert(0, str(HERE))
from dane import kwestia, okno_kwestii, ujecia  # noqa: E402
import zestaw as Z  # noqa: E402

SRC = HERE / "build/Son_of_the_Sun_1080p_YouTube.mp4"
OUT = HERE / "shorts"
PROBA = HERE / "build/shorts_proba"
LEKTOR = HERE / "lektor_en"
DZWIEK = HERE / "dzwiek_en"  # muzyka.wav i efekty.wav z efekty.py, te same co w renderze końcowym (zloz.py)
FPS = 24
SW, SH = 1920, 1080  # kadr renderu końcowego
Q = SH / 720  # kadr renderu na kadr wzorcowy 1280 × 720 (render.py: ROZDZIELCZOSC=1080 → Q = 1,5)
W, H = 1080, 1920
BAND_Y = 450
BAND_H = 826  # wysokość pasa na ekranie (jak w Shortsach „Pierwszego cesarza”)
CH = 917  # wycinek pasa: pełna wysokość sceny nad paskiem napisów filmu (y0 = 921 przy dwóch wierszach)
CW = CH * W / BAND_H  # 1199
CAP_Y = BAND_Y + BAND_H + 40  # górna krawędź napisu
CAP_W = 820  # szerokość tekstu napisu (prawy brzeg z dala od przycisków Shortsa)
FONT = (Z.FONT_PL, Z.PL_IDX)  # Baskerville SemiBold na macOS, jak napisy i zawieszki w filmie

KURTYNA_ZYSK = 1.0  # synteza kurtyny (efekty.kurtyna_nowa) w miksie: zloz.EFEKTY = 1,0, kurtyna w efekty.py z wagą 1,0
# Render końcowy jest o 2,57 dB cichszy niż miks ścieżek z zloz.py (pomiar 24.11.2026 w czterech miejscach filmu: −2,56…−2,58 dB,
# stała różnica, czyli liniowe wzmocnienie po limiterze). Część z dźwiękiem ze ścieżek dostaje to samo, inaczej byłaby głośniejsza.
FILM_ZYSK_DB = -2.57

# czesci: kawałki filmu (od ujęcia, do ujęcia włącznie), sklejone jeden za drugim
# kurtyna: "start" = Shorts zaczyna się od zasuniętej kurtyny, która się rozsuwa; "koniec" = kurtyna zasuwa się na
# końcu. Oba końce zasunięte = pętla bez szwu: YouTube puszcza Shortsa w kółko, kurtyna się zasuwa i znów rozsuwa.
SHORTS = {
    # 1. wybór (23.11.2026): akt III, wąż o ośmiu głowach. Zaczepka to pytanie aktu III z filmu.
    # Montaż reżysera (23.11): najpierw Susanoo niszczy pola ryżowe siostry (2:00,4–2:10,1), potem zjeżdża na linkach na
    # ziemię (do „Susanoo was banished to earth,”), zaraz po wylądowaniu rozstawia kadzie z sake — bez rozmowy ze starcami
    # i dziewczyną — i dalej wąż, picie, miecz. Lektor czyta: „Susanoo was banished to earth, and set out eight vats…”.
    "waz": dict(
        czesci=[("susanoo", "susanoo"),
                # 0,85 s: kurtyna aktu III z filmu już poza pasem (jej rozsuwanie słychać w miksie, więc dźwięk ze ścieżek);
                # 3,1 s: przed gagiem „AW!...” (3,3 s) i przed „to the land of Izumo”
                dict(od="wygnanie", do="wygnanie", od_w=0.85, do_w=3.1, lektor=0.4),
                # 4,22 s: pauza lektora przed „and set out eight vats of strong sake”, starcy już zeszli
                dict(od="kadzie", do="miecz", od_w=4.22)],
        koniec=-0.35,  # miecz kończy scenę ściemnieniem (render.CIEMNO = 0,35 s): Shorts kończy się przed nim
        kurtyna=("start", "koniec"),
        tekst={"wygnanie": "Susanoo was banished to earth,"},
        tytul=["HOW DO YOU BEAT", "AN 8-HEADED SERPENT?"],
        kadr={
            "susanoo": [(0, .33), (2.4, .33), (4.0, .40), (5.0, .55), (6.6, .70)],  # za Susanoo: chata z ryżem, potem dach
            "wygnanie": [(0, .50)],  # zejście na linkach pośrodku
            "kadzie": [(0, .58), (1.6, .58), (3.0, .33)],  # w Shortsie od 4,22 s: Susanoo z grzebieniem i kadzie
            "orochi": [(0, .32), (2.0, .32), (4.5, .50)],  # pierwsze głowy wyrastają przy Susanoo, potem całe osiem
            "pije": [(0, .50)],
            "miecz": [(0, .40), (3.0, .40), (4.6, .55)],  # cięcie i „HELP!”, potem miecz wyrasta z ogona po prawej
        }),
    # Cały film w jednym Shortsie, najwyżej minuta (24.11.2026, reżyser: „shorts z całego filmu, potnij go fajnie, żeby
    # wszystko miało ręce i nogi”, a po wersji 2-minutowej: „skróć do minuty, przecież to na YT”). Same pełne zdania
    # lektora z filmu, ułożone w opowieść, którą obiecuje zapowiedź: bogowie (wyspa z kropli) → potwór (Susanoo i wąż
    # → miecz) → czterej bracia, z których przeżył jeden → pierwszy cesarz → „kraj, który zaczął się od kropli
    # z włóczni”, czyli klamra z początkiem. Bracia jak w haku filmu: kurtyna odsłania czterech („Only one of them
    # survived.”), potem po kolei, jak zginęli trzej (strzała, cień, burza), więc „he” przy tronie to ten, który przeżył,
    # a imię Jimmu pada w ostatnim zdaniu. W minutę nie weszły: przyczyna wygnania Susanoo (pola ryżowe), „HIC!”,
    # skarby dla Ninigiego, wyprawa na wschód, złoty ptak.
    "calosc": dict(
        czesci=[dict(od="zap_jaskinia", do="zap_blysk", do_w=0.47),  # zapowiedź: bogowie, potwory, czterej bracia
                dict(od="wlocznia", do="wlocznia", od_w=0.31, do_w=5.66),  # „They” = dwaj bogowie na moście w kadrze
                dict(od="kropla", do="kropla", od_w=0.27, do_w=6.42),  # kropla, wyspa i „TA-DA!”
                dict(od="wygnanie", do="wygnanie", od_w=0.85, do_w=3.1, lektor=0.4),  # jak w „waz”
                # kadzie i wąż do „eight heads and eight tails” (pauza 0,33 s przed „and it stretched”)
                dict(od="kadzie", do="orochi", od_w=4.22, do_w=3.1),
                dict(od="miecz", do="miecz", od_w=0.19, do_w=6.12),  # do „found a sword in its tail” (przed „tradition says”)
                dict(od="teatr", do="teatr", od_w=0.07, do_w=2.67),  # kurtyna sceny odsłania czterech braci
                dict(od="hak_rana", do="hak_rana", od_w=0.26, do_w=4.16),
                dict(od="hak_cien", do="hak_cien", od_w=0.16, do_w=4.06),
                dict(od="hak_burza", do="hak_burza", od_w=0.33, do_w=3.03),  # „AAAA!”, „BROTHER!”
                dict(od="tron", do="tron", od_w=2.21, do_w=8.39),  # od „in 660 BC” (po pauzie za „new year,”)
                dict(od="koniec", do="koniec", od_w=0.26, do_w=8.71)],  # odjazd do ramy teatru, scena gaśnie
        kurtyna=("start", "koniec"),
        tekst={"wygnanie": "Susanoo was banished to earth,",
               "orochi": "The serpent had eight heads and eight tails.",
               "miecz": "When the drunken heads fell asleep, Susanoo cut the serpent apart and found a sword in its tail.",
               "tron": "In 660 BC, he took the throne there as the first emperor of Japan."},
        tytul=["JAPAN'S ENTIRE MYTH", "IN 60 SECONDS"],
        kadr={
            "zap_jaskinia": [(0, .55)], "zap_susanoo": [(0, .40)], "zap_miecz": [(0, .47)], "zap_strzaly": [(0, .50)],
            "zap_uzume": [(0, .50)], "zap_pulapka": [(0, .45)], "zap_niedzwiedz": [(0, .60)], "zap_wrona": [(0, .45)],
            "zap_bitwa": [(0, .40)], "zap_blysk": [(0, .35)],
            "wlocznia": [(0, .52)],
            "kropla": [(0, .50)],
            "wygnanie": [(0, .50)],
            "kadzie": [(0, .31)],  # od 4,22 s: Susanoo z kadziami przy lewym brzegu kadru filmu
            "orochi": [(0, .32), (1.6, .32), (3.1, .40)],  # głowy wyrastają przy Susanoo
            "miecz": [(0, .38), (3.6, .38), (4.6, .55)],  # „HELP!” po lewej cały, potem miecz z ogona
            "teatr": [(0, .50)],
            "hak_rana": [(0, .52)],
            "hak_cien": [(0, .42)],
            "hak_burza": [(0, .40), (1.9, .40), (2.6, .58)],  # „AAAA!” po lewej, potem „BROTHER!” po prawej
            "tron": [(0, .45)],  # „660 BC” po lewej
            "koniec": [(0, .50)],
        }),
}


# ---------- czas ----------

def siatka(t):
    return math.floor(t * FPS + 0.5) / FPS


def plan(cfg):
    """Części Shortsa, każda to lista ujęć: (klucz, start w filmie, koniec w filmie, tekst kwestii, start i długość
    kwestii w ujęciu)."""
    t, wszystkie = 0.0, []
    for u in ujecia():
        a, t = siatka(t), t + u[5]
        vs, vl = okno_kwestii(u[7])
        wszystkie.append((u[2], a, siatka(t), kwestia(u[7]), vs, vl))
    klucze = [w[0] for w in wszystkie]
    out = []
    for c in cfg["czesci"]:
        c = c if isinstance(c, dict) else dict(od=c[0], do=c[1])
        out.append((wszystkie[klucze.index(c["od"]):klucze.index(c["do"]) + 1], c))
    return out


def wysokosc_wycinka(txt):
    """Wysokość wycinka nad wypalonym napisem filmu w tym ujęciu (render.subtitle przy Q = 1,5: wiersze po 60 znaków,
    54 px każdy, pasek od y = 1050 − 54 × wiersze − 21). Przy trzech wierszach pasek zaczyna się na 867, więc wycinek
    jest niższy, a pas pokazuje go trochę bliżej."""
    if not txt:
        return CH
    wiersze, cur = 1, ""
    for w in txt.split():
        if cur and len(cur) + len(w) + 1 > 60:
            wiersze, cur = wiersze + 1, w
        else:
            cur = f"{cur} {w}".strip()
    return min(CH, round(SH - 20 * Q - 36 * Q * wiersze - 14 * Q) - 4)


def sciezka_kadru(cfg, uj, k0, n):
    """Środek wycinka (ułamek szerokości kadru) i jego wysokość dla każdej klatki: łamana przez punkty `kadr`,
    wygładzona w obrębie ujęcia."""
    c, ch = np.zeros(n), np.full(n, float(CH))
    for key, a, b, txt, *_ in uj:
        i0, i1 = max(0, round(a * FPS) - k0), min(n, round(b * FPS) - k0)
        if i1 <= i0:
            continue
        ch[i0:i1] = wysokosc_wycinka(txt)
        half = ch[i0] * CW / CH / 2 / SW
        pts = cfg["kadr"][key]
        tt = (np.arange(i0, i1) + k0) / FPS - a
        seg = np.interp(tt, [p[0] for p in pts], [p[1] for p in pts])
        sig = 0.35 * FPS  # wygładzenie: ruszenie i hamowanie kamery zamiast szarpnięć na punktach
        r = int(3 * sig)
        g = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2)
        seg = np.convolve(np.pad(seg, r, mode="edge"), g / g.sum(), mode="valid")
        c[i0:i1] = np.clip(seg, half, 1 - half)
    return np.stack([c, ch], 1)


def mowa(key):
    """Nagranie lektora: (środki pauz, odcinki mowy) w s od początku nagrania; pauza = cisza co najmniej 0,15 s."""
    with wave.open(str(LEKTOR / f"{key}.wav")) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
        sr, ch = w.getframerate(), w.getnchannels()
    x = x.reshape(-1, ch).mean(1)
    hop = sr // 100
    rms = np.sqrt(np.convolve(x ** 2, np.ones(hop * 2) / (hop * 2), mode="same")[::hop])
    glos = rms >= 0.08 * np.percentile(rms, 95)
    odc, i = [], 0
    while i < len(glos):  # odcinki mowy, sklejone przez przerwy krótsze niż 0,15 s
        if glos[i]:
            j = i
            while j < len(glos) and (glos[j] or glos[j:j + 15].any()):
                j += 1
            odc.append((i / 100, j / 100))
            i = j
        else:
            i += 1
    return [(a[1] + b[0]) / 2 for a, b in zip(odc, odc[1:])], odc


def czas_w_mowie(odc, frac):
    """Moment, w którym pada ułamek `frac` tekstu: tekst rozłożony równo na sam czas mowy, bez pauz."""
    cel = frac * sum(b - a for a, b in odc)
    for a, b in odc:
        if cel <= b - a:
            return a + cel
        cel -= b - a
    return odc[-1][1]


# ---------- napisy ----------

def font(size):
    return ImageFont.truetype(FONT[0], size, index=FONT[1])


def zawin(txt, f, maks):
    lines, cur = [], ""
    for w in txt.split():
        nxt = f"{cur} {w}".strip()
        if cur and f.getlength(nxt) > maks:
            lines.append(cur)
            cur = w
        else:
            cur = nxt
    return lines + [cur]


SLABE = {"a", "an", "the", "of", "to", "and", "so", "his", "her", "its", "their", "that", "was", "were", "which", "with",
         "in", "on", "at", "by", "for", "from", "who", "he", "she", "it", "had", "could", "would"}
ZDANIE = {"that", "because", "so", "and", "but", "while", "when", "which", "who", "before", "after", "until"}  # cięcie przed nimi


def kawalki(txt, f):
    """Kwestia na kawałki po najwyżej dwa wiersze: najmniej kawałków, cięcie najchętniej po przecinku,
    nigdy po słowie, które ciągnie zdanie dalej („so | long”, „the | king”), długości możliwie równe."""
    slowa = txt.split()
    if len(zawin(txt, f, CAP_W)) <= 2:
        return [txt]
    best = None
    for k in range(2, 8):
        for cuts in combinations(range(1, len(slowa)), k - 1):
            czesci = [" ".join(slowa[a:b]) for a, b in zip((0,) + cuts, cuts + (len(slowa),))]
            if any(len(zawin(c, f, CAP_W)) > 2 for c in czesci):
                continue
            kara = sum(0 if slowa[c - 1][-1] in ",;:." else 5 if slowa[c - 1].lower() in SLABE
                       else 1 if slowa[c].lower() in ZDANIE else 3 for c in cuts)
            sr = len(txt) / k
            koszt = kara + 1.5 * sum(abs(len(c) - sr) for c in czesci) / len(txt) + 0.5 * (k - 2)
            if best is None or koszt < best[0]:
                best = (koszt, czesci)
        if best and k >= 3:
            break
    return best[1]


def _slowa(txt):
    return [w.strip(".,;:!?'\"‘’“”").lower() for w in txt.split()]


def wpisy(uj, tekst=None):
    """Napisy Shortsa: (od, do, tekst) w czasie filmu; granice kawałków dociągnięte do pauz lektora. `tekst` podmienia
    napis kwestii (klucz → tekst), gdy Shorts bierze z niej tylko kawałek (początek, środek albo koniec): kawałek
    leży w czasie tam, gdzie te słowa padają w całej kwestii. Kwestia dłuższa niż jej ujęcie (zapowiedź, mówiona
    przez kilka krótkich ujęć) ma napis do końca kwestii, a nie do końca ujęcia."""
    f, out = font(CAP_SIZE), []
    for key, a, b, pelny, vs, vl in uj:
        txt = (tekst or {}).get(key, pelny)
        if not txt:
            continue
        czesci = kawalki(txt, f)
        p, odc = mowa(key) if (LEKTOR / f"{key}.wav").exists() else ([], [(0.0, vl)])
        cale, kaw = _slowa(pelny), _slowa(txt)
        i = next((i for i in range(len(cale) - len(kaw) + 1) if cale[i:i + len(kaw)] == kaw), None)
        if txt == pelny or i is None:
            off, razem, do_konca, spacja = 0, sum(len(c) for c in czesci), True, 0
        else:  # kawałek kwestii: ułamki liczone na całym tekście (ze spacjami), od miejsca, gdzie kawałek się zaczyna
            sl = pelny.split()
            off = len(" ".join(sl[:i])) + (1 if i else 0)
            razem, do_konca, spacja = len(pelny), i + len(kaw) == len(cale), 1

        def granica(fr):
            g = czas_w_mowie(odc, fr)
            blisko = [q for q in p if abs(q - g) < 0.8]
            return min(blisko, key=lambda q: abs(q - g)) if blisko else g

        granice, acc = [granica(off / razem) if off else 0.0], off
        for c in czesci[:-1]:
            acc += len(c) + spacja
            granice.append(granica(acc / razem))
        # jak w filmie: napis zostaje 0,35 s po kwestii (po ostatnim słowie kawałka)
        granice.append((vl if do_konca else granica((off + len(txt)) / razem)) + 0.35)
        for c, g0, g1 in zip(czesci, granice, granice[1:]):
            koniec = b if a + vs + vl + 0.35 <= b else a + vs + vl + 0.35
            out.append((a + vs + g0, min(koniec, a + vs + g1), c))
    return out


CAP_SIZE = 50


def obraz_napisu(txt):
    """Napis jak w filmie (pasek kremowego papieru, ciemny tekst), tylko większy."""
    f = font(CAP_SIZE)
    lines = zawin(txt, f, CAP_W)
    lh, pad = 64, 22
    tw = max(f.getlength(ln) for ln in lines)
    bw, bh = int(tw + 2 * 30), int(lh * len(lines) + 2 * pad)
    im = Image.new("RGBA", (W, bh + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0 = (W - bw) // 2
    d.rounded_rectangle([x0 + 5, 7, x0 + bw + 5, bh + 7], 8, fill=(20, 12, 8, 110))
    d.rounded_rectangle([x0, 0, x0 + bw, bh], 8, fill=(238, 224, 192, 242))
    for n, ln in enumerate(lines):
        d.text((W / 2, pad + lh * n + lh / 2 - 2), ln, font=f, fill=(44, 28, 22, 255), anchor="mm")
    return im


def obraz_tytulu(lines, size=74):
    """Zaczepka na papierowej zawieszce z filmu (zestaw.stack: ten sam papier i ta sama czcionka co „KILL THE KING!”)."""
    f = font(size * 2)
    tw = max(f.getlength(ln) for ln in lines) / 2
    w, lh = int(tw + 96), size * 1.22
    h = int(lh * len(lines) + 56)
    parts = [(Z.poly([(4, 4), (w - 4, 4), (w - 4, h - 4), (4, h - 4)]), (240, 226, 194),
              dict(kind="gladki", edge=4, contrast=1.3))]
    for n, ln in enumerate(lines):
        parts.append((Z.glyphs(ln, size, FONT[0], FONT[1], (w / 2, 28 + lh * n + lh / 2 + 2), "mm"), (48, 30, 24),
                      dict(kind="gladki", rough=0.5)))
    tag = Z.stack(w, h, parts, seed=len(lines[0])).rotate(-1.5, resample=Image.BICUBIC, expand=True)
    im = Image.new("RGBA", (W, tag.height + 40), (0, 0, 0, 0))
    cien = Image.new("RGBA", tag.size, (20, 12, 8, 0))
    cien.putalpha(tag.getchannel("A").point(lambda v: v * 0.55))
    x = (W - tag.width) // 2
    im.alpha_composite(cien.filter(ImageFilter.GaussianBlur(6)), (x + 6, 14))
    im.alpha_composite(tag, (x, 4))
    return im


def cien_pasa():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(im).rectangle([0, BAND_Y + 6, W, BAND_Y + BAND_H + 16], fill=(0, 0, 0, 170))
    return im.filter(ImageFilter.GaussianBlur(14))


# ---------- składanie ----------

def klatka(src, c, ch=CH):
    cw = ch * CW / CH
    x0 = c * SW - cw / 2
    band = src.resize((W, BAND_H), Image.LANCZOS, box=(x0, 0, x0 + cw, ch))
    bw = SH * 9 / 16  # tło: pionowy wycinek pełnej wysokości kadru
    bx = min(max(c * SW - bw / 2, 0), SW - bw)
    small = src.resize((54, 96), Image.BILINEAR, box=(bx, 0, bx + bw, SH)).filter(ImageFilter.GaussianBlur(2.5))
    tlo = small.point(lambda v: int(v * 0.42)).resize((W, H), Image.BICUBIC).convert("RGBA")
    return tlo, band


# ---------- kurtyna ----------

KURTYNA_RUCH = (0.1, 0.85, 0.8)  # start: zasunięta przez 0,1 s, rozsuwa się 0,85 s; koniec: zasuwa się 0,8 s (render.KURTYNA)
_kurtyna_img = {}


def kurtyna_obraz(strona):
    """Połowa kurtyny z filmu (zestaw.kurtyna), zwykła alfa zamiast wymnożonej."""
    if strona not in _kurtyna_img:
        m = Z.kurtyna(strona).mips[0]
        _kurtyna_img[strona] = Image.frombytes("RGBa", m.size, m.tobytes()).convert("RGBA")
    return _kurtyna_img[strona]


def kurtyna_k(i, n, cfg):
    """Jak bardzo zasunięta jest kurtyna w klatce i (0 otwarta, 1 zasunięta)."""
    czekaj, otw, zam = cfg.get("kurtyna_ruch", KURTYNA_RUCH)
    t, T, k = i / FPS, n / FPS, 0.0
    if "start" in cfg.get("kurtyna", ()):
        k = max(k, 1 - min(1.0, max(0.0, (t - czekaj) / otw)))
    if "koniec" in cfg.get("kurtyna", ()):
        k = max(k, min(1.0, max(0.0, (t - (T - zam - 2 / FPS)) / zam)))  # dwie ostatnie klatki: zasunięta
    return k


def kurtyna_na_pasie(band, k):
    """Kurtyna przed pasem jak render.kurtyna: połowy po 700 px kadru wzorcowego, zakładka 60 px na środku, przy
    otwieraniu zsuwają się na boki i ściskają (0,86 szerokości). Środek kurtyny = środek pasa, więc pętla jest bez szwu
    bez względu na to, gdzie stoi wycinek."""
    if k <= 0.001:
        return band
    s = Q * W / CW  # piksele pasa na piksel kadru wzorcowego 1280 × 720 (kadr filmu = Q × wzorcowy)
    e = Z.ease(k)
    przes = (1 - e) * 760
    band = band.copy()
    for strona in (-1, 1):
        img = kurtyna_obraz(strona)
        w = 700 * (0.86 + 0.14 * e) * s
        h = 700 * img.height / img.width * s
        im = img.resize((max(1, round(w)), round(h)), Image.BILINEAR)
        brzeg = 640 - 30 * strona + strona * przes  # wewnętrzna krawędź połowy w kadrze wzorcowym
        xb = W / 2 + (brzeg - 640) * s
        x, y = round(xb - w if strona < 0 else xb), round(-70 * s)
        cien = im.getchannel("A").point(lambda v: int(v * 0.45)).filter(ImageFilter.GaussianBlur(7 * s))
        band.paste((20, 12, 8), (x + round(8 * strona * s), y), cien)
        band.paste(im.convert("RGB"), (x, y), im.getchannel("A"))
    return band


def dzwiek_kurtyny(n, cfg, path):
    """Szelest kurtyny (synteza z filmu, efekty.kurtyna_nowa) w chwilach ruchu nakładki; WAV 44,1 kHz mono."""
    import efekty as E
    czekaj, _otw, zam = cfg.get("kurtyna_ruch", KURTYNA_RUCH)
    x = np.zeros(int(n / FPS * E.SR) + 1)
    zdarzenia = []
    if "start" in cfg.get("kurtyna", ()) and cfg.get("dzwiek_startu", True):
        zdarzenia.append((czekaj, E.kurtyna_nowa(False)))
    if "koniec" in cfg.get("kurtyna", ()):
        zdarzenia.append((n / FPS - zam - 2 / FPS, E.kurtyna_nowa(True)))
    for t, s in zdarzenia:
        i = int(t * E.SR)
        s = s[:len(x) - i]
        x[i:i + len(s)] += s * KURTYNA_ZYSK
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(E.SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


# ---------- dźwięk części ze ścieżek filmu ----------

def dzwiek_ze_sciezek(t0, t1, opoz, path):
    """Dźwięk odcinka filmu [t0, t1) złożony od nowa jak w zloz.py (lektor 100 %, muzyka 80 %, efekty 100 %), ale bez
    rozsuwania kurtyny aktu w efektach i z lektorem `opoz` s później niż w filmie. Kurtyna jest odjęta dokładnie:
    efekty.wav = 0,9 · tanh(1,2 · suma) (efekty.zapisz), a kurtyna to efekty.kurtyna_nowa(False) razy ściszanie pod
    lektorem (efekty.main), więc po odwróceniu tanh da się ją odjąć próbka w próbkę."""
    import efekty as E
    import render as R
    SR = E.SR

    def czytaj(f, a=0, ile=10 ** 9):  # fragment WAV mono 16 bit od próbki a
        with wave.open(str(f)) as w:
            w.setpos(a)
            return np.frombuffer(w.readframes(ile), np.int16).astype(np.float64) / 32767

    us = ujecia()
    n = E.N(sum(u[5] for u in us))
    voice, kurtyny, tu = np.zeros(n, bool), [], 0.0  # jak efekty.main: czas nierówny z rozpiski
    zam, dl, czekaj, otw = R.KURTYNA
    for idx, u in enumerate(us):
        vs, vl = okno_kwestii(u[7])
        if vl:
            voice[E.N(tu + vs):E.N(tu + vs + vl)] = True
        g = R.GRANICE[idx]
        if g["pierwsze_aktu"] and idx > 0 and g["akt"] not in R.BEZ_KURTYNY:
            kurtyny.append(tu + czekaj)
        if g["ostatnie_aktu"] and idx < len(us) - 1 and g["akt"] + 1 not in R.BEZ_KURTYNY:
            assert not (t0 < tu + u[5] and tu + u[5] - zam < t1), "zasuwanie kurtyny w części: nieobsłużone"
        tu += u[5]
    i0, i1 = E.N(t0), E.N(t0) + E.N(t1 - t0)
    w0 = i0 - 10 * SR  # ściszanie liczone na oknie z zapasem (10 s przed, 5 s po): obwiednia zdąży się ustalić
    env = E.sciszanie(voice[w0:i1 + 5 * SR], -5.0)  # env[i - w0] = ściszanie w próbce i filmu
    fx = czytaj(DZWIEK / "efekty.wav", i0 - SR, i1 - i0 + 2 * SR)
    lin = np.arctanh(np.clip(fx / 0.9, -0.999999, 0.999999)) / 1.2  # sekunda zapasu z obu stron
    k = E.kurtyna_nowa(False)
    odjete = 0
    for tk in kurtyny:
        j = E.N(tk)
        if j + len(k) <= i0 - SR or j >= i1 + SR:
            continue
        a, b = max(j, i0 - SR), min(j + len(k), i1 + SR)
        lin[a - (i0 - SR):b - (i0 - SR)] -= k[a - j:b - j] * env[a - w0:b - w0]
        odjete += 1
    fx_seg = (0.9 * np.tanh(1.2 * lin))[SR:SR + (i1 - i0)]
    mus = czytaj(DZWIEK / "muzyka.wav", i0, i1 - i0)
    glos = np.zeros(i1 - i0)
    t = 0.0
    for u in us:  # lektor jak w zloz.py: klatka startu ujęcia + oddech
        a = siatka(t)
        t += u[5]
        vs, vl = okno_kwestii(u[7])
        if not vl or a + vs + opoz >= t1 or a + vs + opoz + vl + 0.5 <= t0:
            continue
        x = czytaj(LEKTOR / f"{u[2]}.wav")
        j = E.N(a + vs + opoz) - i0
        lo, hi = max(0, j), min(len(glos), j + len(x))
        glos[lo:hi] += x[lo - j:hi - j]
    y = glos + 0.8 * mus + fx_seg
    print(f"    dźwięk ze ścieżek {t0:.3f}–{t1:.3f} s: odjęte kurtyny {odjete}, szczyt {np.abs(y).max():.2f}")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


# ---------- składanie ----------

def main():
    nazwa = sys.argv[1] if len(sys.argv) > 1 else "waz"
    cfg = SHORTS[nazwa]
    czesci = plan(cfg)
    okna, sciezka, caps, n = [], [], [], 0  # okna: (pierwsza klatka w filmie, liczba klatek, część) każdej części
    for j, (uj, c) in enumerate(czesci):
        t0 = uj[0][1] + c.get("od_w", 0.0)
        t1 = (uj[-1][1] + c["do_w"] if "do_w" in c
              else uj[-1][2] + c.get("tyl", cfg.get("koniec", 0.0) if j == len(czesci) - 1 else 0.0))
        k0, nj = round(t0 * FPS), round(t1 * FPS) - round(t0 * FPS)
        okna.append((k0, nj, c))
        sciezka.append(sciezka_kadru(cfg, uj, k0, nj))
        przes = c.get("lektor", 0.0)  # napisy idą za lektorem
        for a, b, txt in wpisy(uj, cfg.get("tekst")):
            fa, fb = max(round((a + przes) * FPS), k0), min(round((b + przes) * FPS), k0 + nj)
            if fb - fa >= FPS // 2:  # napis przycięty do części; okruchy krótsze niż 0,5 s odpadają
                caps.append((fa - k0 + n, fb - k0 + n, obraz_napisu(txt)))
        print(f"  część {j + 1}: film {k0 / FPS:.3f}–{(k0 + nj) / FPS:.3f} s ({nj / FPS:.2f} s)"
              + (f", dźwięk ze ścieżek, lektor +{przes} s" if "lektor" in c else ""))
        n += nj
    sciezka = np.concatenate(sciezka)
    tytul, cien = obraz_tytulu(cfg["tytul"]), cien_pasa()
    tyt_y = max(150, (BAND_Y - tytul.height) // 2 + 10)
    proba = [float(x) for x in sys.argv[sys.argv.index("--proba") + 1:]] if "--proba" in sys.argv else None
    OUT.mkdir(exist_ok=True)
    PROBA.mkdir(parents=True, exist_ok=True)
    print(f"{nazwa}: {n / FPS:.2f} s, {n} klatek, {len(okna)} części, {len(caps)} napisów, kurtyna: {cfg.get('kurtyna')}")

    enc, kwav = None, OUT / f".{nazwa}_kurtyna.wav"
    if proba is None:
        T = n / FPS
        wej, fil = [], ""
        for j, (k0, nj, c) in enumerate(okna):  # dźwięk filmu z każdej części; na sklejeniach krótkie wyciszenie
            if "lektor" in c:
                pw = OUT / f".{nazwa}_czesc{j + 1}.wav"
                dzwiek_ze_sciezek(k0 / FPS, (k0 + nj) / FPS, c["lektor"], pw)
                wej += ["-i", str(pw)]
            else:
                wej += ["-ss", f"{k0 / FPS:.4f}", "-t", f"{nj / FPS:.4f}", "-i", str(SRC)]
            f = [] if j == len(okna) - 1 else [f"afade=t=out:st={nj / FPS - 0.15:.4f}:d=0.15"]
            f += [] if j == 0 else ["afade=t=in:d=0.15"]
            f += ["alimiter=limit=0.95", f"volume={FILM_ZYSK_DB}dB"] if "lektor" in c else []  # jak zloz.py + render
            fil += f"[{j + 1}:a]{','.join(f + ['aformat=sample_rates=48000:channel_layouts=stereo'])}[s{j}];"
        fil += "".join(f"[s{j}]" for j in range(len(okna))) + f"concat=n={len(okna)}:v=0:a=1,"
        fil += f"afade=t=in:d=0.12,afade=t=out:st={T - 0.6:.4f}:d=0.6[m];"
        if cfg.get("kurtyna"):
            dzwiek_kurtyny(n, cfg, kwav)
            wej += ["-i", str(kwav)]
            fil += (f"[{len(okna) + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo[k];"
                    "[m][k]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
        else:
            fil += "[m]anull[a]"
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             *wej, "-filter_complex", fil, "-map", "0:v", "-map", "[a]",
             "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-t", f"{T:.4f}", "-movflags", "+faststart", str(OUT / f"{nazwa}.mp4")],
            stdin=subprocess.PIPE)
    rozmiar = SW * SH * 3
    i = 0
    for k0, nj, _c in okna:
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{k0 / FPS - 0.005:.4f}", "-i", str(SRC),
                                "-frames:v", str(nj), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        for _ in range(nj):
            buf = dec.stdout.read(rozmiar)
            if len(buf) < rozmiar:
                raise SystemExit(f"za mało klatek w źródle: klatka {i} z {n}")
            if proba is None or any(abs(i / FPS - p) < 0.5 / FPS for p in proba):
                src = Image.frombuffer("RGB", (SW, SH), buf)
                tlo, band = klatka(src, *sciezka[i])
                band = kurtyna_na_pasie(band, kurtyna_k(i, n, cfg))
                tlo.alpha_composite(cien)
                tlo.paste(band, (0, BAND_Y))
                tlo.alpha_composite(tytul, (0, tyt_y))
                for a, b, im in caps:
                    if a <= i < b:
                        tlo.alpha_composite(im, (0, CAP_Y))
                if proba is not None:
                    tlo.convert("RGB").save(PROBA / f"{nazwa}_proba_{i / FPS:05.2f}.png")
                else:
                    enc.stdin.write(tlo.convert("RGB").tobytes())
            if i % 240 == 0:
                print(f"  {i / FPS:5.1f} s", flush=True)
            i += 1
        dec.stdout.close()
        dec.wait()
    if enc:
        enc.stdin.close()
        enc.wait()
        kwav.unlink(missing_ok=True)
        for pw in OUT.glob(f".{nazwa}_czesc*.wav"):
            pw.unlink()
        print("gotowe:", OUT / f"{nazwa}.mp4")


if __name__ == "__main__":
    main()
