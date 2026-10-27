"""Multilingual Studio TTS; no English-specific text rewriting or tempo guessing."""
import argparse
import json
import re
import hashlib
import os
import random
import sys
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("reference")
    parser.add_argument("output")
    parser.add_argument("--language", default="pl")
    args = parser.parse_args()
    import numpy as np
    import soundfile as sf
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    device=os.environ.get("DOCOS_TTS_DEVICE",data.get("config",{}).get("device","auto"))
    if device=="auto":
        memory=int(subprocess.check_output(["sysctl","-n","hw.memsize"])) if sys.platform=="darwin" else 0
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() and memory>12*1024**3 else "cpu"
    if device not in ("cpu","mps","cuda"): raise ValueError("Nieobsługiwane urządzenie głosu")
    if device=="cuda" and not torch.cuda.is_available(): raise ValueError("CUDA jest niedostępne. Wybierz Auto lub CPU.")
    if device=="mps" and not torch.backends.mps.is_available(): raise ValueError("MPS jest niedostępne. Wybierz Auto lub CPU.")
    if device=="cpu": torch.set_num_threads(min(4,os.cpu_count() or 2))
    print("DEVICE "+device,flush=True)
    # Chatterbox checkpoints are loaded on the selected device, including MPS hosts.
    original_load = torch.load
    torch.load = lambda *a, **kw: original_load(*a, **{**kw, "map_location": torch.device(device)})
    narration = data["narration"]
    config = {"exaggeration": .5, "cfg_weight": .4, "temperature": .7, "pause": .25, "seed": 42, **data.get("config", {})}
    cache = Path(data.get("cache_dir") or Path(args.output).parent/"sentence-cache")
    cache.mkdir(parents=True, exist_ok=True)
    sentences = data.get("sentences") or [{"id":str(i),"text":text,"spoken_text":text} for i,text in enumerate(re.split(r"(?<=[.!?])\s+",narration.strip())) if text]
    parts, manifest, cursor = [], [], 0
    model = None
    reference_hash = hashlib.sha256(Path(args.reference).read_bytes()).hexdigest()
    for sentence in sentences:
        text = sentence.get("spoken_text") or sentence["text"]
        if not text:
            continue
        key = hashlib.sha256(json.dumps({"version":2,"device":device,"text":text,"language":args.language,"reference":reference_hash,"config":config},sort_keys=True).encode()).hexdigest()
        path = cache/(key+".wav")
        if not path.is_file():
            if model is None: model = ChatterboxMultilingualTTS.from_pretrained(device=device)
            torch.manual_seed(int(config["seed"])); random.seed(int(config["seed"])); np.random.seed(int(config["seed"]))
            audio = model.generate(text, language_id=args.language, audio_prompt_path=args.reference,
                                   exaggeration=config["exaggeration"], cfg_weight=config["cfg_weight"], temperature=config["temperature"]).detach().cpu().numpy().squeeze()
            temporary = path.with_suffix(".part.wav")
            sf.write(temporary, audio.astype(np.float32), model.sr); os.replace(temporary,path)
        audio, sr = sf.read(path,dtype="float32")
        if audio.ndim>1: audio=audio.mean(axis=1)
        manifest.append({"id":sentence["id"],"text":sentence["text"],"spoken_text":text,"filename":str(path),"start":cursor/sr,"end":(cursor+len(audio))/sr,"duration":len(audio)/sr,"input_hash":sentence.get("input_hash","")})
        parts.extend([audio, np.zeros(round(sr*config["pause"]),dtype=np.float32)])
        cursor+=len(audio)+round(sr*config["pause"])
        print("SENTENCE "+str(len(manifest))+"/"+str(len(sentences)),flush=True)
    if not parts:
        raise ValueError("Brak tekstu do nagrania")
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, np.concatenate(parts[:-1]), sr)
    output.with_suffix(".json").write_text(json.dumps({"sentences":manifest,"sample_rate":sr,"device":device,"model":"chatterbox-multilingual"},ensure_ascii=False),encoding="utf-8")


if __name__ == "__main__":
    main()
