"""Kontrola układu sceny (uklad.py) w KAŻDEJ klatce ujęć filmu o Szamilu (Wytyczne 1.32 i 3.3).

  python3 kontrola_ukladu.py [klucz,klucz,…] [--krok N] [--czesc i/n]   — raport docs/filmy/szamil-diuna/kontrola_ukladu.md
  (--czesc i/n: co n-te ujęcie od i-tego, do równoległych procesów; raport kontrola_ukladu_<i>.md)

Dla każdego ujęcia, które układa scenę przez uklad.py, sprawdza wszystkie kontrole w każdej klatce (24 kl./s): rzecz
w dłoni, siedzenie w siodle i na siedzisku, zasięg ręki, otwory, widoczność tematu ujęcia. Kontrola pominięta ma powód,
a sprawdzona w zero klatek jest błędem (uklad.raport_md). Kod wyjścia 1, gdy jest jakikolwiek błąd.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render  # noqa: E402
import uklad as U  # noqa: E402

RAPORT = HERE.parents[1] / "docs/filmy/szamil-diuna/kontrola_ukladu.md"


def kontroluj(klucze=None, krok=1, czesc=(0, 1), raport=RAPORT):
    wyniki, czesci, bledy_razem, ujec = {}, [], 0, 0
    for i, klucz in enumerate(render.KOL):
        if render.FNS[i] is None or (klucze and klucz not in klucze) or i % czesc[1] != czesc[0]:
            continue
        a, b = render.SCENES[i][:2]
        rap, n = {}, 0
        for f in range(0, int((b - a) * render.FPS), krok):
            t = a + f / render.FPS
            st, _ = render.uloz(t)
            if getattr(st, "uklad", None) is None:
                break
            if n == 0 and not (st.uklad.kontrole or st.uklad.wiezy):
                break  # ujęcie bez rzeczy w dłoniach, siedzenia i otworów — nie ma czego sprawdzać w buforze
            U.zlicz(rap, st, U.kontrola(st)[0], t - a)
            n += 1
        if not rap:
            continue
        ujec += 1
        tekst, bledy = U.raport_md(rap, f"{render.ODN[i]} {klucz} — {n} klatek (co {krok}.)")
        bledy_razem += bledy
        czesci.append(tekst)
        wyniki[klucz] = bledy
        print(f"{render.ODN[i]} {klucz}: {n} klatek, {len(rap)} kontroli, błędów {bledy}", flush=True)
    raport.write_text("# Kontrola układu sceny (uklad.py) — film o Szamilu\n\n" + f"Ujęć: {ujec}, błędów razem: {bledy_razem}.\n\n"
                      + "\n\n".join(czesci) + "\n", encoding="utf-8")
    return bledy_razem, wyniki


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    krok = int(sys.argv[sys.argv.index("--krok") + 1]) if "--krok" in sys.argv else 1
    if "--krok" in sys.argv:
        args = [x for x in args if x != str(krok)]
    klucze = set(args[0].split(",")) if args else None
    cz = tuple(int(v) for v in sys.argv[sys.argv.index("--czesc") + 1].split("/")) if "--czesc" in sys.argv else (0, 1)
    if "--czesc" in sys.argv:
        args = [x for x in args if "/" not in x]
        klucze = set(args[0].split(",")) if args else None
    rap = RAPORT if cz[1] == 1 else RAPORT.with_name(f"kontrola_ukladu_{cz[0]}.md")
    bl, _ = kontroluj(klucze, krok, cz, rap)
    print(f"raport: {rap} | błędów: {bl}")
    sys.exit(1 if bl else 0)
