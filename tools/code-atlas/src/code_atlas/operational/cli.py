from __future__ import annotations

import argparse
import json

from .final_runner import run_operational_atlas


def main(argv=None):
    ap = argparse.ArgumentParser(prog="code-atlas-operational")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--result-root", default=None)
    ns = ap.parse_args(argv)
    print(json.dumps(run_operational_atlas(ns.repo, ns.out, ns.result_root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
