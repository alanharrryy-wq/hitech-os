#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
import pathlib
import sys
import tempfile


def _decode_bytes(args: argparse.Namespace) -> bytes:
    if args.stdin:
        return sys.stdin.buffer.read()
    if args.content_b64 is not None:
        return base64.b64decode(args.content_b64.encode("ascii"), validate=True)
    raise ValueError("one input source is required: --stdin or --content-b64")


def _normalize_text_payload(payload: bytes) -> bytes:
    text = payload.decode("utf-8")
    if not text.endswith("\n"):
        text += "\n"
    return text.encode("utf-8")


def _atomic_write(path: pathlib.Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    tmp_path = pathlib.Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic UTF-8 text writer with trailing newline and atomic replace."
    )
    parser.add_argument("--path", required=True, help="Target file path (relative or absolute).")
    parser.add_argument("--stdin", action="store_true", help="Read content bytes from STDIN.")
    parser.add_argument(
        "--content-b64",
        default=None,
        help="Base64-encoded content payload when STDIN is not used.",
    )
    args = parser.parse_args()

    if bool(args.stdin) == bool(args.content_b64 is not None):
        print("Exactly one of --stdin or --content-b64 must be provided.", file=sys.stderr)
        return 1

    try:
        payload = _decode_bytes(args)
        normalized = _normalize_text_payload(payload)
        target = pathlib.Path(args.path).expanduser()
        if not target.is_absolute():
            target = pathlib.Path.cwd() / target
        _atomic_write(target, normalized)
    except Exception as exc:
        print(f"write failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
