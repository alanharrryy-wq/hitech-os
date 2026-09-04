from __future__ import annotations
import importlib.util, subprocess, sys
from pathlib import Path
from typing import Any
from .errors import ProjectionFailure, UnsupportedProjectionMode
from .security import contained_path, ensure_path_object_contained
from .transaction import atomic_write

def _load_tablet_generator(repo_root:Path):
    path=contained_path(repo_root,"prisma-html/tools/generate_tablet_visual_runtime.py",must_exist=True,field="tablet generator")
    spec=importlib.util.spec_from_file_location("prisma_tablet_generator",path)
    if spec is None or spec.loader is None: raise ProjectionFailure("cannot load canonical Tablet generator")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def governed_outputs(target:dict[str,Any],repo_root:Path,authority_commit:str|None)->list[Path]:
    mode=target["projectionMode"]
    if mode=="exact-byte-copy":
        return [contained_path(repo_root,target["generatedOutputPath"],field="generatedOutputPath")]
    if mode=="existing-rifat-tablet-generator":
        if not authority_commit or len(authority_commit)!=40: raise ProjectionFailure("authorityCommit required for generator mode")
        module=_load_tablet_generator(repo_root); expected,_,_=module.collect_expected(authority_commit)
        out=[]
        for p in expected:
            out.append(ensure_path_object_contained(repo_root,Path(p),field="generator output"))
        if len({p.resolve(strict=False).as_posix() for p in out})!=len(out):
            raise ProjectionFailure("generator returned duplicate outputs")
        return sorted(out,key=lambda p:p.as_posix())
    raise UnsupportedProjectionMode(mode)

def project(target:dict[str,Any],repo_root:Path,authority_commit:str|None,check:bool=False)->None:
    mode=target["projectionMode"]
    source=contained_path(repo_root,target["canonicalSourcePath"],must_exist=True,field="canonicalSourcePath")
    if mode=="exact-byte-copy":
        output=contained_path(repo_root,target["generatedOutputPath"],field="generatedOutputPath")
        if check:
            if not output.is_file() or output.is_symlink() or output.read_bytes()!=source.read_bytes():
                raise ProjectionFailure("exact-copy projection drift")
        else:
            output.parent.mkdir(parents=True,exist_ok=True)
            atomic_write(output,source.read_bytes())
        return
    if mode=="existing-rifat-tablet-generator":
        script=contained_path(repo_root,"prisma-html/tools/generate_tablet_visual_runtime.py",must_exist=True,field="tablet generator")
        cmd=[sys.executable,str(script)]
        if authority_commit: cmd+=["--authority-commit",authority_commit]
        if check: cmd.append("--check")
        try:
            cp=subprocess.run(cmd,cwd=repo_root,text=True,capture_output=True,timeout=180)
        except (OSError,subprocess.TimeoutExpired) as exc:
            raise ProjectionFailure(f"generator execution failed: {exc}") from exc
        if cp.returncode: raise ProjectionFailure((cp.stdout+"\n"+cp.stderr).strip())
        return
    raise UnsupportedProjectionMode(mode)
