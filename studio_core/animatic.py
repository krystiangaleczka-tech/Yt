"""Animatic export: composes scene layers frame by frame (PIL) and encodes MP4 with FFmpeg.

Motion presets mirror the browser preview (apps/studio/src/studio.css) so the export matches what
the director approved: camera push/pull/pan/shake, foreground parallax, actor enter/exit/breathing,
props that appear or fade in, burned-in captions and Kokoro draft voices.
"""
from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = Path(__file__).resolve().parents[1] / "pilot/fonts/Montserrat.ttf"
RATE = 44100
DUCK = .35  # music level under dialogue
GAP = .15  # seconds between spoken lines, as in the player


def ordered_scenes(project):
    """Story order: scenes of each beat in beat order, then scenes without a beat."""
    beats = [b.id for b in project.beats]
    return [s for b in beats for s in project.stage_scenes if s.beat_id == b] + [s for s in project.stage_scenes if s.beat_id not in beats]


def ease(t):
    t = min(1, max(0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(1, max(0, t))
    return 1 - (1 - t) ** 2


def decode(path: Path) -> np.ndarray:
    """Any audio file -> mono float32 at RATE (FFmpeg handles format and resampling)."""
    run = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(RATE), "-"],
                         capture_output=True, timeout=300, check=False)
    if run.returncode:
        raise ValueError(f"Nie udało się odczytać dźwięku {path.name}")
    return np.frombuffer(run.stdout, dtype=np.float32).copy()


def moving_average(signal: np.ndarray, width: int) -> np.ndarray:
    total = np.concatenate([[0], np.cumsum(signal, dtype=np.float64)])
    half = width // 2
    lo = np.clip(np.arange(len(signal)) - half, 0, len(signal))
    hi = np.clip(np.arange(len(signal)) + half + 1, 0, len(signal))
    return ((total[hi] - total[lo]) / np.maximum(1, hi - lo)).astype(np.float32)


def fades(length: int, fade_in: float, fade_out: float) -> np.ndarray:
    gain = np.ones(length, dtype=np.float32)
    a, b = min(length, int(fade_in * RATE)), min(length, int(fade_out * RATE))
    if a:
        gain[:a] *= np.linspace(0, 1, a, dtype=np.float32)
    if b:
        gain[length - b:] *= np.linspace(1, 0, b, dtype=np.float32)
    return gain


class Mixer:
    """Builds the soundtrack scene by scene so long films never hold the whole mix in memory."""

    def __init__(self, project, timeline, sounds, audio_path):
        self.sounds, self.audio_path, self.cache = sounds, audio_path, {}
        index = {item["scene"].id: i for i, item in enumerate(timeline)}
        self.music = []
        for cue in project.music_cues:
            sound = sounds.get(cue.sound_id)
            if not sound or cue.from_scene_id not in index or cue.to_scene_id not in index:
                continue
            first, last = sorted((index[cue.from_scene_id], index[cue.to_scene_id]))
            begin = timeline[first]["start"]
            end = timeline[last]["start"] + timeline[last]["duration"]
            self.music.append((cue, sound, begin, end))

    def data(self, sound):
        if sound.file not in self.cache:
            self.cache[sound.file] = decode(self.audio_path(sound.file))
        return self.cache[sound.file]

    @staticmethod
    def loop(data, start, length):
        if not len(data):
            return np.zeros(length, dtype=np.float32)
        return data[(np.arange(length) + start) % len(data)]

    def scene(self, item):
        n = max(1, round(item["duration"] * RATE))
        voice = np.zeros(n, dtype=np.float32)
        for line in item["lines"]:
            if line["audio"]:
                data = decode(Path(line["audio"]))
                at = int(line["start"] * RATE)
                voice[at:at + len(data)] += data[:max(0, n - at)]
        effects = np.zeros(n, dtype=np.float32)
        for cue in item["scene"].audio:
            sound = self.sounds.get(cue.sound_id)
            if not sound:
                continue
            data, gain = self.data(sound), cue.volume * sound.volume
            if sound.kind == "ambience":
                effects += self.loop(data, 0, n) * fades(n, .3, .3) * gain * .35
            else:
                at = int(cue.at * item["duration"] * RATE)
                effects[at:at + len(data)] += data[:max(0, n - at)] * gain
        music = np.zeros(n, dtype=np.float32)
        scene_start, scene_end = item["start"], item["start"] + item["duration"]
        for cue, sound, begin, end in self.music:
            if end <= scene_start or begin >= scene_end:
                continue
            offset = int((scene_start - begin + cue.offset) * RATE)
            track = self.loop(self.data(sound), offset, n)
            # Fades at the start and end of the whole range, not every scene.
            t = scene_start + np.arange(n, dtype=np.float32) / RATE
            ramp = np.clip((t - begin) / 1.0, 0, 1) * np.clip((end - t) / 1.5, 0, 1)
            music += track * ramp * cue.volume * sound.volume
        if music.any():
            speech = moving_average((np.abs(voice) > .01).astype(np.float32), int(.35 * RATE))
            music *= 1 - (1 - DUCK) * np.clip(speech * 3, 0, 1)
        return np.clip(voice + effects + music, -1, 1)


