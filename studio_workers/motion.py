"""Render a fixed Remotion template, then register an immutable video asset."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

from studio_core.inserts import definition, signature, require_ready, find_insert
from studio_core.media import asset_path, import_media, probe
from studio_core.store import atomic_json

REPO = Path(__file__).resolve().parents[1]
STUDIO = REPO / "apps" / "studio"


def runtime_ready():
    return bool(shutil.which("node") and (STUDIO / "node_modules" / "@remotion" / "renderer" / "package.json").is_file())


def stop_process(process):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()


def run_motion(store, project, insert_id, job_id, progress, cancel):
    item = find_insert(project, insert_id)
    require_ready(project, item)
    if not runtime_ready():
        raise ValueError("Zainstaluj moduły: npm --prefix apps/studio ci; instrukcja Remotion w docs/STUDIO.md")
    work = store.folder(project.id) / "jobs" / job_id
    public = work / "public"
    public.mkdir(parents=True, exist_ok=True)
    output = work / "insert.mp4"
    expected_signature = signature(project, item)
    urls = []
    try:
        for asset_id in item.image_ids:
            source = asset_path(store, project.id, asset_id)
            shutil.copyfile(source, public / source.name)
            urls.append("static:" + source.name)
        payload = {"insert": definition(item), "imageUrls": urls, "width": project.sequence.width,
                   "height": project.sequence.height, "fps": project.sequence.fps_num / project.sequence.fps_den}
        atomic_json(work / "input.json", payload)
        cmd = [shutil.which("node"), str(STUDIO / "scripts" / "render-insert.mjs"), str(work / "input.json"), str(output)]
        # A separate process group also contains the renderer's Chromium/FFmpeg children.
        with (work / "worker.log").open("w+", encoding="utf-8") as stream:
            process = subprocess.Popen(cmd, cwd=STUDIO, stdout=stream, stderr=stream, start_new_session=os.name != "nt")
            start = time.monotonic()
            offset = 0
            while process.poll() is None:
                if cancel.wait(.2):
                    stop_process(process)
                    raise InterruptedError()
                if time.monotonic() - start > 1200:
                    stop_process(process)
                    raise ValueError("Render Remotion przekroczył dwadzieścia minut")
                with (work / "worker.log").open(encoding="utf-8") as reader:
                    reader.seek(offset)
                    lines = reader.readlines()
                    offset = reader.tell()
                for line in lines:
                    try:
                        message = json.loads(line)
                        progress(float(message["progress"]), str(message["message"]))
                    except (ValueError, KeyError, TypeError):
                        pass
            if process.returncode or not output.is_file():
                stream.seek(0)
                detail = stream.read()[-1800:]
                raise ValueError("Remotion: " + detail + "\nPrzy pierwszym uruchomieniu przygotuj przeglądarkę: npm --prefix apps/studio run remotion:setup")
        if cancel.is_set():
            raise InterruptedError()
        info = probe(output)
        seconds = float(info.get("format", {}).get("duration", 0))
        rate = payload["fps"]
        video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
        if abs(seconds - item.duration / rate) > max(.08, 2 / rate) or video.get("width") != payload["width"] or video.get("height") != payload["height"]:
            raise ValueError("Niepoprawny czas lub rozdzielczość renderu Remotion")
        asset, _ = import_media(store, project.id, output, item.title + ".mp4", {
            "provenance": {"kind": "remotion", "insert_id": item.id, "signature": expected_signature,
                           "definition": definition(item), "input_revision": project.revision, "job_id": job_id},
        })
        with store.lock:
            current = store.get(project.id)
            found = next((i for i in current.inserts if i.id == item.id), None)
            attached = bool(found and signature(current, found) == expected_signature)
            if attached:
                def attach(p):
                    target = find_insert(p, item.id)
                    target.rendered_asset_id = asset.id
                    target.rendered_signature = expected_signature
                store.mutate(project.id, current.revision, attach)
        return {"asset_id": asset.id, "insert_id": item.id, "attached": attached, "revision": project.revision,
                "url": f"/api/projects/{project.id}/media/{asset.id}"}
    finally:
        shutil.rmtree(work / "bundle", ignore_errors=True)
        shutil.rmtree(public, ignore_errors=True)
