"""Single template frames from the publication renderer, without an encode job."""
from pathlib import Path
import hashlib
import os
from studio_core.freshness import fingerprint
from studio_core.models import fps
from studio_core.templates import validate_parameters
from .templates import MediaFrames,paint,FONT,LAND,font_hash


def poster(store,project,clip,frame=0):
    frame=int(frame)
    if not 0<=frame<clip.duration: raise ValueError("Klatka poza ujęciem")
    ids=set(clip.asset_ids+([clip.asset_id] if clip.asset_id else []))
    files=[]
    for asset in project.assets:
        if asset.id in ids:
            path=store.folder(project.id)/"media"/asset.filename;stat=path.stat()
            files.append([asset.id,asset.sha256,stat.st_size,stat.st_mtime_ns])
    code=Path(__file__).with_name("templates.py")
    key=fingerprint({"renderer":hashlib.sha256(code.read_bytes()).hexdigest(),"land":hashlib.sha256(LAND.read_bytes()).hexdigest(),"clip":clip.model_dump(),"frame":frame,"assets":files,"style":project.channel_profile,"font":font_hash()})
    folder=store.root/"cache/posters";folder.mkdir(parents=True,exist_ok=True);output=folder/(key+".png")
    if output.is_file():return output
    width=min(640,project.sequence.width);height=max(2,round(width*project.sequence.height/project.sequence.width))
    source=clip.model_copy(deep=True);source.duration=1;source.source_in+=round(frame*clip.speed)
    source.parameters={**source.parameters,"_frame_offset":source.parameters.get("_frame_offset",0)+frame,"_original_duration":clip.parameters.get("_original_duration",clip.duration)}
    media=MediaFrames(store,project,source,width,height,fps(project))
    try:
        image=paint(source,validate_parameters(source.template,source.parameters),media,0,width,height,fps(project),project.channel_profile)
        import tempfile
        with tempfile.NamedTemporaryFile(dir=folder,suffix=".png",delete=False) as temporary:
            temporary_name=temporary.name
        try: image.save(temporary_name);os.replace(temporary_name,output)
        finally: Path(temporary_name).unlink(missing_ok=True)
    finally:media.close()
    return output
