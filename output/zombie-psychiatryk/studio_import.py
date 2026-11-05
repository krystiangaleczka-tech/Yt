"""Rozkłada gotowy film „Oddział C” (2 × 25 s) na etapy DocOS Studio: pomysł, Story Bible, Master Story,
akty, sekwencje, scenariusz, plan scen i reżyserię z prawdziwymi czasami ujęć z render.py / render2.py.

uruchom (Studio musi działać):  python3 studio_import.py flow  <id projektu> [port]
po zatwierdzeniu etapów i „Utwórz ujęcia z planu”:  python3 studio_import.py media <id projektu> [port]
po poprawkach w render.py / render2.py:  python3 studio_import.py update <id projektu> [port]
  — renderuje same ujęcia (bez eksportu filmu), podmienia je w Ujęciach i przesuwa montaż: obraz, lektor, efekty
"""
import json
import mimetypes
import subprocess
import sys
import tempfile
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
FLOW_TYPES = HERE.parents[1] / ".claude/worktrees/film-flow/apps/studio/src/flowTypes.ts"
mode, PID = sys.argv[1], sys.argv[2]
API = f"http://127.0.0.1:{sys.argv[3] if len(sys.argv) > 3 else 8878}/api"


def call(path, body=None, method=None):
    req = urllib.request.Request(API + path, method=method or ("POST" if body is not None else "GET"),
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "X-Docos-Request": "1"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def upload(path, name=None):
    boundary = uuid.uuid4().hex
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name or path.name}\"\r\n"
            f"Content-Type: {mimetypes.guess_type(str(path))[0] or 'application/octet-stream'}\r\n\r\n").encode()
    req = urllib.request.Request(API + f"/projects/{PID}/media", method="POST",
                                 data=head + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode(),
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "X-Docos-Request": "1"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["asset"]["id"]


def node(nid, title, description):
    return {"id": nid, "variants": [{"id": nid + "_v1", "title": title, "description": description}], "selected": nid + "_v1"}


# (część, start w renderze, długość, tytuł, opis, plik lektora, start lektora w renderze, ujęcia)
# ujęcie: (typ, tytuł, opis, długość s, przejście, dźwięk, beat)
SCENES = [
    (1, 0.0, 7.0, "Szpital przy Leśnej",
     "Noc. Ogólny plan szpitala psychiatrycznego za płotem i bramą. Wiatr szarpie drzewami nierównymi podmuchami. "
     "W jednym z okien ktoś podchodzi, przekrzywia głowę i nagle odskakuje.",
     "l1.wav", 1.00,
     [("establishing", "Szpital nocą", "Plan ogólny budynku, bramy i drzew; kamera przez całe ujęcie najeżdża aż do okna "
       "(zoom 1,0→3,4). Sylwetka w oknie podchodzi (3,0 s), przekrzywia głowę i odskakuje (5,9 s) — cała w obrębie okna.",
       7.0, "cut", "Niski dron, wiatr, skrzyp bramy w 0,9 s", 0)],
     [("Miejsce, w którym zawsze ktoś krzyczy", "Ustawić miejsce i obietnicę grozy jednym kadrem.", 1, 3,
       "To szpital psychiatryczny; coś jest w oknie.", "Narrator zna to miejsce, jest tu w pracy.", "Wiatr, brama", "exposition")]),
    (1, 7.0, 5.0, "Cisza na oddziale C",
     "Korytarz oddziału C. Sanitariusz (narrator) idzie z latarką, staje, rozgląda się w lewo i w prawo, rusza wolniej. "
     "Zamiast krzyków — tylko bzyczenie świetlówek.",
     "l2.wav", 7.90,
     [("over-shoulder", "Sanitariusz z latarką", "Zza pleców sanitariusza w głąb korytarza; idzie, staje (1,8–3,4 s), "
       "latarka w lewo, w prawo, na wprost. Lekki najazd 1,00→1,06.", 5.0, "cut", "Kroki tylko gdy idzie, bzyczenie świetlówek", 0)],
     [("Za cicho", "Cisza jako sygnał zagrożenia.", 3, 4, "Na oddziale nikt nie krzyczy — to nienormalne.",
       "Sanitariusz czuje, że coś jest nie tak.", "Świetlówki zamiast krzyków", "slow-burn")]),
    (1, 12.0, 5.6, "Pan Henryk w okienku",
     "Drzwi izolatki z okienkiem z siatką. W ciemności przez moment błyskają dwa oczy. Nagle twarz pana Henryka uderza w szybę; "
     "głowa powoli się przekrzywia, oczy się nie ruszają, dłoń zsuwa się po szybie, oddech paruje na szkle.",
     "l3.wav", 13.20,
     [("static-hold", "Ciemne okienko", "Nieruchome okienko izolatki z siatką, powolny najazd; dwa bliki oczu przez chwilę.",
       2.9, "cut", "Cisza", 0),
      ("extreme-close-up", "Twarz w szybie", "Uderzenie twarzą w szybę (2,9 s) i gwałtowny najazd. Głowa się przekrzywia, "
       "nie mruga, dłoń zsuwa się po szybie, oddech paruje. Od 1,5 s szybki najazd +25%. Żuchwa w obrębie okienka.", 2.7, "smash-cut", "Uderzenie w szybę, potem jego powolny oddech", 1)],
     [("Coś w ciemności", "Budować oczekiwanie w ciszy.", 4, 6, "W izolatce ktoś jest.", "Sanitariusz zagląda.", "Cisza", "slow-burn"),
      ("Pan Henryk nie mruga", "Szok i nienaturalny bezruch.", 6, 8, "Pacjent zachowuje się jak nieżywy, ale oddycha.",
       "Sanitariusz widzi, że Henryk jest zmieniony.", "Uderzenie w szybę", "jumpscare")]),
    (1, 17.6, 5.8, "Drzwi za mną",
     "Zbliżenie na twarz sanitariusza. Wzrok znudzony błądzi w dół; za plecami skrzypią drzwi. Oczy w lewo, zastyga, "
     "jedno powolne mrugnięcie, wstrzymany oddech, znów w lewo — już w panice. Oddech coraz szybszy.",
     "l4.wav", 19.50,
     [("close-up", "Znudzony wzrok", "Twarz sanitariusza, mruga, wzrok w dół. Najazd 1,00→1,18 przez całą scenę.",
       1.2, "cut", "Bzyczenie świetlówek", 0),
      ("reaction", "Skrzypnięcie za plecami", "Skrzyp (1,2 s): otwierają się tylko dalsze drzwi po prawej, bliższe zostają "
       "zamknięte; z otwartych wychodzi jeden pacjent. Oczy w lewo, zastyga, mikrosakkady, powolne mrugnięcie, "
       "znów w lewo w panice; oddech wstrzymany, potem szybki.", 4.6, "cut", "Skrzyp drzwi, wstrzymany oddech, gwałtowny wdech", 1)],
     [("Rutyna", "Chwila oddechu przed uderzeniem.", 6, 5, "Sanitariusz jest sam.", "Nie wie, co jest za nim.", "", "anticipation"),
      ("Zrozumienie", "Widz razem z bohaterem dociera do prawdy.", 5, 9, "Drzwi za nim są otwarte.",
       "Właśnie to zrozumiał.", "Skrzyp drzwi", "anticipation")]),
    (1, 23.4, 4.1, "Wszystkie",
     "Plan ogólny korytarza: wszystkie drzwi sal otwarte. Pacjenci wychodzą z sal, najpierw stoją i się kołyszą, "
     "potem ruszają — każdy kiedy indziej, ze szarpnięciami. Na „Wszystkie” uderzenie.",
     "l5.wav", 25.40,
     [("wide", "Otwarte drzwi", "Korytarz z otwartymi salami, pacjenci-zombie wychodzą i ruszają nierówno; lekki najazd 1,00→1,05.",
       4.1, "cut", "Narastający chór jęków i uderzenie na „Wszystkie”", 0)],
     [("Wszystkie", "Payoff części 1 — skala zagrożenia.", 9, 10, "Wszyscy pacjenci są zarażeni i wolni.",
       "Sanitariusz jest otoczony.", "Chór jęków, uderzenie", "reveal")]),
    (2, 0.0, 4.4, "Bieg do dyżurki",
     "Sanitariusz biegnie korytarzem w stronę dyżurki na końcu. W połowie potyka się, zapada i odbija w bok. "
     "Mijane: kalendarz i szafka.",
     "p2_l1.wav", 0.50,
     [("tracking", "Ucieczka", "Kamera towarzyszy biegnącemu; potknięcie w 2,75 s. Zombie za nim od 2 s unoszą ręce.",
       4.4, "cut", "Szybkie kroki, oddech", 0)],
     [("Ucieczka", "Otworzyć część 2 akcją.", 7, 8, "Zombie są za nim.", "Biegnie do jedynego zamykanego pokoju.", "Kroki", "chase")]),
    (2, 4.4, 6.6, "Klucz i światło",
     "Dyżurka. Zbliżenie: ręka drży, klucz za pierwszym razem się zacina i odskakuje, za drugim przekręca. "
     "Potem sanitariusz przy włączniku dyszy po biegu; pstryk — gaśnie światło; odwraca głowę do szyby i nasłuchuje.",
     "p2_l2.wav", 6.50,
     [("insert", "Klucz w zamku", "Detal ręki z kluczem: drży, zacina się, odskakuje, za drugim razem przekręca. "
       "Dłoń zasłania dziurkę.",
       2.6, "cut", "Zgrzyt klucza", 0),
      ("medium", "Gaśnie światło", "Dyżurka: drzwi z szybą po prawej, biurko z telefonem. Najpierw sprawdza klamkę — "
       "dwa razy w dół, drzwi zamknięte. Pstryk w 5,1 s — ciemność; głowa do szyby.", 4.0, "cut",
       "Dyszenie, klamka, pstryk włącznika", 1)],
     [("Zamknąć się", "Napięcie w drobnej czynności.", 8, 7, "Zamek może nie zadziałać.", "Musi zamknąć drzwi.", "Klucz", "anticipation"),
      ("Ciemność", "Złudna ulga — schowany.", 7, 5, "Jest bezpieczny… na razie.", "Ukrył się w ciemności.", "Pstryk", "false-relief")]),
    (2, 11.0, 6.0, "Sylwetki za szybą",
     "Sanitariusz skulony pod szybą w drzwiach; za szybą jasny korytarz, w pokoju ciemno. Sylwetki przechodzą, kołysząc się. "
     "Jedna przystaje i powoli przekręca głowę w stronę szyby — nie do końca. Wstrzymuje oddech, ręka na ustach drży.",
     "p2_l3.wav", 11.80,
     [("medium", "Pod szybą", "Sanitariusz pod szybą, wzrok wodzi za sylwetkami; najazd 1,00→1,08. Sylwetka staje w 3,0–4,6 s, "
       "ostatnia przystaje w 5,25–5,8 s. Od 3,4 s łza z jednego oka.",
       6.0, "cut", "Szuranie kroków za drzwiami, wstrzymany oddech", 0)],
     [("Przechodzą obok", "Widz widzi zagrożenie przez szybę.", 5, 8, "Jedna z nich prawie go zauważa.",
       "Patrzy i nie oddycha.", "Szuranie", "slow-burn")]),
    (2, 17.0, 3.6, "Telefon",
     "Stary telefon z tarczą na biurku. Chwila ciszy — i pierwszy dzwonek.",
     "p2_l4.wav", 18.60,
     [("insert", "Stary telefon", "Detal telefonu z tarczą, najazd 1,05→1,15; pierwszy dzwonek w 0,9 s; "
       "w 2,0 s od drgań słuchawka spada na stół.",
       3.6, "cut", "Cisza, potem dzwonek", 0)],
     [("Dzwonek", "Zerwać ciszę dźwiękiem.", 5, 9, "Telefon zdradza, że ktoś jest w dyżurce.", "Nie zdąży go wyciszyć.",
       "Dzwonek telefonu", "rapid-intercut")]),
    (2, 20.6, 5.4, "Wszyscy naraz",
     "Szyba w drzwiach: wszystkie sylwetki stoją. Dzwonek trwa. Głowy odwracają się do szyby nierówno — jedna spóźniona — "
     "białe oczy. Dzwonek milknie. Gaśnie wszystko poza oczami.",
     "p2_l5.wav", 21.10,
     [("pov", "Głowy się odwracają", "Widok z dyżurki przez szybę; od 1,6 s najazd do 1,35. Głowy odwracają się w 1,3 s, "
       "z opóźnieniami 0 / 0,35 / 0,12 / 0,75 s.", 3.9, "cut", "Dzwonek do 2,2 s, potem cisza", 0),
      ("static-hold", "Tylko oczy", "Ciemność; zostają tylko białe oczy w szybie.", 1.5, "dip", "Cisza", 1)],
     [("Wszyscy naraz", "Kulminacja: zostali odkryci.", 8, 10, "Wszyscy wiedzą, gdzie jest.", "Wie, że go widzą.",
       "Dzwonek", "shot-reverse"),
      ("Ciemność", "Zawieszenie zamiast rozwiązania.", 10, 9, "Nie wiemy, co będzie dalej.", "Nie ma dokąd uciec.", "Cisza", "aftermath")]),
]


def build_flow():
    acts = [node("act_1", "Część 1 · Oddział C",
                 "Sanitariusz na nocnym dyżurze odkrywa, że cały oddział C ucichł, a pacjenci się zmienili. 27,5 s."),
            node("act_2", "Część 2 · Dyżurka",
                 "Sanitariusz chowa się w dyżurce; telefon zdradza go przed tłumem pacjentów. 26,0 s.")]
    seqs = [("seq_1a", "act_1", "Cisza na oddziale", "Miejsce, cisza i pan Henryk w izolatce.", [0, 1, 2]),
            ("seq_1b", "act_1", "Otwarte drzwi", "Skrzyp za plecami i otwarte wszystkie sale.", [3, 4]),
            ("seq_2a", "act_2", "Ucieczka i ukrycie", "Bieg, klucz w zamku i zgaszone światło.", [5, 6]),
            ("seq_2b", "act_2", "Za szybą", "Sylwetki mijają drzwi dyżurki.", [7]),
            ("seq_2c", "act_2", "Telefon", "Dzwonek i odwracające się głowy.", [8, 9])]
    sequences, outlines, plans = [], [], {}
    for sid, act, title, desc, idx in seqs:
        sequences.append({**node(sid, title, desc), "actId": act, "seconds": round(sum(SCENES[i][2] for i in idx), 1)})
        for i in idx:
            part, start, dur, stitle, sdesc, vo, vs, shots, beats = SCENES[i]
            oid = f"sc_{i + 1:02d}"
            outlines.append({**node(oid, stitle, sdesc), "sectionId": sid, "seconds": dur})
            bids = [f"{oid}_b{k + 1}" for k in range(len(beats))]
            plans[oid] = {
                "outlineId": oid, "sourceSignature": "", "patternId": beats[0][6], "mode": "manual",
                "notes": f"Render: render{'' if part == 1 else '2'}.py, część {part}, {start:.1f}–{start + dur:.1f} s. "
                         f"Lektor {vo} od {vs - start:.1f} s sceny.",
                "beats": [{"id": b, "title": t, "goal": g, "tensionBefore": tb, "tensionAfter": ta, "viewerKnows": vk,
                           "characterKnows": ck, "soundCue": sc, "patternId": pat}
                          for b, (t, g, tb, ta, vk, ck, sc, pat) in zip(bids, beats)],
                "shots": [{"id": f"{oid}_s{k + 1}", "beatId": bids[beat], "typeId": typ, "title": t, "description": d,
                           "duration": du, "transition": tr, "sound": snd}
                          for k, (typ, t, d, du, tr, snd, beat) in enumerate(shots)]}
    pl = {1: [], 2: []}
    from_render = {1: (HERE / "render.py").read_text(), 2: (HERE / "render2.py").read_text()}
    for part, start, dur, title, desc, vo, vs, *_ in SCENES:
        line = [l for l in from_render[part].splitlines() if f'"{vo}"' in l and l.strip().startswith("(")][0]
        pl[part].append(line.split('"')[3].replace("\\n", " "))
    return {
        "version": 1, "factual": False, "sourceIdeaId": IDEA_ID,
        "bible": {
            "characters": "Narrator — sanitariusz na nocnym dyżurze (krótkie włosy, zarost, latarka), mówi w 1. osobie, głos autora (klon).\n"
                          "Pan Henryk — pacjent izolatki nr 3, pierwszy widoczny „zmieniony”: nie mruga, oddycha.\n"
                          "Pacjenci oddziału C — zombie: kołyszą się, ruszają nierówno, białe oczy.",
            "chronology": "Jedna noc. Część 1: przed szpitalem → korytarz oddziału C → izolatka → odkrycie otwartych drzwi. "
                          "Część 2 zaczyna się sekundy później: ucieczka do dyżurki → ukrycie → telefon.",
            "narration": "Pierwsza osoba, czas przeszły, krótkie zdania, po jednym na scenę; pauzy przed i po kwestii.\n"
                         "Lektor: klon głosu autora (Chatterbox, voice_clone.py), próbka bez pogłosu (studio_clean.py), "
                         "pasmo odbudowane resemble-enhance (studio_lines.py). Wersja EN: FILM_LANG=en, voice/en/.",
            "visuals": "Płaska animacja 2D w PIL z grubym czarnym konturem, który „gotuje się” 8 razy na sekundę. "
                       "Stonowane kolory, chłodny zielonkawy grading, winieta, ziarno, maska światła. Kamera z ręki "
                       "(najazdy, mikrodrgania). Napisy: biały tekst na czarnych boksach. 1280×720, 24 kl./s.",
            "facts": "Fikcja — brak tez do weryfikacji. Historia i postacie są własne.",
            "transitions": "Część 1 kończy się otwartymi drzwiami, część 2 zaczyna od ucieczki. Telefon na biurku "
                           "widoczny w scenie z włącznikiem (zapowiedź), zanim zadzwoni.",
        },
        "master": node("master", "Oddział C",
                       "Nocny dyżur w szpitalu psychiatrycznym przy Leśnej. Zwykle ktoś krzyczy, ale tej nocy cały oddział C "
                       "ucichł. Sanitariusz zagląda do izolatki: pan Henryk uderza twarzą w szybę i nie mruga. Za plecami "
                       "skrzypią drzwi — wszystkie sale są otwarte, pacjenci wychodzą. Sanitariusz ucieka do dyżurki, "
                       "zamyka się na klucz i gasi światło. Przez szybę widzi, jak przechodzą obok. Wtedy dzwoni stary "
                       "telefon — i wszyscy naraz odwracają głowy do szyby. Ciemność, zostają tylko oczy."),
        "acts": acts, "sequences": sequences, "outlines": outlines,
        "scripts": {"act_1": "\n\n".join(pl[1]), "act_2": "\n\n".join(pl[2])},
        "approved": {},
        "reviews": [
            {"id": "rev_audio_echo", "agent": "Produkcja · lektor (pogłos)",
             "verdict": "Naprawione. Echo w narracji pochodziło z pogłosu pokoju w próbce głosu — Chatterbox kopiuje akustykę referencji.",
             "issues": ["Pogłos w nagraniu referencyjnym", "Chatterbox przenosi akustykę próbki na każde zdanie"],
             "suggestions": ["studio_clean.py: resemble-enhance zdejmuje pogłos i szum → probka-studio.wav",
                             "Klonować z probka-studio.wav, nie z oryginału"]},
            {"id": "rev_audio_muffled", "agent": "Produkcja · lektor (zamulenie)",
             "verdict": "Naprawione. Chatterbox prawie nie generuje pasma powyżej ~8 kHz (−52 dB w 8–12 kHz), stąd głos „zza ściany”.",
             "issues": ["Brak wysokich tonów w wyjściu TTS", "afftdn i lowpass 11 kHz w filtrze FX ścinały resztę"],
             "suggestions": ["studio_lines.py: resemble-enhance odbudowuje pasmo w gotowych zdaniach (oryginały w voice-raw/)",
                             "Usunięte afftdn i lowpass z FX w voice_clone.py"]},
            {"id": "rev_en", "agent": "Produkcja · wersja angielska",
             "verdict": "Gotowa. Whisper potwierdza tekst; dwa miejsca z polskim akcentem.",
             "issues": ["l1 „Forest Road” słyszane jako „force road”", "p2_l4 „Then” brzmi jak „than”"],
             "suggestions": ["Na PC z CUDA wygenerować angielskim modelem Chatterbox (--lang en --takes 8 --refs 3)"]},
            {"id": "rev_picture", "agent": "Produkcja · obraz",
             "verdict": "Naprawione: sylwetki w części 2 były widoczne poza szybą drzwi dyżurki.",
             "issues": ["window_view rysował przechodzących także na ścianie"],
             "suggestions": ["Po narysowaniu sylwetek zasłonić ścianę i drzwi prostokątami (render2.py, window_view)"]},
        ],
        "director": {"mode": "manual", "plans": plans, "customPatterns": []},
    }


IDEA_ID = "idea_" + "5a0b1e" + "c0ffee" + "0c00"

if mode == "flow":
    p = call(f"/projects/{PID}")
    dev = p["development"]
    dev.update(topic_area="Krótki (2 × 25 s) animowany horror o apokalipsie zombie w szpitalu psychiatrycznym, w konwencji "
                          "animowanych strasznych historii: gruby kontur, płaskie kolory, narracja w 1. osobie, białe napisy.",
               audience="Widzowie krótkich animowanych horrorów (Shorts/Reels), PL i EN.", target_minutes=1,
               ideas=[{"id": IDEA_ID, "title": "Zombie Psychiatryk — Oddział C",
                       "question": "Co, jeśli w szpitalu, w którym zawsze ktoś krzyczy, nagle zapada cisza?",
                       "angle": "Groza z ciszy i bezruchu, nie z krwi; jeden bohater, jedno miejsce, jedna noc.",
                       "notes": "Film już zrealizowany — ten projekt to jego rozbiór na etapy.", "origin": "manual", "stories": []}])
    p = call(f"/projects/{PID}", {"expected_revision": p["revision"], "changes": {"development": dev}}, "PATCH")
    p = call(f"/projects/{PID}/development/select", {"expected_revision": p["revision"], "idea_id": IDEA_ID})
    signed = subprocess.run(["node", "--experimental-strip-types", str(HERE / "studio_signatures.mjs"), str(FLOW_TYPES)],
                            input=json.dumps(build_flow()), capture_output=True, text=True, check=True).stdout
    p = call(f"/projects/{PID}/flow", {"expected_revision": p["revision"], "flow": json.loads(signed)}, "PUT")
    print("flow zapisany, rewizja", p["revision"], "tytuł:", p["title"])

if mode == "media":
    import wave

    import numpy as np
    sys.path.insert(0, str(HERE))
    import render
    import render2
    tmp = Path(tempfile.mkdtemp())
    # dźwięki bez lektora: audio() z ciszą zamiast nagrań (ta sama długość, więc te same czasy)
    silent = tmp / "silent"
    silent.mkdir()
    for f in (HERE / "voice").glob("*.wav"):
        with wave.open(str(f)) as w:
            params, n = w.getparams(), w.getnframes()
        with wave.open(str(silent / f.name), "w") as w:
            w.setparams(params)
            w.writeframes(np.zeros(n * params.nchannels, np.int16).tobytes())
    render.VOICE_DIR = render2.VOICE_DIR = silent
    render.audio(tmp / "efekty-cz1.wav")
    render2.audio(tmp / "efekty-cz2.wav")

    p = call(f"/projects/{PID}")
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    by_shot = {s["legacy"].get("flow_director_shot_id"): s for s in p["scenes"]}
    clips = []
    outline_start = {}
    for i, (part, start, dur, title, desc, vo, vs, shots, beats) in enumerate(SCENES):
        oid = f"sc_{i + 1:02d}"
        offset = 0.0
        for k, (typ, t, d, du, tr, snd, beat) in enumerate(shots):
            scene = by_shot[f"{oid}_s{k + 1}"]
            outline_start.setdefault(oid, scene["start"])
            clip = tmp / f"{oid}_s{k + 1}.mp4"
            src = HERE / ("zombie-psychiatryk.mp4" if part == 1 else "zombie-psychiatryk-2.mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start + offset:.3f}", "-i", str(src),
                            "-t", f"{du:.3f}", "-an", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(clip)], check=True)
            scene["asset_id"] = upload(clip, f"{oid}_s{k + 1} {t}.mp4")
            scene["mode"], scene["animation"], scene["description"] = "upload", "static", d
            if offset <= vs - start < offset + du:
                text = [l for l in (HERE / ("render.py" if part == 1 else "render2.py")).read_text().splitlines()
                        if f'"{vo}"' in l and l.strip().startswith("(")][0].split('"')[3].replace("\\n", " ")
                scene["narration"] = text
                scene["voice_asset_id"] = upload(HERE / "voice" / vo, f"lektor {vo}")
                clips.append({"track_id": "a1", "asset_id": scene["voice_asset_id"], "scene_id": scene["id"],
                              "title": f"Lektor · {text}", "start": outline_start[oid] + round((vs - start) * fps),
                              "src": HERE / "voice" / vo})
            offset += du
    rev = call(f"/projects/{PID}")["revision"]  # wgrane materiały podbiły rewizję
    p = call(f"/projects/{PID}", {"expected_revision": rev, "changes": {"scenes": p["scenes"]}}, "PATCH")
    for scene in p["scenes"]:
        p = call(f"/projects/{PID}/scenes/{scene['id']}/to-timeline", {"expected_revision": p["revision"]})
    ops = []
    for c in clips:
        with wave.open(str(c.pop("src"))) as w:
            c["duration"] = max(1, round(w.getnframes() / w.getframerate() * fps))
        ops.append({"type": "add_clip", "clip": c})
    part2 = sum(round(shot[3] * fps) for s in SCENES if s[0] == 1 for shot in s[7])
    for n, start in ((1, 0), (2, part2)):
        f = tmp / f"efekty-cz{n}.wav"
        aid = upload(f, f"efekty i muzyka — część {n} (bez lektora).wav")
        with wave.open(str(f)) as w:
            ops.append({"type": "add_clip", "clip": {"track_id": "a3", "asset_id": aid, "title": f"Efekty · część {n}",
                                                     "start": start, "duration": round(w.getnframes() / w.getframerate() * fps)}})
    p = call(f"/projects/{PID}/edits", {"expected_revision": call(f"/projects/{PID}")["revision"], "operations": ops})
    for f in ("zombie-psychiatryk-calosc-lekki.mp4", "zombie-psychiatryk-calosc-en-lekki.mp4"):  # lekkie kopie, pełne mają po 87 MB
        upload(HERE / f, f"gotowy render · {f}")
    p = call(f"/projects/{PID}")
    print("ujęcia z materiałem:", sum(bool(s["asset_id"]) for s in p["scenes"]), "/", len(p["scenes"]),
          "| klipy na osi:", len(p["sequence"]["clips"]), "| materiały:", len(p["assets"]))

