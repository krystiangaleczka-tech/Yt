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


def text_card(clip: Clip, path: Path, width: int, height: int):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", max(16, round(width * .035)))
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


def build_command(store: ProjectStore, project: Project, output: Path, *, preview=False, temp: Path | None = None) -> list[str]:
    temp = temp or output.parent
    temp.mkdir(parents=True, exist_ok=True)
    rate = fps(project)
    total = duration(project) / rate
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
    for track in project.sequence.tracks:
        if track.muted:
            continue
        for clip in sorted([c for c in project.sequence.clips if c.track_id == track.id], key=lambda c: (c.start, c.id)):
            a = assets.get(clip.asset_id)
            if track.kind != "text" and not a:
                raise ValueError(f"Brak materiału dla klipu {clip.title}")
            length, start = clip.duration / rate, clip.start / rate
            if track.kind == "text":
                path = temp / (clip.id + ".png")
                text_card(clip, path, w, h)
            else:
                path = asset_path(store, project.id, a.id)
                if not path.exists():
                    raise ValueError(f"Brakuje pliku: {a.name}")
            image = track.kind == "text" or a and a.kind == "image"
            if image:
                cmd += ["-loop", "1", "-framerate", str(rate), "-t", str(length), "-i", str(path)]
            else:
                cmd += ["-ss", str(clip.source_in / rate), "-t", str(length * clip.speed), "-i", str(path)]
            if track.kind == "audio":
                chain = f"[{index}:a]asetpts=PTS-STARTPTS"
                speed = clip.speed
                while speed > 2:
                    chain += ",atempo=2"; speed /= 2
                while speed < .5:
                    chain += ",atempo=0.5"; speed *= 2
                chain += f",atempo={speed},atrim=duration={length},volume='{expression(clip, 'volume', rate)}':eval=frame"
                if clip.fade_in:
                    chain += f",afade=t=in:st=0:d={min(length, clip.fade_in/rate)}"
                if clip.fade_out:
                    fade = min(length, clip.fade_out / rate)
                    chain += f",afade=t=out:st={length-fade}:d={fade}"
                chain += f",adelay={round(start*1000)}:all=1[a{index}]"
                filters.append(chain); audio_labels.append(f"[a{index}]")
            else:
                chain = f"[{index}:v]setpts=(PTS-STARTPTS)/{1 if image else clip.speed},fps={rate},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,format=rgba"
                scale = expression(clip, "scale", rate)
                local = "clip(t/" + str(max(length, .01)) + ",0,1)"
                if clip.animation == "zoom-in":
                    scale = f"({scale})*(1+0.08*{local})"
                elif clip.animation == "zoom-out":
                    scale = f"({scale})*(1.08-0.08*{local})"
                elif clip.animation in ("pan-left", "pan-right"):
                    scale = f"({scale})*1.1"
                chain += f",scale=w='max(2,trunc(iw*({scale})/2)*2)':h='max(2,trunc(ih*({scale})/2)*2)':eval=frame"
                if clip.rotation or any(k.property == "rotation" for k in clip.keyframes):
                    rotation = expression(clip, "rotation", rate)
                    chain += f",rotate='({rotation})*PI/180':ow='ceil(iw*1.42/2)*2':oh='ceil(ih*1.42/2)*2':c=none"
                if any(k.property == "opacity" for k in clip.keyframes):
                    opacity = expression(clip, "opacity", rate, "T")
                    chain += f",geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*({opacity})'"
                elif clip.opacity != 1:
                    chain += f",colorchannelmixer=aa={clip.opacity}"
                if clip.fade_in:
                    chain += f",fade=t=in:st=0:d={min(length,clip.fade_in/rate)}:alpha=1"
                if clip.fade_out:
                    fade = min(length, clip.fade_out / rate)
                    chain += f",fade=t=out:st={length-fade}:d={fade}:alpha=1"
                chain += f",setpts=PTS+{start}/TB[v{index}]"
                filters.append(chain)
                x = expression(clip, "x", rate, f"(t-{start})")
                y = expression(clip, "y", rate, f"(t-{start})")
                if clip.animation in ("pan-left", "pan-right"):
                    x = f"({x})+{1 if clip.animation == 'pan-right' else -1}*.05*(2*clip((t-{start})/{length},0,1)-1)"
                next_layer = f"layer{index}"
                filters.append(f"[{layer}][v{index}]overlay=x='(W-w)/2+({x})*W':y='(H-h)/2+({y})*H':eof_action=pass:repeatlast=0:enable='gte(t,{start})*lt(t,{start+length})'[{next_layer}]")
                layer = next_layer
            index += 1
    filters.append(f"[{layer}]format=yuv420p[final]")
    if audio_labels:
        filters.append("".join(audio_labels) + f"amix=inputs={len(audio_labels)}:normalize=0:duration=longest,alimiter=limit=0.95[audio]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[final]"]
    if audio_labels:
        cmd += ["-map", "[audio]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += ["-t", str(total), "-r", str(rate), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24" if preview else "20",
            "-threads", "2", "-movflags", "+faststart", "-progress", "pipe:1", "-nostats", str(output)]
    return cmd


def render(store: ProjectStore, project: Project, output: Path, progress, cancel: threading.Event, preview=False):
    command = build_command(store, project, output, preview=preview, temp=output.parent / (output.stem + "-layers"))
    total = duration(project) / fps(project)
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
            raise ValueError("FFmpeg: " + errors.read()[-2200:])
    info = probe(output)
    if not any(s.get("codec_type") == "video" for s in info.get("streams", [])):
        raise ValueError("Renderer nie utworzył poprawnego filmu")
    progress(1, "Film gotowy")
