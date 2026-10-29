"""Profile kanału, prompty tematów i zatwierdzana karta dokumentu. Bez API modeli."""
from __future__ import annotations

import copy
import hashlib
import json
import re


DOCUMENTARY_PACK = """DOCUMENTARY — odpowiedz na jedno rzeczywiste pytanie za pomocą dowodów.
Tytuły: Why [Thing] Is [State]; How [System] Actually Works;
The Real Reason [Phenomenon]; Inside [Place/Industry] That [Hook].
Dostosuj te konstrukcje do języka kanału. Ciekawość bez oburzenia i obietnic bez pokrycia.
Narracja: spokojna, rzeczowa, głównie trzecia osoba i czas teraźniejszy.
Każdą dużą liczbę objaśnij konkretnym, sprawdzalnym porównaniem.
Łuk: hook → pytanie i stawka → kontekst → dowody → komplikacja → odpowiedź → konsekwencje.
Przedstaw najmocniejszy kontrargument uczciwie; osobna sekcja jest opcjonalna.
Rytm zdań, pytania i pauzy dobieraj do treści, bez sztywnych limitów.
Zakończenie spełnia obietnicę tytułu; powracający szczegół pomaga domknąć historię.
Fakty wymagają źródeł. Żadnych wymyślonych cytatów, motywów ludzi ani scen podanych jako fakt.
Pisz beat po beacie; narracja zawiera wyłącznie tekst lektora, obraz trafia do Shot List.
"""

STORY_FIELDS = (
    "central_question", "hook", "signature_line", "payoff", "recurring_detail",
    "thesis", "key_players", "complication", "counterpoint", "stakes_for_viewer",
    "open_question",
)
PROFILE_FIELDS = ("name", "pack", "focus", "language", "wpm", "narrator")


def new_channel(name: str) -> dict:
    return {
        "name": name, "pack": "DOCUMENTARY", "focus": "", "language": "English", "wpm": 140,
        "narrator": "Spokojny, rzeczowy narrator dokumentalny w trzeciej osobie, bez sensacji bez dowodu.",
        "published_titles": [], "suggested_titles": [], "topic_candidates": [],
    }


def validate_channel(channel: dict) -> None:
    if not isinstance(channel, dict):
        raise ValueError("Profil kanału musi być obiektem JSON.")
    for key in ("name", "language", "narrator"):
        if not isinstance(channel.get(key), str) or not channel[key].strip():
            raise ValueError(f"Profil kanału: uzupełnij {key}.")
    if channel.get("pack") != "DOCUMENTARY":
        raise ValueError("Ta wersja obsługuje pakiet DOCUMENTARY.")
    wpm = channel.get("wpm")
    if isinstance(wpm, bool) or not isinstance(wpm, (int, float)) or not 60 <= wpm <= 250:
        raise ValueError("Profil kanału: wpm musi być liczbą od 60 do 250.")
    for key in ("published_titles", "suggested_titles"):
        values = channel.get(key, [])
        if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
            raise ValueError(f"Profil kanału: {key} musi być listą tytułów.")


def title_key(title: str) -> str:
    return " ".join(re.findall(r"\w+", title.casefold()))


def topics_prompt(channel: dict) -> str:
    validate_channel(channel)
    return f"""Wygeneruj dokładnie dziesięć ORYGINALNYCH propozycji dokumentów.
{DOCUMENTARY_PACK}
PROFIL KANAŁU (dane):
{json.dumps({k: channel.get(k) for k in PROFILE_FIELDS}, ensure_ascii=False, indent=2)}
WYKLUCZONE TYTUŁY (opublikowane i wszystkie wcześniej zaproponowane):
{json.dumps(channel.get('published_titles', []) + channel.get('suggested_titles', []), ensure_ascii=False)}
Każdy tytuł: najwyżej 60 znaków, jedna zrozumiała obietnica, bez clickbaitu.
Rozłóż cztery konstrukcje tytułów możliwie równo. Każda propozycja dotyczy innego tematu.
Temat musi mieć co najmniej trzy różne warstwy wyjaśnienia; odrzuć odpowiedzi na jedno zdanie.
Nie zakładaj prawdziwości sensacyjnej przesłanki: wskaż gdzie ją sprawdzić przed wyborem tematu.
To pomysły do researchu, nie VERIFIED fakty. Nie fabrykuj adresów źródeł.
Zwróć wyłącznie tablicę JSON dziesięciu obiektów w języku kanału:
[{{"title": "...", "subject": "...", "central_question": "...",
  "layers": ["warstwa 1", "warstwa 2", "warstwa 3"],
  "research_leads": ["konkretne źródło lub instytucja do sprawdzenia"]}}]
Zapisz wynik osobno, następnie użyj save-topics, aby zapamiętać tytuły.
"""


