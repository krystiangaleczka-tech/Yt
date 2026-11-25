"""Word-by-word captions, hook title and watermark as an ASS subtitle file (burned by ffmpeg/libass)."""
from __future__ import annotations

import re

from .util import hex_to_ass

# 13 caption looks. font = family name of a font in <workspace>/fonts (see setup.FONTS)
THEMES: dict[str, dict] = {
    "classic":  {"label": "Klasyczny", "font": "Poppins Black", "size": 84, "upper": True, "text": "#FFFFFF", "active": "#FFD400", "outline": "#000000", "ow": 7, "shadow": 2, "pop": True, "words": 3},
    "hormozi":  {"label": "Hormozi", "font": "Poppins Black", "size": 92, "upper": True, "text": "#FFFFFF", "active": "#3CFF5A", "outline": "#000000", "ow": 8, "shadow": 0, "pop": True, "words": 2},
    "beast":    {"label": "Beast", "font": "Luckiest Guy", "size": 96, "upper": True, "text": "#FFFFFF", "active": "#FF2D55", "outline": "#000000", "ow": 9, "shadow": 4, "pop": True, "words": 2},
    "karaoke":  {"label": "Karaoke", "font": "Poppins Black", "size": 80, "upper": True, "text": "#7A7A7A", "active": "#FFFFFF", "outline": "#000000", "ow": 6, "shadow": 0, "pop": False, "words": 4, "fill": True},
    "mozi":     {"label": "Mozi", "font": "Anton", "size": 100, "upper": True, "text": "#FFFFFF", "active": "#00E5FF", "outline": "#000000", "ow": 6, "shadow": 3, "pop": True, "words": 2},
    "pill":     {"label": "Pigułka", "font": "Poppins Black", "size": 72, "upper": False, "text": "#111111", "active": "#111111", "outline": "#FFFFFF", "ow": 18, "shadow": 0, "pop": True, "words": 3, "box": "#FFFFFF"},
    "lemon":    {"label": "Cytryna", "font": "Poppins Black", "size": 80, "upper": True, "text": "#111111", "active": "#111111", "outline": "#FFE600", "ow": 16, "shadow": 0, "pop": True, "words": 3, "box": "#FFE600"},
    "bubble":   {"label": "Bańka", "font": "Bangers", "size": 98, "upper": True, "text": "#FFFFFF", "active": "#FF9F1C", "outline": "#1A1A1A", "ow": 8, "shadow": 5, "pop": True, "words": 2},
    "neon":     {"label": "Neon", "font": "Poppins Black", "size": 84, "upper": True, "text": "#E8FFFF", "active": "#FF2BD6", "outline": "#2B00FF", "ow": 5, "shadow": 6, "pop": True, "words": 3},
    "ember":    {"label": "Żar", "font": "Anton", "size": 96, "upper": True, "text": "#FFF3E0", "active": "#FF6A00", "outline": "#3A0A00", "ow": 7, "shadow": 3, "pop": True, "words": 2},
    "retro":    {"label": "Retro", "font": "Bebas Neue", "size": 110, "upper": True, "text": "#FFF5D6", "active": "#FF5E5B", "outline": "#2D1B4E", "ow": 7, "shadow": 6, "pop": False, "words": 3},
    "crimson":  {"label": "Karmin", "font": "Anton", "size": 96, "upper": True, "text": "#FFFFFF", "active": "#E10600", "outline": "#000000", "ow": 7, "shadow": 2, "pop": True, "words": 2},
    "minimal":  {"label": "Minimalny", "font": "Poppins Black", "size": 62, "upper": False, "text": "#FFFFFF", "active": "#FFFFFF", "outline": "#000000", "ow": 3, "shadow": 1, "pop": False, "words": 5},
}

# on-screen only: audio is never changed
SLURS = re.compile(r"\b(n[i1]gg(a|er|ah)s?|f[a@]gg?(ot)?s?|retard(ed)?s?|tr[a@]nn(y|ies)|k[i1]ke?s?|ch[i1]nks?|sp[i1]cs?)\b", re.I)


