"""Znak wodny marki na filmy (YouTube Studio → Personalizacja → Znak wodny marki): kółko ze sceną ze zdjęcia
profilowego (kanal/profil_fuji.png) w złotej obwódce, przezroczyste tło. YouTube pokazuje go w prawym dolnym rogu
filmu; kliknięcie daje subskrypcję. Wymagania YouTube: kwadrat co najmniej 150 × 150, do 1 MB.

  python3 kanal_znak.py   → kanal/znak_wodny.png (300 × 300) i kanal/podglad_znak_wodny.png (na kadrze filmu)
"""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
K = HERE / "kanal"
N = 300
S = 4  # rysowane 4× większe i zmniejszane: gładkie brzegi kółka

prof = Image.open(K / "profil_fuji.png").convert("RGBA").resize((N * S, N * S), Image.LANCZOS)
maska = Image.new("L", (N * S, N * S), 0)
ImageDraw.Draw(maska).ellipse([0, 0, N * S - 1, N * S - 1], fill=255)
znak = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
znak.paste(prof, (0, 0), maska)
d = ImageDraw.Draw(znak)
r = 9 * S  # złota obwódka jak listwa teatru, z ciemnym brzegiem: odcina się i od jasnego, i od ciemnego kadru
d.ellipse([0, 0, N * S - 1, N * S - 1], outline=(30, 22, 20, 255), width=3 * S)
d.ellipse([3 * S, 3 * S, N * S - 1 - 3 * S, N * S - 1 - 3 * S], outline=(214, 170, 86, 255), width=r)
znak = znak.resize((N, N), Image.LANCZOS)
znak.save(K / "znak_wodny.png", optimize=True)

# podgląd: znak w prawym dolnym rogu kadru filmu (miniaturka 1280 × 720), w rozmiarze jak na YouTube (ok. 5% wysokości)
kadr = Image.open(HERE / "miniatura" / "miniatura_en_fuji.jpg").convert("RGBA")
m = znak.resize((40, 40), Image.LANCZOS)
kadr.alpha_composite(m, (kadr.width - 40 - 24, kadr.height - 40 - 52))
kadr.convert("RGB").save(K / "podglad_znak_wodny.png")
print(K / "znak_wodny.png", f"{(K / 'znak_wodny.png').stat().st_size / 1e3:.0f} kB")
