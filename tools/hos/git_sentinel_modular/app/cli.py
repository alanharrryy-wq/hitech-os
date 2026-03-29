from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..core.orchestrator import OrchestratorConfig, SentinelOrchestrator


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run modular Git Sentinel orchestrator once.")
    parser.add_argument("--repo-root", required=True, help="Repository root to analyze.")
    parser.add_argument("--learning-db", required=True, help="SQLite path for learning state.")
    parser.add_argument("--report-json", default="", help="Optional JSON report output path.")
    parser.add_argument("--report-md", default="", help="Optional Markdown report output path.")
    parser.add_argument("--alert-out", default="", help="Optional alert output path.")
    parser.add_argument("--no-alerting", action="store_true", help="Disable alert file generation.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    config = OrchestratorConfig(
        repo_root=args.repo_root,
        learning_db_path=args.learning_db,
        report_json_path=args.report_json,
        report_md_path=args.report_md,
        alert_output_path=args.alert_out,
        run_alerting=not args.no_alerting,
    )
    result = SentinelOrchestrator(config).run_once()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
