"""Studio: film „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” — etapy od Story Bible do ujęć, bez eksportu.

Wzór: output/bonnie-i-clyde/studio_film.py (ten sam plan: akty, sekwencje, sceny, beaty, ujęcia, księga świata).

  python3 -I studio_film.py rozwoj   — Story Bible, fakty i źródła, księga świata i warsztat (nic poza tym nie rusza)
  python3 -I studio_film.py szkice   — import szkiców A/B/C z docs/filmy/szamil-diuna/szkice/
  python3 -I studio_film.py klatki [tylko=3,6]  — po jednej klatce ze środka ujęcia na oś montażu (v1): Montaż ma co odtwarzać,
                                       a ruch ujęć Studio rysuje na żywo z kodu (legacy.teatr, na_zywo.py)
  python3 -I studio_film.py os       — klatki ujęć (już wgrane) od nowa na oś v1 w miejscach ujęć, po zmianie długości
                                       (np. po nagraniu lektora); bez rysowania klatek
  python3 -I studio_film.py lektor   — kwestie lektora z lektor_en/*.wav na ścieżkę Lektor (a1), od oddechu w ujęciu
  python3 -I studio_film.py dzwiek   — muzyka (a2, głośność 0,8) i efekty (a3) z dzwiek_en/*.wav, po jednym klipie na cały
                                       film (efekty.py; próbkę zatwierdza reżyser — ZGODA="cytat" trafia do dziennika)
  python3 -I studio_film.py plan     — Master Story, akty, sekwencje, scenariusz, plan scen, reżyseria i ujęcia z rozpiski
                                       (dane.py); ujęcia Studio dopasowane po legacy.klucz; kontrola ciągłości i wpis w dzienniku
Studio musi działać (port 8876). Identyfikator projektu pamięta studio.json obok skryptu.
"""
import hashlib
import json
import math
import mimetypes
import wave
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import uuid
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/Users/krystiangaleczka/Documents/YT")  # Studio i flowTypes.ts żyją w głównym katalogu (worktree filmu ma dowiązania)
FILM = REPO / "docs/filmy/szamil-diuna"
sys.path.insert(0, str(FILM / "ujecia"))
import ksiega  # noqa: E402
from dane import AKTY, HAK, LEKTOR, kwestia, okno_kwestii, ujecia  # noqa: E402

AUTO_UWAGA = re.compile(r"^(Kadr|Typ|Beat|Dźwięk|Cel|Przejście):")
API = f"http://127.0.0.1:{os.environ.get('DOCOS_API_PORT', '8876')}/api"
HEAD = {"Content-Type": "application/json", "X-Docos-Request": "1"}
STATE = HERE / "studio.json"
TITLE = "The Imam Who Fought Russia for 25 Years — and Ended Up in Dune"
KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal", "TYT": "karta / napis"}
RUCH = {"stat": "statyczna", "naj": "najazd", "odj": "odjazd", "pan": "panorama", "jaz": "jazda za postacią",
        "szarp": "szarpnięcie kamery", "kb": "Ken Burns po obrazie z wydarzeniem"}
TYPE = {"PO": "wide", "PP": "wide", "PŚ": "medium", "Z": "close-up", "D": "insert", "TYT": "insert"}
NAPIECIE = {0: 7, 1: 6, 2: 7, 3: 7, 4: 8, 5: 8, 6: 5}  # krzywa filmu (szkic E): napięcie aktu 0–10

