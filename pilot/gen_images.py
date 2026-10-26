"""Generate scene stills locally with Stable Diffusion 1.5 (open weights) on Apple MPS."""
import sys
from pathlib import Path

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

STYLE = ("1990s archival documentary photograph, black and white, film grain, "
         "high contrast, dim lighting, realistic, 35mm")
NEG = ("color, cartoon, illustration, painting, text, watermark, logo, "
       "blurry, deformed, extra fingers, lowres")

SCENES = {
    "s1_ocean": "research vessel at night on a dark calm Pacific ocean, cable lowered into the water, " + STYLE,
    "s2_lab": "close-up of a paper sonar spectrogram printout on a cluttered desk, hand-written notes, lamp light, " + STYLE,
    "s3_whale": "humpback whale swimming underwater, full body side view, head on the left, tail on the right, sun rays from the surface, " + STYLE,
    "s3_deep": "empty pitch black deep ocean abyss, faint particles, something enormous barely visible in the dark, " + STYLE,
    "s_sonar": "1980s navy sonar room, operator wearing headphones in front of glowing round CRT sonar screens and analog consoles, " + STYLE,
    "s_buoy": "scientists on a ship deck lowering a hydrophone instrument on a steel cable into the ocean, overcast sky, " + STYLE,
    "s_monitor": "old beige 1990s computer monitor glowing in a dark bedroom at night, crt screen light on the wall, " + STYLE,
    "s_scientist": "scientist at a desk looking at a computer screen with waveform data, office at night, desk lamp, " + STYLE,
    "s_iceberg": "massive antarctic iceberg cracking and calving into the sea, huge ice cliff, mist, " + STYLE,
    "s_deep": "underwater hydrophone hanging on a cable in the dark deep ocean, faint light beams from above, particles, " + STYLE,
}

pipe = StableDiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16, variant="fp16",
    safety_checker=None, requires_safety_checker=False,
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
pipe = pipe.to("mps")
pipe.enable_attention_slicing()

only = set(sys.argv[1:])
for i, (name, prompt) in enumerate(SCENES.items()):
    if only and name not in only:
        continue
    g = torch.Generator("cpu").manual_seed(1997 + i)
    img = pipe(prompt, negative_prompt=NEG, width=768, height=448,
               num_inference_steps=25, guidance_scale=7.0, generator=g).images[0]
    img.save(OUT / f"{name}.png")
    print("saved", name, flush=True)
