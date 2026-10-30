"""One FFmpeg compositor for accurate previews and final exports."""
from __future__ import annotations

import json
import math
import subprocess
import threading
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from studio_core.models import Project, Clip, fps, duration
from studio_core.media import asset_path, probe
from studio_core.store import ProjectStore
from .templates import template_video, FONT,FONTS


def expression(clip: Clip, prop: str, rate: float, variable="t") -> str:
    points = sorted([k for k in clip.keyframes if k.property == prop], key=lambda k: k.frame)
    base = getattr(clip, prop)
    if not points:
        return str(base)
    if points[0].frame != 0:
        points.insert(0, type(points[0])(property=prop, frame=0, value=base))
    expr = str(points[-1].value)
    for left, right in reversed(list(zip(points, points[1:]))):
        a, b = left.frame / rate, right.frame / rate
        if b <= a:
            continue
        linear = f"({left.value}+({right.value-left.value})*clip(({variable}-{a})/{b-a},0,1))"
        expr = f"if(lt({variable},{b}),{linear},{expr})"
    return expr


def text_card(clip: Clip, path: Path, width: int, height: int,face=FONT):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(str(face), max(16, round(width * .035)))
    except OSError:
        font = ImageFont.load_default(size=max(16, round(width * .035)))
    lines, current = [], ""
    for word in (clip.text or clip.title).split():
        proposal = (current + " " + word).strip()
        if draw.textlength(proposal, font=font) > width * .8 and current:
            lines.append(current); current = word
        else:
            current = proposal
    lines.append(current)
    text = "\n".join(lines[:10])
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=12, align="center")
    x, y = (width - bbox[2]) / 2, (height - bbox[3]) / 2
    draw.rounded_rectangle((width * .07, y - 28, width * .93, y + bbox[3] + 32), radius=12, fill=(12, 16, 22, 210))
    draw.multiline_text((x, y), text, font=font, fill=(244, 242, 235), spacing=12, align="center")
    image.save(path)


def envelope(clip,rate,variable):
    offset=clip.parameters.get("_frame_offset",0)/rate
    length=clip.parameters.get("_original_duration",clip.duration)/rate
    fade_in=clip.parameters.get("_original_fade_in",clip.fade_in)/rate
    fade_out=clip.parameters.get("_original_fade_out",clip.fade_out)/rate
    incoming=f"clip(({variable}+{offset})/{fade_in},0,1)" if fade_in else "1"
    outgoing=f"clip(({length}-{variable}-{offset})/{fade_out},0,1)" if fade_out else "1"
    return f"min({incoming},{outgoing})"


