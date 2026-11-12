"""Rig postaci wariantu A: gra aktorska ujęcia — głowa (obrót, skręt, skinienie), tułów (pochylenie, ramiona),
ręce (gest przy mówieniu) i usta zsynchronizowane z prawdziwym oknem kwestii.

Ujęcie dostaje akcje w słowniku RIG pliku dnia (render_dNN.py), np.
    RIG = {7: {"zosia": "mowi"}, 9: {"nowak": ("kreci", {"t": 0.4})}, 12: {"*": "w_dol"}}
Klucz to numer ujęcia w dniu (jak w FNS), wartość: postać → akcja albo (akcja, parametry) albo lista akcji.
„*” — każda postać rysowana w ujęciu (np. zbliżenie narratora, który w kodzie nie ma nazwy).
dzien_base.frame ustawia bieżące ujęcie (set_shot) przed rysowaniem, a kit_a.face_cu / figure / figure_back /
narrator_cu pytają o pozę (pose). Ujęcie bez wpisu w RIG rysuje się dokładnie tak jak wcześniej.

Jednostki pozy: przesunięcia w promieniach głowy (zbliżenie: 120 px, plan ogólny: 46·s), obrót w stopniach,
yaw -1..1 (skręt twarzy w bok), shrug 0..1 (ramiona w górę), lean — skala „pochylenia ku kamerze”.
Zasady (WYTYCZNE_UJEC): ciało jest jednym kawałkiem (szyja idzie za głową, ręka za barkiem), tłum ma osobne
opóźnienia (seed postaci), pan Henryk rusza się wolno i nie mruga.
"""
import math

from render import ease, noise

SHOT = {"day": 0, "i": 0, "lt": 0.0, "T": 1.0, "vs": 0.0, "vl": 0.0}
ACTS = {}  # postać → [(akcja, parametry)]
SLOW = {"henryk": 1.6}  # pan Henryk wszystko robi wolniej

NEUTRAL = dict(rot=0.0, hx=0.0, hy=0.0, bx=0.0, by=0.0, yaw=0.0, shrug=0.0, lean=0.0, gx=0.0, gy=0.0,
               breath=1.0, breath_add=0.0, mouth=None, gesture=0.0, hand="r", gdx=0.0, gdy=0.0, swallow=0.0)


def _norm(spec):
    if spec is None:
        return []
    if isinstance(spec, str):
        return [(spec, {})]
    if isinstance(spec, tuple) and len(spec) == 2 and isinstance(spec[0], str) and isinstance(spec[1], dict):
        return [spec]
    out = []
    for s in spec:
        out += _norm(s)
    return out


def set_shot(day, i, lt, T, vs, vl, rig):
    """Wołane przez dzien_base.frame przed rysowaniem ujęcia."""
    SHOT.update(day=day, i=i, lt=lt, T=T, vs=vs, vl=vl)
    ACTS.clear()
    for who, spec in (rig or {}).items():
        ACTS[who] = _norm(spec)


def active():
    return bool(ACTS)


def bump(x, a, b):
    """0 → 1 → 0 między a i b (gładko)."""
    if x <= a or x >= b:
        return 0.0
    return math.sin(math.pi * (x - a) / (b - a)) ** 2


def step(x, a, d):
    return ease((x - a) / max(d, 1e-3))


def _seed(who, k):
    return sum(map(ord, who)) * 37 + SHOT["day"] * 101 + SHOT["i"] * 7 + k * 13


def speaking(lt=None):
    lt = SHOT["lt"] if lt is None else lt
    return SHOT["vl"] > 0 and SHOT["vs"] <= lt <= SHOT["vs"] + SHOT["vl"]


def _syllables(lt, seed):
    """Otwarcie ust w czasie kwestii: sylaby (ok. 6/s) z krótkimi przerwami między słowami."""
    vs, vl = SHOT["vs"], SHOT["vl"]
    if not (vl > 0 and vs <= lt <= vs + vl):
        return 0.0
    edge = min(1.0, (lt - vs) / 0.08, (vs + vl - lt) / 0.1)
    syl = abs(math.sin(lt * 19.0 + 2.0 * noise(lt, seed, 2.0)))
    gap = 0.0 if noise(lt, seed + 5, 2.6) < -0.55 else 1.0  # pauza między słowami
    return edge * gap * (0.25 + 0.75 * syl)


