"""Compose the 10 s pilot: stills -> Ken Burns + grain + typewriter titles + comparison card -> ffmpeg."""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
A = ROOT / "assets"
W, H, FPS, DUR = 1920, 1080, 30, 10.0
XF = 0.4  # crossfade length

MONO_B = str(ROOT / "fonts/CourierPrime-Bold.ttf")
MONO = str(ROOT / "fonts/CourierPrime-Regular.ttf")
SANS = str(ROOT / "fonts/Montserrat.ttf")

# scene boundaries (seconds) — tuned to the narration
S1, S2, S3 = (0.0, 3.9), (3.9, 6.7), (6.7, DUR)
BLOOP_AT = 8.7  # when "The Bloop" is spoken

LANG = sys.argv[3] if len(sys.argv) > 3 else "en"
TXT = {
    "en": dict(title="Summer", signal="UNIDENTIFIED SIGNAL", known="KNOWN: WHALE", bloop="THE BLOOP"),
    "pl": dict(title="Lato", signal="NIEZIDENTYFIKOWANY SYGNAŁ", known="WIELORYB", bloop="BLOOP"),
}[LANG]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def load(name, scale=1.25):
    im = Image.open(A / f"{name}.png").convert("L").convert("RGB")
    return im.resize((int(W * scale), int(H * scale)), Image.LANCZOS)


def ken_burns(im, p, z0, z1, dx=0.0, dy=0.0):
    """Crop a moving window from a pre-upscaled image; p in [0,1]."""
    z = z0 + (z1 - z0) * p
    cw, ch = im.width / z, im.height / z
    cx = im.width / 2 + dx * p * (im.width - cw) / 2
    cy = im.height / 2 + dy * p * (im.height - ch) / 2
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return im.resize((W, H), Image.BICUBIC, box=box)


def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def typewriter(draw, xy, text, f, t, start, cps=14, fill=(235, 235, 230)):
    n = int(max(0.0, t - start) * cps)
    if n > 0:
        draw.text(xy, text[:n], font=f, fill=fill)


# ---------- precomputed layers ----------
img1, img2 = load("s1_ocean"), load("s2_lab")
whale = Image.open(A / "s3_whale.png").convert("L").convert("RGB")
deep = Image.open(A / "s3_deep.png").convert("L").convert("RGB")

yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGNETTE = np.clip(1.15 - 0.55 * r ** 2, 0.25, 1.0)[..., None].astype(np.float32)

F_TITLE = font(MONO_B, 120)
F_YEAR = font(MONO, 64)
F_LABEL = font(MONO_B, 54)
F_CARD = font(SANS, 46, wght=600)


def rounded_card(src, w, h, rad=28):
    src = src.resize((w, int(w * src.height / src.width)), Image.LANCZOS)
    top = (src.height - h) // 2
    src = src.crop((0, top, w, top + h))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), rad, fill=255)
    return src, mask


def bloop_signal(sr=2000, dur=6.0):
    """Synthetic 'bloop': slow rising ultra-low-frequency sweeps with harmonics + ocean noise."""
    t = np.arange(int(sr * dur)) / sr
    sig = np.zeros_like(t)
    for start in (0.4, 2.3, 4.1):
        tt = np.clip(t - start, 0, None)
        env = np.where(t >= start, np.exp(-tt * 1.6) * (1 - np.exp(-tt * 25)), 0)
        f = 30 + 110 * (1 - np.exp(-tt * 1.4))
        ph = 2 * np.pi * np.cumsum(f) / sr
        sig += env * (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph))
    return sig + 0.08 * np.random.default_rng(3).normal(size=t.size), sr


