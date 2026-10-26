"""Jednorazowo: nazwy zdań w voice/sent z numeru (B01_00.wav) na skrót treści (B01_<sha1>.wav)."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import re  # noqa: E402

prj = json.loads(Path(sys.argv[1]).read_text())
sent = Path(sys.argv[2])
spec = __import__("importlib.util").util.spec_from_file_location("vb_say", Path(__file__).parent / "voice_beats.py")
src = (Path(__file__).parent / "voice_beats.py").read_text()
SAY = eval(src[src.index("SAY = ["):src.index("]\n\n\ndef speakable") + 1].split("=", 1)[1])


def speakable(text):
    for pat, rep in SAY:
        text = re.sub(pat, rep, text)
    return text


n = 0
for b in prj["beats"]:
    sents = [s for s in re.split(r"(?<=[.!?])\s+", b.get("narration", "").strip()) if s]
    for i, s in enumerate(sents):
        old = sent / f"{b['id']}_{i:02d}.wav"
        new = sent / f"{b['id']}_{hashlib.sha1(speakable(s).encode()).hexdigest()[:10]}.wav"
        if old.exists() and not new.exists():
            old.rename(new)
            n += 1
print(f"przemianowano {n} zdań")