if mode == "update":
    import math
    import wave

    import numpy as np
    sys.path.insert(0, str(HERE))
    import render
    import render2
    tmp = Path(tempfile.mkdtemp())
    CACHE = Path(tempfile.gettempdir()) / "zombie-psychiatryk-ujecia"
    CACHE.mkdir(exist_ok=True)
    silent = tmp / "silent"
    silent.mkdir()
    for f in (HERE / "voice").glob("*.wav"):
        with wave.open(str(f)) as w:
            params, n = w.getparams(), w.getnframes()
        with wave.open(str(silent / f.name), "w") as w:
            w.setparams(params)
            w.writeframes(np.zeros(n * params.nchannels, np.int16).tobytes())
    render.VOICE_DIR = render2.VOICE_DIR = silent
    render.audio(tmp / "efekty-cz1.wav")
    render2.audio(tmp / "efekty-cz2.wav")

    p = call(f"/projects/{PID}")
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    by_shot = {s["legacy"].get("flow_director_shot_id"): s for s in p["scenes"]}
    clips = {c["scene_id"]: c for c in p["sequence"]["clips"] if c["track_id"] == "v1" and c.get("scene_id")}
    voices = {c["scene_id"]: c for c in p["sequence"]["clips"] if c["track_id"] == "a1" and c.get("scene_id")}
    ops, cursor = [], 0
    for i, (part, start, dur, title, desc, vo, vs, shots, beats) in enumerate(SCENES):
        oid = f"sc_{i + 1:02d}"
        outline_start, offset = cursor, 0.0
        frame_fn = render.frame if part == 1 else render2.frame
        for k, (typ, t, d, du, tr, snd, beat) in enumerate(shots):
            scene = by_shot[f"{oid}_s{k + 1}"]
            # same ujęcie, bez dźwięku i bez eksportu filmu — prosto z klatek renderu
            clip = CACHE / f"{oid}_s{k + 1}.mp4"
            first = round((start + offset) * render.FPS)
            fresh = clip.exists() and clip.stat().st_mtime > max((HERE / f).stat().st_mtime for f in ("render.py", "render2.py"))
            if not fresh:  # ujęcie wyrenderowane z bieżącej wersji rysunków zostaje z poprzedniego uruchomienia
                proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                         "-s", f"{render.W}x{render.H}", "-r", str(render.FPS), "-i", "-", "-c:v", "libx264",
                                         "-crf", "20", "-pix_fmt", "yuv420p", str(clip)], stdin=subprocess.PIPE)
                # klatki renderu muszą pokryć całe ujęcie na osi montażu (inne kl./s)
                for f in range(first, first + math.ceil(round(du * fps) / fps * render.FPS - 1e-9)):
                    proc.stdin.write(frame_fn(f / render.FPS).tobytes())
                proc.stdin.close()
                if proc.wait():
                    raise SystemExit(f"ffmpeg: {clip}")
            scene["asset_id"] = upload(clip, f"{oid}_s{k + 1} {t}.mp4")
            scene["description"] = scene["prompt"] = d
            scene["start"], scene["duration"] = cursor, round(du * fps)
            ops.append({"type": "update_clip", "clip_id": clips[scene["id"]]["id"],
                        "changes": {"asset_id": scene["asset_id"], "start": cursor, "duration": scene["duration"]}})
            if scene["id"] in voices:
                ops.append({"type": "update_clip", "clip_id": voices[scene["id"]]["id"],
                            "changes": {"start": outline_start + round((vs - start) * fps)}})
            cursor += scene["duration"]
            offset += du
            print(f"{oid}_s{k + 1} {t}: {du:.1f} s", flush=True)
        if i == 4:
            part2 = cursor
    for n, start in ((1, 0), (2, part2)):
        f = tmp / f"efekty-cz{n}.wav"
        aid = upload(f, f"efekty i muzyka — część {n} (bez lektora).wav")
        fx = next(c for c in p["sequence"]["clips"] if c["track_id"] == "a3" and c["title"] == f"Efekty · część {n}")
        with wave.open(str(f)) as w:
            ops.append({"type": "update_clip", "clip_id": fx["id"], "changes": {
                "asset_id": aid, "start": start, "duration": round(w.getnframes() / w.getframerate() * fps)}})
    # najpierw oś (nowy materiał razem z nową długością), potem ujęcia — inaczej klip byłby dłuższy od starego pliku
    scenes = p["scenes"]
    p = call(f"/projects/{PID}/edits", {"expected_revision": call(f"/projects/{PID}")["revision"], "operations": ops})
    p = call(f"/projects/{PID}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
    print("ujęcia podmienione:", len(SCENES and by_shot), "| długość montażu:", cursor / fps, "s | rewizja", p["revision"])
