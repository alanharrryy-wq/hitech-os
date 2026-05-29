from __future__ import annotations
import argparse,json
from pathlib import Path
from .rollback_core import rollback_latest
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default=r"F:\repos\hitech-os"); ap.add_argument("--out",default=r"F:\descargasf"); ns=ap.parse_args(argv)
    print(json.dumps(rollback_latest(Path(ns.repo),Path(ns.out)),indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
