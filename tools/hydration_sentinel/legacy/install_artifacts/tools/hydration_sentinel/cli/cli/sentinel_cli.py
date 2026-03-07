from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..engine.runner import ScanRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Hydration Sentinel PRO - ZIP 1 core engine CLI')
    parser.add_argument('--repo-root', required=True, help='Path to the repository root.')
    parser.add_argument('--config', default=None, help='Optional path to config.json override.')
    parser.add_argument('--baseline', default=None, help='Optional path to baseline.json override.')
    parser.add_argument('--diff-only', action='store_true', help='Scan only files changed relative to --diff-base-ref.')
    parser.add_argument('--diff-base-ref', default=None, help='Git ref used for diff selection. Default comes from config.')
    parser.add_argument('--write-json', default=None, help='Write full findings payload to this JSON file.')
    parser.add_argument('--write-summary', default=None, help='Write summary payload to this JSON file.')
    parser.add_argument('--write-baseline', action='store_true', help='Write current findings as a new baseline file.')
    parser.add_argument('--baseline-notes', default='', help='Optional notes when writing the baseline file.')
    parser.add_argument('--print-summary', action='store_true', help='Print summary JSON to stdout.')
    parser.add_argument('--print-top', type=int, default=0, help='Print the first N active findings to stdout.')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    runner = ScanRunner(
        args.repo_root,
        config_path=args.config,
        baseline_path=args.baseline,
        force_diff_enabled=True if args.diff_only else None,
        force_diff_base_ref=args.diff_base_ref,
    )
    output = runner.run()

    if args.write_json:
        _write_json(Path(args.write_json), output.to_findings_payload())
    if args.write_summary:
        _write_json(Path(args.write_summary), output.to_summary())
    if args.write_baseline:
        baseline_path = runner.write_baseline([finding for finding in output.findings if not finding.ignored], notes=args.baseline_notes)
        print(f'Baseline written to {baseline_path}')

    if args.print_summary or not args.write_json:
        print(json.dumps(output.to_summary(), indent=2, ensure_ascii=False))

    if args.print_top > 0:
        active = [finding for finding in output.findings if not finding.ignored][: args.print_top]
        print('\nTop findings:')
        for finding in active:
            print(f'- [{finding.severity}] {finding.rule_id} {finding.relpath}:{finding.line_number} -> {finding.message}')

    return 0


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
