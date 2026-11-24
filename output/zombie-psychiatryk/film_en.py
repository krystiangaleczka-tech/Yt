"""Cały wariant A po angielsku (US) jednym plikiem: zimne otwarcie + dni 1–30, obraz 1440p, lektor i dialogi z klonów.

uruchom (venv z numpy/pillow/scipy; ffmpeg w PATH):
  python -I film_en.py braki                  → napisy w kadrze bez tłumaczenia (próbka klatek każdego ujęcia, 720p)
  python -I film_en.py obraz [jednostki] -j 8 → build/en-1440/vNN.mp4 (0 = otwarcie, 1–30 = dni); gotowe pomija
  python -I film_en.py dzwiek [jednostki]     → build/en-1440/aNN.wav (otwarcie: render.audio/render2.audio; dni: tło + głosy)
  python -I film_en.py sklej                  → oddzial-c-en-1440p.mp4
  python -I film_en.py klatki 5 12.0 40.5     → podgląd klatek dnia 5 (s od początku dnia) w build/en-1440/
Rozdzielczość: --res 1440 (domyślnie) albo 2160.
"""
import argparse
import importlib
import json
import math
import os
import subprocess
import sys
import wave
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
FPS = 24
SR = 44100


def env(res):
    os.environ["FILM_LANG"] = "en"
    os.environ["FILM_RES"] = str(res)
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))


def build_dir(res):
    d = HERE / "build" / f"en-{res}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- obraz ----------

def unit_frames(u):
    """(liczba klatek, frame(k)) jednostki: 0 = otwarcie (render + render2), 1–30 = dzień."""
    if u == 0:
        import render as R1
        import render2 as R2
        n1, n2 = round(R1.DUR * FPS), round(R2.DUR * FPS)
        return n1 + n2, lambda k: R1.frame(k / FPS) if k < n1 else R2.frame((k - n1) / FPS)
    m = importlib.import_module(f"render_d{u:02d}")
    n = round(m.DUR * FPS)
    return n, lambda k: m.frame(min(k / FPS, m.DUR - 1e-3))


def encoder(crf):
    """FILM_ENC=nvenc — koder sprzętowy karty NVIDIA (rysowanie klatek staje się wąskim gardłem, nie kodowanie);
    domyślnie x264 slow. Wszystkie jednostki filmu muszą mieć ten sam koder, bo „sklej” łączy je bez przekodowania."""
    if os.environ.get("FILM_ENC") == "nvenc":
        return ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", str(crf + 1), "-b:v", "0", "-profile:v", "high",
                "-pix_fmt", "yuv420p", "-g", "48"]
    return ["-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-tune", "animation",
            "-threads", "2", "-rc-lookahead", "20"]


