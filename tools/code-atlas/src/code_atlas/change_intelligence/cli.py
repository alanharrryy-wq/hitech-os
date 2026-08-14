from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .authority_pack import validate_authority_pack
from .connector_parsers import normalize_ci_result, parse_codeowners, parse_coverage_summary, parse_junit_xml, parse_sarif
from .verification import verify_change


def _read_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _emit(payload: Any, output: str | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="code-atlas-change", description="Neutral change intelligence contract tools")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-pack")
    validate.add_argument("--pack", required=True)
    validate.add_argument("--output")

    verify = sub.add_parser("verify-change")
    verify.add_argument("--pack", required=True)
    verify.add_argument("--change", required=True)
    verify.add_argument("--snapshot", required=True)
    verify.add_argument("--evidence")
    verify.add_argument("--output")

    for name in ("parse-junit", "parse-sarif", "parse-codeowners", "parse-coverage", "normalize-ci"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--input", required=True)
        cmd.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-pack":
        _emit(validate_authority_pack(_read_json(args.pack)), args.output)
        return 0
    if args.command == "verify-change":
        evidence = _read_json(args.evidence) if args.evidence else []
        _emit(verify_change(
            authority_pack=_read_json(args.pack),
            change_manifest=_read_json(args.change),
            current_snapshot=_read_json(args.snapshot),
            produced_evidence=evidence,
        ), args.output)
        return 0

    path = Path(args.input)
    if args.command == "parse-junit":
        payload = parse_junit_xml(path.read_text(encoding="utf-8"))
    elif args.command == "parse-sarif":
        payload = parse_sarif(_read_json(args.input))
    elif args.command == "parse-codeowners":
        payload = parse_codeowners(path.read_text(encoding="utf-8"))
    elif args.command == "parse-coverage":
        payload = parse_coverage_summary(_read_json(args.input))
    elif args.command == "normalize-ci":
        payload = normalize_ci_result(_read_json(args.input))
    else:
        raise RuntimeError("unreachable")
    _emit(payload, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