def spectrogram_card(w, h):
    sig, sr = bloop_signal()
    n, hop = 256, 16
    win = np.hanning(n)
    frames = np.stack([sig[i:i + n] * win for i in range(0, sig.size - n, hop)])
    spec = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1)).T + 1e-6)
    spec = spec[: int(spec.shape[0] * 0.5)][::-1]  # keep 0–500 Hz, low at bottom
    spec = np.clip((spec - spec.max() + 55) / 55, 0, 1) ** 1.4
    im = Image.fromarray((spec * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(0.8)).convert("RGB")
    d = ImageDraw.Draw(im)
    for i in range(1, 5):  # faint grid like a printout
        d.line((0, h * i / 5, w, h * i / 5), fill=(60, 60, 60))
        d.line((w * i / 5, 0, w * i / 5, h), fill=(60, 60, 60))
    d.text((14, 10), "HYDROPHONE  /  1997  /  0-500 Hz", font=font(MONO, 20), fill=(170, 170, 170))
    return im


CW, CH = 640, 400
CARD_L = rounded_card(whale, CW, CH)
CARD_R = rounded_card(spectrogram_card(CW, CH), CW, CH)


def comparison(t):
    p = t - S3[0]
    bg = Image.new("RGB", (W, H), (8, 8, 8))
    d = ImageDraw.Draw(bg)
    d.rectangle((W // 2, 0, W, H), fill=(74, 14, 18))
    # subtle radial lift on the red half
    canvas = bg
    centers = (W // 4, 3 * W // 4)
    for i, (card, mask) in enumerate((CARD_L, CARD_R)):
        a = ease((p - 0.15 - 0.35 * i) / 0.6)
        if a <= 0:
            continue
        y = int(H / 2 - CH / 2 - 60 + (1 - a) * 40)
        x = centers[i] - CW // 2
        layer = Image.new("RGB", (W, H))
        layer.paste(card, (x, y), mask)
        m = Image.new("L", (W, H), 0)
        m.paste(mask.point(lambda v: int(v * a)), (x, y))
        canvas = Image.composite(layer, canvas, m)
    d = ImageDraw.Draw(canvas)
    labels = [(TXT["known"], 0.6), (TXT["bloop"], BLOOP_AT - S3[0])]
    for i, (txt, at) in enumerate(labels):
        a = ease((p - at) / 0.4)
        if a <= 0:
            continue
        spaced = " ".join(txt)
        tw = d.textlength(spaced, font=F_CARD)
        c = int(235 * a)
        d.text((centers[i] - tw / 2, H / 2 + CH / 2 - 10), spaced, font=F_CARD, fill=(c, c, c))
    # whole-frame slow push
    return ken_burns(canvas.resize((int(W * 1.25), int(H * 1.25))), p / (S3[1] - S3[0]), 1.0, 1.04)


def scene1(t):
    p = (t - S1[0]) / (S1[1] - S1[0] + XF)
    f = ken_burns(img1, p, 1.0, 1.10, dx=0.15)
    d = ImageDraw.Draw(f)
    typewriter(d, (110, 90), TXT["title"], F_TITLE, t, 0.5, cps=10)
    typewriter(d, (116, 225), "1997", F_YEAR, t, 1.2, cps=8, fill=(200, 200, 195))
    return f


def scene2(t):
    p = (t - S2[0] + XF) / (S2[1] - S2[0] + 2 * XF)
    f = ken_burns(img2, p, 1.12, 1.02, dx=-0.3, dy=0.1)
    a = ease((t - S2[0] - 0.4) / 0.25)
    if a > 0:
        d = ImageDraw.Draw(f)
        txt = TXT["signal"]
        tw = d.textlength(txt, font=F_LABEL)
        x0, y0 = W - tw - 200, H - 230
        d.rectangle((x0 - 26, y0 - 14, x0 + tw + 26, y0 + 72), fill=(int(240 * a),) * 3)
        d.text((x0, y0), txt, font=F_LABEL, fill=(15, 15, 15) if a > 0.5 else (int(240 * a),) * 3)
    return f


def frame(t, rng):
    if t < S1[1]:
        f = scene1(t)
    elif t < S1[1] + XF:
        f = Image.blend(scene1(t), scene2(t), ease((t - S1[1]) / XF))
    elif t < S2[1]:
        f = scene2(t)
    elif t < S2[1] + XF:
        f = Image.blend(scene2(t), comparison(t), ease((t - S2[1]) / XF))
    else:
        f = comparison(t)
    arr = np.asarray(f, dtype=np.float32)
    arr *= VIGNETTE
    arr *= 1.0 + 0.025 * np.sin(t * 23.0)  # projector flicker
    arr += rng.normal(0, 9, (H, W, 1)).astype(np.float32)  # film grain
    fade = min(ease(t / 0.5), ease((DUR - t) / 0.4))
    arr *= fade
    return np.clip(arr, 0, 255).astype(np.uint8)


def main():
    voice = Path(sys.argv[1]) if len(sys.argv) > 1 else A / "voice.wav"
    out = ROOT / (sys.argv[2] if len(sys.argv) > 2 else "pilot_bloop.mp4")
    # one sweep of the synthetic bloop, heard as the name is spoken
    sig, sr = bloop_signal()
    sweep = sig[int(0.4 * sr): int(2.3 * sr)]
    with wave.open(str(A / "bloop.wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((sweep / np.abs(sweep).max() * 0.9 * 32767).astype(np.int16).tobytes())
    audio = (
        f"[2:a]aresample=48000,lowpass=f=400,volume=0.9,adelay={int(BLOOP_AT * 1000)}|{int(BLOOP_AT * 1000)}[b];"
        # voice (delayed 0.35 s) + low drone + brown-noise rumble + two sonar pings
        "[1:a]adelay=350|350,highpass=f=80,acompressor=threshold=-18dB:ratio=3,volume=1.6[v];"
        "sine=f=55:d=10,volume=0.10[d1];"
        "anoisesrc=d=10:c=brown:a=0.25,lowpass=f=300,volume=0.35[n];"
        "sine=f=1180:d=0.9,afade=t=out:st=0.02:d=0.85,volume=0.35,aecho=0.8:0.7:420:0.35,"
        "asplit=2[pa][pb];"
        "[pa]adelay=150|150[p1];[pb]adelay=6700|6700[p2];"
        "[v][d1][n][p1][p2][b]amix=inputs=6:normalize=0,afade=t=in:d=0.4,afade=t=out:st=9.5:d=0.5,"
        "alimiter=limit=0.9,aformat=channel_layouts=stereo[a]"
    )
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(voice), "-i", str(A / "bloop.wav"),
        "-filter_complex", audio, "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rng = np.random.default_rng(7)
    for i in range(int(DUR * FPS)):
        proc.stdin.write(frame(i / FPS, rng).tobytes())
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
