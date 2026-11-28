"""Gotowość filmu do oddania: kroki produkcji po Ujęciach i Montażu, liczone z danych projektu.

Podręcznik („Nowy film krok po kroku”, kroki 7–13; rozdziały „Lektor” i „Dźwięk”) opisuje, co film musi mieć,
zanim reżyser zrobi render końcowy. Ten moduł niczego nie zmienia i nie używa AI: patrzy na ujęcia, oś montażu,
dziennik, recenzje jednostek i kontrolę ciągłości i mówi, czego brakuje.

Zgoda reżysera na próbkę dźwięku to wpis dziennika ``kind = "próbka dźwięku"`` z polami ``decision``
(``zatwierdzona`` albo ``do poprawy``) i ``quote`` (słowa reżysera); dopisuje go
``POST /api/projects/{id}/gotowosc/probka``. Starsze filmy mają zgodę tylko w opisie wgrania
(„Próbkę zatwierdził reżyser 19.11.2026 („Zatwierdzam, wgraj”)”) — taki opis też się liczy.
"""
from __future__ import annotations

import datetime
import re
import uuid
from pathlib import Path

from . import continuity

READY, MISSING, STALE, WARN, INFO, NA = "gotowe", "brak", "do przeliczenia", "uwagi", "informacja", "nie dotyczy"
BLOCKING = (MISSING, STALE)
TOLERANCE = 0.5  # s: dźwięk krótszy od osi o mniej niż pół sekundy nie psuje końca filmu
SAMPLE_KIND = "próbka dźwięku"
REVIEW_FORMS = {"robocza": ("robocza", "robocze", "roboczych"), "nieaktualna": ("nieaktualna", "nieaktualne", "nieaktualnych"),
                "do poprawy": ("do poprawy",) * 3, "brak": ("bez recenzji",) * 3}
DECISIONS = ("zatwierdzona", "do poprawy")
SCRIPT = re.compile(r"(output/[A-Za-z0-9][A-Za-z0-9._-]*)/studio_film\.py")
APPROVAL_TEXT = re.compile(
    r"(?:[Pp]róbk[ęa](?:\s+\w+){0,2}\s+zatwierdził\w*\s+reżyser\w*|[Rr]eżyser\w*\s+zatwierdził\w*\s+próbkę(?:\s+\w+){0,2})"
    r"\s*(?P<date>\d{1,2}\.\d{1,2}\.\d{4})?(?:[^(„]{0,20}?\(?\s*(?P<quote>„[^”]{1,300}”))?")


def _now() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _tc(seconds: float) -> str:
    seconds = max(0.0, seconds)
    return f"{int(seconds // 60)}:{seconds % 60:04.1f}".replace(".", ",")


def _day(iso: str) -> str:
    try:
        return datetime.datetime.fromisoformat(str(iso)).strftime("%d.%m.%Y")
    except ValueError:
        return str(iso)[:10]