def censor(word: str) -> str:
    return SLURS.sub(lambda m: m.group(0)[0] + "*" * (len(m.group(0)) - 1), word)


def _ts(t: float) -> str:
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _esc(text: str) -> str:
    return text.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def chunk_words(words: list[dict], max_words: int, max_chars: int = 18, gap: float = 0.6) -> list[list[dict]]:
    chunks, cur = [], []
    for w in words:
        txt = " ".join(x["w"] for x in cur + [w])
        if cur and (len(cur) >= max_words or len(txt) > max_chars or w["s"] - cur[-1]["e"] > gap
                    or re.search(r"[.!?]$", cur[-1]["w"])):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(words: list[dict], duration: float, theme_name: str, hook: str = "", keywords=(), *,
              cap_y: int = 1340, hook_y: int = 260, hook_secs: float = 3.5, watermark: str = "",
              accent: str = "#FFD400", keyword_color: str = "#2BE36B", censor_on: bool = True) -> str:
    th = THEMES.get(theme_name, THEMES["classic"])
    kw = {k.lower().strip(".,!?") for k in keywords if k}
    box = th.get("box")
    border_style = 3 if box else 1
    outline_col = hex_to_ass(box) if box else hex_to_ass(th["outline"])
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{th['font']},{th['size']},{hex_to_ass(th['text'])},&H000000FF,{outline_col},&H96000000,0,0,0,0,100,100,1,0,{border_style},{th['ow']},{th['shadow']},5,60,60,0,1
Style: Hook,Poppins Black,78,&H00111111,&H000000FF,{hex_to_ass(accent)},&H64000000,0,0,0,0,100,100,0,0,3,22,0,5,70,70,0,1
Style: Mark,Poppins Black,40,&H66FFFFFF,&H000000FF,&H99000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,40,40,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if hook:
        h = _esc(hook.upper())
        # wrap long hooks onto two lines
        parts = h.split()
        if len(h) > 18 and len(parts) > 2:
            mid = len(parts) // 2
            h = " ".join(parts[:mid]) + "\\N" + " ".join(parts[mid:])
        ev.append(f"Dialogue: 2,{_ts(0)},{_ts(min(hook_secs, duration))},Hook,,0,0,0,,"
                  f"{{\\pos(540,{hook_y})\\fscx60\\fscy60\\t(0,140,\\fscx104\\fscy104)\\t(140,220,\\fscx100\\fscy100)}}{h}")
    if watermark:
        ev.append(f"Dialogue: 1,{_ts(0)},{_ts(duration)},Mark,,0,0,0,,{_esc(watermark)}")

    def fmt(w):
        t = w["w"]
        if censor_on:
            t = censor(t)
        return _esc(t.upper() if th["upper"] else t)

    act = hex_to_ass(th["active"])
    base = hex_to_ass(th["text"])
    kwc = hex_to_ass(keyword_color)
    chunks = chunk_words(words, th["words"])
    for ci, ch in enumerate(chunks):
        c_start = ch[0]["s"]
        c_end = ch[-1]["e"] + 0.15
        if ci + 1 < len(chunks):  # never overlap the next phrase
            c_end = min(c_end, chunks[ci + 1][0]["s"])
        for i, w in enumerate(ch):
            a = c_start if i == 0 else w["s"]
            b = ch[i + 1]["s"] if i + 1 < len(ch) else c_end
            if b <= a:
                continue
            parts = []
            for j, x in enumerate(ch):
                is_kw = x["w"].lower().strip(".,!?'\"") in kw
                if th.get("fill") and j > i:
                    col = base
                elif j == i or (th.get("fill") and j < i):
                    col = act
                else:
                    col = base
                if is_kw:
                    col = kwc
                parts.append(f"{{\\c{col}}}{fmt(x)}")
            pop = "\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)" if th["pop"] and i == 0 else ""
            ev.append(f"Dialogue: 0,{_ts(a)},{_ts(min(b, duration))},Cap,,0,0,0,,{{\\pos(540,{cap_y}){pop}}}" + " ".join(parts))
    return head + "\n".join(ev) + "\n"