class Images:
    def __init__(self, cast, channel_id):
        self.cast, self.channel_id, self.cache = cast, channel_id, {}

    def get(self, file, height=None, width=None):
        key = (file, height, width)
        if key not in self.cache:
            path, _ = self.cast.image_path(self.channel_id, file)
            with Image.open(path) as source:
                im = source.convert("RGBA")
            if width and height:  # cover
                scale = max(width / im.width, height / im.height)
                im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
                left, top = (im.width - width) // 2, (im.height - height) // 2
                im = im.crop((left, top, left + width, top + height))
            elif height:
                im = im.resize((max(1, round(im.width * height / im.height)), max(1, round(height))), Image.LANCZOS)
            self.cache[key] = im
        return self.cache[key]


def camera(move, strength, t):
    """(scale, dx, dy) of the world for scene progress t in 0..1; offsets are fractions of frame size."""
    s = strength
    if move == "push_in":
        return 1 + .3 * s * ease(t), 0, 0
    if move == "pull_out":
        return 1 + .3 * s * (1 - ease(t)), 0, 0
    if move in ("pan_left", "pan_right"):
        direction = -1 if move == "pan_left" else 1
        return 1.12, direction * (-.05 + .1 * ease(t)) * s, 0
    return 1, 0, 0


def shake(strength, seconds):
    phase = seconds / .35 * 2 * math.pi
    return .006 * strength * math.sin(phase * 1.0), .005 * strength * math.cos(phase * 1.3)


def transform(layer: Image.Image, scale, dx, dy, size):
    """Zoom around the frame centre (slightly below middle, like the preview) and shift."""
    w, h = size
    if scale == 1 and dx == 0 and dy == 0:
        return layer
    cw, ch = w / scale, h / scale
    cx, cy = w * .5 - dx * w / scale, h * .55 - dy * h / scale
    box = (cx - cw * .5, cy - ch * .55, cx + cw * .5, cy + ch * .45)
    return layer.transform(size, Image.EXTENT, box, Image.BILINEAR)


def framing(image: Image.Image, zoom, fx, fy):
    """Camera framing: crop around the focus point (kept inside the frame) and scale back to full size."""
    if zoom <= 1:
        return image
    w, h = image.size
    cw, ch = w / zoom, h / zoom
    cx = min(max(fx * w, cw / 2), w - cw / 2)
    cy = min(max(fy * h, ch / 2), h - ch / 2)
    return image.transform(image.size, Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BICUBIC)


