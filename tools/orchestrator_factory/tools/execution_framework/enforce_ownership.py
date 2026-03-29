from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.bundles import validate_bundle_zip
from lib.common import discover_repo_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Check ownership violations for a bundle.")
    parser.add_argument("bundle_zip")
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    result = validate_bundle_zip(Path(args.bundle_zip), repo_root)
    for issue in result["ownership_errors"]:
        print(issue)
    return 0 if not result["ownership_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
