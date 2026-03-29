from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.bundles import validate_bundle_zip
from lib.common import discover_repo_root, stable_json_dumps


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one package worker bundle zip.")
    parser.add_argument("bundle_zip")
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    result = validate_bundle_zip(Path(args.bundle_zip), repo_root)
    print(stable_json_dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
