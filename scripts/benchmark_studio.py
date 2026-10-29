"""Bounded 500-shot project benchmark, without model downloads or remote APIs."""
import argparse
import json
import platform
from pathlib import Path
import statistics
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studio_core.models import Project,Scene,Clip
from studio_core.service import ProjectService
from studio_core.store import atomic_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True);parser.add_argument("--shots",type=int,default=500);args=parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        store=ProjectService(Path(directory));p=Project(title="Benchmark")
        for index in range(args.shots):
            scene=Scene(title=f"Ujęcie {index+1}",narration=f"Test narracji numer {index+1}.",start=index*180,duration=180,template="title",parameters={"text":f"Ujęcie {index+1}"})
            p.scenes.append(scene);p.sequence.clips.append(Clip(track_id="v1",scene_id=scene.id,start=scene.start,duration=scene.duration,template=scene.template,parameters=scene.parameters))
        p=store.create(p);path=store.folder(p.id)/"project.json"
        # Exercise the steady-state full undo history, not just an empty project.
        for index in range(40):
            current=store.get(p.id);store.edit(p.id,current.revision,[{"type":"update_clip","clip_id":p.sequence.clips[-1].id,"changes":{"title":f"Historia {index}"}}])
        loads=[];saves=[]
        for index in range(8):
            start=time.perf_counter();current=store.get(p.id);loads.append((time.perf_counter()-start)*1000)
            start=time.perf_counter();store.edit(p.id,current.revision,[{"type":"update_clip","clip_id":p.sequence.clips[-1].id,"changes":{"title":f"Wariant {index}"}}]);saves.append((time.perf_counter()-start)*1000)
        def measure(values):return {"median_ms":round(statistics.median(values),2),"p95_ms":round(sorted(values)[round((len(values)-1)*.95)],2)}
        report={"system":platform.platform(),"python":platform.python_version(),"shots":args.shots,"clips":args.shots,"undo_depth":40,"load":measure(loads),"save":measure(saves),"project_json_bytes":path.stat().st_size,"target":{"load_p95_ms":500,"save_p95_ms":1000},"includes":"JSON load/validation, shared service edit, locks, fsync and durable undo; excludes browser paint and model inference"}
        atomic_json(args.output,report);print(json.dumps(report,indent=2))


if __name__=="__main__":main()
