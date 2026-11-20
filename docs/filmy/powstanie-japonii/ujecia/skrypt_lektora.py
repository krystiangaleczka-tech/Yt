"""Skrypt lektora EN do nagrania przez reżysera: ujęcie, chwila w filmie, co widać, kwestia, ile mówić.

  python3 docs/filmy/powstanie-japonii/ujecia/skrypt_lektora.py   (wynik: ../SKRYPT_LEKTORA_EN.md)

Czasy z rozpiski wersji EN (dane.py z JEZYK=en). „Mów ok.” to długość roboczego lektora (klon) albo szacunek z tempa EN
dla kwestii bez nagrania; „Maks.” — ile można mówić, żeby po kwestii została co najmniej 1 s obrazu przed cięciem
(Podręcznik, Rytm 2). Reżyser 20.11.2026: „daj mi cały skrypt do wylektorowania, ujęcie, kwestia, ile mam mówić”.
"""
import os
import sys
from pathlib import Path

os.environ["JEZYK"] = "en"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dane  # noqa: E402
from kwestie_en import ETYKIETY, WYMOWA_EN  # noqa: E402

PO_KWESTII = 1.0  # najkrótszy obraz po ostatnim słowie


def tc(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def co_widac(opis):
    """Pierwsze zdarzenie z opisu ujęcia, bez nawiasu o skrócie („hak (skrót ujęcia …): …”)."""
    if opis.startswith(("zapowiedź (", "hak (", "teatr cieni (")) and "): " in opis:
        opis = opis.split("): ", 1)[1]
    opis = opis.split(";")[0].strip()
    return opis if len(opis) <= 90 else opis[:88].rsplit(" ", 1)[0] + " …"


def tytul_aktu(n, tytul):
    if n == 0:
        return "Prologue · teaser and hook"
    return ETYKIETY.get(f"Akt {n} · {tytul}", tytul)


def main():
    us = dane.ujecia()
    zap = sum(u[5] for u in us if u[2].startswith("zap_"))
    tytuly = {n: t for n, t, _o, _s in dane.AKTY}
    out, t, akt, mowa_razem, n_kwestii = [], 0.0, None, 0.0, 0
    for nr, (a, _k, klucz, _kadr, _ruch, sec, opis, snd) in enumerate(us, 1):
        txt = dane.kwestia(snd)
        if a != akt:
            akt = a
            out += ["", f"## {tytul_aktu(a, tytuly[a])}", "",
                    "| Ujęcie | Start | Co widać | Kwestia | Mów ok. | Maks. |", "|---|---|---|---|---|---|"]
        if txt:
            start, mowa = dane.okno_kwestii(snd)
            miejsce = zap if klucz == "zap_jaskinia" else sec  # zdanie z zapowiedzi biegnie przez całą zapowiedź
            maks = miejsce - start - (0.3 if klucz == "zap_jaskinia" else PO_KWESTII)
            mowione = dane.slownie(txt)
            if mowa > maks:  # nagranie klona dłuższe niż ujęcie (np. z długimi pauzami) — pokaż tempo lektora EN
                mowa = min(mowa, len(mowione.split()) / dane.TEMPO_EN)
            czytaj = f"<br>*czytaj: {mowione}*" if mowione != txt else ""
            uwaga = " ⚠" if mowa > maks + 0.05 else ""
            out.append(f"| {nr} | {tc(t + start)} | {co_widac(opis)} | {txt}{czytaj} | {mowa:.1f} s | {maks:.1f} s{uwaga} |")
            mowa_razem += mowa
            n_kwestii += 1
        t += sec
    wymowa = ", ".join(f"**{a}** — {b}" for a, b in WYMOWA_EN)
    head = ["# Son of the Sun — skrypt lektora (EN)", "",
            f"Film {tc(t)}, {len(us)} ujęć, {n_kwestii} kwestii (ok. {mowa_razem / 60:.1f} min mówienia). Stan rozpiski: "
            "`docs/filmy/powstanie-japonii/ujecia/dane.py`; po zmianach ujęć skrypt odświeża "
            "`python3 docs/filmy/powstanie-japonii/ujecia/skrypt_lektora.py`.", "",
            "**Jak czytać kolumny**", "",
            "- **Ujęcie** — numer ujęcia w Studio (od 1).",
            "- **Start** — kiedy w filmie zaczynasz mówić.",
            "- **Mów ok.** — tyle trwa kwestia w roboczym lektorze (klon) albo szacunek dla nowych kwestii; to tempo, w którym "
            "ujęcia są teraz policzone.",
            "- **Maks.** — najdłużej, ile możesz mówić, żeby po ostatnim słowie została co najmniej 1 s obrazu przed cięciem. "
            "Dłużej też można: wtedy przedłużę ujęcie stopklatką. ⚠ — roboczy lektor już się nie mieści.",
            "- Pierwsza kwestia leci przez całą zapowiedź (10 szybkich cięć), od ok. 0,6 s.", "",
            f"**Wymowa imion:** {wymowa}.", "",
            "**Liczby czytasz słowami** — przy takiej kwestii w tabeli jest „czytaj: …”."]
    (HERE.parent / "SKRYPT_LEKTORA_EN.md").write_text("\n".join(head + out) + "\n", encoding="utf-8")
    print(f"SKRYPT_LEKTORA_EN.md: {n_kwestii} kwestii, {tc(t)}")


if __name__ == "__main__":
    main()
