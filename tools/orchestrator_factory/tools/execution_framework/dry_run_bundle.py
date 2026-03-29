from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.bundles import validate_bundle_zip
from lib.common import discover_repo_root, extract_zip_to_temp


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run a package bundle application.")
    parser.add_argument("bundle_zip")
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    result = validate_bundle_zip(Path(args.bundle_zip), repo_root)
    if not result["ok"]:
        print("[ERROR] bundle is not valid enough for dry run")
        return 1
    extracted = extract_zip_to_temp(Path(args.bundle_zip))
    payload = extracted / "payload"
    for path in sorted(payload.rglob("*")):
        if path.is_file():
            rel = path.relative_to(payload)
            target = repo_root / rel
            status = "overwrite" if target.exists() else "new"
            print(f"[{status}] {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
