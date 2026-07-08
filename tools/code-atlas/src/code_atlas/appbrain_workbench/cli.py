from __future__ import annotations

import argparse
from pathlib import Path

from .runner import run_self_test, run_workbench


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="code_atlas.appbrain_workbench", description="Code Atlas AppBrain Workbench importer")
    parser.add_argument("--source", default=None, help="Path to appbrain1 result.zip. If omitted, the latest appbrain1 result in F:\\descargasf is used.")
    parser.add_argument("--out", default=r"F:\descargasf", help="Output root for generated workbench ZIP.")
    parser.add_argument("--repo", default=r"F:\repos\hitech-os", help="Repository root used for reports only.")
    parser.add_argument("--label", default="appbrain-workbench", help="Output ZIP label.")
    parser.add_argument("--output-zip", default=None, help="Optional exact output ZIP path, mostly for smoke tests.")
    parser.add_argument("--self-test", action="store_true", help="Run an internal synthetic self-test.")
    parser.add_argument("--no-open", action="store_true", help="Reserved for UI launchers; does not open folders.")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test(Path(args.out), Path(args.repo))
    result = run_workbench(
        source_zip=Path(args.source) if args.source else None,
        out_root=Path(args.out),
        repo_root=Path(args.repo),
        label=args.label,
        output_zip=Path(args.output_zip) if args.output_zip else None,
    )
    print("RESULT_ZIP=" + str(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
