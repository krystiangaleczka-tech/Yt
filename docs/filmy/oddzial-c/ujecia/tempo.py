"""Tempo ujęć według wzorca zimnego otwarcia (docs/filmy/oddzial-c/MASTER_BIBLE.md, WYTYCZNE_UJEC.md 1.9).

Długość ujęcia wynika z jego roli i kwestii, nigdy z siatki:
- kwestia (lektor / dialog / megafon): oddech przed + wypowiedzenie (~2,6 słowa/s) + pauza po;
- otwarcie sceny: plan ogólny trwa długo (4–7 s), żeby widz się zorientował;
- akcja (bieg, upadek, uderzenie): 1–1,8 s; reakcja bez słów: krótko; detal: krótko;
- napięcie i cisza (najazd, nasłuchiwanie, ciemność): ujęcie trzyma dłużej; koniec sceny dostaje „trzymanie”;
- sąsiednie ujęcia różnią się co najmniej o 1/4 s; rozrzut jest deterministyczny (ten sam przy każdym przeliczeniu);
- dzień ma długość, jaką dają jego ujęcia — każdy inny, od ok. 55 s do ok. 80 s.
Długości są wielokrotnością 1/6 s, więc wypadają w pełnych klatkach i przy 24, i przy 30 kl./s.
Dni z listy AUTO w a_dane*.py dostają czasy z tej zasady; ręcznie ustawione dni (np. 1) zostają.
"""
import math
import re
import sys
import zlib

SPEECH_WPS = 2.6
DZIEN_MIN, DZIEN_MAX = 55, 80  # długość dnia zależnie od tego, co się w nim dzieje (reżyser, 4.11.2026)
STEP = 1 / 6
# Dni narysowane wcześniej (2–20) zostają przy starej regule odsuwania sąsiadów, żeby nie rozjechać wgranego materiału;
# przy ponownym renderze dnia można obniżyć ten próg.
ODSUW_OD_DNIA = 21
ACTION_WORDS = ("biegnie", "bieg", "toczy", "spada", "wypada", "uderz", "rzuca", "przewraca", "wbiega", "ucieka", "szarp",
                "wyrywa", "zatrzaskuje", "łapie", "rzuca się", "skacze", "potyka", "gasi", "chwyta", "zatrzaskują")
TENSION_WORDS = ("patrzy", "nasłuch", "cisza", "ciemn", "nie mruga", "wstrzym", "zastyga", "oddech", "szepcze", "czeka",
                 "nie oddycha", "powoli")


def words_spoken(sound):
    if sound.startswith("L:"):
        return len(sound[2:].split())
    m = re.search(r"„([^”]+)”", sound)
    return len(m.group(1).split()) if m else 0


