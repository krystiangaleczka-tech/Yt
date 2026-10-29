"""Opt-in reference-guided transparent cutout production.

The reference is submitted only after an explicit generation request. The
official Images edit endpoint is fixed (no arbitrary URLs or remote callbacks).
The provider must return a *real* PNG with meaningful transparency; never
replace opaque backgrounds with guessed alpha or slice the flattened draft.
"""
from __future__ import annotations

import base64
import binascii
import io
import json
import math
from pathlib import Path

import httpx
from PIL import Image

from .store import atomic_json, now
from .models import uid

MODELS = ("gpt-image-2.5-sunburst", "gpt-image-2.5-flare")
IMAGE_API_URL = "https://api.openai.com/v1/images/edits"
MAX_REFERENCE_BYTES = 6_000_000
MAX_OUTPUT_BYTES = 25_000_000


def reserve_cutout_cost(store, project, estimate: float):
    """Reserve an explicit estimate against the existing per-project API cap."""
    if isinstance(estimate, bool) or not isinstance(estimate, (int, float)) or not math.isfinite(estimate) or estimate <= 0:
        raise ValueError("Ustaw dodatni szacowany koszt jednego generowanego wycinka")
    path = store.folder(project.id) / "spending.json"
    with store.lock:
        entries = json.loads(path.read_text()) if path.exists() else []
        if sum(entry["estimate"] for entry in entries) + estimate > project.budget.get("max_cost", 0):
            raise ValueError("Generowanie PNG przekroczyłoby limit kosztu projektu")
        entries.append({
            "id": uid("cost_"), "at": now(), "revision": project.revision,
            "estimate": estimate, "state": "reserved",
            "provider": "openai-images", "kind": "paper-theatre-cutout",
        })
        atomic_json(path, entries)


def check_reference(path: Path) -> tuple[bytes, str]:
    if path.stat().st_size > MAX_REFERENCE_BYTES:
        raise ValueError("Referencja musi mieć maksymalnie 6 MB")
    with Image.open(path) as im:
        if im.format not in ("PNG", "JPEG"):
            raise ValueError("Referencją może być wyłącznie PNG lub JPEG")
        if im.width > 4096 or im.height > 4096:
            raise ValueError("Referencja ma zbyt duże wymiary")
        mime = "image/png" if im.format == "PNG" else "image/jpeg"
    return path.read_bytes(), mime


def validate_cutout_png(raw: bytes) -> dict:
    if not isinstance(raw, bytes) or not 1 <= len(raw) <= MAX_OUTPUT_BYTES:
        raise ValueError("Generator zwrócił nieprawidłową wielkość pliku PNG")
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != "PNG":
                raise ValueError("Generator nie zwrócił pliku PNG")
            if not 1 <= image.width <= 4096 or not 1 <= image.height <= 4096:
                raise ValueError("Generator zwrócił nieobsługiwane wymiary PNG")
            if image.mode != "RGBA" and "transparency" not in image.info:
                raise ValueError("Wynik nie ma kanału alpha")
            alpha = image.convert("RGBA").getchannel("A")
            lo, hi = alpha.getextrema()
            if not lo < 255 or hi == 0:
                raise ValueError("Wycinek ma nieprzezroczyste lub puste tło")
            if alpha.getbbox() is None:
                raise ValueError("Wycinek jest całkowicie pusty")
            return {"width": image.width, "height": image.height, "alpha_min": lo, "alpha_max": hi}
    except (OSError, Image.DecompressionBombError) as error:
        raise ValueError("Nie udało się odczytać wygenerowanego PNG") from error


def generate_cutout_png(reference_path: Path, prompt: str, *, key: str, model: str) -> bytes:
    if model not in MODELS:
        raise ValueError("Model nie obsługuje zatwierdzonej integracji transparent PNG")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("Ustaw prywatny klucz do generatora obrazów w Połączeniach")
    if not isinstance(prompt, str) or not 1 <= len(prompt) <= 10000:
        raise ValueError("Prompt pojedynczego wycinka ma niepoprawną długość")
    reference, mime = check_reference(reference_path)
    fields = {
        "model": model,
        "prompt": prompt,
        "background": "transparent",
        "output_format": "png",
        "size": "1024x1024",
        "quality": "high",
        "n": "1",
    }
    try:
        with httpx.Client(timeout=210, follow_redirects=False) as client:
            response = client.post(
                IMAGE_API_URL,
                headers={"Authorization": "Bearer " + key.strip()},
                data=fields,
                files={"image[]": ("approved-storyboard.png" if mime == "image/png" else "approved-storyboard.jpg", reference, mime)},
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.TimeoutException as error:
        raise ValueError("Generator obrazów nie odpowiedział w limicie czasu") from error
    except httpx.HTTPStatusError as error:
        code = error.response.status_code
        raise ValueError(f"Generator obrazów odrzucił żądanie (HTTP {code}). Sprawdź klucz, limit i model.") from error
    except (httpx.HTTPError, ValueError) as error:
        raise ValueError("Nie udało się połączyć z generatorem obrazów") from error
    try:
        encoded = payload["data"][0]["b64_json"]
        if not isinstance(encoded, str) or len(encoded) > (MAX_OUTPUT_BYTES * 4 // 3) + 10_000:
            raise ValueError("Obraz przekracza dopuszczalny rozmiar")
        result = base64.b64decode(encoded, validate=True)
    except (KeyError, IndexError, TypeError, ValueError, binascii.Error) as error:
        raise ValueError("Generator nie zwrócił poprawnego PNG w polu b64_json") from error
    validate_cutout_png(result)
    return result
