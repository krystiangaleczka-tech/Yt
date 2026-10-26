# Instalacja i sprzęt

## Wymagania
- macOS (Apple Silicon, MPS) lub Linux/Windows z NVIDIA (CUDA)
- [uv](https://github.com/astral-sh/uv), ffmpeg (`brew install ffmpeg`)
- ~10 GB wolnego miejsca (modele ~5 GB + media odcinka ~3 GB)

## Dwa środowiska Pythona
Chatterbox wymaga innej wersji torch niż diffusers, dlatego są dwa venvy:

```bash
uv venv -p 3.12 pilot/.venv
uv pip install -p pilot/.venv/bin/python -r requirements-render.txt

uv venv -p 3.11 pilot/.venv-tts
uv pip install -p pilot/.venv-tts/bin/python -r requirements-tts.txt
```

`docos/docos.py` uruchamia się przez `uv run -q docos.py ...` (PEP 723 — openpyxl instaluje się sam).

## Modele (pobierają się przy pierwszym użyciu)
| Model | Do czego | Licencja |
|---|---|---|
| `stable-diffusion-v1-5/stable-diffusion-v1-5` (fp16) | kadry AI (opcjonalnie; v5 nie używa AI) | CreativeML OpenRAIL-M |
| Kokoro-82M (`kokoro-v1.0.onnx`, `voices-v1.0.bin`) | szybki lektor zastępczy | Apache 2.0 |
| `ResembleAI/chatterbox` (multilingual) | klon głosu | MIT (+ watermark Perth) |

Kokoro: pliki z https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0) do `pilot/models/`.

## Wydajność (zmierzone)
| Etap | MacBook M3, 8 GB | uwagi |
|---|---|---|
| Klon głosu, film ~4 min | ~50–60 min | wąskie gardło: RAM/swap |
| Kadr SD 1.5 | ~1 min | przy swapie ~12 min |
| Podgląd 360p, cały film | ~2 min 20 s (3 rdzenie) | 6 rdzeni szybciej |
| Podgląd po zmianie 1 ujęcia | ~30 s | cache segmentów |
| Render finalny 1080p | ~15–20 min | |

Zasada: **nie uruchamiaj klonowania głosu i SD jednocześnie** na 8 GB RAM — oba trafią do swapu.
Najwięcej przyspieszy więcej RAM (M1/M2/M3 Max 32–64 GB) albo karta NVIDIA (RTX 4070+: lektor ~3–5 min, kadr ~3 s).
