"""Typed presentation catalog used by forms, migration and the compositor."""
from __future__ import annotations

import re
import math


def field(key, label, kind="text", default="", **rules):
    return {"key": key, "label": label, "type": kind, "default": default, **rules}


TEXT = field("text", "Treść")
CAPTION = field("caption", "Podpis i źródło")
TEMPLATES = [
    {"id": "media", "name": "Zdjęcie / film", "fields": [CAPTION]},
    {"id": "document", "name": "Dokument", "fields": [CAPTION]},
    {"id": "title", "name": "Plansza tytułowa", "fields": [TEXT, CAPTION]},
    {"id": "quote", "name": "Cytat", "fields": [TEXT, field("author", "Autor"), CAPTION]},
    {"id": "press", "name": "Prasa", "fields": [TEXT, field("publication", "Publikacja i data"), CAPTION]},
    {"id": "lower-third", "name": "Podpis osoby", "fields": [TEXT, field("subtitle", "Funkcja / opis"), CAPTION]},
    {"id": "counter", "name": "Licznik", "fields": [field("from", "Od", "number", 0), field("to", "Do", "number", 100), field("unit", "Jednostka"), CAPTION]},
    {"id": "timeline", "name": "Oś wydarzeń", "fields": [field("events", "Wydarzenia", "json", [{"date": "", "text": ""}]), CAPTION]},
    {"id": "map", "name": "Mapa geograficzna", "fields": [field("bounds", "Obszar [zachód, południe, wschód, północ]", "json", [-180, -85, 180, 85]), field("points", "Punkty [{lon,lat,label}]", "json", []), field("routes", "Trasy [[lon,lat],…]", "json", []), CAPTION]},
    {"id": "diagram", "name": "Diagram", "fields": [TEXT, field("nodes", "Węzły [{id,text,x,y}]", "json", []), field("edges", "Połączenia [[id,id],…]", "json", []), CAPTION]},
    {"id": "waveform", "name": "Oscylogram nagrania", "fields": [field("source_in", "Początek nagrania (s)", "number", 0, min=0), CAPTION]},
    {"id": "spectrogram", "name": "Spektrogram nagrania", "fields": [field("source_in", "Początek nagrania (s)", "number", 0, min=0), field("span", "Zakres audio (s; 0 = czas ujęcia)", "number", 0, min=0,max=3600),field("max_hz", "Górna częstotliwość (Hz)", "number", 2000, min=10, max=8000), CAPTION]},
    {"id": "loupe", "name": "Lupa", "fields": [field("x", "Środek X", "number", .5, min=0, max=1), field("y", "Środek Y", "number", .5, min=0, max=1), field("zoom", "Powiększenie", "number", 2, min=1, max=8), CAPTION]},
    {"id": "split", "name": "Dzielony ekran", "fields": [field("left", "Podpis po lewej"), field("right", "Podpis po prawej"), CAPTION]},
    {"id": "comparison", "name": "Porównanie", "fields": [field("left", "Podpis po lewej"), field("right", "Podpis po prawej"), CAPTION]},
    {"id": "stack", "name": "Stos zdjęć", "fields": [CAPTION]},
    {"id": "qa", "name": "Pytanie i odpowiedź", "fields": [field("question", "Pytanie"), field("answer", "Odpowiedź / dosłowny cytat"), field("author", "Źródło odpowiedzi"), CAPTION]},
    {"id": "slogan", "name": "Hasło kinetyczne", "fields": [TEXT, CAPTION]},
    {"id": "cards", "name": "Karty informacji", "fields": [field("items", "Karty [tekst,…]", "json", []), CAPTION]},
    {"id": "parallax", "name": "Parallax z warstw", "fields": [
        field("depth", "Głębokość ruchu", "number", .06, min=0, max=.3),
        field("assembly_start", "Początek dokładania warstw (s)", "number", 0, min=0, max=3600),
        field("assembly_interval", "Odstęp między warstwami (s; 0 = wszystkie razem)", "number", 0, min=0, max=60),
        field("assembly_duration", "Czas pojawiania się warstwy (s)", "number", .35, min=0, max=10),
        field("assembly_drop", "Przesunięcie podczas wejścia (0–0,3 wysokości)", "number", .06, min=0, max=.3),
        field("layer_cues", "Wyjątki dla warstw [{layer,start,duration,drop,depth}]", "json", []),
        CAPTION,
    ], "note": "Tło to główny materiał, a warstwy PNG z przezroczystością pojawiają się w wybranej kolejności. Odstęp 0 zachowuje dawny wygląd; wyjątki layer liczymy od 1."},
]
CATALOG = {item["id"]: item for item in TEMPLATES}
LEGACY = {"ARCHIWUM": "media", "AI_OBRAZ": "media", "DOKUMENT": "document", "TYTUŁ": "title", "CYTAT": "quote", "PRASA": "press", "PODPIS": "lower-third", "LICZNIK": "counter", "OŚ_CZASU": "timeline", "MAPA": "map", "DIAGRAM": "diagram", "WAVEFORM": "waveform", "SPEKTRO": "spectrogram", "LUPA": "loupe", "SPLIT": "split", "PORÓWNANIE": "comparison", "STOS": "stack", "QA": "qa", "HASŁO": "slogan"}
MEDIA_TEMPLATES = {"media", "document", "lower-third", "loupe", "split", "comparison", "stack", "parallax", "waveform", "spectrogram"}


