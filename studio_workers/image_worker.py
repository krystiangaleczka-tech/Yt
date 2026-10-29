"""Executed only in the user's image-model environment; never loaded by the API."""
import argparse
import json
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=448)
    parser.add_argument("--steps", type=int, default=25)
    args = parser.parse_args()
    import torch
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    if args.width % 8 or args.height % 8 or not 256 <= args.width <= 1024 or not 256 <= args.height <= 1024 or not 1 <= args.steps <= 75:
        raise ValueError("Rozmiar musi być wielokrotnością 8 w zakresie 256–1024; liczba kroków 1–75")
    pipeline = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float32 if device == "cpu" else torch.float16, use_safetensors=False)
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    pipeline.to(device); pipeline.enable_attention_slicing()
    started=time.monotonic()
    def report(pipe,step,timestep,values):
        print(f"STEP {step+1}/{args.steps}",flush=True)
        return values
    image = pipeline(args.prompt, width=args.width, height=args.height, num_inference_steps=args.steps,callback_on_step_end=report,
                     generator=torch.Generator("cpu").manual_seed(args.seed)).images[0]
    image.save(Path(args.output))
    Path(args.output).with_suffix(".json").write_text(json.dumps({"model":"stable-diffusion-v1-5/stable-diffusion-v1-5","device":device,"seed":args.seed,"width":args.width,"height":args.height,"steps":args.steps,"elapsed_seconds":round(time.monotonic()-started,3)}))


if __name__ == "__main__":
    main()
