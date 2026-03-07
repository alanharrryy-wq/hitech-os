from __future__ import annotations

import argparse
import json
import sys

from .ci_integration import CIIntegration


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Hydration Sentinel PRO CI entrypoint')
    parser.add_argument('--repo-root', required=True)
    parser.add_argument('--config', default=None)
    parser.add_argument('--baseline', default=None)
    parser.add_argument('--report-root', default=None)
    parser.add_argument('--fail-threshold', type=float, default=60.0)
    parser.add_argument('--warn-threshold', type=float, default=25.0)
    parser.add_argument('--diff-only', action='store_true')
    parser.add_argument('--diff-base-ref', default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = CIIntegration(
        args.repo_root,
        config_path=args.config,
        baseline_path=args.baseline,
        report_root=args.report_root,
        fail_threshold=args.fail_threshold,
        warn_threshold=args.warn_threshold,
        diff_only=args.diff_only,
        diff_base_ref=args.diff_base_ref,
    ).run()
    print(json.dumps({
        'exit_code': result.exit_code,
        'risk_level': result.risk_level,
        'risk_score': result.risk_score,
        'report_paths': result.report_paths,
        'message': result.message,
    }, indent=2, ensure_ascii=False))
    return result.exit_code


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