ZRODLA = [
    {"id": "src_larb_collins", "title": "The Secret History of Dune", "author": "Will Collins", "edition": "Los Angeles Review of "
     "Books, 16.09.2017", "url": "https://lareviewofbooks.org/article/the-secret-history-of-dune/", "accessed_at": "2026-11-27"},
    {"id": "src_wiki_shamil", "title": "Imam Shamil", "author": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Imam_Shamil",
     "accessed_at": "2026-11-27"},
    {"id": "src_wiki_akhulgo", "title": "Siege of Akhoulgo", "author": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Siege_of_Akhoulgo",
     "accessed_at": "2026-11-27"},
    {"id": "src_wiki_gunib", "title": "Battle of Ghunib", "author": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Battle_of_Ghunib",
     "accessed_at": "2026-11-27"},
    {"id": "src_wiki_chavchavadze", "title": "Chavchavadze", "author": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Chavchavadze",
     "accessed_at": "2026-11-27"},
    {"id": "src_nplg_tsinandali", "title": "Shamil and the Chavchavadze family (Tsinandali)", "author": "National Parliamentary "
     "Library of Georgia", "url": "https://www.nplg.gov.ge/chavchavadze/en/shamil.html", "accessed_at": "2026-11-27"},
    {"id": "src_kennedy", "title": "Frank Herbert's Dune: A Critical Companion", "author": "Kara Kennedy", "edition": "Palgrave "
     "Macmillan, 2022", "url": "https://www.springer.com/book/9783031139345", "accessed_at": "2026-11-28"},
    {"id": "src_commons_horschelt", "title": "Horschelt. Surrender of Shamil. 1863 (Wikimedia Commons)", "author": "Theodor Horschelt",
     "url": "https://commons.wikimedia.org/wiki/File:Horschelt._Surrender_of_Shamil._1863.jpg", "accessed_at": "2026-11-28"},
    {"id": "src_commons_denier", "title": "Shamil by Denier, 1859 (Wikimedia Commons)", "author": "Andrey Denier",
     "url": "https://commons.wikimedia.org/wiki/File:Shamil_by_Denier.jpg", "accessed_at": "2026-11-28"},
    {"id": "src_met_exchange", "title": "Exchange and Ransoming from Schamyl of the Family of Prince David Chavchavadze and Princess "
     "Orbelian (1855)", "author": "The Metropolitan Museum of Art", "url": "https://www.metmuseum.org/art/collection/search/423472",
     "accessed_at": "2026-11-28"},
    {"id": "src_space_dune3", "title": "Dune: Part Three — release date, plot, cast", "author": "Space.com",
     "url": "https://www.space.com/entertainment/space-movies-shows/everything-we-know-about-dune-messiah", "accessed_at": "2026-11-27"},
]
L, S, A, G, C, T, K, HO, DE, MET, D3 = (z["id"] for z in ZRODLA)
FAKTY = [
    ("Herbert took chakobsa, kanly, kindjal, sietch, tabr, padishah and siridar from Lesley Blanch's The Sabres of Paradise "
     "(1960), a history of Imam Shamil's war against Russia.", L, "VERIFIED", "Esej Collinsa; słowa i ich znaczenia u Blanch."),
    ("Blanch: \"To kill with the point lacked artistry.\" Dune has an almost identical line in young Paul's weapons training.",
     L, "VERIFIED", "Blanch za esejem i Wikipedią. Brzmienie w Diunie NIESPRAWDZONE: źródła cytują „tip” albo „point”, mówi "
     "Duncan Idaho albo Gurney Halleck — karta w kadrze dopiero po sprawdzeniu w wydaniu, z numerem strony."),
    ("Blanch: \"Polish comes from the city, wisdom from the hills.\" Dune: \"Polish comes from the cities, wisdom from the "
     "desert.\"", L, "VERIFIED", "Przysłowie kaukaskie u Blanch; aforyzm pustyni w Diunie."),
    ("Shamil (born 1797 in Gimry) became imam in 1834 and led the resistance until 1859.", S, "VERIFIED", "Infobox: Imam of Dagestan "
     "1834–1859; lead podaje też 1840–1859 jako imama Czeczenii."),
    ("At Akhulgo in 1839 Shamil handed over his son Jamal al-Din as a hostage; the fortress fell and Shamil escaped by night, "
     "with a raft of dummies set adrift as a decoy.", A, "VERIFIED", "Wiek syna różni się: 6 (NPLG), ok. 7 (Central Asian "
     "Survey), 8 (Blanch), 12 (Wikipedia) → „still a boy”."),
    ("Jamal al-Din was raised in Russia and became an officer of the imperial army; he returned to his father in 1855 and died "
     "of illness in 1858.", S, "VERIFIED", ""),
    ("In summer 1854 Shamil's son Ghazi Muhammad raided Tsinandali and captured Princess Anna Chavchavadze and Princess Varvara "
     "Orbeliani with their children.", C, "VERIFIED", "Data najazdu różni się w źródłach (2 albo 4 lipca 1854)."),
    ("On 22 March 1855 (10 March Old Style) the captives were exchanged at the river Michik for Jamal al-Din, 40,000 silver "
     "roubles and an exchange of prisoners; Shamil's first demands were much higher.", T, "VERIFIED",
     "Z księżnymi były dzieci i służba (ok. 23–24 osoby, w tym guwernantka Anna Drancy); niewola ok. 8–9 miesięcy w Wedeno."),
    ("On 6 September 1859 (25 August Old Style) Shamil surrendered at Gunib to Prince Baryatinsky; about 400 defenders faced "
     "about 16,000 Russian troops.", G, "VERIFIED", "W filmie kalendarz gregoriański (księga D6); liczby z infoboksu — „about”."),
    ("After surrender Shamil met Tsar Alexander II, lived in honourable exile in Kaluga, made the pilgrimage and died in Medina in "
     "1871.", S, "VERIFIED", ""),
    ("Kara Kennedy's critical companion to Dune discusses Herbert's borrowings from Blanch.", K, "UNVERIFIED",
     "Książka istnieje (Palgrave 2022); że pisze o Blanch — tylko według fact-checku ChatGPT, do sprawdzenia w indeksie."),
    ("Theodor Horschelt's Surrender of Shamil (1863) and Andrey Denier's portrait of Shamil (1859) are public domain on Wikimedia "
     "Commons.", HO, "UNVERIFIED", "Według fact-checku 28.11; licencję sprawdzić na stronie pliku przy pobraniu (też " + DE + ")."),
    ("Dune: Part Three adapts Dune Messiah and is scheduled for 18 December 2026.", D3, "VERIFIED", "Data docelowa, nie zamknięta "
     "oficjalnie; w kwestii bez daty."),
]


