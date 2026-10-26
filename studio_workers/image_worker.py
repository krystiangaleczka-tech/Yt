"""Executed only in the user's image-model environment; never loaded by the API."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    import torch
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    pipeline = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float32 if device == "cpu" else torch.float16)
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    pipeline.to(device); pipeline.enable_attention_slicing()
    image = pipeline(args.prompt, width=768, height=448, num_inference_steps=25,
                     generator=torch.Generator("cpu").manual_seed(args.seed)).images[0]
    image.save(Path(args.output))


if __name__ == "__main__":
    main()