def _apply(P, act, prm, who, k, hint=None):
    lt, T, vs, vl = SHOT["lt"], SHOT["T"], SHOT["vs"], SHOT["vl"]
    sl = prm.get("wolno", SLOW.get(who, 1.0))
    seed = _seed(who, k)
    if "strona" in prm:
        side = prm["strona"]
    elif hint is not None and abs(hint) > 0.2:  # spojrzenie ujęcia mówi, gdzie jest ta druga osoba / rzecz
        side = 1 if hint > 0 else -1
    else:
        side = 1 if (seed // 7) % 2 else -1
    has_v = vl > 0.2
    t0 = prm.get("t", None)
    if t0 is None:
        t0 = (vs + 0.15) if has_v else min(0.35 * T, 0.6)
    elif t0 < 0:  # ujemny: liczony od końca ujęcia
        t0 = T + t0
    amp = prm.get("sila", 1.0)

    if act == "mowi":  # mówi: głowa akcentuje sylaby, na początku lekko się unosi, na końcu domyka skinieniem
        if has_v:
            on = bump(lt, vs - 0.1, vs + vl + 0.25) ** 0.3
            P["hy"] += amp * on * (0.05 * max(0.0, noise(lt, seed, 3.1)) - 0.04 * bump(lt, vs - 0.1, vs + 0.5))
            P["rot"] += amp * on * 3.6 * noise(lt, seed + 1, 0.8)
            P["hx"] += amp * on * 0.025 * noise(lt, seed + 2, 0.6)
            P["hy"] += amp * 0.07 * bump(lt, vs + vl - 0.05, vs + vl + 0.45)
            P["shrug"] += amp * 0.12 * bump(lt, vs - 0.1, vs + 0.6)
            P["mouth"] = _syllables(lt, seed)
            P["gesture"] = max(P["gesture"], amp * on * (0.75 + 0.25 * noise(lt, seed + 3, 1.4)))
            P["gdx"] += 6 * noise(lt, seed + 4, 1.7)
            P["gdy"] += 8 * noise(lt, seed + 6, 2.1)
            P["hand"] = prm.get("reka", P["hand"])
    elif act == "slucha":  # słucha: przekrzywia głowę i potakuje drobnie w swoim rytmie
        k_ = step(lt, prm.get("t", 0.25), 0.9 * sl)
        P["rot"] += amp * side * 7.0 * k_
        P["hx"] += amp * side * 0.03 * k_
        for n in range(3):
            c = prm.get("t", 0.25) + 0.9 * sl + n * (1.3 + 0.4 * (seed % 3)) * sl
            P["hy"] += amp * 0.045 * bump(lt, c, c + 0.45 * sl)
        P["yaw"] += amp * side * 0.12 * k_
    elif act == "kiwa":  # kiwa głową: dwa skinienia
        for n in range(prm.get("ile", 2)):
            c = t0 + n * 0.42 * sl
            P["hy"] += amp * 0.12 * bump(lt, c, c + 0.38 * sl)
            P["gy"] += amp * 0.5 * bump(lt, c, c + 0.38 * sl)
            P["rot"] += amp * 1.5 * bump(lt, c, c + 0.38 * sl)
    elif act == "kreci":  # kręci głową: „nie”
        d = prm.get("d", 1.1) * sl
        e = bump(lt, t0, t0 + d) ** 0.5
        w = math.sin(2 * math.pi * (lt - t0) / (d / prm.get("ile", 2.5)))
        P["yaw"] += amp * 0.42 * e * w
        P["gx"] += amp * 0.5 * e * w
        P["rot"] += amp * 2.0 * e * w
    elif act in ("odwraca", "patrzy"):  # odwraca głowę (i zostaje) / spogląda w bok
        d = prm.get("d", 0.5) * sl
        k_ = step(lt, t0, d)
        if "wraca" in prm:
            k_ *= 1 - step(lt, prm["wraca"] if prm["wraca"] >= 0 else T + prm["wraca"], d)
        y = (0.7 if act == "odwraca" else 0.46) * amp
        P["yaw"] += side * y * k_
        P["gx"] += side * min(1.0, y * 1.6) * k_
        P["rot"] += side * 3.5 * k_
        P["hx"] += side * 0.05 * k_
        if act == "odwraca":
            P["gy"] += 0.25 * k_
    elif act == "w_gore":  # podnosi wzrok
        k_ = step(lt, t0, prm.get("d", 0.6) * sl)
        P["hy"] -= amp * 0.07 * k_
        P["gy"] -= amp * 0.8 * k_
        P["rot"] += amp * side * 2 * k_
    elif act == "w_dol":  # spuszcza głowę / wzrok
        k_ = step(lt, t0, prm.get("d", 0.8) * sl)
        P["hy"] += amp * 0.1 * k_
        P["gy"] += amp * 0.85 * k_
        P["shrug"] -= amp * 0.12 * k_
        P["rot"] += amp * side * 3 * k_
    elif act == "wzrusza":  # wzrusza ramionami
        d = prm.get("d", 0.85) * sl
        e = bump(lt, t0, t0 + d)
        P["shrug"] += amp * 0.9 * e
        P["rot"] += amp * side * 4 * e
        P["hy"] -= amp * 0.03 * e
        P["gesture"] = max(P["gesture"], 0.5 * e)
    elif act == "nachyla":  # pochyla się ku drugiej osobie / ku kamerze (szept)
        k_ = step(lt, t0, prm.get("d", 0.8) * sl)
        if "wraca" in prm:
            k_ *= 1 - step(lt, prm["wraca"] if prm["wraca"] >= 0 else T + prm["wraca"], 0.6)
        P["lean"] += amp * 0.055 * k_
        P["by"] += amp * 0.05 * k_
        P["rot"] += amp * side * 3 * k_
        P["hy"] += amp * 0.03 * k_
    elif act == "cofa":  # cofa się gwałtownie (wzdrygnięcie), potem zostaje lekko odsunięty
        k_ = step(lt, t0, 0.14)
        back = 1 - 0.4 * step(lt, t0 + 0.2, 0.6)
        P["lean"] -= amp * 0.05 * k_ * back
        P["rot"] -= amp * side * 5 * k_ * back
        P["hy"] -= amp * 0.05 * k_ * back
        P["shrug"] += amp * 0.4 * k_ * back
    elif act == "wstrzymuje":  # wstrzymuje oddech: ramiona w górę, bezruch, na końcu wydech
        t1 = prm.get("do", T - 0.35)
        up = step(lt, t0, 0.35) * (1 - step(lt, t1, 0.35))
        P["shrug"] += amp * 0.45 * up
        P["breath"] *= 1 - up
        P["hy"] -= amp * 0.025 * up
        P["breath_add"] -= amp * 0.8 * bump(lt, t1, t1 + 0.6)
    elif act == "oddycha":  # oddycha ciężko / szybko
        f = prm.get("tempo", 1.6)
        b = math.sin(2 * math.pi * f * lt)
        P["breath_add"] += amp * 2.2 * b
        P["shrug"] += amp * 0.12 * (b + 1) / 2
        P["hy"] -= amp * 0.015 * b
    elif act == "rozglada":  # rozgląda się: w bok, w drugi bok, na wprost
        d = prm.get("d", 0.45) * sl
        a1, a2, a3 = t0, t0 + d + 0.5 * sl, t0 + 2 * d + 1.0 * sl
        y = side * 0.42 * amp * (step(lt, a1, d) - 2 * step(lt, a2, d) + step(lt, a3, d))
        P["yaw"] += y
        P["gx"] += y * 1.8
        P["rot"] += y * 4
    elif act == "wzdycha":  # wzdycha: ramiona w górę, potem opadają niżej niż były
        e = bump(lt, t0, t0 + 0.7 * sl)
        k_ = step(lt, t0 + 0.4 * sl, 0.9 * sl)
        P["shrug"] += amp * (0.5 * e - 0.18 * k_)
        P["hy"] += amp * 0.05 * k_
        P["gy"] += amp * 0.4 * k_
        P["breath_add"] += amp * 1.2 * e
    elif act == "budzi":  # budzi się: głowa podnosi się z opuszczenia
        k_ = step(lt, t0, prm.get("d", 1.1) * sl)
        P["hy"] += amp * 0.16 * (1 - k_)
        P["rot"] += amp * side * 8 * (1 - k_)
        P["gy"] += 0.6 * (1 - k_)
    elif act == "kolysze":  # kołysze się (zmęczenie, gorączka, płacz)
        P["bx"] += amp * 0.05 * math.sin(2 * math.pi * 0.5 * lt / sl + seed)
        P["rot"] += amp * 3 * math.sin(2 * math.pi * 0.5 * lt / sl + seed + 0.6)
    elif act == "ciezar":  # przenosi ciężar z nogi na nogę (plan ogólny)
        P["bx"] += amp * side * 0.5 * (step(lt, t0, 0.7 * sl) - 0.5)
        P["rot"] += amp * side * 2 * step(lt, t0, 0.7 * sl)
    elif act == "gest":  # gest ręką bez kwestii (pokazuje, uspokaja)
        d = prm.get("d", 1.2) * sl
        P["gesture"] = max(P["gesture"], amp * bump(lt, t0, t0 + d) ** 0.5)
        P["hand"] = prm.get("reka", P["hand"])
        P["gdy"] += 6 * noise(lt, seed + 4, 1.5)
    elif act == "kaszle":  # kaszle: trzy krótkie zgięcia do przodu z otwartymi ustami
        for n in range(prm.get("ile", 3)):
            c = t0 + n * 0.34 * sl
            e = bump(lt, c, c + 0.26 * sl)
            P["lean"] += amp * 0.03 * e
            P["hy"] += amp * 0.07 * e
            P["shrug"] += amp * 0.3 * e
            P["rot"] += amp * side * 2 * e
            if e > 0.05:
                P["mouth"] = max(P["mouth"] or 0.0, 0.8 * e)
    elif act == "przelyka":  # przełyka ślinę (zbliżenie narratora ma przełknięcie w szyi)
        P["swallow"] = bump(lt, t0, t0 + 0.5)
        P["hy"] += 0.03 * bump(lt, t0, t0 + 0.5)
    else:
        raise KeyError(f"nieznana akcja rigu: {act}")


def pose(who, hint=None):
    """Poza postaci w bieżącej klatce (słownik NEUTRAL, gdy ujęcie nie ma akcji dla tej postaci).
    hint — kierunek spojrzenia z ujęcia (gaze x / look): w tę stronę postać się odwraca i spogląda."""
    P = dict(NEUTRAL)
    acts = ACTS.get(who, []) + (ACTS.get("*", []) if who not in ACTS else [])
    for k, (act, prm) in enumerate(acts):
        _apply(P, act, prm, who, k, hint)
    P["active"] = bool(acts)
    return P