def is_action(shots):
    moves = [s[1] for s in shots]
    acts = sum(any(w in s[3].lower() for w in ACTION_WORDS) for s in shots)
    return bool({"szarp", "drg"} & set(moves)) or moves.count("jaz") >= 2 or acts >= max(2, len(shots) // 2)


def rola(kadr, ruch, desc, sound, action_beat, first):
    d, n = desc.lower(), words_spoken(sound)
    if kadr == "TYT":
        return "karta"
    if first and kadr in ("PO", "PŚ", "POV"):
        return "otwarcie"
    if ruch in ("szarp", "drg") or any(w in d for w in ACTION_WORDS) or (action_beat and not n):
        return "akcja"
    if ruch == "naj" or sound.strip() == "cisza" or any(w in d for w in TENSION_WORDS):
        return "napięcie"
    if kadr in ("D", "WZ"):
        return "detal"
    if kadr == "Z" and not n:
        return "reakcja"
    if kadr == "PO":
        return "plan"
    return "zwykłe"


BASE = {"karta": 2.0, "otwarcie": 4.6, "akcja": 1.3, "napięcie": 3.0, "detal": 1.8, "reakcja": 1.5, "plan": 3.2,
        "zwykłe": 2.2}
PRE = {"akcja": 0.4, "otwarcie": 1.0, "napięcie": 1.1, "plan": 0.9}
POST = {"akcja": 0.3, "napięcie": 1.0, "otwarcie": 0.9}


def _jit(day, i, lo, hi):
    h = zlib.crc32(f"{day}:{i}".encode()) / 0xFFFFFFFF
    return lo + (hi - lo) * h


def _q(x):
    return math.ceil(x / STEP - 1e-6) * STEP


def plan_dnia(day):
    """[(sec, start_kwestii, długość_kwestii)] dla każdego ujęcia dnia (krotka z DAYS)."""
    n_day, _, scenes = day
    out, roles, i = [], [], 0
    for _, _, beats in scenes:
        flat = [(b, s) for b, (_, shots) in enumerate(beats) for s in shots]
        for j, (b, (kadr, ruch, _, desc, sound)) in enumerate(flat):
            first = j == 0 or (j == 1 and flat[0][1][0] == "TYT")
            last = j == len(flat) - 1
            r = rola(kadr, ruch, desc, sound, is_action(beats[b][1]), first)
            n = words_spoken(sound)
            if r == "karta":
                sec, vs, vl = 2.0, 0.0, 0.0
            elif n:
                vl = n / SPEECH_WPS
                vs = PRE.get(r, 0.7) * _jit(n_day, i, 0.75, 1.3)
                post = (1.2 if last else POST.get(r, 0.55)) * _jit(n_day, i + 99, 0.8, 1.25)
                sec = max(vs + vl + post, BASE[r] * 0.9 if r == "otwarcie" else 0)
            else:
                vs = vl = 0.0
                sec = BASE[r] * _jit(n_day, i, 0.82, 1.18)
                if ruch == "szarp":
                    sec = min(sec, 1.2)
                if sound and r != "akcja":
                    sec += 0.3  # wydarzenie dźwiękowe potrzebuje chwili przed i po
                if last:
                    sec += 0.8 if r in ("napięcie", "plan", "zwykłe", "detal") else 0.3
            out.append([_q(min(7.0, max(1.0, sec))), vs, vl])
            roles.append(r)
            i += 1
    for k in range(1, len(out)):  # sąsiednie ujęcia nie mogą mieć tej samej długości
        if abs(out[k][0] - out[k - 1][0]) < 0.25:
            floor_ = max(1.0, out[k][1] + out[k][2] + 0.2)
            if n_day >= ODSUW_OD_DNIA:  # odsuń od sąsiada (stara reguła odsuwała od siebie i zostawiała 1/6 s różnicy)
                up, down = out[k - 1][0] + 2 * STEP, out[k - 1][0] - 2 * STEP
                out[k][0] = up if roles[k] in ("napięcie", "otwarcie", "plan") or down < floor_ else down
            elif roles[k] in ("napięcie", "otwarcie", "plan") or out[k][0] - 2 * STEP < floor_:
                out[k][0] += 2 * STEP
            else:
                out[k][0] -= 2 * STEP
    total = sum(o[0] for o in out)
    if total < DZIEN_MIN or total > DZIEN_MAX:  # dzień poza zakresem: rozciągnij/ściśnij ujęcia bez słów
        free = [k for k, r in enumerate(roles) if r != "karta" and not out[k][2]]
        tgt = DZIEN_MIN + 1 if total < DZIEN_MIN else DZIEN_MAX - 1
        if free:
            add = (tgt - total) / len(free)
            for k in free:
                out[k][0] = _q(min(7.0, max(1.0, out[k][0] + add)))
        while sum(o[0] for o in out) > DZIEN_MAX and free:  # zaokrąglenia w górę mogły przekroczyć zakres
            k = max(free, key=lambda f: out[f][0])
            out[k][0] -= STEP
    return [tuple(o) for o in out]


def przelicz(days, dni):
    """Podmienia czasy ujęć w podanych dniach według zasady (reszta bez zmian)."""
    res = []
    for day in days:
        n, title, scenes = day
        if n not in dni:
            res.append(day)
            continue
        plan = iter(plan_dnia(day))
        new_scenes = [(st, pl, [(bt, [(k, r, round(next(plan)[0], 4), de, so) for k, r, _, de, so in shots])
                                for bt, shots in beats]) for st, pl, beats in scenes]
        res.append((n, title, new_scenes))
        dl = sum(sh[2] for _, _, b in new_scenes for _, shots in b for sh in shots)
        if not DZIEN_MIN <= dl <= DZIEN_MAX:
            print(f"uwaga: dzień {n} trwa {dl:.1f} s — poza {DZIEN_MIN}–{DZIEN_MAX} s, przebuduj rozpiskę", file=sys.stderr)
    return res


def kwestie(day):
    """Start i długość kwestii w każdym ujęciu (do napisów w renderze)."""
    return [(vs, vl) for _, vs, vl in plan_dnia(day)]
