# Prompty dni 21–30 (wersja rysowana kodem). Ujęcia powstają w PIL (render_dNN.py), więc prompt jest opisem kadru
# z rozpiski — zawsze w tej samej kolejności co rozpiska. (kadr, prompt albo None, uwaga produkcyjna)
from a_dane1 import DAYS as _D1
from a_dane2 import DAYS as _D2

CARD = "Karta dnia robiona w Studio (biały napis na czerni) — nie generować."
NAMES = {"PO": "Wide shot", "PP": "Wide shot", "PŚ": "Medium shot", "NR": "Over-the-shoulder shot", "Z": "Close-up",
         "WZ": "Extreme close-up", "D": "Detail shot", "POV": "Point-of-view shot"}

SHOTS = {}
for _n, _t, _sc in _D1 + _D2:
    if 21 <= _n <= 30:
        SHOTS[_n] = [(k, None, CARD) if k == "TYT" else (k, f"{NAMES.get(k, 'Shot')} (ujęcie rysowane kodem): {de}.", "")
                     for _, _, beats in _sc for _, shots in beats for k, _r, _s, de, _so in shots]
