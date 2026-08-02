from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import run_uimap, zip_artifact


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the read-only PRISMA UI Component Atlas")
    parser.add_argument("--product-root", required=True)
    parser.add_argument("--governor-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--zip-path", default=None)
    parser.add_argument("--embedded-evidence", default=None)
    parser.add_argument("--input-audit", default=None)
    parser.add_argument("--run-timestamp", default=None)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--product-hash-exclude", action="append", default=[])
    parser.add_argument("--git-context", default=None)
    parser.add_argument("--backup-manifest", default=None)
    parser.add_argument("--rollback-file", action="append", default=[])
    parser.add_argument("--previous-batches-source", default=None)
    return parser


def load_json(path: str | None):
    if not path:
        return None
    target = Path(path)
    if not target.exists():
        return None
    return json.loads(target.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rollback_files = {}
    for item in args.rollback_file:
        if "=" not in item:
            continue
        name, path = item.split("=", 1)
        rollback_files[name] = path
    result = run_uimap(
        product_root=args.product_root,
        governor_root=args.governor_root,
        output_dir=args.output_dir,
        embedded_evidence=args.embedded_evidence,
        input_audit=args.input_audit,
        run_timestamp=args.run_timestamp,
        workers=max(1, min(18, args.workers)),
        product_hash_exclude=args.product_hash_exclude,
        git_context=load_json(args.git_context),
        backup_manifest=load_json(args.backup_manifest),
        rollback_files=rollback_files,
        previous_batches_source=args.previous_batches_source,
    )
    if args.zip_path:
        result["zipPath"] = args.zip_path
        result["zipSha256"] = zip_artifact(Path(args.output_dir), Path(args.zip_path))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
