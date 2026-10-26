"""render_plan.json -> lokalne kadry AI (Stable Diffusion 1.5) + lista materiałów do zdobycia.

Uruchamiaj pythonem z venv pilota (ma torch + diffusers):
    ../pilot/.venv/bin/python -I make_assets.py examples/bloop/bloop_render_plan.json [--limit N] [--beat B01]
"""
import argparse
import json
import re
from pathlib import Path

NEG = ("color, cartoon, illustration, painting, text, watermark, logo, "
       "blurry, deformed, extra limbs, extra fingers, lowres")

ap = argparse.ArgumentParser()
ap.add_argument("plan")
ap.add_argument("--limit", type=int, default=0, help="max liczba kadrów AI (0 = wszystkie)")
ap.add_argument("--beat", default="", help="tylko ten beat")
ap.add_argument("--steps", type=int, default=25)
ap.add_argument("--archive-as-ai", action="store_true",
                help="zastąp ARCHIWUM/DOKUMENT kadrami AI (gdy nie ma jeszcze prawdziwych materiałów)")
ap.add_argument("--style", default="1990s archival documentary photograph, black and white, film grain, vignette, high contrast")
ap.add_argument("--redo", action="append", default=[], metavar='B04_wiz02="prompt"',
                help="wygeneruj ponownie kadr z nowym promptem (warianty trafiają do assets/_candidates/)")
ap.add_argument("--variants", type=int, default=3)
a = ap.parse_args()

plan_path = Path(a.plan)
plan = json.loads(plan_path.read_text(encoding="utf-8"))
plan_style = a.style
out = plan_path.parent / "assets"
out.mkdir(exist_ok=True)

shots = [s for s in plan["shots"] if not a.beat or s["beat"] == a.beat]
# spektrogramy i tabele rysuje renderer proceduralnie — SD robi z nich śmieci
PROCEDURAL = re.compile(r"spectrogram|log sheet", re.I)
ai = [s for s in shots if s["asset"] == "AI_OBRAZ" and s["prompt"] and not PROCEDURAL.search(s["desc"])]
if a.archive_as_ai:
    for s in shots:
        if s["asset"] in ("ARCHIWUM", "DOKUMENT") and not PROCEDURAL.search(s["desc"]):
            desc = s["desc"].split(" — search")[0]
            ai.append(dict(s, prompt=f"{desc}, {plan_style}"))
todo = [s for s in shots if s not in ai and s["asset"] != "AI_OBRAZ"]

# lista dla montażysty: wszystko, czego nie generujemy (archiwum, dokumenty, plansze)
lines = ["# Materiały do zdobycia / zrobienia\n"]
for s in todo:
    lines.append(f"- [ ] {s['beat']} WIZ {s['wiz']} @ {s['start']}s ({s['dur']}s) **{s['asset']}** ({s['framing']}): {s['desc']}")
(plan_path.parent / "assets_todo.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"assets_todo.md: {len(todo)} pozycji (archiwum, dokumenty, plansze)")

if a.limit:
    ai = ai[: a.limit]
if not ai and not a.redo:
    raise SystemExit("Brak kadrów AI_OBRAZ do wygenerowania.")

import torch  # noqa: E402
from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline  # noqa: E402

pipe = StableDiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float16, variant="fp16",
    safety_checker=None, requires_safety_checker=False)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
pipe = pipe.to("mps" if torch.backends.mps.is_available() else "cpu")
pipe.enable_attention_slicing()

if a.redo:
    cand = out / "_candidates"
    cand.mkdir(exist_ok=True)
    for spec in a.redo:
        name, prompt = spec.split("=", 1)
        for v in range(a.variants):
            g = torch.Generator("cpu").manual_seed(5000 + 97 * v)
            img = pipe(f"{prompt.strip(chr(34))}, {plan_style}", negative_prompt=NEG, width=768, height=448,
                       num_inference_steps=a.steps, guidance_scale=7.0, generator=g).images[0]
            img.save(cand / f"{name}_v{v}.png")
            print("wariant", f"{name}_v{v}.png", flush=True)
    raise SystemExit(0)

for i, s in enumerate(ai):
    name = f"{s['beat']}_wiz{s['wiz']:02d}.png"
    if (out / name).exists():
        print("jest już", name)
        continue
    g = torch.Generator("cpu").manual_seed(1000 + i)
    img = pipe(s["prompt"], negative_prompt=NEG, width=768, height=448,
               num_inference_steps=a.steps, guidance_scale=7.0, generator=g).images[0]
    img.save(out / name)
    print("zapisano", name, flush=True)
