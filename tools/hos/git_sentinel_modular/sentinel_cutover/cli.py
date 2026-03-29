from __future__ import annotations

import argparse
import json

from .bundle import build_cutover_readiness_bundle

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build cutover readiness bundle from a shadow workspace.")
    parser.add_argument("--workspace-root", required=True)
    args = parser.parse_args(argv)
    payload = build_cutover_readiness_bundle(args.workspace_root)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0