def validate_parameters(template: str, parameters: dict) -> dict:
    if template not in CATALOG:
        raise ValueError("Nieznany typ ujęcia")
    result = dict(parameters)
    for spec in CATALOG[template]["fields"]:
        value = result.get(spec["key"], spec["default"])
        if spec["type"] == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(spec["label"] + ": podaj liczbę")
            if not math.isfinite(value) or value < spec.get("min", -1e12) or value > spec.get("max", 1e12):
                raise ValueError(spec["label"] + ": wartość poza zakresem")
        elif spec["type"] == "text" and not isinstance(value, str):
            raise ValueError(spec["label"] + ": wymagany tekst")
        elif spec["type"] == "json" and not isinstance(value, list):
            raise ValueError(spec["label"] + ": wymagana lista")
        result[spec["key"]] = value
    def number(value,low,high): return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and low<=value<=high
    if template == "map":
        bounds = result["bounds"]
        if len(bounds) != 4 or not all(number(v,-180,180) for v in bounds) or not -180 <= bounds[0] < bounds[2] <= 180 or not -90 <= bounds[1] < bounds[3] <= 90:
            raise ValueError("Obszar mapy: podaj poprawne długości i szerokości geograficzne")
        for point in result["points"]:
            if not isinstance(point, dict) or not number(point.get("lon"),-180,180) or not number(point.get("lat"),-90,90):
                raise ValueError("Punkt mapy wymaga współrzędnych lon/lat")
        if any(not isinstance(p,list) or len(p)!=2 or not number(p[0],-180,180) or not number(p[1],-90,90) for p in result["routes"]): raise ValueError("Trasa wymaga listy współrzędnych [lon,lat]")
    if template=="diagram":
        nodes=result["nodes"]
        if any(not isinstance(n,dict) or not isinstance(n.get("id"),str) or not number(n.get("x",.5),0,1) or not number(n.get("y",.5),0,1) for n in nodes): raise ValueError("Węzły diagramu wymagają id oraz x/y od 0 do 1")
        ids={n["id"] for n in nodes}
        if len(ids)!=len(nodes) or any(not isinstance(e,list) or len(e)!=2 or any(v not in ids for v in e) for e in result["edges"]): raise ValueError("Połączenia diagramu muszą wskazywać istniejące, unikalne węzły")
    if template=="timeline" and any(not isinstance(e,dict) or not isinstance(e.get("date",""),str) or not isinstance(e.get("text",""),str) for e in result["events"]): raise ValueError("Wydarzenia wymagają tekstowych pól date i text")
    if template=="parallax":
        seen_layers = set()
        allowed = {"layer", "start", "duration", "drop", "depth"}
        for cue in result["layer_cues"]:
            if not isinstance(cue, dict) or not set(cue) <= allowed:
                raise ValueError("Wejście warstwy wymaga obiektu z polami layer/start/duration/drop/depth")
            layer = cue.get("layer")
            if isinstance(layer, bool) or not isinstance(layer, int) or not 1 <= layer <= 1000 or layer in seen_layers:
                raise ValueError("Warstwy mają unikalne numery od 1 do 1000")
            seen_layers.add(layer)
            for key, low, high in (("start", 0, 3600), ("duration", 0, 10), ("drop", 0, .3), ("depth", 0, 10)):
                if key in cue and not number(cue[key], low, high):
                    raise ValueError("Niepoprawna wartość " + key + " dla warstwy " + str(layer))
    if template=="cards" and any(not isinstance(e,str) for e in result["items"]): raise ValueError("Karty wymagają listy tekstów")
    if any(isinstance(v,list) and len(v)>1000 for v in result.values()): raise ValueError("Maksymalnie tysiąc elementów szablonu")
    return result


