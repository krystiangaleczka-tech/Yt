"""Write the shared Paper Theatre motion vectors (Python renderer → JSON).

The browser preview (apps/studio/src/paperTheatreMotion.ts) and the MP4
renderer (studio_timeline/paper_theatre.py: rig_motion) must agree on every
number that places a cutout. Both test suites compare against this file:

    python3 scripts/paper_theatre_motion_fixture.py          # regenerate
    python3 scripts/paper_theatre_motion_fixture.py --check  # verify only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from studio_timeline.paper_theatre import rig_motion  # noqa: E402

FIXTURE = ROOT / "apps/studio/tests/fixtures/paper-theatre-motion.json"

CUES = {
    "hanging_drop": [
        {},
        {"string_visible": True, "swing_deg": 3.2, "swing_decay": 1.1, "overshoot": .025,
         "settle_duration": .22},
        {"string_visible": True, "string_length": .3, "swing_deg": 0, "overshoot": 0},
        {"string_visible": True, "settle_duration": 0, "swing_deg": 7.5, "swing_decay": 3},
    ],
    "bottom_rise": [{}, {"overshoot": .018, "settle_duration": .22}, {"overshoot": 0, "settle_duration": 0}],
    "rake_lift": [
        {},
        {"pivot_x": .5, "pivot_y": 1, "start_rotation": 82, "overshoot_rotation": -5,
         "stick_visible": True, "stick_length": .1, "settle_duration": .22},
        {"pivot_x": .2, "pivot_y": .85, "start_rotation": 88, "overshoot_rotation": 7,
         "stick_visible": True, "settle_duration": .5},
        {"start_rotation": 90, "stick_visible": False, "settle_duration": 0},
    ],
}
BOUNDS = [(400, 30, 620, 210), (0, 0, 1280, 720), (515, 240, 641, 711)]
FRAMES = [(1280, 720), (1920, 1080)]
ELAPSED = [-.1, 0, .05, .2, .5, .64, .7, .95, 1.25, 7.5]
DURATIONS = [.6, .95]


def vectors() -> list[dict]:
    cases = []
    for rig, cues in CUES.items():
        for cue in cues:
            for bounds in BOUNDS:
                for width, height in FRAMES:
                    for duration in DURATIONS:
                        for elapsed in ELAPSED:
                            cases.append({
                                "rig": rig, "cue": cue, "elapsed": elapsed, "duration": duration,
                                "bounds": list(bounds), "width": width, "height": height,
                                "motion": rig_motion(rig, cue, elapsed, duration, bounds, width, height),
                            })
        for cue in cues:  # zero-length entrances jump straight to the settle
            for elapsed in ELAPSED:
                cases.append({"rig": rig, "cue": cue, "elapsed": elapsed, "duration": 0,
                              "bounds": [-40, -12, 80, 95], "width": 640, "height": 360,
                              "motion": rig_motion(rig, cue, elapsed, 0, (-40, -12, 80, 95), 640, 360)})
    return cases


def main() -> int:
    # One compact case per line: small file, readable diffs.
    lines = [json.dumps(case, ensure_ascii=False, separators=(",", ":")) for case in vectors()]
    text = ('{"generator":"scripts/paper_theatre_motion_fixture.py","cases":[\n'
            + ",\n".join(lines) + "\n]}\n")
    if "--check" in sys.argv:
        current = FIXTURE.read_text(encoding="utf-8") if FIXTURE.is_file() else ""
        if current != text:
            print("Fixture is stale: run python3 scripts/paper_theatre_motion_fixture.py")
            return 1
        print("Fixture up to date:", FIXTURE.relative_to(ROOT))
        return 0
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(text, encoding="utf-8")
    print("Wrote", FIXTURE.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
