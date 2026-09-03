from __future__ import annotations
import importlib.util, subprocess, sys
from pathlib import Path
from typing import Any
from .errors import ProjectionFailure, UnsupportedProjectionMode


def _load_tablet_generator(repo_root: Path):
    path=repo_root/"prisma-html/tools/generate_tablet_visual_runtime.py"
    spec=importlib.util.spec_from_file_location("prisma_tablet_generator",path)
    if spec is None or spec.loader is None: raise ProjectionFailure("cannot load canonical Tablet generator")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def governed_outputs(target: dict[str,Any], repo_root: Path, authority_commit: str|None) -> list[Path]:
    mode=target["projectionMode"]
    if mode=="exact-byte-copy": return [repo_root/target["generatedOutputPath"]]
    if mode=="existing-rifat-tablet-generator":
        if not authority_commit or len(authority_commit)!=40: raise ProjectionFailure("authorityCommit required for generator mode")
        module=_load_tablet_generator(repo_root); expected,_,_=module.collect_expected(authority_commit)
        return sorted(expected)
    raise UnsupportedProjectionMode(mode)
def project(target: dict[str,Any], repo_root: Path, authority_commit: str|None, check: bool=False) -> None:
    mode=target["projectionMode"]
    source=repo_root/target["canonicalSourcePath"]
    if mode=="exact-byte-copy":
        output=repo_root/target["generatedOutputPath"]
        if check:
            if not output.is_file() or output.read_bytes()!=source.read_bytes(): raise ProjectionFailure("exact-copy projection drift")
        else:
            output.parent.mkdir(parents=True,exist_ok=True); output.write_bytes(source.read_bytes())
        return
    if mode=="existing-rifat-tablet-generator":
        script=repo_root/"prisma-html/tools/generate_tablet_visual_runtime.py"
        cmd=[sys.executable,str(script)]
        if authority_commit: cmd += ["--authority-commit",authority_commit]
        if check: cmd.append("--check")
        cp=subprocess.run(cmd,cwd=repo_root,text=True,capture_output=True)
        if cp.returncode: raise ProjectionFailure((cp.stdout+"\n"+cp.stderr).strip())
        return
    raise UnsupportedProjectionMode(mode)
