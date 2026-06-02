from __future__ import annotations
import argparse
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from .config import Policy
from .context import Context
from .diagnostics import write_failure
from .orchestrator import Orchestrator
from .progress import line
def main(argv=None):
    ap=argparse.ArgumentParser(description="AutoGit Curator fail-fast engine"); ap.add_argument("--repo",default=r"F:\repos\hitech-os"); ap.add_argument("--out",default=r"F:\descargasf"); ap.add_argument("--mode",default="full",choices=["full","audit","commit-only","pr-only"]); ns=ap.parse_args(argv)
    package_root=Path(__file__).resolve().parents[1]; policy=Policy.load(package_root); policy.mode=ns.mode
    ctx=Context(Path(ns.repo).resolve(),Path(ns.out).resolve(),package_root,policy).initialize()
    try: Orchestrator(ctx).run(); line("AUTOGIT OK"); return 0
    except BaseException as exc:
        try: zip_path=write_failure(ctx,exc); line(f"AUTOGIT FAILED: {exc}"); line(f"FAILED_ZIP: {zip_path}")
        except Exception as diag: line(f"AUTOGIT FAILED AND DIAGNOSTIC FAILED: {exc} / {diag}")
        return 1
if __name__=="__main__": raise SystemExit(main())
