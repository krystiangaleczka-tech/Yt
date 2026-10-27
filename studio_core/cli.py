"""Headless access to the exact service used by the desktop UI."""
import argparse
import json
import os
from pathlib import Path
import threading

from .service import ProjectService
from .models import Project,import_content
from .bundles import export_bundle,import_bundle
from .quality import check_project


def main():
    parser=argparse.ArgumentParser(prog="python -m studio_core.cli")
    parser.add_argument("--home",type=Path,default=Path(os.environ.get("DOCOS_STUDIO_HOME",Path(__file__).resolve().parents[1]/".docos-studio")))
    commands=parser.add_subparsers(dest="command",required=True)
    commands.add_parser("list")
    for name in ("get","check","backup","undo","redo"):
        command=commands.add_parser(name); command.add_argument("id")
        if name in ("undo","redo"): command.add_argument("--revision",required=True,type=int)
    command=commands.add_parser("import"); command.add_argument("file",type=Path)
    command=commands.add_parser("edit"); command.add_argument("id"); command.add_argument("file",type=Path); command.add_argument("--revision",required=True,type=int)
    command=commands.add_parser("patch"); command.add_argument("id"); command.add_argument("file",type=Path); command.add_argument("--revision",required=True,type=int)
    command=commands.add_parser("render"); command.add_argument("id"); command.add_argument("output",type=Path); command.add_argument("--start",type=int,default=0); command.add_argument("--end",type=int)
    args=parser.parse_args(); service=ProjectService(args.home)
    if args.command=="list": result=service.list(include_archived=True)
    elif args.command=="import": result=import_bundle(service,args.file) if args.file.suffix==".zip" else service.create(import_content(json.loads(args.file.read_text())))
    elif args.command=="get": result=service.get(args.id)
    elif args.command=="check": result=check_project(service,service.get(args.id))
    elif args.command=="backup": result=str(export_bundle(service,service.get(args.id)))
    elif args.command in ("undo","redo"): result=service.restore(args.id,args.revision,args.command)
    elif args.command=="edit": result=service.edit(args.id,args.revision,json.loads(args.file.read_text()))
    elif args.command=="patch": result=service.patch(args.id,args.revision,json.loads(args.file.read_text()))
    else:
        from studio_timeline.render import render
        args.output.parent.mkdir(parents=True,exist_ok=True)
        render(service,service.get(args.id),args.output,lambda value,message:None,threading.Event(),start_frame=args.start,end_frame=args.end)
        result=str(args.output)
    print(json.dumps(result.model_dump() if hasattr(result,"model_dump") else result,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
