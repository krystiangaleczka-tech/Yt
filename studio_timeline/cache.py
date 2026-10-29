"""Cache overlapping composition ranges, including audio, fonts and source bytes."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from studio_core.freshness import fingerprint
from studio_core.models import Keyframe, fps, duration
from studio_core.store import atomic_json
from studio_core.media import probe
from .operations import value_at


def slice_project(project, begin, end):
    draft=project.model_copy(deep=True)
    clips=[]
    for source in project.sequence.clips:
        first=max(begin,source.start); last=min(end,source.start+source.duration)
        if last<=first: continue
        clip=source.model_copy(deep=True); offset=first-source.start
        clip.start=first-begin; clip.duration=last-first
        clip.source_in+=round(offset*clip.speed)
        clip.parameters={**clip.parameters,"_frame_offset":source.parameters.get("_frame_offset",0)+offset,"_original_duration":source.parameters.get("_original_duration",source.duration),"_original_fade_in":source.parameters.get("_original_fade_in",source.fade_in),"_original_fade_out":source.parameters.get("_original_fade_out",source.fade_out)}
        keys=[]
        for prop in {k.property for k in source.keyframes}:
            keys.append(Keyframe(property=prop,frame=0,value=value_at(source,prop,offset)))
            keys.extend(k.model_copy(update={"frame":k.frame-offset}) for k in source.keyframes if k.property==prop and offset<k.frame<offset+clip.duration)
            keys.append(Keyframe(property=prop,frame=clip.duration,value=value_at(source,prop,offset+clip.duration)))
        clip.keyframes=keys
        clip.fade_in=max(0,source.fade_in-offset)
        clip.fade_out=max(0,source.fade_out-(source.duration-offset-clip.duration))
        if offset:
            clip.transition="cut"; clip.transition_duration=0
        else:
            clip.transition_duration=min(clip.duration,source.transition_duration)
        clips.append(clip)
    draft.sequence.clips=clips
    draft.legacy={**draft.legacy,"_render_duration":end-begin,"_force_audio":any(t.kind=="audio" and not t.muted and any(c.track_id==t.id for c in project.sequence.clips) for t in project.sequence.tracks)}
    return draft


def process(command, cancel, error_path):
    with error_path.open("w+") as log:
        child=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=log)
        while True:
            try:
                code=child.wait(timeout=.15); break
            except subprocess.TimeoutExpired:
                if cancel.is_set():
                    child.terminate()
                    try: child.wait(timeout=3)
                    except subprocess.TimeoutExpired: child.kill(); child.wait()
                    raise InterruptedError("Anulowano render")
        if code:
            log.seek(0)
            detail = log.read()[-2000:].strip() or "brak komunikatu stderr"
            raise ValueError(f"FFmpeg (etap cache, kod {code}): {detail}")


def render_cached(store, project, output, progress, cancel, preview=False, start_frame=0, end_frame=None):
    from .render import render_full
    from .templates import FONT,font_hash
    rate=fps(project); total=duration(project)
    end_frame=total if end_frame is None else min(total,int(end_frame))
    start_frame=int(start_frame)
    if start_frame<0 or end_frame<=start_frame:
        raise ValueError("Wybierz niepusty zakres wewnątrz filmu")
    folder=store.root/"cache/ranges"; folder.mkdir(parents=True,exist_ok=True)
    work=output.parent/(output.stem+"-work"); work.mkdir(parents=True,exist_ok=True)
    code_hash=fingerprint({**{str(p.relative_to(Path(__file__).parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.rglob("*") if p.suffix in (".py",".json")},"font":font_hash()})
    used={c.asset_id for c in project.sequence.clips if c.asset_id}|{a for c in project.sequence.clips for a in c.asset_ids}
    asset_hash={}
    for asset in project.assets:
        if asset.id in used:
            path=store.folder(project.id)/"media"/asset.filename
            with path.open("rb") as stream: digest=hashlib.file_digest(stream,"sha256").hexdigest()
            if digest!=asset.sha256:
                raise ValueError("Plik medium zmienił treść poza biblioteką: "+asset.name+". Zaimportuj go ponownie jako nową wersję.")
            asset_hash[asset.id]=asset.model_dump()
    chunk=max(1,round(rate*5)); parts=[]; reused=0
    ranges=list(range(start_frame,end_frame,chunk))
    guard=max((c.transition_duration for c in project.sequence.clips),default=0)+1
    for index,begin in enumerate(ranges):
        if cancel.is_set(): raise InterruptedError("Anulowano render")
        end=min(begin+chunk,end_frame); padded=max(0,begin-guard)
        draft=slice_project(project,padded,end)
        relevant={c.asset_id for c in draft.sequence.clips if c.asset_id}|{a for c in draft.sequence.clips for a in c.asset_ids}
        key=fingerprint({"renderer":code_hash,"sequence":draft.sequence.model_dump(),"range":[begin-padded,end-padded],"assets":{k:asset_hash[k] for k in relevant},"preview":preview,"style":project.channel_profile,"force_audio":draft.legacy["_force_audio"]})
        part=folder/(key+".mkv")
        if part.is_file():
            reused+=1
        else:
            full=work/(key+"-full.mkv")
            render_full(store,draft,full,lambda value,message:progress((index+value*.75)/len(ranges)*.95,message),cancel,preview)
            temporary=part.with_suffix(".part.mkv")
            try:
                process(["ffmpeg","-v","error","-y","-ss",str((begin-padded)/rate),"-i",str(full),"-t",str((end-begin)/rate),"-map","0:v","-map","0:a?","-c:v","libx264","-preset","veryfast","-crf","20","-threads","2","-c:a","pcm_s16le",str(temporary)],cancel,work/"trim.log")
                info=probe(temporary)
                if abs(float(info["format"]["duration"])-(end-begin)/rate)>max(.12,2/rate):
                    raise ValueError("Cache ma niepoprawny czas trwania")
                temporary.replace(part)
            finally:
                temporary.unlink(missing_ok=True); full.unlink(missing_ok=True)
        parts.append(part)
        progress((index+1)/len(ranges)*.95,f"Zakres {index+1}/{len(ranges)} · z cache: {reused}")
    listing=work/"concat.txt"
    listing.write_text("\n".join("file '"+str(path).replace("'","'\\''")+"'" for path in parts))
    temporary=output.with_suffix(".part.mp4")
    try:
        process(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(listing),"-t",str((end_frame-start_frame)/rate),"-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart",str(temporary)],cancel,work/"mux.log")
        info=probe(temporary)
        if abs(float(info["format"]["duration"])-(end_frame-start_frame)/rate)>max(.15,2/rate):
            raise ValueError("Gotowy plik ma niepoprawny czas trwania")
        temporary.replace(output)
        atomic_json(output.with_suffix(".cache.json"),{"ranges":len(parts),"reused":reused,"revision":project.revision,"start_frame":start_frame,"end_frame":end_frame})
    finally:
        temporary.unlink(missing_ok=True)
    progress(1,f"Film gotowy · {reused}/{len(parts)} zakresów z cache")