class SceneRenderer:
    def __init__(self, scene, bank, images, size):
        self.scene, self.images, self.size = scene, images, size
        characters, locations, items = bank
        w, h = size
        location = locations.get(scene.location_id)
        state = location and (next((s for s in location.states if s.id == scene.location_state_id), None) or next((s for s in location.states if s.image), None))
        self.background = images.get(state.image.file, h, w) if state and state.image else Image.new("RGBA", size, (40, 42, 48, 255))
        self.foreground = images.get(state.foreground.file, h, w) if state and state.foreground else None
        self.night = bool(state and state.time_of_day == "night")
        self.regions = {r.id: r for r in (state.regions if state else [])}
        self.actors = []
        for placed in scene.characters:
            character = characters.get(placed.character_id)
            pose = character and (next((p for p in character.poses if p.id == placed.pose_id), None)
                                  or next((p for p in character.poses if p.id == character.default_pose_id), None)
                                  or (character.poses[0] if character.poses else None))
            if pose:
                im = images.get(pose.image.file, round(placed.scale * h))
                self.actors.append((placed, im.transpose(Image.FLIP_LEFT_RIGHT) if placed.flip else im))
        self.props = []
        for placed in scene.props:
            item = items.get(placed.item_id)
            variant = item and (next((v for v in item.variants if v.id == placed.variant_id), None) or (item.variants[0] if item.variants else None))
            if variant:
                im = images.get(variant.image.file, round(placed.scale * h))
                self.props.append((placed, im.rotate(-placed.rotation, expand=True, resample=Image.BICUBIC) if placed.rotation else im))

    def prop(self, canvas, placed, im, t, seconds):
        w, h = self.size
        alpha, grow = 1.0, 1.0
        start = placed.at * seconds
        if placed.motion == "appear":
            k = (t * seconds - start) / .25
            if k < 0:
                return
            grow = .6 + .4 * ease_out(k)
        elif placed.motion == "fade_in":
            alpha = min(1, max(0, (t * seconds - start) / .8))
            if alpha <= 0:
                return
        if grow != 1:
            im = im.resize((max(1, round(im.width * grow)), max(1, round(im.height * grow))), Image.BILINEAR)
        if alpha < 1:
            im = im.copy()
            im.putalpha(im.getchannel("A").point(lambda a: round(a * alpha)))
        canvas.alpha_composite(im, (round(placed.x * w - im.width / 2), round(placed.y * h - im.height / 2)))

    def actor(self, canvas, placed, im, t, seconds):
        w, h = self.size
        x, lift, stretch = placed.x, 0.0, 1.0
        travel = min(2.4, seconds) / seconds
        if placed.motion in ("enter_left", "enter_right"):
            k = ease_out(t / travel)
            x = (-.2 if placed.motion == "enter_left" else 1.2) * (1 - k) + placed.x * k
            lift = .025 * abs(math.sin(t * seconds / .45 * math.pi)) if k < 1 else 0
        elif placed.motion in ("exit_left", "exit_right"):
            k = ease((t - .45) / travel) if t > .45 else 0
            x = placed.x * (1 - k) + (-.2 if placed.motion == "exit_left" else 1.2) * k
            lift = .025 * abs(math.sin(t * seconds / .45 * math.pi)) if 0 < k < 1 else 0
        elif placed.motion == "idle":
            stretch = 1 + .009 * (1 - math.cos(t * seconds / 3.2 * 2 * math.pi))
        if stretch != 1:
            im = im.resize((im.width, max(1, round(im.height * stretch))), Image.BILINEAR)
        top = placed.y * h - im.height - lift * im.height
        canvas.alpha_composite(im, (round(x * w - im.width / 2), round(top)))

    def clipped(self, world, placed, draw):
        """Draw an element; when it belongs to a region (window, doorway) keep only the part inside it."""
        region = self.regions.get(getattr(placed, "region_id", ""))
        if not region:
            return draw(world)
        w, h = self.size
        layer = Image.new("RGBA", self.size, (0, 0, 0, 0))
        draw(layer)
        box = (round(region.x0 * w), round(region.y0 * h), round(region.x1 * w), round(region.y1 * h))
        world.alpha_composite(layer.crop(box), box[:2])

    def frame(self, t, seconds, caption):
        w, h = self.size
        world = self.background.copy()
        for placed, im in self.props:
            if placed.layer == "behind":
                self.clipped(world, placed, lambda c, placed=placed, im=im: self.prop(c, placed, im, t, seconds))
        for placed, im in self.actors:
            self.clipped(world, placed, lambda c, placed=placed, im=im: self.actor(c, placed, im, t, seconds))
        for placed, im in self.props:
            if placed.layer == "front":
                self.clipped(world, placed, lambda c, placed=placed, im=im: self.prop(c, placed, im, t, seconds))
        move, strength = self.scene.motion.camera, self.scene.motion.strength
        scale, dx, dy = camera(move, strength, t)
        if move == "shake":
            dx, dy = shake(strength, t * seconds)
        out = transform(world, scale, dx, dy, self.size)
        if self.foreground is not None:
            fscale, fdx = scale, dx
            if move in ("pan_left", "pan_right"):
                fdx = dx + (-1 if move == "pan_left" else 1) * .06 * strength * ease(t)
            elif move == "push_in":
                fscale = scale * (1 + .12 * strength * ease(t))
            out.alpha_composite(transform(self.foreground, fscale, fdx, dy, self.size))
        motion = self.scene.motion
        out = framing(out, motion.zoom, motion.focus_x, motion.focus_y)
        if self.night:
            out.alpha_composite(Image.new("RGBA", self.size, (10, 16, 40, 46)))
        if caption:
            draw_caption(out, caption)
        return out.convert("RGB")