def legacy_parameters(shot: dict) -> tuple[str, dict]:
    desc = str(shot.get("desc", ""))
    quoted = re.findall(r'["“](.*?)["”]', desc)
    template = LEGACY.get(shot.get("asset"), "media")
    params = {"text": quoted[0] if quoted else desc, "caption": quoted[1] if len(quoted) > 1 else "", "legacy_desc": desc}
    cap=re.search(r'CAPTION:\s*["“](.*?)["”]',desc)
    if cap: params["caption"]=cap.group(1)
    match = re.search(r"FILE:\s*(.*?)(?=\s+[A-Z_]+:|$)", desc)
    if match:
        params["pending_files"] = [match.group(1).strip()]
    match = re.search(r"FILES:\s*(.*?)(?=\s+[A-Z_]+:|$)", desc)
    if match:
        params["pending_files"] = [name.strip() for name in match.group(1).split("|")]
    match = re.search(r"START:\s*([\d.]+)", desc)
    if match:
        params["source_in"] = float(match.group(1))
    if template=="spectrogram":
        for old,new in (("SPAN","span"),("MAXHZ","max_hz")):
            match=re.search(old+r":\s*([\d.]+)",desc)
            if match: params[new]=float(match.group(1))
    if template=="timeline" and quoted:
        params["events"]=[{"date":value.strip(),"text":""} for value in quoted[0].split("/")]
    if template=="map" and "Juan de Fuca" in desc:
        # Preserve the approximate data of the legacy renderer as editable data.
        params.update(bounds=[-136,40,-118,50.5],points=[{"lon":-122.6,"lat":48.3,"label":"Whidbey Island"},{"lon":-130,"lat":45.9,"label":"Juan de Fuca Ridge"}],routes=[[-130.6,44.4],[-130,45.9],[-129.6,47],[-129,48.5]],caption="Map approximate — legacy DocOS")
    if template=="diagram" and "SOFAR" in desc:
        params.update(text="How sound crosses an ocean",nodes=[{"id":"source","text":"Source","x":.15,"y":.5},{"id":"channel","text":"SOFAR channel (~1 km; varies)","x":.5,"y":.5},{"id":"receiver","text":"Hydrophone","x":.85,"y":.5}],edges=[["source","channel"],["channel","receiver"]],caption="Schematic — legacy DocOS, after NOAA")
    if template == "counter":
        numbers = re.findall(r"\d[\d,.]*", quoted[0] if quoted else desc)
        if numbers:
            params["from"] = float(numbers[0].replace(",", ""))
            params["to"] = float(numbers[-1].replace(",", ""))
            params["unit"] = re.sub(r"[\d,.→\s]", "", quoted[0] if quoted else "")
    if template == "qa":
        params.update(question=quoted[0] if quoted else "", answer=quoted[1] if len(quoted) > 1 else "", author=desc.split("—")[-1].strip())
    if template in ("press", "quote"):
        params["publication" if template == "press" else "author"] = desc.split("—")[-1].strip() if "—" in desc else ""
    if template == "loupe":
        match = re.search(r"ZOOM:\s*([\d.]+),([\d.]+),([\d.]+)", desc)
        if match:
            x, y, width = map(float, match.groups()); params.update(x=x+width/2, y=y+width/2, zoom=1/max(.125, width))
    if template in ("split", "comparison"):
        params.update(left=quoted[0] if quoted else "", right=quoted[1] if len(quoted) > 1 else "")
        if "cards" in desc and not params.get("pending_files"):
            template="cards";params["items"]=quoted or [desc]
    return template, params
