#!/usr/bin/env python3
"""Compile PRISMA identity authority without projecting application runtime."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from identity_dictionary_core import COMPILED, build_compilation, validate_model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.check == args.write:
        parser.error("choose exactly one of --check or --write")
    files = build_compilation()
    if args.write:
        COMPILED.mkdir(parents=True, exist_ok=True)
        for relative, content in files.items():
            path = COMPILED / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    problems, warnings = validate_model(check_compiled=True)
    payload = {
        "status": "PASS" if not problems else "FAIL",
        "mode": "check" if args.check else "write",
        "compiledRoot": COMPILED.as_posix(),
        "fileCount": len(files),
        "runtimeMutationCount": 0,
        "warnings": warnings,
        "problems": problems,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
