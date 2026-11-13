"""Muzyka dni 1–30 wariantu A: własna, syntezowana (bez bibliotek i licencji), ułożona ze scen rozpiski.

Każda scena rozpiski dostaje nastrój z napięcia jej ujęć (plan miksu z efekty_dni.py) i z treści:
  brak       — cisza w rozpisce, karta dnia, kołysanka grana w kadrze (d30: muzyka jest w scenie, nie pod nią)
  pad cichy  — niskie, ledwie słyszalne tło harmoniczne (spokój, rozmowa)
  pad        — ciemne akordy a-moll: Am – F – Dm – E (niepokój)
  puls       — pad + niski puls jak bicie serca + wysokie tremolo (napięcie)
  napęd      — ostinato basu, puls, akordy Am – F – E (akcja, ucieczka, alarm)
  kołysanka  — motyw kołysanki żony pana Henryka na fortepianie nad padem (wspomnienie, czułość) — ten sam motyw,
               który Henryk gra w d30 (zasiew → rozwiązanie)
  finał      — kołysanka smyczkowa, narasta i rozwiązuje się do C-dur o świcie (d30, ostatnie ujęcia)
Poziom (RMS dBFS): pad cichy −38, pad −33, puls −29, napęd −25, kołysanka −30, finał −26; pod kwestiami film ścisza
muzykę o 8 dB (film_en.py), wersja Studio ma to już w pliku.

uruchom:  python -I muzyka_dni.py [dni] [-j 4]  → build/muzyka/mNN.wav, mNN_studio.wav, cue/dNN_KK.wav, mNN.json
"""
import argparse
import json
import math
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "build" / "muzyka"
SR = 44100
FPS = 24
LEVEL = {"pad cichy": -38.0, "pad": -33.0, "puls": -29.0, "napęd": -25.0, "kołysanka": -30.0, "finał": -26.0}
LULLABY = [72, 71, 69, 71, 72, 67, 69, 71, 72, 74, 72, 71, 69, 67, 69, 67]  # ten sam co w efekty_dni (d30)
# motyw kołysanki to zasiew przed d30: tylko wspomnienia pana Henryka i chwile czułości, nie każdy uśmiech
EMO_H = re.compile(r"kołysank|żon[aęyi]|basi|córk|odzyskał|ostatni raz|uśmiecha się|pianin|zasnął|zasypia")
EMO = re.compile(r"płacze|przytula|obejmuje|wspólny oddech|oddychają razem|oddychają w|nuci")


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


_TABLE = None


def saw(freq, n, ph0=0.0, harm=10):
    """Piła z ograniczoną liczbą harmonicznych (tablica), freq — liczba albo tablica Hz."""
    global _TABLE
    if _TABLE is None:
        x = np.arange(4096) / 4096
        _TABLE = sum(np.sin(2 * np.pi * k * x) / k for k in range(1, harm + 1)) * 0.55
    ph = (ph0 + np.cumsum(np.broadcast_to(freq, (n,)) / SR)) % 1.0
    return _TABLE[(ph * 4096).astype(int)]


def lowpass(x, f):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)


def env(n, a=1.2, r=1.5):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    e[:na] = np.linspace(0, 1, na) ** 2
    e[n - nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def pad(chords, t0, n, chord_len, rng, cut=1100, voices=(-6, 0, 6)):
    """Akordy zmieniane co chord_len s (licząc od początku dnia, więc sąsiednie sceny się zgadzają)."""
    ts = t0 + np.arange(n) / SR
    out = np.zeros(n)
    idx = (ts // chord_len).astype(int) % len(chords)
    for c in range(len(chords)):
        mask = (idx == c).astype(float)
        if not mask.any():
            continue
        mask = np.convolve(mask, np.ones(int(0.6 * SR)) / int(0.6 * SR), mode="same")  # płynne przejście akordów
        for m in chords[c]:
            for cents in voices:
                out += mask * saw(midi(m) * 2 ** (cents / 1200), n, rng.uniform(0, 1)) / len(voices)
        out += mask * 0.5 * np.sin(2 * np.pi * midi(chords[c][0] - 12) * ts)  # sub
    out = lowpass(out, cut)
    return out * (1 + 0.1 * np.sin(2 * np.pi * 0.09 * ts))


def kick(f0=55, d=0.35):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f0 * t * (1 + 1.5 * np.exp(-t / 0.02))) * np.exp(-t / 0.12)


def pulse(t0, n, bpm, double=True):
    out = np.zeros(n)
    beat = 60 / bpm
    first = math.ceil(t0 / beat) * beat - t0
    k = kick()
    t = first
    while t < n / SR:
        for dt, a in ((0.0, 1.0), (0.22, 0.6)) if double else ((0.0, 1.0),):
            i = int((t + dt) * SR)
            out[i:i + len(k)] += a * k[: max(0, n - i)]
        t += beat
    return out


def tremolo(t0, n, notes=(81, 82), rate=6.0):
    ts = t0 + np.arange(n) / SR
    x = sum(saw(midi(m), n, 0.3 * j) for j, m in enumerate(notes))
    return lowpass(x, 4000) * (0.55 + 0.45 * np.sin(2 * np.pi * rate * ts)) * 0.25


def ostinato(t0, n, bpm, seq=(33, 33, 36, 33, 40, 33, 31, 33)):
    out = np.zeros(n)
    step = 60 / bpm / 2
    first = math.ceil(t0 / step) * step - t0
    t, k = first, int(round((t0 + first) / step))
    L = int(step * 0.9 * SR)
    e = np.exp(-np.arange(L) / (0.12 * SR))
    while t < n / SR:
        m = seq[k % len(seq)]
        i = int(t * SR)
        x = saw(midi(m), L) * e
        out[i:i + L] += x[: max(0, n - i)]
        t += step
        k += 1
    return lowpass(out, 650)


def piano(notes, n, vel=1.0):
    out = np.zeros(n)
    for s, m, d in notes:
        f = midi(m)
        t = np.arange(int(d * SR)) / SR
        tone = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.4 * np.exp(-t * (1.0 + 0.9 * k)) for k in range(1, 7))
        tone[: int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))
        i = int(s * SR)
        if i < n:
            out[i:i + len(tone)] += vel * tone[: n - i]
    return out


