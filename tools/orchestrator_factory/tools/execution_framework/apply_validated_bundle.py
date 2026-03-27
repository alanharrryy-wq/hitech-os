from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.bundles import validate_bundle_zip
from lib.common import copy_payload, discover_repo_root, extract_zip_to_temp


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a validated bundle to the repo.")
    parser.add_argument("bundle_zip")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    result = validate_bundle_zip(Path(args.bundle_zip), repo_root)
    if not result["ok"] and not args.force:
        print("[ERROR] bundle validation failed; use --force only if you understand the risk")
        return 1
    extracted = extract_zip_to_temp(Path(args.bundle_zip))
    payload = extracted / "payload"
    copied = copy_payload(payload, repo_root, dry_run=False)
    print(f"[OK] applied {len(copied)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
