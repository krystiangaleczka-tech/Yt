"""Parameterized documentary shots; real media/audio, no topic-specific facts."""
from __future__ import annotations

import hashlib
import math
import subprocess
import json
import re
from functools import lru_cache
from contextlib import ExitStack
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from studio_core.freshness import fingerprint
from studio_core.media import asset_path, probe
from studio_core.templates import validate_parameters
from studio_core.models import fps
from .paper_theatre import rig_image

FONT = Path(__file__).resolve().parents[1] / "pilot/fonts/Montserrat.ttf"
FONTS={"montserrat":FONT,"courier":FONT.with_name("CourierPrime-Regular.ttf"),"courier-bold":FONT.with_name("CourierPrime-Bold.ttf")}
LAND = Path(__file__).parent/"data/land-110m.json"


@lru_cache(maxsize=1)
def land(): return json.loads(LAND.read_text())


def font_hash():return fingerprint({name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in FONTS.items()})


def font(size,path=FONT):
    return ImageFont.truetype(str(path), max(9, round(size)))


def wrap(draw, text, face, width):
    lines, line = [], ""
    for word in str(text).split():
        trial = (line+" "+word).strip()
        if line and draw.textlength(trial, font=face) > width:
            lines.append(line); line = word
        else:
            line = trial
    return "\n".join(lines+[line])


class MediaFrames:
    def __init__(self, store, project, clip, w, h, rate):
        self.images = []; self.streams = []; self.last = {}; self.w=w; self.h=h
        assets = {a.id: a for a in project.assets}
        ids = list(dict.fromkeys(([clip.asset_id] if clip.asset_id else []) + clip.asset_ids))
        self.audio = np.zeros(0, dtype=np.float32)
        self.spectrum=None
        self.speed=clip.speed
        offset=clip.parameters.get("_frame_offset",0)
        for aid in ids:
            asset = assets[aid]; path = asset_path(store, project.id, aid,project=project)
            if asset.kind == "image":
                self.images.append(Image.open(path).convert("RGBA")); self.streams.append(None)
            elif asset.kind == "video":
                source=clip.parameters["source_in"]+offset/rate*clip.speed if "source_in" in clip.parameters else clip.source_in/rate
                command = ["ffmpeg", "-v", "error", "-ss", str(source), "-i", str(path), "-vf", f"setpts=(PTS-STARTPTS)/{clip.speed},fps={rate},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}", "-pix_fmt", "rgba", "-f", "rawvideo", "pipe:1"]
                self.streams.append(subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)); self.images.append(None)
            elif asset.kind == "audio":
                base=clip.parameters.get("source_in",(clip.source_in-round(offset*clip.speed))/rate)
                original=clip.parameters.get("span") or clip.parameters.get("_original_duration",clip.duration)/rate
                result = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(base), "-i", str(path), "-t", str(original*clip.speed+1), "-ac", "1", "-ar", "16000", "-f", "f32le", "pipe:1"], capture_output=True, check=True)
                self.audio = np.frombuffer(result.stdout, dtype=np.float32)

    def frame(self, index, n):
        if index >= len(self.images):
            return None
        process = self.streams[index]
        if process:
            data = process.stdout.read(self.w*self.h*4)
            if len(data) == self.w*self.h*4:
                self.last[index] = Image.frombytes("RGBA", (self.w,self.h), data)
            return self.last.get(index)
        return self.images[index]

    def close(self):
        for process in self.streams:
            if process:
                process.stdout.close(); process.terminate()
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired: process.kill(); process.wait()
        for image in self.images:
            if image: image.close()