def lullaby_notes(t0, dur, beat=0.78, start=0.6):
    """Melodia kołysanki w czasie dnia (powtarzana), z basem na pierwszej nucie każdego taktu."""
    notes = []
    k = 0
    while True:
        s = start + k * beat
        if s > dur - 0.6:
            break
        m = LULLABY[k % len(LULLABY)]
        notes.append((s, m, 1.6))
        if k % 4 == 0:
            notes.append((s, [57, 53, 48, 55][(k // 4) % 4] - 12, 2.8))
        k += 1
    return notes


def strings(melody, n, t0):
    out = np.zeros(n)
    for s, m, d in melody:
        L = int(d * SR)
        i = int(s * SR)
        if i >= n:
            continue
        t = np.arange(L) / SR
        f = midi(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t))
        x = (saw(f, L) + saw(f * 1.003, L, 0.4)) * np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.4)
        out[i:i + L] += x[: n - i]
    return lowpass(out, 2200)


def at_level(x, db):
    a = np.abs(x)
    if not len(x) or a.max() == 0:
        return x
    act = x[a > 0.1 * a.max()]
    return x * (10 ** (db / 20) / (math.sqrt(float(np.mean(act ** 2))) + 1e-12))


def cue_audio(mood, t0, dur, rng):
    n = int(dur * SR)
    if mood == "pad cichy":
        x = pad([[45, 52], [45, 52, 59]], t0, n, 8.0, rng, cut=700)
    elif mood == "pad":
        x = pad([[45, 48, 52], [41, 45, 48], [38, 41, 45], [40, 44, 47]], t0, n, 5.0, rng)
    elif mood == "puls":
        x = pad([[45, 52], [45, 51]], t0, n, 6.0, rng, cut=800) + 0.9 * pulse(t0, n, 70) + tremolo(t0, n)
    elif mood == "napęd":
        x = (pad([[45, 48, 52], [41, 45, 48], [40, 44, 47]], t0, n, 3.0, rng, cut=900) * 0.7 + 1.1 * ostinato(t0, n, 104)
             + 0.9 * pulse(t0, n, 104, double=False) + tremolo(t0, n, (81, 82), 9.0))
    elif mood == "kołysanka":
        x = pad([[45, 48, 52], [41, 45, 48], [48, 52, 55], [43, 47, 50]], t0, n, 3.12, rng, cut=900) * 0.35
        x = x + 1.4 * piano(lullaby_notes(t0, dur), n, 0.9)
    elif mood == "finał":
        mel = [(0.8 + k * 1.1, m + 12 * 0 - 12, 1.3) for k, m in enumerate(LULLABY) if 0.8 + k * 1.1 < dur - 2.5]
        x = strings(mel, n, t0) + pad([[45, 48, 52], [41, 45, 48], [48, 52, 55], [43, 47, 50]], t0, n, 4.4, rng, cut=1400) * 0.6
        tail = int(min(dur, 4.0) * SR)  # rozwiązanie: C-dur o świcie
        x[-tail:] += pad([[48, 52, 55, 60]], 0.0, tail, 99.0, rng, cut=1600) * np.linspace(0, 1, tail) ** 0.7
        x *= np.linspace(0.55, 1.0, n)  # narasta
    else:
        return np.zeros(n)
    return x


def beats_of(day):
    """Beaty rozpiski dnia: [(scena · beat, [i…])] — muzyka zmienia się co beat, nie co scenę."""
    import dzien_base as B
    out, i = [], 0
    for stitle, place_, beats in B.day_tuple(day)[2]:
        for btitle, shots in beats:
            out.append((f"{stitle} · {btitle}", list(range(i, i + len(shots)))))
            i += len(shots)
    return out


def merged(ms):
    """Sąsiednie beaty o tym samym nastroju grają jako jedna fraza."""
    out = []
    for title, idx, mood in ms:
        if out and out[-1][2] == mood and idx:
            out[-1] = (out[-1][0], out[-1][1] + idx, mood)
        else:
            out.append((title, list(idx), mood))
    return out


def moods(day, rows, plan, scenes):
    """Nastrój każdego beatu rozpiski."""
    out = []
    for stitle, idx in scenes:
        shots = [i for i in idx if rows[i][0] != "TYT"]
        if not shots:
            out.append((stitle, idx, "brak"))
            continue
        nap = float(np.mean([plan[i]["napiecie"] for i in shots]))
        txt = " ".join((rows[i][3] + " " + (rows[i][4] or "")).lower() for i in shots)
        quiet = sum((rows[i][4] or "").strip().lower().startswith("cisza") for i in shots) > len(shots) / 2
        action = any(rows[i][1] in ("szarp", "drg") for i in shots) and nap >= 7.5
        if day == 30 and any(i <= 13 for i in shots) and not any(i >= 15 for i in shots):
            mood = "brak"  # kołysanka i alarm grają w kadrze
        elif day == 30 and any(i >= 15 for i in shots):
            mood = "finał"
        elif quiet:
            mood = "brak"
        elif action:
            mood = "napęd"
        elif ((EMO_H.search(txt) and "henryk" in txt) or EMO.search(txt)) and nap < 8:
            mood = "kołysanka"
        elif nap >= 7:
            mood = "puls"
        elif nap >= 4.5:
            mood = "pad"
        elif nap >= 3:
            mood = "pad cichy"
        else:
            mood = "brak"
        out.append((stitle, idx, mood))
    return merged(out)


def day_music(day):
    os.environ.setdefault("FILM_LANG", "en")
    os.environ.setdefault("FILM_RES", "720")
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
    import importlib

    import dzien_base as B
    import efekty_dni as E
    m = importlib.import_module(f"render_d{day:02d}")
    rows = B.rows(day)
    shots = []
    for i, sc in enumerate(m.SCENES):
        if len(sc) == 4:
            a, b, ruch, txt = sc
            vs, vl = m.VWIN[i]
            vl = max(0.0, vl - 0.35) if txt else 0.0
        else:
            a, b, ruch, txt, vs, vl = sc
        shots.append((a, b, txt, vs, vl))
    plan = E.mix_plan(day, rows, [b - a for a, b, *_ in shots])
    scenes = beats_of(day)
    rng = np.random.default_rng(9000 + day)
    n = int(round(m.DUR * FPS) / FPS * SR)
    day_mix = np.zeros(n)
    duck = np.zeros(n)
    for a, b, txt, vs, vl in shots:
        if txt and vl > 0:
            duck[int((a + vs) * SR):min(n, int((a + vs + vl) * SR))] = 1
    duck = np.clip(np.convolve(duck, np.ones(int(0.4 * SR)) / int(0.4 * SR), mode="same"), 0, 1)
    (OUT / "cue").mkdir(parents=True, exist_ok=True)
    cues = []
    TAIL = 1.5
    for k, (stitle, idx, mood) in enumerate(moods(day, rows, plan, scenes)):
        if mood == "brak" or not idx:
            cues.append({"scena": stitle, "ujecia": [idx[0], idx[-1]] if idx else [], "nastroj": mood})
            continue
        a, b = shots[idx[0]][0], shots[idx[-1]][1]
        a0 = max(0.0, a - 0.4)
        dur = min(n / SR, b + TAIL) - a0
        x = cue_audio(mood, a0, dur, rng)
        x = at_level(x, LEVEL[mood]) * env(len(x), 1.2, TAIL)
        i0 = int(a0 * SR)
        L = min(len(x), n - i0)
        day_mix[i0:i0 + L] += x[:L]
        studio = x[:L] * (1 - 0.6 * duck[i0:i0 + L])  # −8 dB pod kwestiami
        f = OUT / "cue" / f"d{day:02d}_{k + 1:02d}.wav"
        write_wav(f, studio)
        cues.append({"scena": stitle, "ujecia": [idx[0], idx[-1]], "nastroj": mood, "db": LEVEL[mood],
                     "start": round(a0, 3), "koniec": round(a0 + L / SR, 3), "plik": f.name,
                     "napiecie": round(float(np.mean([plan[i]["napiecie"] for i in idx if rows[i][0] != "TYT"] or [0])), 1)})
    write_wav(OUT / f"m{day:02d}.wav", day_mix)
    write_wav(OUT / f"m{day:02d}_studio.wav", day_mix * (1 - 0.6 * duck))
    (OUT / f"m{day:02d}.json").write_text(json.dumps({"dzien": day, "sceny": cues}, ensure_ascii=False, indent=1), encoding="utf-8")
    return day, [c["nastroj"] for c in cues]


def write_wav(path, x):
    import wave
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dni", nargs="*", type=int)
    ap.add_argument("-j", type=int, default=4)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(a.j) as ex:
        for day, ms in ex.map(day_music, a.dni or list(range(1, 31))):
            print(f"m{day:02d}: " + ", ".join(ms), flush=True)


if __name__ == "__main__":
    main()
