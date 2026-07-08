
from __future__ import annotations
import argparse
from pathlib import Path
from .runner import run_workbench_batch_packager


def main(argv=None):
    parser = argparse.ArgumentParser(description="Code Atlas AppBrain Batch Packager")
    parser.add_argument("--source", help="Path to appbrain-workbench result.zip")
    parser.add_argument("--repo", default=r"F:\repos\hitech-os")
    parser.add_argument("--out", default=r"F:\descargasf")
    parser.add_argument("--batch", help="Batch id or text filter")
    parser.add_argument("--app", help="App filter, e.g. 03_TABLET")
    parser.add_argument("--semantic-group", help="Semantic group filter, e.g. revenue_core")
    parser.add_argument("--output-zip")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_workbench_batch_packager(
        source_zip=Path(args.source) if args.source else None,
        repo_root=Path(args.repo),
        out_root=Path(args.out),
        batch_id=args.batch,
        app=args.app,
        semantic_group=args.semantic_group,
        output_zip=Path(args.output_zip) if args.output_zip else None,
        dry_run=args.dry_run,
    )
    print(f"RESULT_ZIP={result}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
