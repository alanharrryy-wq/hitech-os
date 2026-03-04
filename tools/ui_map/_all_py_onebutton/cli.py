from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .analyze_repo import analyze_repository
from .emit_dictionary import emit_ui_dictionary
from .emit_docs import emit_meta_docs, emit_query_docs
from .emit_mermaid import emit_mermaid_graphs
from .io_utils import detect_repo_root, ensure_directory, load_json, write_json
from .progress import ProgressLogger, default_run_tag
from .query_engine import QueryEngine
from .validators import run_validation


def _resolve_repo(repo_arg: str | None) -> Path:
    if repo_arg:
        return Path(repo_arg).resolve()
    return detect_repo_root()


def _resolve_out(repo_root: Path, out_arg: str | None) -> Path:
    out_rel = Path(out_arg or "docs/ui-map")
    if out_rel.is_absolute():
        return out_rel
    return (repo_root / out_rel).resolve()


def _logger(repo_root: Path, run_tag: str, command: str) -> ProgressLogger:
    logs_root = ensure_directory(repo_root / "tools" / "ui_map" / "_logs")
    return ProgressLogger(logs_root, run_tag, command)


def _load_dictionary_and_discovery(out_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    dictionary = load_json(out_dir / "ui_dictionary.json")
    discovery_path = out_dir / "meta" / "discovery.json"
    discovery = load_json(discovery_path) if discovery_path.exists() else {"screen_mapping": {}}
    return dictionary, discovery


def _render_query_samples(dictionary: dict[str, Any], discovery: dict[str, Any]) -> str:
    engine = QueryEngine(dictionary, discovery)

    first_component = dictionary.get("components", [{}])[0].get("component_id", "") if dictionary.get("components") else ""
    first_file = dictionary.get("components", [{}])[0].get("file_path", "") if dictionary.get("components") else ""
    first_state = dictionary.get("states", [{}])[0].get("state_id", "") if dictionary.get("states") else ""
    first_screen = sorted(discovery.get("screen_mapping", {}).keys())[0] if discovery.get("screen_mapping") else "screen-01"

    samples: list[tuple[str, Any, str]] = [
        ("dependents_of_file", engine.dependents_of_file(first_file), "[{component_id,file_path,reason}]"),
        ("screens_using_component", engine.screens_using_component(first_component), "[screen_id]"),
        ("files_touched_by_screen", engine.files_touched_by_screen(first_screen), "[file_path]"),
        ("state_readers", engine.state_readers(first_state), "[component_id]"),
        ("state_writers", engine.state_writers(first_state), "[component_id]"),
        ("assets_used_by_screen", engine.assets_used_by_screen(first_screen), "[{asset_id,file_path,kind}]"),
        ("styles_used_by_screen", engine.styles_used_by_screen(first_screen), "[{style_id,file_path}]"),
        ("hotspots_by_risk", engine.hotspots_by_risk("high"), "[hotspot]"),
        ("component_tree", engine.component_tree(first_screen), "{screen_id,root_component_id,component_ids,edges}"),
        ("imports_of_file", engine.imports_of_file(first_file), "[file_path]"),
        ("routes_index", engine.routes_index(), "[{route_id,path,entry_file,screen_component_id}]"),
        ("changeset_hint", engine.changeset_hint(first_component or first_file), "{type,target,...}"),
    ]

    lines = [
        "# Query Samples",
        "",
        "Each sample is deterministic for the same dictionary input.",
        "",
    ]
    for name, result, shape in samples:
        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- expected_output_shape: `{shape}`")
        lines.append("- sample_output:")
        lines.append("```json")
        lines.append(json.dumps(result, indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def cmd_doctor(args: argparse.Namespace) -> int:
    repo_root = _resolve_repo(args.repo)
    out_dir = _resolve_out(repo_root, args.out)
    run_tag = args.run_tag or default_run_tag()
    logger = _logger(repo_root, run_tag, "doctor")

    logger.event("starting doctor", percent=5, details={"repo": str(repo_root), "out": str(out_dir)})
    analysis = analyze_repository(repo_root)
    ensure_directory(out_dir / "meta")
    write_json(out_dir / "meta" / "discovery.json", analysis["discovery"])
    logger.event("doctor completed", percent=100, details=analysis["discovery"])

    print(json.dumps({"ok": True, "discovery": analysis["discovery"]}, indent=2, sort_keys=True))
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    repo_root = _resolve_repo(args.repo)
    out_dir = _resolve_out(repo_root, args.out)
    run_tag = args.run_tag or default_run_tag()
    logger = _logger(repo_root, run_tag, "generate")

    logger.event("starting generate", percent=5)
    analysis = analyze_repository(repo_root)
    dictionary = analysis["ui_dictionary"]
    discovery = analysis["discovery"]

    logger.event("writing dictionary", percent=30)
    emit_ui_dictionary(out_dir, dictionary)

    logger.event("writing mermaid graphs", percent=55)
    emit_mermaid_graphs(out_dir, dictionary, discovery)

    logger.event("writing meta docs", percent=75)
    emit_meta_docs(out_dir, dictionary, discovery, blocked_reason=None)
    write_json(out_dir / "meta" / "discovery.json", discovery)

    logger.event("writing query docs", percent=90)
    engine = QueryEngine(dictionary, discovery)
    query_names = engine.available_queries()
    samples_md = _render_query_samples(dictionary, discovery)
    emit_query_docs(out_dir, query_names, samples_md)

    logger.event("generate completed", percent=100)
    print(json.dumps({"ok": True, "out": str(out_dir), "counts": {"routes": len(dictionary.get("routes", [])), "components": len(dictionary.get("components", []))}}, indent=2, sort_keys=True))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    repo_root = _resolve_repo(args.repo)
    out_dir = _resolve_out(repo_root, args.out)
    run_tag = args.run_tag or default_run_tag()
    logger = _logger(repo_root, run_tag, "validate")

    logger.event("starting validate", percent=10)
    discovery_path = out_dir / "meta" / "discovery.json"
    discovery = load_json(discovery_path) if discovery_path.exists() else {"paths_searched": ["apps/keystone/**", "packages/ui-kit/**"], "route_files": [], "screen_roots": [], "screen_mapping": {}}

    result = run_validation(out_dir, discovery)
    logger.event("validation completed", percent=100, details=result, level="INFO" if result.get("ok") else "ERROR")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


def cmd_queries(args: argparse.Namespace) -> int:
    repo_root = _resolve_repo(args.repo)
    out_dir = _resolve_out(repo_root, args.out)
    run_tag = args.run_tag or default_run_tag()
    logger = _logger(repo_root, run_tag, "queries")

    logger.event("starting queries", percent=10)
    dictionary, discovery = _load_dictionary_and_discovery(out_dir)

    engine = QueryEngine(dictionary, discovery)
    query_names = engine.available_queries()
    samples_md = _render_query_samples(dictionary, discovery)
    emit_query_docs(out_dir, query_names, samples_md)

    logger.event("queries completed", percent=100, details={"queries": query_names})
    print(json.dumps({"ok": True, "queries": query_names}, indent=2, sort_keys=True))
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    repo_root = _resolve_repo(args.repo)
    run_tag = args.run_tag or default_run_tag()
    logger = _logger(repo_root, run_tag, "test")

    logger.event("starting tests", percent=10)
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tools/ui_map/tests", "-p", "test_*.py"]
    completed = subprocess.run(command, cwd=repo_root)
    ok = completed.returncode == 0
    logger.event("tests completed", percent=100, level="INFO" if ok else "ERROR", details={"returncode": completed.returncode})
    return completed.returncode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.ui_map.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_flags(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--repo", default=None, help="Repository root. Auto-detected if omitted.")
        subparser.add_argument("--out", default="docs/ui-map", help="Output directory relative to repo unless absolute.")
        subparser.add_argument("--run-tag", default=None, help="Optional run tag used for structured logs.")

    doctor = subparsers.add_parser("doctor", help="Discover Keystone UI map scope and write discovery metadata.")
    add_common_flags(doctor)
    doctor.set_defaults(func=cmd_doctor)

    generate = subparsers.add_parser("generate", help="Generate dictionary, mermaid graphs, and docs.")
    add_common_flags(generate)
    generate.set_defaults(func=cmd_generate)

    validate = subparsers.add_parser("validate", help="Validate generated outputs and deterministic constraints.")
    add_common_flags(validate)
    validate.set_defaults(func=cmd_validate)

    queries = subparsers.add_parser("queries", help="Emit deterministic query docs and examples.")
    add_common_flags(queries)
    queries.set_defaults(func=cmd_queries)

    test = subparsers.add_parser("test", help="Run lightweight offline tests for tools/ui_map.")
    add_common_flags(test)
    test.set_defaults(func=cmd_test)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