def build_command(store: ProjectStore, project: Project, output: Path, *, preview=False, temp: Path | None = None, cancel=None) -> list[str]:
    temp = temp or output.parent
    temp.mkdir(parents=True, exist_ok=True)
    rate = fps(project)
    total = project.legacy.get("_render_duration", duration(project)) / rate
    if total <= 0:
        raise ValueError("Oś czasu jest pusta")
    w, h = project.sequence.width, project.sequence.height
    if preview:
        factor = min(1, 640 / w)
        w, h = max(144, round(w * factor / 2) * 2), max(144, round(h * factor / 2) * 2)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-filter_complex_threads", "1", "-f", "lavfi", "-i",
           f"color=c=0x101318:s={w}x{h}:r={project.sequence.fps_num}/{project.sequence.fps_den}:d={total}"]
    filters, audio_labels, layer = [], [], "0:v"
    index = 1
    assets = {a.id: a for a in project.assets}
    solo = any(t.solo for t in project.sequence.tracks)
    audible = [t for t in project.sequence.tracks if not t.muted and (not solo or t.solo)]
    narration = [c for c in project.sequence.clips if any(t.id == c.track_id and t.role == "narration" for t in audible)]
    for track in project.sequence.tracks:
        if track.muted or solo and not track.solo:
            continue
        for clip in sorted([c for c in project.sequence.clips if c.track_id == track.id], key=lambda c: (c.start, c.id)):
            a = assets.get(clip.asset_id)
            if track.kind != "text" and not a and clip.template == "media":
                raise ValueError(f"Brak materiału dla klipu {clip.title}")
            length, start = clip.duration / rate, clip.start / rate
            procedural = track.kind == "video" and clip.template != "media"
            if procedural:
                path = template_video(store, project, clip, w, h, rate, cancel)
            elif track.kind == "text":
                path = temp / (clip.id + ".png")
                text_card(clip, path, w, h,FONTS.get(project.channel_profile.get("font"),FONT))
            else:
                path = asset_path(store, project.id, a.id,project=project)
                if not path.exists():
                    raise ValueError(f"Brakuje pliku: {a.name}")
            image = track.kind == "text" or not procedural and a and a.kind == "image"
            if image:
                cmd += ["-loop", "1", "-framerate", str(rate), "-t", str(length), "-i", str(path)]
            else:
                cmd += ["-ss", str(0 if procedural else clip.source_in / rate), "-t", str(length * (1 if procedural else clip.speed)), "-i", str(path)]
            if track.kind == "audio":
                chain = f"[{index}:a]asetpts=PTS-STARTPTS"
                speed = clip.speed
                while speed > 2:
                    chain += ",atempo=2"; speed /= 2
                while speed < .5:
                    chain += ",atempo=0.5"; speed *= 2
                chain += f",atempo={speed},atrim=duration={length},volume='{expression(clip, 'volume', rate)}':eval=frame"
                if project.sequence.ducking and track.role == "music" and narration:
                    intervals = "+".join(f"between(t,{max(0,(c.start-clip.start)/rate)},{min(length,(c.start+c.duration-clip.start)/rate)})" for c in narration if c.start < clip.start+clip.duration and c.start+c.duration > clip.start)
                    if intervals:
                        chain += f",volume='if(gt({intervals},0),{project.sequence.ducking_gain},1)':eval=frame"
                chain += f",volume='{envelope(clip,rate,'t')}':eval=frame"
                chain += f",adelay={round(start*1000)}:all=1[a{index}]"
                filters.append(chain); audio_labels.append(f"[a{index}]")
            else:
                chain = f"[{index}:v]setpts=(PTS-STARTPTS)/{1 if image or procedural else clip.speed},fps={rate},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,format=rgba"
                if clip.crop:
                    x,y,cw,ch = (clip.crop.get(k, default) for k,default in (("x",0),("y",0),("width",1),("height",1)))
                    chain += f",crop=w=iw*{cw}:h=ih*{ch}:x=iw*{x}:y=ih*{y},scale={w}:{h}"
                scale = expression(clip, "scale", rate)
                offset = clip.parameters.get("_frame_offset", 0)/rate
                original_length = clip.parameters.get("_original_duration", clip.duration)/rate
                local = f"clip((t+{offset})/{max(original_length,.01)},0,1)"
                if clip.animation == "zoom-in":
                    scale = f"({scale})*(1+0.08*{local})"
                elif clip.animation == "zoom-out":
                    scale = f"({scale})*(1.08-0.08*{local})"
                elif clip.animation in ("pan-left", "pan-right"):
                    scale = f"({scale})*1.1"
                if clip.transition == "zoom" and clip.transition_duration:
                    scale = f"({scale})*(1.15-.15*clip(t/{clip.transition_duration/rate},0,1))"
                chain += f",scale=w='max(2,trunc(iw*({scale})/2)*2)':h='max(2,trunc(ih*({scale})/2)*2)':eval=frame"
                if clip.rotation or any(k.property == "rotation" for k in clip.keyframes):
                    rotation = expression(clip, "rotation", rate)
                    chain += f",rotate='({rotation})*PI/180':ow='ceil(iw*1.42/2)*2':oh='ceil(ih*1.42/2)*2':c=none"
                # FFmpeg may segfault when a dynamic scale feeds geq alpha on packed RGBA.
                # Convert explicitly to planar GBR+alpha before geq (including fades/wipes).
                chain += ",format=gbrap"
                if any(k.property == "opacity" for k in clip.keyframes):
                    opacity = expression(clip, "opacity", rate, "T")
                    chain += f",geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*({opacity})'"
                elif clip.opacity != 1:
                    chain += f",colorchannelmixer=aa={clip.opacity}"
                transition_length = min(length, clip.transition_duration/rate) if clip.transition != "cut" else 0
                chain += f",geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*({envelope(clip,rate,'T')})'"
                fade_length = transition_length if clip.transition in ("dissolve", "fade-black", "zoom") else 0
                if fade_length:
                    chain += f",fade=t=in:st=0:d={fade_length}:alpha=1"
                if transition_length and clip.transition in ("wipe-left", "wipe-right"):
                    reveal = f"(T/{transition_length})*W"
                    predicate = f"lt(X,{reveal})" if clip.transition == "wipe-right" else f"gt(X,W-{reveal})"
                    chain += f",geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*if(lt(T,{transition_length}),{predicate},1)'"
                chain += f",setpts=PTS+{start}/TB[v{index}]"
                filters.append(chain)
                x = expression(clip, "x", rate, f"(t-{start})")
                y = expression(clip, "y", rate, f"(t-{start})")
                if transition_length and clip.transition in ("slide-left", "slide-right"):
                    x = f"({x})+{1 if clip.transition == 'slide-left' else -1}*(1-clip((t-{start})/{transition_length},0,1))"
                if clip.animation in ("pan-left", "pan-right"):
                    x = f"({x})+{1 if clip.animation == 'pan-right' else -1}*.05*(2*clip((t-{start}+{offset})/{original_length},0,1)-1)"
                next_layer = f"layer{index}"
                next_clip = next((c for c in project.sequence.clips if c.track_id == clip.track_id and c.start == clip.start+clip.duration and c.transition not in ("cut", "fade-black") and c.transition_duration), None)
                hold = next_clip.transition_duration/rate if next_clip else 0
                if hold:
                    filters[-1] = filters[-1].replace(f",setpts=PTS+{start}/TB", f",tpad=stop_mode=clone:stop_duration={hold},setpts=PTS+{start}/TB")
                filters.append(f"[{layer}][v{index}]overlay=x='(W-w)/2+({x})*W':y='(H-h)/2+({y})*H':eof_action=pass:repeatlast=0:enable='gte(t,{start})*lt(t,{start+length+hold})'[{next_layer}]")
                layer = next_layer
            index += 1
    filters.append(f"[{layer}]format=yuv420p[final]")
    if not audio_labels and project.legacy.get("_force_audio"):
        cmd += ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=48000:cl=stereo"]
        filters.append(f"[{index}:a]anull[silence]"); audio_labels.append("[silence]")
    if audio_labels:
        filters.append("".join(audio_labels) + f"amix=inputs={len(audio_labels)}:normalize=0:duration=longest,alimiter=limit=0.95,apad,atrim=duration={total}[audio]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[final]"]
    if audio_labels:
        cmd += ["-map", "[audio]", "-c:a", "pcm_s16le" if output.suffix == ".mkv" else "aac", "-ar", "48000", "-ac", "2"]
    cmd += ["-t", str(total), "-r", str(rate), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24" if preview else "20",
            "-threads", "2", *([] if output.suffix == ".mkv" else ["-movflags", "+faststart"]), "-progress", "pipe:1", "-nostats", str(output)]
    return cmd


