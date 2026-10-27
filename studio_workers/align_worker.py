"""Local ASR word timing. Recognized text is reviewable, never fabricated timing."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("audio"); parser.add_argument("output")
    parser.add_argument("--language",default="pl"); parser.add_argument("--model",default="small")
    args=parser.parse_args()
    from faster_whisper import WhisperModel
    model=WhisperModel(args.model,device="cpu",compute_type="int8")
    segments,info=model.transcribe(args.audio,language=args.language,word_timestamps=True,beam_size=5,vad_filter=True)
    words=[]
    for segment in segments:
        for word in segment.words or []:
            if word.end>word.start:
                words.append({"word":word.word.strip(),"start":round(word.start,3),"end":round(word.end,3),"probability":round(word.probability,3)})
    if not words: raise ValueError("Nie rozpoznano mowy. Sprawdź nagranie i język.")
    Path(args.output).write_text(json.dumps({"words":words,"language":info.language,"model":args.model,"method":"faster-whisper-ASR"},ensure_ascii=False))


if __name__=="__main__": main()