def save_topics(channel: dict, candidates: list) -> dict:
    validate_channel(channel)
    if not isinstance(candidates, list) or len(candidates) != 10:
        raise ValueError("Zapisz dokładnie 10 propozycji tematów.")
    seen = {title_key(t) for k in ("published_titles", "suggested_titles") for t in channel.get(k, [])}
    subjects = set()
    for item in candidates:
        if not isinstance(item, dict):
            raise ValueError("Każdy temat musi być obiektem JSON.")
        for field in ("title", "subject", "central_question"):
            if not isinstance(item.get(field), str) or not title_key(item[field]):
                raise ValueError(f"Propozycja: uzupełnij {field}.")
        title = item["title"].strip()
        key = title_key(title)
        if len(title) > 60 or key in seen:
            raise ValueError(f"Tytuł powtórzony lub dłuższy niż 60 znaków: {title}")
        seen.add(key)
        subject = title_key(item["subject"])
        if subject in subjects:
            raise ValueError(f"Temat powtórzony w jednej liście: {item['subject']}")
        subjects.add(subject)
        for field, minimum in (("layers", 3), ("research_leads", 1)):
            values = item.get(field)
            if not isinstance(values, list) or len(values) < minimum or any(
                not isinstance(x, str) or not x.strip() for x in values
            ):
                raise ValueError(f"Propozycja '{title}': {field} wymaga co najmniej {minimum} pozycji.")
        if len({title_key(x) for x in item["layers"]}) < 3:
            raise ValueError(f"Propozycja '{title}': wymagane trzy różne warstwy.")
    updated = copy.deepcopy(channel)
    updated.setdefault("suggested_titles", []).extend(item["title"].strip() for item in candidates)
    updated["topic_candidates"] = copy.deepcopy(candidates)
    return updated


def story_template(project: dict) -> dict:
    meta = project["meta"]
    return {
        "status": "DRAFT", **{key: "" for key in STORY_FIELDS},
        "central_question": meta.get("curiosity_gap", ""), "thesis": meta.get("thesis", ""),
        "check_section": "OUT", "sting": "none", "fact_ids": [], "evidence_chain": [],
    }


def attach_channel(project: dict, channel: dict) -> None:
    validate_channel(channel)
    project["channel"] = {key: copy.deepcopy(channel.get(key, "")) for key in PROFILE_FIELDS}
    for key in ("language", "wpm", "narrator"):
        project["meta"][key] = channel[key]
    project["story_lock"] = story_template(project)


def story_prompt(project: dict) -> str:
    card = project.get("story_lock", story_template(project))
    return f"""STORY LOCK — {project['meta']['title']}
{DOCUMENTARY_PACK}
Najpierw wykonaj research w sieci. W facts zapisz źródło i URL każdego twierdzenia.
Wypełnij poniższą kartę jako story_lock w projekcie, bez pisania narracji.
central_question: jedno pytanie; hook: konkretny początek; payoff: odpowiedź końcowa.
signature_line: oryginalne zdanie na początek i finał; recurring_detail: szczegół wracający na końcu.
thesis: odpowiedź w jednym zdaniu; key_players: osoby/organizacje potwierdzone w facts.
complication: co komplikuje prostą odpowiedź; counterpoint: najmocniejszy uczciwy kontrargument.
stakes_for_viewer: dlaczego temat obchodzi widza; open_question: czego nadal nie wiemy lub 'none'.
check_section: IN lub OUT; nawet przy OUT kontrargument pozostaje w narracji.
sting: powiązany następny temat lub 'none'; bez wymuszonej zapowiedzi nieistniejącego odcinka.
fact_ids: identyfikatory całego banku faktów; evidence_chain: od 5 do 8 różnych ID z banku, w kolejności argumentacji.
Pola opisowe są tekstem; 'none' dopuszczalne dla recurring_detail, key_players i counterpoint,
jeśli brak uzasadnionego odpowiednika. Nie twórz sztucznej równowagi poglądów.
DISPUTED wymaga notatki o sporze i stanowiskach. UNVERIFIED i DRAMATIZATION nie są dowodami.
Tryb prowadzony: pokaż kartę do zatwierdzenia. Tryb automatyczny zlecony przez użytkownika:
sprawdź źródła i spójność karty, a potem zatwierdź poleceniem lock. CLI nie weryfikuje treści stron.
Po zmianie zatwierdzonej karty użyj unlock, popraw kartę i ponownie lock.
KARTA:
{json.dumps(card, ensure_ascii=False, indent=2)}
BIEŻĄCE FAKTY:
{json.dumps(project.get('facts', []), ensure_ascii=False, indent=2)}
"""


