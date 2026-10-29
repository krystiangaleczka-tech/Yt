"""Reference-guided planning: cheap story-first draft before isolated cutouts.

A reference is *visual guidance*, never a source of cropped alpha layers.
The optional vision request is explicit and uses the already connected model
provider. It is never sent to an outside service without a user action.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

from .paper_theatre_asset_first import DEFAULT_STYLE, drafting_prompt


def draft_prompt(scene, brief: str = "", style: str = DEFAULT_STYLE) -> str:
    narration = (getattr(scene, "narration", "") or "").strip()
    scene_description = (getattr(scene, "prompt", "") or "").strip()
    title = (getattr(scene, "title", "") or "").strip()
    if not isinstance(brief, str) or len(brief) > 4000:
        raise ValueError("Opis sceny przekracza limit")
    if not isinstance(style, str) or not style.strip() or len(style) > 3000:
        raise ValueError("Określ jednolity styl scenografii")
    context = brief.strip() or narration or scene_description or title
    if not context:
        raise ValueError("Scena wymaga opisu, narracji lub tytułu")
    return (
        "Draft composition reference for a theatrical paper-cut documentary shot. "
        "ONE coherent complete 16:9 storyboard illustration with all planned "
        "objects in their desired FINAL positions. Stage, hierarchy, occlusion "
        "and proportions must be unambiguous. No texts, labels, watermark, "
        "photo frame or storyboard panels. This is ONLY a small preview to guide "
        "subsequent separate transparent PNG assets; do not use it in the final render. "
        "STYLE: " + style.strip() + ". "
        "SCENE: " + context +
        (". NARRATION: " + narration[:1500] if narration and context != narration else "")
    )


def vision_object_prompt(scene, brief: str, style: str, notes: str = "") -> str:
    prompt = drafting_prompt(brief or scene.narration or scene.title, style)
    if not isinstance(notes, str) or len(notes) > 3000:
        raise ValueError("Opis kompozycji jest za długi")
    return (
        prompt
        + "\nZALACZONY OBRAZ TO ZATWIERDZONY MAŁY DRAFT REFERENCYJNY. "
        "WYDOBĄDŹ Z NIEGO LOGICZNĄ LISTĘ osobnych obiektów i ich pozycje. "
        "Nie wycinaj pikseli, nie traktuj go jak finalnego tła. "
        "Wynikowa lista posłuży do osobnego wygenerowania każdego obiektu. "
        "Zachowaj układ, proporcje i przesłanianie względem referencji. "
        + ("\nUWAGI: " + notes if notes else "")
    )


def propose_objects_from_reference(connectors, store, project, scene, reference_id,
                                   brief, style, notes=""):
    """Opt-in multimodal request to configured OpenAI-compatible vision model."""
    from .media import asset_path
    from studio_connectors.sources import public_url
    from .budget import reserve
    import httpx
    config = connectors.config()
    if not config.get("ai_base_url") or not config.get("ai_model"):
        raise ValueError("Analiza obrazu wymaga skonfigurowanego modelu AI z obsługą obrazów")
    asset = next((a for a in project.assets if a.id == reference_id), None)
    if not asset or asset.kind != "image":
        raise ValueError("Najpierw wybierz plik obrazu referencyjnego")
    file = Path(asset_path(store, project.id, reference_id, project=project))
    if file.stat().st_size > 6_000_000:
        raise ValueError("Draft powinien być mały, maksymalnie 6 MB")
    with file.open("rb") as stream:
        from PIL import Image
        with Image.open(stream) as im:
            if im.format not in ("PNG", "JPEG"):
                raise ValueError("Draft musi mieć format PNG lub JPEG")
            mime = "image/png" if im.format == "PNG" else "image/jpeg"
    prompt = vision_object_prompt(scene, brief, style, notes)
    reserve(store, project, connectors)
    url = public_url(config["ai_base_url"].rstrip("/") + "/chat/completions")
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {
            "url": "data:" + mime + ";base64," + base64.b64encode(file.read_bytes()).decode("ascii"),
            "detail": "high"}},
    ]
    try:
        with httpx.Client(timeout=150, follow_redirects=False) as client:
            response = client.post(url, headers={"Authorization": "Bearer " + config.get("ai_key", "")},
                                   json={"model": config["ai_model"],
                                         "messages": [{"role": "user", "content": content}],
                                         "temperature": .2})
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError) as error:
        raise ValueError("Model nie zanalizował obrazu. Sprawdź, czy obsługuje wejście wizualne: " + str(error)[:250]) from error
    if not isinstance(result, str):
        raise ValueError("Model powinien zwrócić listę obiektów jako JSON")
    cleaned = result.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    from .paper_theatre_asset_first import normalize_manifest
    try:
        raw = json.loads(cleaned)
        if not isinstance(raw, dict):
            raise ValueError("Wynik musi być obiektem JSON")
        raw.update(mode="reference-guided", reference_asset_id=reference_id,
                   reference_notes=notes)
        return normalize_manifest(raw)
    except (ValueError, TypeError) as error:
        raise ValueError("Model nie zwrócił poprawnej listy pojedynczych obiektów: " + str(error)) from error
