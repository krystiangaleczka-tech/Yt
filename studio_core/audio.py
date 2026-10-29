"""Measured audio assembly, waveform data and validation shared by API/CLI."""
import json
import subprocess
import wave

import numpy as np

from .freshness import sentence_hash, voice_config
from .media import asset_path


def run_process(command,cancel,log=None):
    import tempfile
    with tempfile.TemporaryFile(mode="w+") as stream:
        process=subprocess.Popen(command,stdout=stream,stderr=stream)
        while process.poll() is None:
            if cancel.wait(.15):
                process.terminate()
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired: process.kill(); process.wait()
                raise InterruptedError()
        if process.returncode:
            stream.seek(0); message=stream.read()[-2200:]
            if log: log.write_text(message)
            raise ValueError(message)


def assemble(store,project,scene,output,cancel):
    pause=float(voice_config(project,scene)["pause"]); rate=24000
    manifest=[]; cursor=0
    with wave.open(str(output),"wb") as writer:
        writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(rate)
        for index,sentence in enumerate(scene.sentences):
            asset=next((a for a in project.assets if a.id==sentence.asset_id),None)
            if not asset or asset.kind!="audio" or asset.provenance.get("voice_hash")!=sentence_hash(project,scene,sentence.text):
                raise ValueError("Wybierz aktualny wariant zdania: "+sentence.text)
            if cancel.is_set(): raise InterruptedError()
            raw=subprocess.run(["ffmpeg","-v","error","-i",str(asset_path(store,project.id,asset.id,project=project)),"-f","s16le","-ar",str(rate),"-ac","1","pipe:1"],capture_output=True,check=True).stdout
            duration=len(raw)/2/rate
            writer.writeframes(raw)
            manifest.append({"word":sentence.text,"start":cursor,"end":cursor+duration,"method":"measured-sentence","sentence_id":sentence.id})
            cursor+=duration
            if index<len(scene.sentences)-1:
                count=round(rate*pause); writer.writeframes(b"\0\0"*count); cursor+=count/rate
    return manifest


def waveform(path,bins=240):
    bins=max(16,min(2000,int(bins)))
    result=subprocess.run(["ffmpeg","-v","error","-i",str(path),"-vn","-f","f32le","-ar","4000","-ac","1","pipe:1"],capture_output=True,check=True,timeout=90)
    samples=np.frombuffer(result.stdout,dtype="<f4")
    if not len(samples): return {"peaks":[],"duration":0}
    peaks=[round(float(np.max(np.abs(part))),4) if len(part) else 0 for part in np.array_split(samples,bins)]
    return {"peaks":peaks,"duration":len(samples)/4000,"bins":bins}


def validate_words(words,duration):
    if not isinstance(words,list) or len(words)>50000: raise ValueError("Niepoprawne znaczniki słów")
    previous=0
    for item in words:
        if not isinstance(item,dict) or not {"word","start","end"}<=set(item) or not isinstance(item["word"],str): raise ValueError("Każdy znacznik wymaga tekstu word i czasów start, end")
        try:start,end=float(item["start"]),float(item["end"])
        except (TypeError,ValueError) as error:raise ValueError("Czas znacznika musi być liczbą") from error
        if not 0<=start<end<=duration+.1 or start<previous-.01 or not str(item.get("word","")).strip():
            raise ValueError("Znaczniki muszą rosnąć i mieścić się w nagraniu")
        previous=start
    return words