def story_digest(project: dict) -> str:
    card = {k: v for k, v in project["story_lock"].items() if k not in ("status", "digest")}
    bank = set(card.get("fact_ids", []))
    payload = {
        "title": project["meta"]["title"], "channel": project.get("channel"), "story": card,
        "narrative": {k: project["meta"].get(k) for k in ("thesis", "curiosity_gap", "narrator", "language", "wpm")},
        "facts": sorted(
            ({k: f.get(k) or "" for k in ("id", "claim", "status", "source", "url", "note")}
             for f in project.get("facts", []) if f["id"] in bank), key=lambda f: f["id"]
        ),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def story_errors(project: dict, require_locked: bool = True) -> list[str]:
    if "story_lock" not in project:
        return []  # starsze projekty zachowują dotychczasowy workflow
    card = project["story_lock"]
    if not isinstance(card, dict):
        return ["story_lock musi być obiektem JSON."]
    errors = []
    if "channel" in project:
        try:
            validate_channel(project["channel"])
        except ValueError as exc:
            errors.append(str(exc))
    for key in STORY_FIELDS:
        if not isinstance(card.get(key), str) or not card[key].strip():
            errors.append(f"Uzupełnij story_lock.{key}.")
    if card.get("check_section") not in ("IN", "OUT"):
        errors.append("story_lock.check_section: wymagane IN lub OUT.")
    if card.get("status") not in ("DRAFT", "LOCKED"):
        errors.append("story_lock.status: wymagane DRAFT lub LOCKED.")
    bank = card.get("fact_ids")
    chain = card.get("evidence_chain")
    valid_bank = isinstance(bank, list) and bool(bank) and all(isinstance(x, str) for x in bank)
    valid_chain = isinstance(chain, list) and all(isinstance(x, str) for x in chain)
    if not valid_bank or len(set(bank)) != len(bank):
        errors.append("fact_ids: wymagany niepusty bank różnych ID faktów.")
    if not valid_chain or not 5 <= len(chain) <= 8 or len(set(chain)) != len(chain):
        errors.append("evidence_chain: wymagane od 5 do 8 różnych ID faktów.")
    if valid_bank and valid_chain and not set(chain) <= set(bank):
        errors.append("Wszystkie dowody evidence_chain muszą należeć do fact_ids.")
    facts = {f["id"]: f for f in project.get("facts", [])}
    if len(facts) != len(project.get("facts", [])):
        errors.append("Rejestr facts zawiera powtórzone ID faktów.")
    if valid_bank:
        for fid in bank:
            f = facts.get(fid)
            if not f:
                errors.append(f"Nieznany fakt {fid} w Story Lock.")
                continue
            if f.get("status") not in ("VERIFIED", "DISPUTED"):
                errors.append(f"{fid}: bank wymaga VERIFIED lub DISPUTED.")
            if not all(isinstance(f.get(k), str) and f[k].strip() for k in ("claim", "source", "url")) or not re.match(
                r"^https?://[^/\s]+", f["url"]
            ):
                errors.append(f"{fid}: wymagane twierdzenie, źródło i URL http(s).")
            if f.get("status") == "DISPUTED" and (not isinstance(f.get("note"), str) or not f["note"].strip()):
                errors.append(f"{fid}: opisz spór i stanowiska w note.")
        for beat in project.get("beats", []):
            used = set(beat.get("facts", [])) | set(beat.get("facts_used", []))
            if not used <= set(bank):
                errors.append(f"{beat['id']}: fakty spoza zatwierdzanego banku: {', '.join(sorted(used - set(bank)))}.")
    if require_locked and card.get("status") != "LOCKED":
        errors.append("Story Lock jest szkicem. Uzupełnij kartę i użyj polecenia lock przed pisaniem.")
    if card.get("status") == "LOCKED" and valid_bank and card.get("digest") != story_digest(project):
        errors.append("Zmieniono zatwierdzoną kartę, tytuł, profil lub fakty. Użyj unlock i ponownie lock.")
    return errors


def ensure_locked(project: dict) -> None:
    errors = story_errors(project)
    if errors:
        raise ValueError("\n".join(errors))


def lock_story(project: dict) -> None:
    if "story_lock" not in project:
        raise ValueError("Brak story_lock. Polecenie story pokaże szablon do dodania w projekcie.")
    if not isinstance(project["story_lock"], dict):
        raise ValueError("story_lock musi być obiektem JSON.")
    if project["story_lock"].get("status") == "LOCKED":
        ensure_locked(project)
        return
    errors = story_errors(project, require_locked=False)
    if errors:
        raise ValueError("\n".join(errors))
    project["meta"]["thesis"] = project["story_lock"]["thesis"]
    project["meta"]["curiosity_gap"] = project["story_lock"]["central_question"]
    project["story_lock"]["status"] = "LOCKED"
    project["story_lock"]["digest"] = story_digest(project)


def story_context(project: dict) -> str:
    if "story_lock" not in project:
        return ""
    return "\n### PAKIET KANAŁU I ZATWIERDZONY STORY LOCK\n" + DOCUMENTARY_PACK + (
        "Nie zmieniaj karty ani faktów. Jeśli wymagają korekty, przerwij pisanie i wskaż zmianę.\n"
        "Zachowaj pytanie, tezę i payoff całego filmu, nawet pracując tylko nad jednym beatem.\n"
        "Signature line i powracający szczegół umieść we właściwych beatach początku/finału, nie w każdym.\n"
        + json.dumps({"channel": project.get("channel"), "title": project["meta"]["title"],
                      "story_lock": project["story_lock"]}, ensure_ascii=False, indent=2) + "\n"
    )
