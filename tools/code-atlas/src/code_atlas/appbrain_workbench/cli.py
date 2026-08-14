from __future__ import annotations

import argparse
import os
from pathlib import Path

from .runner import run_self_test, run_workbench


def _default_out() -> Path:
    raw = os.environ.get("CODE_ATLAS_OUTPUT_ROOT")
    return Path(raw).expanduser() if raw else Path.cwd() / "code-atlas-out"


def _default_repo() -> Path:
    raw = os.environ.get("CODE_ATLAS_PROJECT_ROOT")
    return Path(raw).expanduser() if raw else Path.cwd()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="code_atlas.appbrain_workbench", description="Code Atlas AppBrain Workbench importer")
    parser.add_argument("--source", default=None, help="Path to an AppBrain result ZIP. If omitted, the latest compatible result under --out is used.")
    parser.add_argument("--out", default=str(_default_out()), help="Output root for generated workbench ZIP.")
    parser.add_argument("--repo", default=str(_default_repo()), help="Repository root used for reports only.")
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