def render_full(store: ProjectStore, project: Project, output: Path, progress, cancel: threading.Event, preview=False):
    command = build_command(store, project, output, preview=preview, temp=output.parent / (output.stem + "-layers"), cancel=cancel)
    total = project.legacy.get("_render_duration", duration(project)) / fps(project)
    error_path = output.with_suffix(".log")
    with error_path.open("w+") as errors:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors, text=True)
        def terminate():
            while process.poll() is None:
                if cancel.wait(.25):
                    process.terminate()
                    try:
                        process.wait(timeout=4)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break
        monitor = threading.Thread(target=terminate, daemon=True); monitor.start()
        for line in process.stdout:
            if line.startswith("out_time_us="):
                try:
                    progress(min(.99, int(line.split("=")[1]) / 1_000_000 / total), "Renderowanie filmu")
                except ValueError:
                    pass
        process.stdout.close()
        code = process.wait(); monitor.join(timeout=.5)
        if cancel.is_set():
            output.unlink(missing_ok=True)
            raise InterruptedError("Anulowano render")
        if code:
            errors.seek(0)
            detail = errors.read()[-2200:].strip() or "brak komunikatu stderr"
            raise ValueError(f"FFmpeg (kompozycja, kod {code}): {detail}")
    info = probe(output)
    if not any(s.get("codec_type") == "video" for s in info.get("streams", [])):
        raise ValueError("Renderer nie utworzył poprawnego filmu")
    if abs(float(info.get("format", {}).get("duration", 0))-total) > max(.12,2/fps(project)):
        raise ValueError("Długość renderu nie odpowiada osi czasu")
    if project.legacy.get("_force_audio") and not any(s.get("codec_type") == "audio" for s in info.get("streams", [])):
        raise ValueError("W renderze brakuje zaplanowanej ścieżki audio")
    progress(1, "Film gotowy")


def render(store, project, output, progress, cancel, preview=False, start_frame=0, end_frame=None):
    from studio_core.paper_theatre_review import require_export_approval
    require_export_approval(store, project)
    from .cache import render_cached
    return render_cached(store, project, output, progress, cancel, preview, start_frame, end_frame)