def _valid_day(day: str) -> bool:
    try:
        datetime.datetime.strptime(day, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def _plural(n: int, one: str, few: str, many: str) -> str:
    if n == 1:
        return one
    return few if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else many


def _flow(project) -> dict:
    flow = project.legacy.get("production_flow")
    return flow if isinstance(flow, dict) else {}


def _clips(project, role: str):
    ids = {t.id for t in project.sequence.tracks if t.role == role}
    return [c for c in project.sequence.clips if c.track_id in ids]


def film_end(project) -> int:
    """Koniec filmu w klatkach: ostatni klip obrazu, a bez osi — ostatnie ujęcie."""
    ends = [c.start + c.duration for c in _clips(project, "picture")]
    if not ends:
        ends = [s.start + s.duration for s in project.scenes]
    return max(ends, default=0)


def commands(project, repo: Path | None) -> dict:
    """Polecenia skryptu filmu z warsztatu (``book.files``); bez warsztatu — ogólne nazwy z Podręcznika."""
    files = ((_flow(project).get("book") or {}).get("files") or [])
    paths = [str(f.get("path") or "") for f in files if isinstance(f, dict)]
    script = next((p for p in paths if SCRIPT.fullmatch(p)), "")
    folder = SCRIPT.fullmatch(script).group(1) if script else ""
    text = ""
    if script and repo:
        try:
            text = (repo / script).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""
    run = f"python3 -I {script}" if script else "python3 -I output/<film>/studio_film.py"
    # Starsze filmy wgrywają lektora razem z dźwiękiem (`dzwiek lektor`), nowsze mają osobne `lektor`.
    voice = "dzwiek lektor" if not re.search(r"^def lektor\(", text, re.M) and re.search(r"def dzwiek\(\s*lektor", text) else "lektor"
    sample = f"{folder}/probka_dzwieku.py" if folder else "output/<film>/probka_dzwieku.py"
    missing = []
    if text and not re.search(r"^def dzwiek\(", text, re.M):
        missing.append("dzwiek")
    return {"script": script, "lektor": f"{run} {voice}", "dzwiek": f"{run} dzwiek", "probka": f"python3 -I {sample}",
            "missing": missing}


def _shot(n: int, scene) -> dict:
    return {"nr": n, "sceneId": scene.id, "title": scene.title, "narration": scene.narration.strip()[:160]}


def narration_item(project, cmd: dict) -> dict:
    clips = _clips(project, "narration")
    by_scene, loose = {}, []
    for c in clips:
        (by_scene.setdefault(c.scene_id, []) if c.scene_id else loose).append(c)
    numbered = list(enumerate(project.scenes, start=1))
    voiced = [(n, s) for n, s in numbered if s.narration.strip()]
    base = {"key": "lektor", "title": "Lektor", "chapter": "lektor", "track": "a1"}
    if not voiced:
        return {**base, "state": NA, "summary": "Żadne ujęcie nie ma kwestii lektora.", "todo": "", "command": "", "shots": []}

    def covered(s):
        return s.id in by_scene or any(c.start < s.start + s.duration and s.start < c.start + c.duration for c in loose)

    missing = [_shot(n, s) for n, s in voiced if not covered(s)]
    shifted = [_shot(n, s) for n, s in voiced if any(not s.start <= c.start < s.start + s.duration for c in by_scene.get(s.id, []))]
    orphans = [_shot(n, s) for n, s in numbered if not s.narration.strip() and s.id in by_scene]
    done, total = len(voiced) - len(missing), len(voiced)
    if missing:
        return {**base, "state": MISSING, "shots": missing,
                "summary": f"{done} z {total} kwestii na ścieżce Lektor; brakuje {len(missing)}.",
                "todo": "Nagraj brakujące kwestie klonem głosu (jedno podejście na kwestię, kontrola Whisperem) i wgraj je na "
                        "ścieżkę Lektor. Potem przelicz dźwięk — ujęcia mają długość z prawdziwych kwestii.",
                "command": cmd["lektor"]}
    if shifted or orphans:
        parts = ([f"{len(shifted)} {_plural(len(shifted), 'kwestia stoi', 'kwestie stoją', 'kwestii stoi')} poza swoim ujęciem"] if shifted else []) + \
                ([f"{len(orphans)} {_plural(len(orphans), 'klip gra kwestię', 'klipy grają kwestie', 'klipów gra kwestie')}, "
                  f"których nie ma już w ujęciach"] if orphans else [])
        return {**base, "state": STALE, "shots": shifted + orphans,
                "summary": "Lektor do przeliczenia: " + "; ".join(parts) + ".",
                "todo": "Po zmianie długości albo treści ujęć wgraj lektora od nowa — każda kwestia stanie w swoim ujęciu.",
                "command": cmd["lektor"]}
    return {**base, "state": READY, "shots": [],
            "summary": f"Wszystkie kwestie ({total}) są na ścieżce Lektor, każda w swoim ujęciu.", "todo": "", "command": ""}


def bed_item(project, role: str, cmd: dict) -> dict:
    """Muzyka albo efekty: jeden klip na cały film, który musi pokryć całą oś."""
    key, title, track = {"music": ("muzyka", "Muzyka", "a2"), "effects": ("efekty", "Efekty", "a3")}[role]
    fps = project.sequence.fps_num / project.sequence.fps_den
    end = film_end(project) / fps
    clips = sorted(_clips(project, role), key=lambda c: c.start)
    base = {"key": key, "title": title, "chapter": "dzwiek", "track": track, "command": cmd["dzwiek"],
            "todo": "Po zgodzie na próbkę przelicz dźwięk (efekty.py) i wgraj go skryptem filmu — jeden klip na cały film. "
                    "Po każdej zmianie długości ujęć i po każdej turze poprawek rysunku od nowa."}
    if "dzwiek" in cmd.get("missing", []):
        base["todo"] += (" Skrypt filmu nie ma jeszcze polecenia „dzwiek” — dopisz je według wzoru z „Bonnie and Clyde” "
                         "(output/bonnie-i-clyde/studio_film.py, funkcja dzwiek).")
    if not clips:
        return {**base, "state": MISSING, "summary": f"Ścieżka {title} jest pusta.", "coverage": None}
    spans = []
    for c in clips:
        a, b = c.start / fps, (c.start + c.duration) / fps
        if spans and a <= spans[-1][1] + TOLERANCE:
            spans[-1][1] = max(spans[-1][1], b)
        else:
            spans.append([a, b])
    first, last = spans[0][0], max(b for _, b in spans)
    holes = [(spans[i][1], spans[i + 1][0]) for i in range(len(spans) - 1)]
    if first > TOLERANCE:
        holes.insert(0, (0.0, first))
    coverage = {"start": round(first, 2), "end": round(last, 2), "film": round(end, 2), "clips": len(clips)}
    muted = any(t.muted for t in project.sequence.tracks if t.role == role)
    if last < end - TOLERANCE:
        state, summary = STALE, (f"{title} kończy się w {_tc(last)}, a film trwa {_tc(end)} — dźwięk do przeliczenia "
                                 f"(zwykle po zmianie długości ujęć).")
    elif last > end + TOLERANCE:
        state, summary = STALE, (f"{title} trwa dłużej niż film ({_tc(last)} przy {_tc(end)}) — dźwięk do przeliczenia "
                                 f"(zwykle po zmianie długości ujęć).")
    elif holes:
        state, summary = STALE, ("Bez dźwięku: " + ", ".join(f"{_tc(a)}–{_tc(b)}" for a, b in holes[:4])
                                 + " — dźwięk do przeliczenia.")
    else:
        state = WARN if muted else READY
        summary = (f"Jeden klip od {_tc(first)} do {_tc(last)} — pokrywa cały film." if len(clips) == 1 else
                   f"{len(clips)} {_plural(len(clips), 'klip', 'klipy', 'klipów')} od {_tc(first)} do {_tc(last)} — "
                   f"{_plural(len(clips), 'pokrywa', 'pokrywają', 'pokrywa')} cały film.")
    if muted:
        summary += " Ścieżka jest wyciszona w Montażu."
    return {**base, "state": state, "summary": summary, "coverage": coverage,
            **({"todo": "", "command": ""} if state == READY else {})}


def sample_decision(flow: dict) -> dict | None:
    """Ostatnia decyzja reżysera o próbce dźwięku: wpis „próbka dźwięku” albo zgoda zapisana w opisie wgrania."""
    for e in reversed(flow.get("log") or []):
        if not isinstance(e, dict):
            continue
        if e.get("kind") == SAMPLE_KIND and e.get("decision") in DECISIONS:
            return {"decision": e["decision"], "quote": str(e.get("quote") or ""), "at": str(e.get("at") or ""),
                    "who": str(e.get("who") or ""), "source": "wpis", "entryId": e.get("id", "")}
        found = APPROVAL_TEXT.search(f"{e.get('summary', '')} {e.get('details', '')}")
        if found:
            day = found.group("date")
            at = (datetime.datetime.strptime(day, "%d.%m.%Y").date().isoformat() if day and _valid_day(day) else str(e.get("at") or ""))
            return {"decision": "zatwierdzona", "quote": (found.group("quote") or "").strip("„”"), "at": at,
                    "who": "reżyser", "source": "opis", "entryId": e.get("id", "")}
    return None


def sample_item(project, cmd: dict) -> dict:
    found = sample_decision(_flow(project))
    base = {"key": "probka", "title": "Próbka dźwięku zatwierdzona", "chapter": "dzwiek", "decision": found,
            "todo": "Zrób próbkę: fragmenty filmu z pełnym miksem i sam dźwięk (tematy, nowe efekty, głosy). Wyślij reżyserowi "
                    "do odsłuchu, a jego odpowiedź zapisz tutaj („Zgoda reżysera na próbkę”). Dźwięk wgrywa się dopiero po zgodzie.",
            "command": cmd["probka"]}
    if found and found["decision"] == "zatwierdzona":
        said = f": „{found['quote']}”" if found["quote"] else ""
        where = " (zgoda zapisana w opisie wgrania w dzienniku)" if found["source"] == "opis" else ""
        return {**base, "state": READY, "summary": f"Zatwierdzona {_day(found['at'])}{said}{where}.", "todo": "", "command": ""}
    sound = bool(_clips(project, "music") or _clips(project, "effects"))
    if found:
        summary = f"Reżyser chce poprawek ({_day(found['at'])})" + (f": „{found['quote']}”." if found["quote"] else ".")
    else:
        summary = "W dzienniku nie ma zgody reżysera na próbkę dźwięku."
        if sound:
            summary += " Dźwięk jest już wgrany — zapisz zgodę, jeśli padła, albo wyślij próbkę do odsłuchu."
    return {**base, "state": MISSING, "summary": summary}


def sample_entry(body: dict) -> dict:
    """Wpis dziennika z decyzją reżysera o próbce dźwięku (z cytatem — Podręcznik: „wpis w dzienniku z cytatem zgody”)."""
    decision = str(body.get("decision") or "")
    if decision not in DECISIONS:
        raise ValueError("Decyzja o próbce: zatwierdzona albo do poprawy")
    quote = str(body.get("quote") or "").strip().strip("„”\"").strip()[:1000]
    if not quote:
        raise ValueError("Wpisz słowa reżysera — cytat zgody albo uwagi do próbki")
    sample = str(body.get("sample") or "").strip()[:300]
    details = str(body.get("details") or "").strip()[:20000]
    return {"id": uuid.uuid4().hex[:12], "at": _now(), "who": str(body.get("who") or "reżyser").strip()[:200] or "reżyser",
            "unit": None, "kind": SAMPLE_KIND, "summary": f"Próbka dźwięku {decision}: „{quote}”"[:2000],
            "details": "\n".join(x for x in (f"Próbka: {sample}" if sample else "", details) if x),
            "files": [str(x)[:300] for x in (body.get("files") or []) if str(x).strip()][:100],
            "decision": decision, "quote": quote}


def reviews_item(project, report: dict) -> dict:
    units = [u for u in report["units"] if u.get("actId")]
    rows = [{"unit": u["unit"], "actId": u["actId"], "title": u["title"], "review": u["review"]} for u in units]
    base = {"key": "recenzje", "title": "Recenzje aktów", "chapter": "recenzja", "units": rows, "command": "",
            "todo": "Przejdź listę kontrolną każdej jednostki (Continuity Editor → Recenzje jednostek). Zatwierdza reżyser."}
    if not units:
        return {**base, "state": MISSING, "summary": "Plan filmu nie ma jeszcze aktów do recenzji."}
    approved = sum(1 for u in units if u["review"] == "zatwierdzona")
    if approved == len(units):
        return {**base, "state": READY, "summary": f"Wszystkie jednostki zatwierdzone ({len(units)}).", "todo": ""}
    counts = {}
    for u in units:
        if u["review"] != "zatwierdzona":
            counts[u["review"]] = counts.get(u["review"], 0) + 1
    rest = ", ".join(f"{n} {_plural(n, *REVIEW_FORMS.get(label, (label,) * 3))}" for label, n in counts.items())
    stale = " Nieaktualna recenzja = jednostka zmieniła się po recenzji." if "nieaktualna" in counts else ""
    return {**base, "state": MISSING, "summary": f"Zatwierdzone {approved} z {len(units)}; {rest}.{stale}"}


def continuity_item(report: dict) -> dict:
    totals = {w: int(report["totals"].get(str(w), 0)) for w in (3, 2, 1)}
    worst = [i for i in report["issues"] if i["severity"] == max((w for w in (3, 2) if totals[w]), default=0)][:5]
    base = {"key": "ciaglosc", "title": "Kontrola ciągłości", "chapter": "sekwencja", "totals": totals, "command": "",
            "issues": [{"severity": i["severity"], "rule": i["rule"], "ref": i["ref"].split("~")[0], "message": i["message"]} for i in worst],
            "todo": "Popraw księgę świata albo ujęcia (Continuity Editor → Kontrola) i sprawdź jeszcze raz."}
    small = f" Drobnych: {totals[1]}." if totals[1] else ""
    if totals[3]:
        return {**base, "state": MISSING, "summary": f"Błędy wagi 3 (psują logikę historii): {totals[3]}; wagi 2: {totals[2]}.{small}"}
    if totals[2]:
        return {**base, "state": WARN, "summary": f"Zero błędów wagi 3; uwagi wagi 2 (widz wyłapie): {totals[2]}.{small}"}
    return {**base, "state": READY, "summary": "Zero błędów wagi 3 i 2." + small, "todo": ""}


def render_item(blocking: list[str]) -> dict:
    summary = ("Wszystko gotowe — film czeka na render końcowy reżysera." if not blocking else
               "Najpierw kroki wyżej: " + ", ".join(blocking) + ".")
    return {"key": "render", "title": "Render końcowy", "chapter": "praca", "state": INFO, "command": "",
            "summary": summary,
            "todo": "Render końcowy robi reżyser (pc\\renderuj*.bat), kiedy wszystko w Studio jest gotowe i zatwierdzone."}


def readiness(project, repo: Path | None = None) -> dict:
    """Stan kroków produkcji po Ujęciach i Montażu. Niczego nie zmienia."""
    cmd = commands(project, repo)
    report = continuity.project_check(project)
    items = [continuity_item(report), reviews_item(project, report), narration_item(project, cmd), sample_item(project, cmd),
             bed_item(project, "music", cmd), bed_item(project, "effects", cmd)]
    blocking = [i["title"] for i in items if i["state"] in BLOCKING]
    items.append(render_item(blocking))
    fps = project.sequence.fps_num / project.sequence.fps_den
    return {"ready": not blocking, "blocking": blocking, "items": items, "script": cmd["script"],
            "film": {"seconds": round(film_end(project) / fps, 2), "shots": len(project.scenes), "revision": project.revision}}
