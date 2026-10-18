"""Optional bridge for Shorts Director -> FilmCraft/EffectCraft.

This module does not create native Craft project files or silently execute edits.
Install Shorts Director locally for full reference parsing and MP4 generation.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
from pathlib import Path

BINARIES = {
    "filmcraft": Path(r"C:\Program Files\FilmCraft\filmcraft-cli.exe"),
    "effectcraft": Path(r"C:\Program Files\EffectCraft\effectcraft-cli.exe"),
}

def cli_path(app: str, override: str | None = None) -> str | None:
    if app not in BINARIES:
        raise ValueError("unknown application")
    path = override or shutil.which(f"{app}-cli") or str(BINARIES[app])
    return path if Path(path).is_file() or shutil.which(path) else None

def config(*, bridge: bool = False) -> dict:
    result = {}
    for name,port in (("filmcraft", 9876),("effectcraft",9877)):
        args = ["mcp"]
        if bridge:
            args += ["--bridge", f"127.0.0.1:{port}" if name == "filmcraft" else str(port)]
        result[name] = {"command":str(BINARIES[name]),"args":args}
    return {"mcpServers":result}

def doctor() -> dict:
    result = {}
    for name in BINARIES:
        cmd = cli_path(name)
        item = {"installed":bool(cmd),"binary":cmd}
        if cmd:
            test = subprocess.run([cmd,"commands","--json"],capture_output=True,
                                  text=True,timeout=30,check=False)
            item["discovery_success"] = test.returncode == 0
            if test.returncode:
                item["error"] = (test.stderr or test.stdout)[:400]
        result[name]=item
    return result

def import_draft(movie: str, *, filmcraft_project: str | None = None,
                 effectcraft_project: str | None = None) -> dict:
    movie_path = Path(movie).resolve()
    if not movie_path.is_file():
        raise FileNotFoundError(movie_path)
    out = {}
    if filmcraft_project:
        p = Path(filmcraft_project).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Open/create FilmCraft project first: {p}")
        out["filmcraft"]=[str(BINARIES["filmcraft"]),"--project",str(p),
                          "--save","import",str(movie_path)]
    if effectcraft_project:
        p = Path(effectcraft_project).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Open/create EffectCraft project first: {p}")
        out["effectcraft"]=[str(BINARIES["effectcraft"]),"exec","file.import",
                            json.dumps({"path":str(movie_path)}),str(p),"--save","--json"]
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["doctor","mcp-config","draft-import"])
    parser.add_argument("--bridge",action="store_true")
    parser.add_argument("--movie")
    parser.add_argument("--filmcraft-project")
    parser.add_argument("--effectcraft-project")
    args=parser.parse_args()
    if args.action=="doctor":
        payload=doctor()
    elif args.action=="mcp-config":
        payload=config(bridge=args.bridge)
    else:
        if not args.movie:
            parser.error("--movie is required for draft-import")
        payload=import_draft(args.movie,filmcraft_project=args.filmcraft_project,
                              effectcraft_project=args.effectcraft_project)
    print(json.dumps(payload,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
