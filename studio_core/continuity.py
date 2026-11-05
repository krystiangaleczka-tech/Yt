"""Księga świata i deterministyczna kontrola ciągłości planu filmu (``legacy.production_flow``).

Dane siedzą w planie filmu obok aktów i reżyserii:

- ``world``        — księga świata: miejsca, postacie, rekwizyty, zasoby, zasady świata w czasie, zdarzenia,
                     wątki (zasiew → wskazówki → rozwiązanie), zakazane wcześniej zdania (spoilery), decyzje;
- ``book``         — warsztat filmu: jak powstają ujęcia i sekwencje (narzędzia, pliki, kolejność pracy);
- ``unitReviews``  — recenzja każdej jednostki filmu (akt = dzień) z podpisem treści, więc zmiana ją unieważnia;
- ``log``          — dziennik pracy.

Odwołanie do ujęcia ma postać ``dNN_KK``: jednostka (akt w kolejności filmu, od 1) i numer ujęcia w niej (od 1).
``sNN_KK`` to zdanie KK scenariusza jednostki NN — dla jednostek, których ujęcia jeszcze nie powstały (liczy się kolejność).
Kotwica ``dNN_KK~słowo`` pilnuje, że odwołanie nadal wskazuje to ujęcie: tekst ujęcia musi zawierać słowo (po wstawieniu
ujęcia numery się przesuwają — wtedy kontrola to zgłasza, zamiast po cichu wskazywać inne ujęcie).
Pierwsze ujęcia aktu można oddać prologowi (``world.prologue = {"1": 14}`` → ``d00_01…d00_14``).
Odwołania do jednostek bez planu reżyserskiego są dozwolone (plan przyszłych dni) — wtedy liczy się tylko kolejność.

Kontrola nie używa AI i niczego nie zmienia; zwraca raport. Waga: 3 — psuje logikę historii, 2 — widz wyłapie,
1 — drobne albo informacja.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import re

REF = re.compile(r"^([ds])(\d{2,3})_(\d{2,3})(?:~(.+))?$")
VOICE = re.compile(r"„[^”]+”")
DEFAULT_TEMPO = {"minSeconds": 0, "maxSeconds": 0, "maxVoiceShare": 0.85}
CHECK_KEYS = ("scenario", "chronology", "beats", "tempo", "narration", "continuity", "frames")


def _chosen(node):
    if not isinstance(node, dict):
        return None
    return next((v for v in node.get("variants", []) if v.get("id") == node.get("selected")), None)


def _digest(value) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return "u1:" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def parse_ref(ref):
    m = REF.match(str(ref or "").strip())
    return (int(m.group(2)), int(m.group(3))) if m else None


def plain_ref(ref):
    return str(ref or "").split("~")[0]


def fmt_ref(unit, k):
    return f"d{unit:02d}_{k:02d}"


def units(flow: dict) -> list[dict]:
    """Jednostki filmu (akty) z ujęciami w kolejności: sekwencje → sceny → ujęcia planu reżyserskiego."""
    world = flow.get("world") or {}
    prologue = {int(k): int(v) for k, v in (world.get("prologue") or {}).items() if str(k).isdigit()}
    plans = (flow.get("director") or {}).get("plans") or {}
    sequences, outlines = flow.get("sequences") or [], flow.get("outlines") or []
    result, prolog_shots = [], []
    for n, act in enumerate(flow.get("acts") or [], start=1):
        shots, missing = [], []
        for section in (s for s in sequences if s.get("actId") == act.get("id")):
            for outline in (o for o in outlines if o.get("sectionId") == section.get("id")):
                plan = plans.get(outline.get("id"))
                if not plan or not plan.get("shots"):
                    missing.append(outline.get("id"))
                    continue
                for shot in plan["shots"]:
                    shots.append({"id": shot.get("id", ""), "outlineId": outline.get("id"), "title": shot.get("title", ""),
                                  "description": shot.get("description", ""), "sound": shot.get("sound", ""),
                                  "duration": float(shot.get("duration") or 0), "typeId": shot.get("typeId", "")})
        skip = prologue.get(n, 0)
        if skip:
            prolog_shots, shots = shots[:skip], shots[skip:]
        for k, shot in enumerate(shots, start=1):
            shot["ref"] = fmt_ref(n, k)
        chosen = _chosen(act) or {}
        result.append({"unit": n, "actId": act.get("id"), "title": chosen.get("title", ""), "shots": shots,
                       "missingPlans": missing, "script": (flow.get("scripts") or {}).get(act.get("id"), "")})
    if prolog_shots:
        for k, shot in enumerate(prolog_shots, start=1):
            shot["ref"] = fmt_ref(0, k)
        result.insert(0, {"unit": 0, "actId": "", "title": "Prolog", "shots": prolog_shots, "missingPlans": [], "script": ""})
    return result


def _text(shot) -> str:
    return " ".join(str(shot.get(k, "")) for k in ("title", "description", "sound"))


def _spoken(shot) -> str:
    sound = str(shot.get("sound", ""))
    if sound.startswith("L:"):
        return sound[2:]
    return " ".join(VOICE.findall(sound))


def _refs_in(value):
    """Wszystkie odwołania dNN_KK w dowolnej strukturze księgi."""
    if isinstance(value, str):
        return [value] if parse_ref(value) else []
    if isinstance(value, dict):
        return [r for v in value.values() for r in _refs_in(v)]
    if isinstance(value, list):
        return [r for v in value for r in _refs_in(v)]
    return []


class _Report:
    def __init__(self):
        self.issues = []

    def add(self, severity, rule, message, ref="", unit=None, hint=""):
        pos = parse_ref(ref)
        self.issues.append({"severity": severity, "rule": rule, "message": message, "ref": ref,
                            "unit": unit if unit is not None else (pos[0] if pos else None), "hint": hint})


def check(flow: dict) -> dict:
    """Raport kontroli ciągłości całego planu filmu."""
    world = flow.get("world") or {}
    tempo = {**DEFAULT_TEMPO, **(world.get("tempo") or {})}
    us = units(flow)
    by_unit = {u["unit"]: u for u in us}
    shot_by_ref = {s["ref"]: s for u in us for s in u["shots"]}
    rep = _Report()

    def key(ref):
        return parse_ref(ref) or (10 ** 6, 0)

    def known(ref, what):
        pos = parse_ref(ref)
        if not pos:
            rep.add(2, "odwołanie", f"{what}: „{ref}” nie jest odwołaniem do ujęcia (dNN_KK) ani zdania scenariusza (sNN_KK)")
            return False
        if str(ref).startswith("s"):
            return True
        anchor = REF.match(str(ref).strip()).group(4)
        plain = str(ref).split("~")[0]
        u = by_unit.get(pos[0])
        if anchor and u and u["shots"] and plain in shot_by_ref and anchor.lower() not in _text(shot_by_ref[plain]).lower():
            rep.add(2, "odwołanie", f"{what}: {plain} nie zawiera „{anchor}” — numer ujęcia się przesunął?", plain)
            return False
        u = by_unit.get(pos[0])
        if u and u["shots"] and str(ref).split("~")[0] not in shot_by_ref:
            rep.add(2, "odwołanie", f"{what}: ujęcie {ref} nie istnieje (jednostka ma {len(u['shots'])} ujęć)", ref)
            return False
        return True

    # --- wątki: zasiew → wskazówki → rozwiązanie
    for th in world.get("threads") or []:
        title = th.get("title") or th.get("id", "wątek")
        setup, clues, payoff = th.get("setup") or [], th.get("clues") or [], th.get("payoff") or []
        for r in setup + clues + payoff:
            known(r, f"wątek „{title}”")
        if payoff and not setup:
            rep.add(3, "wątek", f"„{title}”: rozwiązanie bez zasiewu na ekranie", payoff[0],
                    hint="Dodaj ujęcie, które wcześniej pokazuje to, co rozwiązanie wykorzystuje.")
        if setup and payoff and min(map(key, payoff)) < min(map(key, setup)):
            rep.add(3, "wątek", f"„{title}”: rozwiązanie ({min(payoff, key=key)}) jest przed zasiewem ({min(setup, key=key)})",
                    min(payoff, key=key))
        for c in clues:
            if setup and key(c) < min(map(key, setup)):
                rep.add(2, "wątek", f"„{title}”: wskazówka {c} jest przed zasiewem", c)
            if payoff and key(c) > max(map(key, payoff)):
                rep.add(2, "wątek", f"„{title}”: wskazówka {c} jest po rozwiązaniu", c)
        if setup and not payoff and not th.get("open"):
            rep.add(1, "wątek", f"„{title}”: zasiew bez rozwiązania (oznacz wątek jako otwarty albo dopisz rozwiązanie)",
                    setup[0])

    # --- rekwizyty: nic nie jest użyte przed zasianiem
    for prop in world.get("props") or []:
        name, seeded, uses = prop.get("name") or prop.get("id"), prop.get("seeded", ""), prop.get("uses") or []
        for r in ([seeded] if seeded else []) + uses:
            known(r, f"rekwizyt „{name}”")
        if uses and not seeded:
            rep.add(3, "rekwizyt", f"„{name}” jest użyty, ale nigdzie wcześniej nie pokazany", min(uses, key=key),
                    hint="Zasiej go w ujęciu przed pierwszym użyciem.")
        for u in uses:
            if seeded and key(u) < key(seeded):
                rep.add(3, "rekwizyt", f"„{name}” użyty w {u}, a pokazany dopiero w {seeded}", u)

    # --- zasady świata (przedziały) i zdarzenia, które ich wymagają
    rules = {r.get("id"): r for r in world.get("rules") or []}

    def active(rule_id, at):
        rule = rules.get(rule_id)
        if not rule:
            return None
        start, end = rule.get("from", ""), rule.get("to", "")
        return (not start or key(start) <= key(at)) and (not end or key(at) < key(end))

    for ev in world.get("events") or []:
        at, note = ev.get("at", ""), ev.get("note", "zdarzenie")
        if not known(at, f"zdarzenie „{note}”"):
            continue
        for rid in ev.get("needs") or []:
            state = active(rid, at)
            if state is None:
                rep.add(2, "zasada", f"zdarzenie „{note}” wymaga nieznanej zasady „{rid}”", at)
            elif not state:
                rep.add(3, "zasada", f"„{note}” — w tej chwili nie obowiązuje: {rules[rid].get('name', rid)}", at,
                        hint=rules[rid].get("note", ""))
        for rid in ev.get("needsOff") or []:
            if active(rid, at):
                rep.add(3, "zasada", f"„{note}” — sprzeczne z: {rules[rid].get('name', rid)}", at, hint=rules[rid].get("note", ""))

    # --- obsada w grupie i zasoby (bilans dzień po dniu)
    def party(unit):
        n = 0
        for ch in world.get("characters") or []:
            if not ch.get("party"):
                continue
            j, l = parse_ref(ch.get("joins", "")), parse_ref(ch.get("leaves", ""))
            if (not j or j[0] <= unit) and (not l or l[0] > unit):
                n += 1
        return n

    last_unit = max([u["unit"] for u in us] + [p[0] for p in map(parse_ref, _refs_in(world)) if p] + [0])
    for res in world.get("resources") or []:
        name, per, amount = res.get("name") or res.get("id"), float(res.get("perPersonDay") or 0), float(res.get("start") or 0)
        changes = sorted(res.get("changes") or [], key=lambda c: key(c.get("at", "")))
        claims = sorted(res.get("claims") or [], key=lambda c: key(c.get("at", "")))
        first = min([key(c.get("at", ""))[0] for c in changes + claims] or [1])
        dry = False
        for unit in range(first, last_unit + 1):
            def apply(upto):
                nonlocal amount
                for c in [c for c in changes if key(c.get("at", ""))[0] == unit and not c.get("_done")]:
                    if upto is None or key(c["at"]) <= upto:
                        c["_done"] = True
                        amount = amount * (1 + float(c["share"])) if "share" in c else amount + float(c.get("delta") or 0)
            for cl in [c for c in claims if key(c.get("at", ""))[0] == unit]:
                apply(key(cl["at"]))
                need = per * party(unit)
                days = amount / need if need else float("inf")
                said = float(cl.get("days") or 0)
                if need and abs(days - said) > max(0.5, 0.25 * said):
                    rep.add(3, "zasób", f"{name}: w {cl['at']} pada „{cl.get('note') or said}” ({said:g} dni), a z bilansu "
                            f"wychodzi {days:.1f} dnia ({amount:g} {res.get('unit', '')} dla {party(unit)} osób)", cl["at"],
                            hint="Liczby w kwestiach biorą się z księgi zasobów, nie z głowy.")
            apply(None)
            amount -= per * party(unit)
            if amount < -1e-6:
                if not dry:  # brak zgłaszamy raz — do następnej dostawy
                    rep.add(3, "zasób", f"{name}: bilans spada poniżej zera w dniu {unit} ({amount:.1f} {res.get('unit', '')}) "
                            f"i nic go nie uzupełnia", unit=unit,
                            hint="Dopisz dostawę albo zmniejsz zużycie, zanim historia na tym oprze się dalej.")
                dry, amount = True, 0.0
            elif amount > 1e-6:
                dry = False
        for c in changes:
            c.pop("_done", None)

    # --- imiona: postać z listą ujęć, w których wolno ją nazwać
    for ch in world.get("characters") or []:
        allowed = ch.get("namedIn") or []
        if not allowed:
            continue
        names = [ch.get("name", "")] + list(ch.get("aliases") or [])
        pat = re.compile(r"\b(" + "|".join(re.escape(n) for n in names if n) + r")\b")
        for ref, shot in shot_by_ref.items():
            if pat.search(_text(shot)) and not any(fnmatch.fnmatch(ref, a) for a in allowed):
                rep.add(3, "imię", f"Imię „{ch.get('name')}” należy do postaci: {ch.get('role', '')}; tu nazwano tak kogoś innego "
                        f"albo za wcześnie", ref, hint="Jedno imię = jedna postać (księga świata → postacie).")

    # --- spoilery: zdanie, którego nie wolno powiedzieć przed danym ujęciem
    for sp in world.get("spoilers") or []:
        try:
            pat = re.compile(sp.get("pattern", ""), re.I)
        except re.error:
            rep.add(2, "spoiler", f"Błędny wzorzec: {sp.get('pattern')}")
            continue
        limit = sp.get("notBefore", "")
        for ref, shot in shot_by_ref.items():
            if limit and key(ref) < key(limit) and pat.search(_spoken(shot)):
                rep.add(3, "wiedza", f"Kwestia zdradza za wcześnie: {sp.get('why') or sp.get('pattern')} (wolno od {limit})", ref,
                        hint="Lektor i postacie mówią tylko to, co już wiedzą (księga świata → spoilery).")

    # --- rytm jednostki
    summary = []
    for u in us:
        shots = u["shots"]
        seconds = round(sum(s["duration"] for s in shots), 2)
        voiced = [s for s in shots if _spoken(s).strip()]
        share = len(voiced) / len(shots) if shots else 0.0
        equal = [s["ref"] for a, s in zip(shots, shots[1:]) if abs(a["duration"] - s["duration"]) < 0.25]
        if u["unit"] > 0 and shots:
            lo, hi = float(tempo.get("minSeconds") or 0), float(tempo.get("maxSeconds") or 0)
            if (lo and seconds < lo) or (hi and seconds > hi):
                rep.add(2, "tempo", f"{u['title'] or 'jednostka'} trwa {seconds:g} s — poza zakresem {lo:g}–{hi:g} s", unit=u["unit"])
            if len(equal) >= 3:
                rep.add(1, "tempo", f"{len(equal)} ujęć ma tę samą długość co poprzednie: {', '.join(equal[:6])}", unit=u["unit"])
            if share > float(tempo.get("maxVoiceShare") or 1):
                rep.add(1, "narracja", f"Lektor/dialog w {share:.0%} ujęć — zostaw ciszę reakcjom i detalom", unit=u["unit"])
        if u["missingPlans"]:
            rep.add(1, "plan", f"{len(u['missingPlans'])} scen bez planu reżyserskiego", unit=u["unit"])
        summary.append({"unit": u["unit"], "actId": u["actId"], "title": u["title"], "shots": len(shots), "seconds": seconds,
                        "voiceShare": round(share, 2), "equalNeighbours": len(equal)})

    # --- podpisy jednostek, recenzje i powiązania
    reviews = flow.get("unitReviews") or {}
    links = {}
    for group in ("threads", "props", "rules", "events", "resources", "characters"):
        for item in world.get(group) or []:
            touched = sorted({parse_ref(r)[0] for r in _refs_in(item)})
            for a in touched:
                links.setdefault(a, set()).update(b for b in touched if b != a)
    for s, u in zip(summary, us):
        refs_here = [item for group in world.values() if isinstance(group, list) for item in group
                     if any(parse_ref(r) and parse_ref(r)[0] == u["unit"] for r in _refs_in(item))]
        s["signature"] = _digest({"title": u["title"], "script": u["script"], "shots": u["shots"], "world": refs_here})
        review = reviews.get(u["actId"]) if u["actId"] else None
        if not review:
            s["review"] = "brak"
        elif review.get("signature") != s["signature"]:
            s["review"] = "nieaktualna"
        else:
            s["review"] = review.get("status") or "robocza"
        s["linked"] = sorted(links.get(u["unit"], set()))
        s["issues"] = {str(w): sum(1 for i in rep.issues if i["unit"] == u["unit"] and i["severity"] == w) for w in (3, 2, 1)}
    for s in summary:
        if s["review"] == "nieaktualna":
            for other in summary:
                if other["unit"] in s["linked"] and other["review"] == "zatwierdzona":
                    other.setdefault("impactedBy", []).append(s["unit"])
    rep.issues.sort(key=lambda i: (-i["severity"], i["unit"] if i["unit"] is not None else 999, key(i["ref"]) if i["ref"] else (0, 0)))
    return {"units": summary, "issues": rep.issues,
            "totals": {str(w): sum(1 for i in rep.issues if i["severity"] == w) for w in (3, 2, 1)}}


def unit_signature(flow: dict, act_id: str) -> str:
    report = check(flow)
    found = next((u for u in report["units"] if u["actId"] == act_id), None)
    if not found:
        raise ValueError("Nie ma takiej jednostki filmu")
    return found["signature"]


def timeline_issues(project) -> list[dict]:
    """Dziury i nakładki na ścieżkach obrazu osi montażu (waga 2): widz zobaczy czerń albo dwa klipy naraz."""
    out = []
    rate = (project.sequence.fps_num / project.sequence.fps_den) if project.sequence.fps_den else 30
    for track in (t for t in project.sequence.tracks if t.kind == "video"):
        clips = sorted((c for c in project.sequence.clips if c.track_id == track.id), key=lambda c: c.start)
        if track.id != "v1":
            continue  # wyższe ścieżki to nakładki z założenia
        for a, b in zip(clips, clips[1:]):
            end = a.start + a.duration
            if b.start != end:
                kind = "dziura" if b.start > end else "nakładka"
                out.append({"severity": 2, "rule": "oś", "ref": "", "unit": None, "hint": "Ułóż obraz od nowa (narzędzie filmu) albo popraw w Montażu.",
                            "message": f"{kind} {abs(b.start - end)} kl. na ścieżce {track.id} w {end / rate:.1f} s: "
                                       f"„{a.title[:40]}” → „{b.title[:40]}”"})
    return out