def call(path, body=None, method=None):
    req = urllib.request.Request(API + path, method=method or ("POST" if body is not None else "GET"), headers=HEAD,
                                 data=None if body is None else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Studio odrzuciło {method or 'POST'} {path}: {e.code} {e.read().decode()[:800]}")


def pid():
    return json.loads(STATE.read_text())["pid"]


def tc(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def node(nid, title, description):
    return {"id": nid, "variants": [{"id": nid + "_v1", "title": title, "description": description}], "selected": nid + "_v1"}


def tytul(opis):
    head = opis.split(";")[0].split(":")[0].strip()
    head = head[0].upper() + head[1:]
    return head if len(head) <= 70 else head[:67].rsplit(" ", 1)[0] + "…"


def zapisz_flow(p, flow):
    return call(f"/projects/{p['id']}/flow", {"expected_revision": p["revision"], "flow": flow}, "PUT")


def rozwoj():
    """Story Bible, fakty, źródła, księga świata i warsztat."""
    p = call(f"/projects/{pid()}")
    flow = dict(p["legacy"].get("production_flow") or {})
    flow.setdefault("version", 1)
    flow.update(factual=True, bible=ksiega.BIBLIA, world=ksiega.SWIAT, book=ksiega.WARSZTAT)
    for k, v in {"master": {"id": "master", "variants": [], "selected": None}, "acts": [], "sequences": [], "outlines": [],
                 "scripts": {}, "approved": {}, "reviews": [], "director": {"mode": "manual", "plans": {}, "customPatterns": []}}.items():
        flow.setdefault(k, v)
    p = zapisz_flow(p, flow)
    zrodla = [{"provider": "web", **z} for z in ZRODLA]
    fakty = [{"id": f"fact_{i:02d}", "claim": c, "source": next(z["title"] for z in ZRODLA if z["id"] == s), "source_id": s,
              "url": next(z["url"] for z in ZRODLA if z["id"] == s), "status": st, "note": n, "checked_at": "2026-11-27"}
             for i, (c, s, st, n) in enumerate(FAKTY, 1)]
    p = call(f"/projects/{p['id']}", {"expected_revision": p["revision"], "changes": {"sources": zrodla, "facts": fakty}}, "PATCH")
    print(f"projekt {p['id']} rev {p['revision']}: Story Bible, {len(fakty)} faktów, {len(zrodla)} źródeł, księga świata, warsztat")


def szkice():
    """Import A/B/C; z ZATWIERDZ_SZKIC=<id> i NOTATKA=… ponowne zatwierdzenie wariantu po zmianie."""
    p = call(f"/projects/{pid()}")
    r = call(f"/projects/{p['id']}/sketches/import", {"path": str(FILM / "szkice"), "expected_revision": p["revision"],
                                                     "who": "Claude"})
    print("szkice zaimportowane:", json.dumps(r, ensure_ascii=False)[:200])
    if os.environ.get("ZATWIERDZ_SZKIC"):
        p = call(f"/projects/{pid()}")
        call(f"/projects/{p['id']}/sketches/approve", {"variant_id": os.environ["ZATWIERDZ_SZKIC"], "expected_revision": p["revision"],
                                                      "who": "Claude na polecenie reżysera", "note": os.environ.get("NOTATKA", "")})
        print("zatwierdzony ponownie:", os.environ["ZATWIERDZ_SZKIC"])


def rozpiska():
    flat, out = iter(ujecia()), []
    for n, _, _, sceny in AKTY:
        for si, (stitle, place, beaty) in enumerate(sceny, 1):
            for bi, (btitle, shots) in enumerate(beaty, 1):
                for k in range(1, len(shots) + 1):
                    _, nr, klucz, kadr, ruch, sec, opis, snd = next(flat)
                    out.append(dict(akt=n, nr=nr, scena=si, stitle=stitle, place=place, beat=bi, btitle=btitle, k=k, klucz=klucz,
                                    kadr=kadr, ruch=ruch, sec=sec, opis=opis, snd=snd, ref=f"d{n:02d}_{nr:02d}",
                                    oid=f"sc_d{n:02d}_{si}", bid=f"sc_d{n:02d}_{si}_b{bi}", sid=f"sc_d{n:02d}_{si}_b{bi}_s{k}"))
    return out


def plan():
    p = call(f"/projects/{pid()}")
    rows = rozpiska()
    old = p["legacy"].get("production_flow") or {}
    flow = {**old, "version": 1, "factual": True, "bible": ksiega.BIBLIA, "world": dict(ksiega.SWIAT), "book": ksiega.WARSZTAT,
            "acts": [], "sequences": [], "outlines": [], "scripts": {},
            "director": {"mode": "manual", "plans": {}, "customPatterns": []}}
    # Master Story z rozpiski szkicu E (przebudowa 28.11.2026, reżyser: „przebuduj to”) — nie z migawki zatwierdzonego szkicu D,
    # bo D jest już historią; szkic E czeka na zatwierdzenie reżysera w etapie Szkice ujęć
    flow["master"] = node("master", TITLE, " ".join(a[2] for a in AKTY))
    n0 = sum(r["akt"] == 0 for r in rows)
    flow["world"]["prologue"] = {"1": n0}
    t = 0.0
    for n, atitle, aopis, sceny in AKTY:
        act, seq = f"act_{n:02d}", f"seq_d{n:02d}"
        owner = "act_01" if n == 0 else act
        mine = [r for r in rows if r["akt"] == n]
        if n != 0:
            opis = aopis if n != 1 else next(a[2] for a in AKTY if a[0] == 0) + " " + aopis
            flow["acts"].append(node(act, f"Akt {n} · {atitle}", opis))
        flow["sequences"].append({**node(seq, f"{'Prolog' if n == 0 else 'Akt ' + str(n)} · {atitle}",
                                         " → ".join(s[0] for s in sceny) + "."), "actId": owner,
                                  "seconds": round(sum(r["sec"] for r in mine), 1)})
        flow["scripts"][owner] = "\n\n".join(x for x in [flow["scripts"].get(owner, "")] + [kwestia(r["snd"]) for r in mine] if x)
        for si, (stitle, place, beaty) in enumerate(sceny, 1):
            oid = f"sc_d{n:02d}_{si}"
            srows = [r for r in mine if r["scena"] == si]
            s0, nap = t, NAPIECIE[n]
            beats, shots = [], []
            for bi, (btitle, _) in enumerate(beaty, 1):
                brows = [r for r in srows if r["beat"] == bi]
                beats.append({"id": f"{oid}_b{bi}", "title": btitle, "goal": "; ".join(r["opis"] for r in brows)[:3900],
                              "tensionBefore": max(0, nap - 1), "tensionAfter": min(10, nap + (1 if bi == len(beaty) else 0)),
                              "viewerKnows": " ".join(kwestia(r["snd"]) for r in brows)[:1900], "characterKnows": "",
                              "soundCue": "; ".join(r["snd"] for r in brows if r["snd"] and not r["snd"].startswith("L:"))[:990],
                              "patternId": "exposition" if any(r["kadr"] == "TYT" for r in brows) else
                              ("rapid-intercut" if any(r["ruch"] == "szarp" for r in brows) else
                               "evidence" if n == 6 else "slow-burn")})
                for r in brows:
                    shots.append({"id": r["sid"], "beatId": r["bid"], "typeId": TYPE[r["kadr"]], "title": tytul(r["opis"]),
                                  "description": f"[{tc(t)}–{tc(t + r['sec'])}] ({KADR[r['kadr']]} · {RUCH[r['ruch']]}) {r['opis']}",
                                  "duration": r["sec"], "transition": "dip" if r["kadr"] == "TYT" else "cut", "sound": r["snd"]})
                    r["t0"], r["title"] = t, tytul(r["opis"])
                    t += r["sec"]
            flow["outlines"].append({**node(oid, stitle, f"{place}. Beaty: " + ", ".join(b[0] for b in beaty) + "."),
                                     "sectionId": seq, "seconds": round(t - s0, 1)})
            flow["director"]["plans"][oid] = {"outlineId": oid, "sourceSignature": "", "patternId": beats[0]["patternId"],
                                              "mode": "manual", "notes": f"{'Prolog' if n == 0 else 'Akt ' + str(n)} · scena {si} · "
                                              f"{tc(s0)}–{tc(t)} filmu. Rozpiska: docs/filmy/szamil-diuna/ujecia/dane.py",
                                              "beats": beats, "shots": shots}
    # etapy, które były już zatwierdzone, dostają nowy podpis (ZATWIERDZ=…); inaczej zmiana planu zostawia je nieaktualne
    zatw = os.environ.get("ZATWIERDZ", "")
    signed = subprocess.run(["node", "--experimental-strip-types", str(HERE / "podpisy.mjs"),
                             str(REPO / "apps/studio/src/flowTypes.ts")], input=json.dumps(flow), capture_output=True, text=True,
                            check=True, env={**os.environ, "ZATWIERDZ": zatw}).stdout
    p = zapisz_flow(p, json.loads(signed))

    # ujęcia: istniejące zostają (uwagi, markery), zmienia się opis, kwestia i miejsce na osi
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    by_key = {s["legacy"]["klucz"]: s for s in p["scenes"] if s["legacy"].get("klucz")}
    scenes, cursor = [], 0
    for r in rows:
        frames = max(1, round(r["sec"] * fps))
        s = by_key.get(r["klucz"]) or {"mode": "search", "asset_id": None, "voice_asset_id": None, "variants": [], "fact_ids": [],
                                       "role": "illustration", "locked": False, "animation": "static", "timing": "estimated"}
        jego = [l for l in (s.get("director_notes") or "").split("\n") if l.strip() and not AUTO_UWAGA.match(l.strip())]
        auto_ = f"Kadr: {KADR[r['kadr']]} · {RUCH[r['ruch']]}. Beat: {r['btitle']}. Dźwięk: {r['snd']}"
        s.update(title=f"{r['stitle']} · {r['nr']:02d} · {r['title']}", narration=kwestia(r["snd"]), description=r["opis"],
                 director_notes=("\n\n".join([auto_] + (["\n".join(jego)] if jego else [])))[:3000],
                 start=cursor, duration=frames,
                 prompt=f"Rysowane kodem: output/szamil-diuna, funkcja s_{r['klucz']} ({r['ref']}); podgląd na żywo.",
                 motion_prompt=RUCH[r["ruch"]] if r["ruch"] != "stat" else "", search_query=r["title"],
                 legacy={**s.get("legacy", {}), "flow_act_id": f"act_{max(1, r['akt']):02d}", "flow_section_id": f"seq_d{r['akt']:02d}",
                         "flow_outline_id": r["oid"], "flow_director_shot_id": r["sid"], "flow_director_beat_id": r["bid"],
                         "flow_director_kind": TYPE[r["kadr"]], "klucz": r["klucz"],
                         # podgląd na żywo: Studio rysuje ujęcie z kodu (output/szamil-diuna/na_zywo.py), bez klipów mp4
                         "teatr": {"film": "szamil-diuna", "jezyk": "en", "odn": r["ref"]}})
        scenes.append(s)
        cursor += frames
    # klipy osi, których ujęcia znikają z rozpiski (przebudowa 28.11: wszystkie ujęcia szkicu D), wypadają przed zapisem ujęć
    # (operacja osi `remove_clip`); NOWA_OS=1 zdejmuje też klipy ujęć, które zostają, bo stoją w starych miejscach — `klatki`
    # kładzie je od nowa w miejscu ujęcia
    zostaja = {s.get("id") for s in scenes if s.get("id")}
    usun = [c for c in p["sequence"]["clips"] if (c.get("scene_id") and c["scene_id"] not in zostaja)
            or (os.environ.get("NOWA_OS") == "1" and c["track_id"] == "v1")]
    for i in range(0, len(usun), 200):
        p = call(f"/projects/{p['id']}/edits", {"expected_revision": p["revision"],
                                                 "operations": [{"type": "remove_clip", "clip_id": c["id"]} for c in usun[i:i + 200]]})
    p = call(f"/projects/{p['id']}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
    rep = call(f"/projects/{p['id']}/continuity/check", {})
    tot = rep["totals"]
    for i in rep["issues"]:
        print(f"  [{i['severity']}] {i.get('ref') or ('akt ' + str(i.get('unit')))} {i['rule']}: {i['message']}")
    call(f"/projects/{p['id']}/flow/log", {"entry": {
        "who": "Claude (studio_film.py)", "kind": "tworzenie",
        "summary": f"Plan filmu wgrany z rozpiski: {len(AKTY)} jednostek (prolog + {len(AKTY) - 1} aktów), {len(rows)} ujęć, {tc(t)}",
        "details": f"Kontrola ciągłości (waga 3 / 2 / 1): {tot.get('3', 0)} / {tot.get('2', 0)} / {tot.get('1', 0)}. Źródło: "
                   "szkic E — przebudowa całego filmu 28.11.2026 (reżyser: „przebuduj to”); ujęcia narysowane kodem (output/szamil-diuna, podgląd na żywo).",
        "files": ["docs/filmy/szamil-diuna/ujecia/dane.py", "docs/filmy/szamil-diuna/ujecia/ksiega.py"]}})
    print(f"projekt {p['id']} | {len(rows)} ujęć, {tc(t)} | kontrola {tot.get('3', 0)}/{tot.get('2', 0)}/{tot.get('1', 0)}")


def upload(pid_, path, name):
    b = uuid.uuid4().hex
    head = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            f"Content-Type: {mimetypes.guess_type(name)[0] or 'image/png'}\r\n\r\n").encode()
    req = urllib.request.Request(API + f"/projects/{pid_}/media", method="POST", data=head + path.read_bytes() + f"\r\n--{b}--\r\n".encode(),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}", "X-Docos-Request": "1"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["asset"]["id"]


def klatki(args):
    """Na oś montażu po jednej klatce ze środka ujęcia (szkic 640 × 360) — tak jak „Bonnie and Clyde” (studio_film.klatki).
    Bez tego oś była pusta i Montaż nic nie odtwarzał (reżyser 28.11: „jak naciskam play w montażu to nic nie gra”). Obraz
    ujęć rysuje podgląd na żywo; klatki są zapasem, gdy podgląd jest wyłączony."""
    pid_ = pid()
    only = sorted({int(x) for a in args if a.startswith("tylko=") for x in a[6:].split(",")})
    rows = rozpiska()
    tmp = Path(tempfile.mkdtemp(prefix="szamil-klatki-"))
    lista = [n for n in range(1, len(rows) + 1) if not only or n in only]
    kod = ("import sys; sys.argv=['x']; sys.path.insert(0, %r); import render as R\n"
           "for n in %r:\n    a, b = R.SCENES[n - 1][:2]\n    R.frame(a + (b - a) * 0.6).save(%r %% R.ODN[n - 1])\n") % (
        str(HERE), lista, str(tmp / "%s.png"))
    subprocess.run([sys.executable, "-c", kod], env={**os.environ, "SZKIC": "1"}, check=True)
    p = call(f"/projects/{pid_}")
    by_key = {s["legacy"].get("klucz"): s for s in p["scenes"]}
    done = {}
    for n, r in enumerate(rows, 1):
        img = tmp / f"{r['ref']}.png"
        if n not in lista or not img.exists():
            continue
        done[r["klucz"]] = upload(pid_, img, f"{r['ref']} {r['klucz']} klatka.png")
        img.unlink()
    p = call(f"/projects/{pid_}")
    scenes = [{**s, **({"asset_id": done[k], "mode": "upload", "animation": "static"} if (k := s["legacy"].get("klucz")) in done else {})}
              for s in p["scenes"]]
    p = call(f"/projects/{pid_}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
    on_axis = {c.get("scene_id"): c for c in p["sequence"]["clips"] if c["track_id"] == "v1"}
    mine = [s for s in p["scenes"] if s["legacy"].get("klucz") in done]
    ops = [{"type": "update_clip", "clip_id": on_axis[s["id"]]["id"], "changes": {"asset_id": s["asset_id"]}} for s in mine if s["id"] in on_axis]
    for i in range(0, len(ops), 200):
        p = call(f"/projects/{pid_}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})
    for s in mine:
        if s["id"] not in on_axis:
            p = call(f"/projects/{pid_}/scenes/{s['id']}/to-timeline", {"expected_revision": p["revision"]})
    print(f"klatki: {len(done)} ujęć | klipów na osi {len(p['sequence']['clips'])} | rewizja {p['revision']}")


def os_v1():
    """Po zmianie długości ujęć (plan z NOWA_OS=1 zdjął klipy v1) kładzie wgrane klatki ujęć z powrotem na oś, każdą
    w miejscu i długości swojego ujęcia (to-timeline) — bez rysowania klatek od nowa."""
    pid_ = pid()
    p = call(f"/projects/{pid_}")
    na_osi = {c.get("scene_id") for c in p["sequence"]["clips"] if c["track_id"] == "v1"}
    n = 0
    for s in sorted(p["scenes"], key=lambda s: s["start"]):
        if s.get("asset_id") and s["id"] not in na_osi:
            p = call(f"/projects/{pid_}/scenes/{s['id']}/to-timeline", {"expected_revision": p["revision"]})
            n += 1
    print(f"oś v1: dołożono {n} klipów | klipów na osi {len(p['sequence']['clips'])} | rewizja {p['revision']}")


def dzwiek():
    """Muzyka (a2) i efekty (a3), po jednym klipie na cały film — wzór: „Bonnie and Clyde” studio_film.dzwiek. Stare klipy
    a2/a3 schodzą z osi; klip nie wychodzi poza koniec ostatniego ujęcia."""
    pid_ = pid()
    p = call(f"/projects/{pid_}")
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    total = max(s["start"] + s["duration"] for s in p["scenes"])
    ops = [{"type": "remove_clip", "clip_id": c["id"]} for c in p["sequence"]["clips"] if c["track_id"] in ("a2", "a3")]
    wgrane = []
    for track, name, vol in (("a2", "muzyka", 0.8), ("a3", "efekty", 1.0)):
        wav = HERE / "dzwiek_en" / f"{name}.wav"
        if not wav.exists():
            print(f"brak {wav} — bez ścieżki {name}")
            continue
        aid = upload(pid_, wav, f"{name} — cały film.wav")
        with wave.open(str(wav)) as w:
            frames = min(total, math.floor(w.getnframes() / w.getframerate() * fps))
        ops.append({"type": "add_clip", "clip": {"track_id": track, "asset_id": aid, "title": f"{name.capitalize()} · cały film",
                                                 "start": 0, "duration": frames, "volume": vol}})
        wgrane.append(f"{name} {frames / fps:.1f} s")
    p = call(f"/projects/{pid_}")  # wgrane pliki podbiły rewizję
    p = call(f"/projects/{pid_}/edits", {"expected_revision": p["revision"], "operations": ops})
    zgoda = os.environ.get("ZGODA", "")
    call(f"/projects/{pid_}/flow/log", {"entry": {
        "who": "studio_film.py", "kind": "wgranie", "summary": "Dźwięk wgrany: " + ", ".join(wgrane),
        "details": "Muzyka i efekty: synteza w numpy, output/szamil-diuna/efekty.py — tematy Kaukazu i Diuny (góry: pandur, duduk, "
                   "zurna; lezginka 6/8 z doli i garmoszką; marsz imperium; lament; bałałajka; walc; pustynia: burdon, bendir, ney), "
                   "motyw Szamila (przedstawienie, uścisk, biała flaga), cisza przed szczytami (skok, zasadzka, uścisk, szturm Gunibu), "
                   "efekty z podsłuchu ujęć (konie, kroki lalek, strzały, armaty, pieczątki, koza, robak, kartki, nitki) i tła miejsc; "
                   "pod kwestiami ściszone łagodnie. Bez głosów ludzi." + (f" Próbkę (probka_dzwieku.py) zatwierdził reżyser: „{zgoda}”."
                                                                          if zgoda else ""),
        "files": ["output/szamil-diuna/efekty.py", "output/szamil-diuna/probka_dzwieku.py"]}})
    print(f"dźwięk: {', '.join(wgrane) or 'nic'} | klipów na osi {len(p['sequence']['clips'])} | rewizja {p['revision']}")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def lektor():
    """Lektor (ścieżka a1, klip na kwestię, od oddechu w ujęciu) — wzór: „Bonnie and Clyde” studio_film.dzwiek(lektor=True).
    Plik wgrywa się raz (studio.json pamięta jego sumę), zmieniona kwestia albo nowe nagranie idą od nowa."""
    st = json.loads(STATE.read_text())
    pid_ = st["pid"]
    p = call(f"/projects/{pid_}")
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    by_shot = {s["legacy"].get("flow_director_shot_id"): s for s in p["scenes"]}
    ops = [{"type": "remove_clip", "clip_id": c["id"]} for c in p["sequence"]["clips"] if c["track_id"] == "a1"]
    brak = []
    for r in rozpiska():
        if not kwestia(r["snd"]):
            continue
        sc, wav = by_shot[r["sid"]], LEKTOR / f"{r['klucz']}.wav"
        meta = json.loads(wav.with_suffix(".json").read_text()) if wav.with_suffix(".json").exists() else {}
        if not wav.exists() or meta.get("text") != kwestia(r["snd"]):
            brak.append(r["klucz"])
            continue
        cached = st.setdefault("lektor", {}).get(r["klucz"])
        if not cached or cached["sha"] != _sha(wav):
            cached = st["lektor"][r["klucz"]] = {"asset": upload(pid_, wav, f"lektor {r['ref']} {r['klucz']}.wav"), "sha": _sha(wav)}
            STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1))
        start = sc["start"] + round(okno_kwestii(r["snd"], r["klucz"] in HAK)[0] * fps)  # w haku krótszy oddech
        ops.append({"type": "add_clip", "clip": {"track_id": "a1", "asset_id": cached["asset"], "scene_id": sc["id"],
                                                 "title": f"Lektor · {kwestia(r['snd'])[:80]}", "start": start,
                                                 "duration": max(1, math.ceil(meta["duration"] * fps))}})
    p = call(f"/projects/{pid_}")  # wgrane pliki podbiły rewizję
    for i in range(0, len(ops), 200):
        p = call(f"/projects/{pid_}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})
    n1 = sum(c["track_id"] == "a1" for c in p["sequence"]["clips"])
    call(f"/projects/{pid_}/flow/log", {"entry": {
        "who": "studio_film.py", "kind": "wgranie", "summary": f"Lektor wgrany: {n1} kwestii na ścieżce Lektor",
        "details": "Klon głosu autora (Chatterbox Multilingual, przepis TEATR, jedno podejście na kwestię, ziarno 42; "
                   "lektor_studio.py podejscia --teatr), reżyser 28.11.2026: „nagraj lektora”. Długości ujęć z prawdziwych nagrań "
                   "(dane.nagranie), akcja przełożona na nie (render.czas_akcji)." + (f" Bez nagrania: {', '.join(brak)}." if brak else ""),
        "files": ["output/szamil-diuna/lektor_en.py", "output/szamil-diuna/lektor_en/"]}})
    print(f"lektor: {n1} klipów | bez nagrania: {', '.join(brak) or '—'} | rewizja {p['revision']}")


if __name__ == "__main__":
    if sys.argv[1] == "klatki":
        klatki(sys.argv[2:])
        sys.exit(0)
    {"rozwoj": rozwoj, "szkice": szkice, "plan": plan, "lektor": lektor, "os": os_v1, "dzwiek": dzwiek}[sys.argv[1]]()