def paint(clip, params, media, n, w, h, rate, style=None):
    style = style or {}
    image = Image.new("RGBA", (w,h), "#10151e"); draw = ImageDraw.Draw(image)
    accent = str(style.get("color", "#b6baf0"))
    if not re.fullmatch(r"#[0-9a-fA-F]{6}",accent):
        accent = "#b6baf0"
    face=FONTS.get(style.get("font"),FONT)
    small, normal, large = font(w*.019,face), font(w*.033,face), font(w*.065,face)
    seconds = (n+clip.parameters.get("_frame_offset", 0))/rate
    original_duration = clip.parameters.get("_original_duration", clip.duration)/rate
    phase = min(1, seconds/max(.01, original_duration))
    kind = clip.template
    def text(value, y, face=normal, color="#edf1f7", x=None):
        value = wrap(draw, value, face, w*.82)
        box = draw.multiline_textbbox((0,0),value,font=face,spacing=max(4,round(w*.008)),align="center")
        draw.multiline_text(((w-box[2])/2 if x is None else x,y),value,font=face,fill=color,spacing=max(4,round(w*.008)),align="center")
    def picture(index, box, zoom=1, center=(.5,.5)):
        source = media.frame(index, n)
        if source is None:
            raise ValueError("Szablon "+kind+" wymaga wybrania właściwego medium")
        x,y,r,b = [round(v) for v in box]
        crop = ImageOps.fit(source,(max(1,r-x),max(1,b-y)),centering=center)
        if zoom != 1:
            cw,ch = round(crop.width/zoom),round(crop.height/zoom)
            cx,cy = crop.width*center[0],crop.height*center[1]
            left=max(0,min(crop.width-cw,cx-cw/2)); top=max(0,min(crop.height-ch,cy-ch/2))
            crop=crop.crop((left,top,left+cw,top+ch)).resize((r-x,b-y))
        image.alpha_composite(crop,(x,y))
    if kind=="media":
        picture(0,(0,0,w,h))
    elif kind in ("document", "lower-third", "loupe"):
        zoom = 1+(params.get("zoom",2)-1)*phase if kind=="loupe" else 1+.05*phase
        picture(0,(0,0,w,h),zoom,(params.get("x",.5),params.get("y",.5)))
        draw = ImageDraw.Draw(image)
        if kind=="lower-third":
            draw.rectangle((w*.04,h*.65,w*.85,h*.86),fill="#10151ee8")
            draw.rectangle((w*.04,h*.65,w*.047,h*.86),fill=accent)
            draw.text((w*.07,h*.68),params.get("text",""),font=normal,fill="#ffffff")
            draw.text((w*.07,h*.76),params.get("subtitle",""),font=small,fill="#b8c6da")
        if kind=="loupe":
            size=max(12,w*.08*(1-phase))
            cx,cy=w*params.get("x",.5),h*params.get("y",.5)
            draw.rectangle((cx-size,cy-size,cx+size,cy+size),outline=accent,width=max(1,w//300))
    elif kind in ("split", "comparison"):
        picture(0,(0,0,w/2-3,h)); picture(1,(w/2+3,0,w,h)); draw=ImageDraw.Draw(image)
        for label,x in ((params.get("left",""),w*.04),(params.get("right",""),w*.54)):
            draw.rectangle((x-5,h*.77,x+w*.42,h*.89),fill="#10151ee8")
            draw.text((x,h*.8),label,font=small,fill="#ffffff")
    elif kind in ("stack", "parallax"):
        if kind=="parallax":
            picture(0,(0,0,w,h))
            cues = {cue["layer"]: cue for cue in params.get("layer_cues", [])}
            # A mechanical cue must not accidentally fade unrelated legacy layers.
            assembling = bool(params.get("assembly_start", 0) or params.get("assembly_interval", 0) or any(cue.get("rig", "sequential") == "sequential" for cue in cues.values()))
            for i in range(1, len(media.images)):
                cue = cues.get(i, {})
                start = cue.get("start", params.get("assembly_start", 0) + (i - 1) * params.get("assembly_interval", 0))
                if assembling and seconds < start:
                    continue
                layer = media.frame(i, n)
                if layer:
                    duration = cue.get("duration", params.get("assembly_duration", .35))
                    layer = layer.resize((w, h))
                    depth = cue.get("depth", i)
                    shift = round((phase - .5) * w * params.get("depth", .06) * depth)
                    rig = cue.get("rig", "sequential")
                    if rig != "sequential":
                        image.alpha_composite(
                            rig_image(layer, rig, cue, seconds - start, duration),
                            (shift, 0),
                        )
                        continue
                    # Legacy sequential entrance intentionally stays pixel-compatible.
                    reveal = 1.0
                    if assembling:
                        fraction = min(1.0, max(0.0, (seconds - start) / duration)) if duration else 1.0
                        reveal = fraction * fraction * (3 - 2 * fraction)
                    if reveal < 1:
                        layer.putalpha(layer.getchannel("A").point(lambda alpha: round(alpha * reveal)))
                    drop = round((1 - reveal) * h * cue.get("drop", params.get("assembly_drop", .06))) if assembling else 0
                    image.alpha_composite(layer, (shift, drop))
        else:
            for i in range(min(len(media.images), max(1,math.ceil(phase*len(media.images))))):
                source=media.frame(i,n)
                if source:
                    card=ImageOps.fit(source,(round(w*.65),round(h*.7)))
                    card=ImageOps.expand(card,border=max(2,w//100),fill="white").rotate((i%3-1)*5,expand=True)
                    image.alpha_composite(card,(round(w*.14+i*w*.025),round(h*.12+i*h*.018)))
    elif kind in ("waveform", "spectrogram"):
        if not len(media.audio):
            raise ValueError("Wybierz rzeczywiste nagranie audio dla oscylogramu lub spektrogramu")
        if kind=="waveform":
            head=round(seconds*media.speed*16000); samples=media.audio[max(0,head-8000):head+8000]
            if len(samples):
                values=np.array([np.max(np.abs(chunk)) if len(chunk) else 0 for chunk in np.array_split(samples,max(1,w//3))])
                for i,value in enumerate(values):
                    x=i*3; amplitude=float(value)*h*.38
                    draw.line((x,h/2-amplitude,x,h/2+amplitude),fill=accent,width=2)
        else:
            if media.spectrum is None:
                signal=media.audio; window=512; hop=max(128,len(signal)//max(w*2,1))
                if len(signal)<window: signal=np.pad(signal,(0,window-len(signal)))
                frames=np.lib.stride_tricks.sliding_window_view(signal,window)[::hop]
                spectrum=np.abs(np.fft.rfft(frames*np.hanning(window),axis=1)).T
                spectrum=spectrum[:max(2,round(params.get("max_hz",2000)/16000*window))]
                values=np.clip((20*np.log10(spectrum+1e-7)+65)/70,0,1)[::-1]
                rgb=np.stack((values*.6,values*.85,values),axis=-1)
                media.spectrum=Image.fromarray(np.uint8(rgb*255)).resize((w,round(h*.76)))
            spec=media.spectrum
            image.paste(spec,(0,round(h*.1))); draw=ImageDraw.Draw(image)
            x=round(w*phase); draw.line((x,h*.1,x,h*.86),fill="white",width=max(1,w//400))
    elif kind=="map":
        west,south,east,north=params["bounds"]
        def point(lon,lat): return (w*.08+(float(lon)-west)/(east-west)*w*.84,h*.12+(north-float(lat))/(north-south)*h*.72)
        layer=Image.new("RGBA",(w,h)); coast=ImageDraw.Draw(layer)
        for polygon in land():
            if max(p[0] for p in polygon)<west or min(p[0] for p in polygon)>east or max(p[1] for p in polygon)<south or min(p[1] for p in polygon)>north: continue
            coast.polygon([point(*p) for p in polygon],fill="#28374a",outline="#58657a")
        mask=Image.new("L",(w,h));ImageDraw.Draw(mask).rectangle((w*.08,h*.12,w*.92,h*.84),fill=255)
        image.paste(layer,(0,0),Image.composite(layer.getchannel("A"),Image.new("L",(w,h)),mask));draw=ImageDraw.Draw(image)
        for i in range(9):
            x=w*.08+i*w*.105; draw.line((x,h*.12,x,h*.84),fill="#283348")
            draw.text((x,h*.85),f"{west+i*(east-west)/8:.0f}°",font=small,fill="#9aabc2")
        for i in range(5):
            y=h*.12+i*h*.18; draw.line((w*.08,y,w*.92,y),fill="#283348")
        routes=params.get("routes",[])
        if len(routes)>1:
            draw.line([point(*p) for p in routes],fill=accent,width=max(2,w//200))
        for item in params["points"][:max(1,math.ceil(phase*len(params["points"])) )]:
            x,y=point(item["lon"],item["lat"]); r=max(3,w*.005)
            draw.ellipse((x-r,y-r,x+r,y+r),fill=accent)
            draw.text((x+r+4,y),str(item.get("label","")),font=small,fill="white")
    elif kind=="diagram":
        nodes={str(node["id"]): node for node in params["nodes"]}
        for a,b in params["edges"]:
            if str(a) in nodes and str(b) in nodes:
                first,second=nodes[str(a)],nodes[str(b)]
                draw.line((first.get("x",.5)*w,first.get("y",.5)*h,second.get("x",.5)*w,second.get("y",.5)*h),fill=accent,width=max(2,w//300))
        for node in nodes.values():
            x,y=node.get("x",.5)*w,node.get("y",.5)*h
            draw.rounded_rectangle((x-w*.12,y-h*.06,x+w*.12,y+h*.06),radius=6,fill="#2a3450",outline=accent)
            draw.text((x,y),str(node.get("text","")),font=small,anchor="mm",fill="white")
        text(params.get("text",""),h*.04,small)
    elif kind in ("timeline", "cards"):
        items=params.get("events",[]) if kind=="timeline" else params.get("items",[])
        for i,item in enumerate(items[:6]):
            y=h*.12+i*h*.115
            draw.rounded_rectangle((w*.08,y,w*.92,y+h*.09),radius=5,fill="#253049")
            value=(str(item.get("date",""))+"  "+str(item.get("text",""))) if isinstance(item,dict) else str(item)
            draw.text((w*.11,y+h*.015),value,font=small,fill="white")
    elif kind=="counter":
        value=params["from"]+(params["to"]-params["from"])*min(1,phase*1.7)
        text(f"{value:,.0f} {params.get('unit','')}",h*.34,large,accent)
    elif kind=="qa":
        text(params.get("question",""),h*.2,normal,accent)
        if phase>.25: text(params.get("answer",""),h*.43,normal)
        text(params.get("author",""),h*.75,small)
    else:
        value=params.get("text","")
        if kind=="slogan": value=" ".join(value.split()[:max(1,math.ceil(phase*len(value.split())))])
        if kind=="press":
            draw.rectangle((w*.06,h*.08,w*.94,h*.87),fill="#e5e1d7"); text(value,h*.24,normal,"#24262c")
            text(params.get("publication",""),h*.72,small,"#4c5060")
        else:
            draw.line((w*.12,h*.18,w*.26,h*.18),fill=accent,width=max(2,w//150))
            text(value,h*.29,large if kind=="title" else normal)
            if kind=="quote": text(params.get("author",""),h*.73,small,accent)
    caption=params.get("caption","")
    if caption:
        draw=ImageDraw.Draw(image); draw.rectangle((0,h*.94,w,h),fill="#10151ef0")
        draw.text((w*.03,h*.95),str(caption)[:170],font=font(w*.014,face),fill="#c3cddd")
    return image.convert("RGB")


def template_video(store, project, clip, w, h, rate, cancel=None):
    params=validate_parameters(clip.template,clip.parameters)
    ids=set(clip.asset_ids+([clip.asset_id] if clip.asset_id else []))
    assets=[a.model_dump() for a in project.assets if a.id in ids]
    key=fingerprint({"renderer":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"land":hashlib.sha256(LAND.read_bytes()).hexdigest(),"clip":clip.model_dump(),"assets":assets,"size":[w,h,rate],"style":project.channel_profile,"font":font_hash()})
    folder=store.root/"cache/templates"; folder.mkdir(parents=True,exist_ok=True)
    path=folder/(key+".mp4")
    if path.is_file(): return path
    temporary=path.with_suffix(".part.mp4")
    media=MediaFrames(store,project,clip,w,h,rate)
    process=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r",str(rate),"-i","pipe:0","-an","-c:v","libx264","-preset","veryfast","-crf","18","-threads","2","-pix_fmt","yuv420p",str(temporary)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for frame in range(clip.duration):
            if cancel and cancel.is_set(): raise InterruptedError("Anulowano szablon")
            process.stdin.write(paint(clip,params,media,frame,w,h,rate,project.channel_profile).tobytes())
        process.stdin.close()
        error=process.stderr.read(); code=process.wait()
        if code: raise ValueError("Szablon: "+error.decode(errors="replace")[-1000:])
        if not probe(temporary).get("streams"): raise ValueError("Niepoprawny wynik szablonu")
        temporary.replace(path)
        return path
    finally:
        media.close()
        if process.poll() is None: process.kill(); process.wait()
        process.stderr.close(); temporary.unlink(missing_ok=True)