def render_unit(u, res, crf):
    env(res)
    out = build_dir(res) / f"v{u:02d}.mp4"
    done = out.with_suffix(".ok")
    if done.exists():
        return u, "jest"
    n, frame = unit_frames(u)
    import render as R
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{R.OW}x{R.OH}", "-r", str(FPS), "-i", "-", *encoder(crf), str(out)],
                            stdin=subprocess.PIPE)
    for k in range(n):
        proc.stdin.write(frame(k).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError(f"ffmpeg v{u:02d}")
    done.write_text(json.dumps({"frames": n}))
    return u, f"{n} klatek"


# ---------- dźwięk ----------

def read_wav(path):
    import numpy as np
    with wave.open(str(path)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    if ch > 1:
        v = v.reshape(-1, ch).mean(axis=1)
    assert sr == SR, (path, sr)
    return v


def shape(v, how):
    """Radio / megafon: pasmo telefoniczne i lekki przester; megafon z echem odbitym od budynku."""
    if how not in ("radio", "megafon"):
        return v
    import numpy as np
    from scipy.signal import butter, sosfilt
    sos = butter(4, [350, 3200], btype="band", fs=SR, output="sos")
    v = np.tanh(sosfilt(sos, v) * 2.5) * 0.6
    if how == "megafon":
        d = int(0.23 * SR)
        v = np.concatenate([v, np.zeros(d * 2)])
        v[d:] += 0.35 * v[:-d]
        v[2 * d:] += 0.15 * v[:-2 * d]
    return v


def bed(look, n, rng, t0):
    """Tło ujęcia: noc/ciemność — wiatr i niski dron; oddział — buczenie świetlówek; karta — prawie cisza."""
    import numpy as np
    ts = t0 + np.arange(n) / SR
    noise = np.convolve(rng.normal(0, 1, n + 800), np.ones(800) / 800, mode="same")[400:400 + n] * 6
    room = 0.012 * noise + 0.006 * np.sin(2 * np.pi * 55 * ts)
    if look is None:
        return room * 0.3
    grade, mask = look
    if grade[2] > 0.99 and mask:  # DARK / NIGHT / BASE: zimno, wiatr, dron
        gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * ts + 1.3) * np.sin(2 * np.pi * 0.023 * ts)
        return room + 0.03 * noise * gust + 0.012 * np.sin(2 * np.pi * 49 * ts) * (0.6 + 0.4 * np.sin(ts * 0.9))
    hum = 0.006 * np.sign(np.sin(2 * np.pi * 100 * ts)) * (0.8 + 0.2 * np.sin(ts * 3.1))
    return room + hum


def day_audio(u, out):
    import numpy as np
    import en_film
    m = importlib.import_module(f"render_d{u:02d}")
    rows = [s for _, _, beats in en_film_rows(u) for _, shots in beats for s in shots]
    n = int(round(m.DUR * FPS) / FPS * SR)
    mix = np.zeros(n)
    voice = np.zeros(n)
    rng = np.random.default_rng(100 + u)
    fade = int(0.12 * SR)
    efx = HERE / "build" / "efekty" / f"e{u:02d}.wav"  # efekty_dni.py: tło miejsca + dźwięki zdarzeń (bez lektora)
    if efx.exists():
        e = read_wav(efx)
        mix[: min(n, len(e))] += e[:n]
    for i, (a, b, *_rest) in enumerate(m.SCENES):
        i0, i1 = int(a * SR), min(n, int(b * SR))
        if not efx.exists():
            seg = bed(m.LOOK[i], i1 - i0 + fade, rng, a)
            env_ = np.ones(len(seg))
            env_[:fade] = np.linspace(0, 1, fade)
            env_[-fade:] = np.linspace(1, 0, fade)
            j1 = min(n, i0 + len(seg))
            mix[i0:j1] += (seg * env_)[: j1 - i0]
        f = en_film.voice_file(u, i)
        if f.exists():
            vs = m.SCENES[i][4] if len(m.SCENES[i]) > 4 else m.VWIN[i][0]
            who, how = en_film.speaker(rows[i][4])
            v = shape(read_wav(f), how) * (0.55 if how == "szept" else 0.9)
            k0 = int((a + vs) * SR)
            k1 = min(n, k0 + len(v))
            voice[k0:k1] += v[: k1 - k0]
    # pod głosem efekty o 6 dB, muzyka o 8 dB ciszej (płynnie); muzyka: muzyka_dni.py
    env_v = np.convolve((np.abs(voice) > 0.01).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    dv = np.clip(env_v * 4, 0, 1)
    music = np.zeros(n)
    mus = HERE / "build" / "muzyka" / f"m{u:02d}.wav"
    if mus.exists():
        mm = read_wav(mus)
        music[: min(n, len(mm))] += mm[:n]
    out_ = mix * (1 - 0.5 * dv) + music * (1 - 0.6 * dv) + voice
    write_wav(out, np.tanh(out_ * 1.05) * 0.9)


def en_film_rows(u):
    import dzien_base as B
    return B.day_tuple(u)[2]


def write_wav(path, x):
    import numpy as np
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def audio_unit(u, res):
    env(res)
    out = build_dir(res) / f"a{u:02d}.wav"
    if u == 0:
        import numpy as np
        import render as R1
        import render2 as R2
        d = build_dir(res)
        R1.audio(d / "a00_1.wav")
        R2.audio(d / "a00_2.wav")
        a1, a2 = read_wav(d / "a00_1.wav"), read_wav(d / "a00_2.wav")
        a1 = np.pad(a1, (0, max(0, int(round(R1.DUR * FPS) / FPS * SR) - len(a1))))[: int(round(R1.DUR * FPS) / FPS * SR)]
        a2 = np.pad(a2, (0, max(0, int(round(R2.DUR * FPS) / FPS * SR) - len(a2))))[: int(round(R2.DUR * FPS) / FPS * SR)]
        write_wav(out, np.concatenate([a1, a2]))
    else:
        day_audio(u, out)
    return u


# ---------- reszta ----------

def braki():
    env(720)
    import render as R
    from kwestie_en import napis
    for u in range(1, 31):
        m = importlib.import_module(f"render_d{u:02d}")
        for a, b, *_ in m.SCENES:
            for f in (0.1, 0.5, 0.95):
                m.frame(a + (b - a) * f)
    import render as R1  # noqa: F401
    import render2 as R2
    for t in range(0, int(R1.DUR)):
        R1.frame(t)
    for t in range(0, int(R2.DUR)):
        R2.frame(t)
    missing = sorted(s for s in R.DRAWN if napis(s) == s and any(c.isalpha() for c in s))
    print("napisy w kadrze:", len(R.DRAWN), "| bez tłumaczenia:", missing)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["braki", "obraz", "dzwiek", "sklej", "klatki"])
    ap.add_argument("rest", nargs="*")
    ap.add_argument("-j", type=int, default=8)
    ap.add_argument("--res", type=int, default=1440)
    ap.add_argument("--crf", type=int, default=16)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.cmd == "braki":
        return braki()
    units = [int(x) for x in a.rest] or list(range(0, 31))
    d = build_dir(a.res)
    if a.cmd == "klatki":
        env(a.res)
        u, ts = int(a.rest[0]), [float(x) for x in a.rest[1:]]
        n, frame = unit_frames(u)
        for t in ts:
            frame(int(t * FPS)).save(d / f"klatka-d{u:02d}-{t:06.2f}s.png")
        return
    if a.cmd == "obraz":
        with ProcessPoolExecutor(a.j) as ex:
            futs = [ex.submit(render_unit, u, a.res, a.crf) for u in sorted(units, key=lambda u: -1 if u in (0, 1) else u)]
            for f in as_completed(futs):
                u, msg = f.result()
                print(f"v{u:02d}: {msg}", flush=True)
    elif a.cmd == "dzwiek":
        with ProcessPoolExecutor(min(a.j, 8)) as ex:
            for f in as_completed([ex.submit(audio_unit, u, a.res) for u in units]):
                print(f"a{f.result():02d}", flush=True)
    elif a.cmd == "sklej":
        units = list(range(0, 31))
        for u in units:
            assert (d / f"v{u:02d}.ok").exists() and (d / f"a{u:02d}.wav").exists(), f"brak jednostki {u}"
        (d / "lista.txt").write_text("".join(f"file 'v{u:02d}.mp4'\n" for u in units), encoding="utf-8")
        import numpy as np
        write_wav(d / "audio.wav", np.concatenate([read_wav(d / f"a{u:02d}.wav") for u in units]))
        out = HERE / f"oddzial-c-en-{a.res}p.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(d / "lista.txt"),
                        "-i", str(d / "audio.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-af", "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k",
                        "-shortest", "-movflags", "+faststart", str(out)], check=True)
        print(out)


if __name__ == "__main__":
    main()