def draw_caption(image, text):
    w, h = image.size
    font = ImageFont.truetype(str(FONT), max(14, round(h * .034)))
    try:
        font.set_variation_by_name("SemiBold")  # the bundled Montserrat is a variable font; default is Thin
    except (OSError, ValueError):
        pass
    draw = ImageDraw.Draw(image)
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) > w * .76 and line:
            lines.append(line)
            line = word
        else:
            line = trial
    lines.append(line)
    lines = lines[-2:]
    pad, spacing = round(h * .014), round(h * .012)
    box_h = len(lines) * font.size + (len(lines) - 1) * spacing + pad * 2
    top = round(h * .95) - box_h
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle((w * .08, top, w * .92, top + box_h), radius=round(h * .01), fill=(0, 0, 0, 184))
    image.alpha_composite(overlay)
    draw = ImageDraw.Draw(image)
    for i, row in enumerate(lines):
        draw.text((w / 2, top + pad + i * (font.size + spacing)), row, font=font, fill=(255, 255, 255, 255), anchor="ma")


def plan(project, drafts_for):
    """Per scene: duration and timed lines. Scene lasts for its planned time or its speech, whichever is longer."""
    timeline, start = [], 0.0
    for scene in ordered_scenes(project):
        spoken = [line for line in scene.dialogue if line.text.strip()]
        voiced = drafts_for(scene) if spoken else {}
        cursor, lines = 0.0, []
        for line in spoken:
            clip = voiced.get(line.id)
            length = clip["duration"] if clip else max(1.2, len(line.text.split()) * .38)
            lines.append({"start": cursor, "end": cursor + length, "text": line.text, "speaker": line.speaker, "audio": clip and clip["path"]})
            cursor += length + GAP
        duration = max(scene.seconds, cursor - GAP + .3 if lines else scene.seconds)
        timeline.append({"scene": scene, "start": start, "duration": duration, "lines": lines})
        start += duration
    return timeline


def render_animatic(project, bank, images, drafts_for, output: Path, progress, cancel, *, size=(1280, 720), fps=25, speakers=None):
    timeline = plan(project, drafts_for)
    if not timeline:
        raise ValueError("Animatik nie ma scen")
    total = sum(item["duration"] for item in timeline)
    speakers = speakers or {}
    sounds = {k: v for k, v in bank[2].items() if hasattr(v, "kind")}
    mixer = Mixer(project, timeline, sounds, lambda file: images.cast.audio_path(images.channel_id, file)[0])
    audio_path = output.with_suffix(".wav")
    with wave.open(str(audio_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        written = 0
        for item in timeline:
            if cancel.is_set():
                raise InterruptedError()
            chunk = mixer.scene(item)
            # Keep scene boundaries on the same sample grid as the video frames.
            want = round((item["start"] + item["duration"]) * RATE) - written
            chunk = np.pad(chunk, (0, max(0, want - len(chunk))))[:want]
            w.writeframes((chunk * 32767).astype(np.int16).tobytes())
            written += want
    width, height = size
    command = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps), "-i", "-",
               "-i", str(audio_path), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(output)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    frames = max(1, round(total * fps))
    try:
        done = 0
        for item in timeline:
            renderer = SceneRenderer(item["scene"], bank, images, size)
            count = round((item["start"] + item["duration"]) * fps) - round(item["start"] * fps)
            for i in range(count):
                if cancel.is_set():
                    raise InterruptedError()
                local = i / fps
                line = next((l for l in item["lines"] if l["start"] <= local < l["end"] + GAP), None)
                caption = None
                if line:
                    name = speakers.get(line["speaker"], "")
                    caption = f"{name}: {line['text']}" if name else line["text"]
                encoder.stdin.write(renderer.frame(local / item["duration"], item["duration"], caption).tobytes())
                done += 1
                if done % fps == 0:
                    progress(min(.99, done / frames), f"Klatki {done}/{frames}")
        encoder.stdin.close()
        errors = encoder.stderr.read().decode(errors="replace")
        if encoder.wait() != 0:
            raise ValueError("FFmpeg nie zapisał animatiku: " + errors[-400:])
    except BaseException:
        encoder.kill()
        output.unlink(missing_ok=True)
        raise
    finally:
        encoder.stderr.close()
        audio_path.unlink(missing_ok=True)
    return {"duration": round(total, 3), "scenes": len(timeline), "frames": frames}
