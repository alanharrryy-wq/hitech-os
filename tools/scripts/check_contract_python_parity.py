#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Narrow contract / Python parity checker for HITECH OS.

This checker is intentionally conservative. It does not claim full semantic
equivalence between TypeScript contracts and Python Pydantic models.
Instead it verifies the wiring that should exist based on the generated
python-sync-map.json contract artifact.

Checks performed:
- generated sync map exists
- listed schema files exist
- listed Python file exists
- listed Python class names appear in the Python file
- generated manifest/schema-version files exist when expected

Outputs:
- human-readable log to stdout
- optional JSON report written to output path

Exit codes:
- 0 = success
- 1 = validation failures
- 2 = execution/configuration error
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Finding:
    level: str
    code: str
    message: str
    path: Optional[str] = None
    details: Optional[dict] = None


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def parse_python_class_names(path: Path) -> List[str]:
    tree = ast.parse(load_text(path), filename=str(path))
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            names.append(node.name)
    return sorted(set(names))


def build_paths(repo_root: Path) -> Dict[str, Path]:
    contracts_generated = repo_root / "packages" / "contracts" / "schemas" / "generated"
    return {
        "sync_map": contracts_generated / "python-sync-map.json",
        "manifest": contracts_generated / "manifest.json",
        "schema_version": contracts_generated / "schema-version.json",
        "contracts_generated": contracts_generated,
    }


def validate(repo_root: Path) -> Tuple[List[Finding], dict]:
    findings: List[Finding] = []
    paths = build_paths(repo_root)
    sync_map_path = paths["sync_map"]

    if not sync_map_path.exists():
        findings.append(Finding("error", "sync_map_missing", "python-sync-map.json was not found", str(sync_map_path)))
        return findings, {"paths": {k: str(v) for k, v in paths.items()}}

    try:
        sync_map = json.loads(load_text(sync_map_path))
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("error", "sync_map_invalid_json", f"Unable to parse sync map: {exc}", str(sync_map_path)))
        return findings, {"paths": {k: str(v) for k, v in paths.items()}}

    python_model_map = sync_map.get("pythonModelMap", {})
    schema_files = sync_map.get("schemaFiles", [])

    if not isinstance(python_model_map, dict) or not python_model_map:
        findings.append(Finding("error", "sync_map_missing_model_map", "pythonModelMap is missing or empty", str(sync_map_path)))

    if not isinstance(schema_files, list) or not schema_files:
        findings.append(Finding("error", "sync_map_missing_schema_files", "schemaFiles is missing or empty", str(sync_map_path)))

    if not paths["manifest"].exists():
        findings.append(Finding("warning", "generated_manifest_missing", "manifest.json is missing", str(paths["manifest"])))

    if not paths["schema_version"].exists():
        findings.append(Finding("warning", "schema_version_missing", "schema-version.json is missing", str(paths["schema_version"])))

    schema_results = []
    for schema_name in schema_files if isinstance(schema_files, list) else []:
        schema_path = paths["contracts_generated"] / schema_name
        exists = schema_path.exists()
        schema_results.append({"schema_file": schema_name, "exists": exists, "path": str(schema_path)})
        if not exists:
            findings.append(Finding("error", "schema_file_missing", f"Schema file referenced in sync map is missing: {schema_name}", str(schema_path)))

    python_targets = []
    for contract_name, mapping in (python_model_map.items() if isinstance(python_model_map, dict) else []):
        mapping_str = str(mapping)
        if "::" not in mapping_str:
            findings.append(
                Finding(
                    "error",
                    "python_mapping_invalid",
                    f"Mapping for contract '{contract_name}' does not contain '::' separator",
                    details={"mapping": mapping_str},
                )
            )
            continue

        relfile, class_name = mapping_str.split("::", 1)
        py_file = repo_root / Path(relfile)
        target_info = {
            "contract_name": contract_name,
            "mapping": mapping_str,
            "python_file": str(py_file),
            "class_name": class_name,
            "python_file_exists": py_file.exists(),
            "class_present": False,
            "available_classes": [],
        }

        if not py_file.exists():
            findings.append(Finding("error", "python_file_missing", f"Python target file is missing for '{contract_name}'", str(py_file)))
            python_targets.append(target_info)
            continue

        try:
            class_names = parse_python_class_names(py_file)
            target_info["available_classes"] = class_names
            target_info["class_present"] = class_name in class_names
            if class_name not in class_names:
                findings.append(
                    Finding(
                        "error",
                        "python_class_missing",
                        f"Mapped Python class '{class_name}' was not found for contract '{contract_name}'",
                        str(py_file),
                        {"available_classes": class_names},
                    )
                )
        except Exception as exc:  # noqa: BLE001
            findings.append(Finding("error", "python_parse_failure", f"Failed to parse Python target '{py_file}': {exc}", str(py_file)))
        python_targets.append(target_info)

    summary = {
        "generated_at": dt.datetime.now().isoformat(),
        "repo_root": str(repo_root),
        "paths": {k: str(v) for k, v in paths.items()},
        "schema_results": schema_results,
        "python_targets": python_targets,
        "finding_counts": {
            "error": sum(1 for f in findings if f.level == "error"),
            "warning": sum(1 for f in findings if f.level == "warning"),
            "info": sum(1 for f in findings if f.level == "info"),
        },
    }
    return findings, summary


def render_text(findings: List[Finding], summary: dict) -> str:
    lines: List[str] = []
    lines.append("HITECH OS - Contract/Python parity report")
    lines.append(f"generated_at: {summary['generated_at']}")
    lines.append(f"repo_root: {summary['repo_root']}")
    lines.append("")
    lines.append("schema results:")
    for item in summary["schema_results"]:
        lines.append(f"- {item['schema_file']} | exists={item['exists']} | path={item['path']}")
    lines.append("")
    lines.append("python targets:")
    for item in summary["python_targets"]:
        lines.append(
            f"- {item['contract_name']} -> {item['class_name']} | file_exists={item['python_file_exists']} | class_present={item['class_present']} | file={item['python_file']}"
        )
    lines.append("")
    lines.append("findings:")
    if findings:
        for finding in findings:
            lines.append(f"- [{finding.level.upper()}] {finding.code}: {finding.message}")
            if finding.path:
                lines.append(f"  path: {finding.path}")
            if finding.details:
                lines.append(f"  details: {json.dumps(finding.details, ensure_ascii=False, sort_keys=True)}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-text", default="")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    if not repo_root.exists():
        print(f"[ERROR] repo root does not exist: {repo_root}", file=sys.stderr)
        return 2

    findings, summary = validate(repo_root)
    report_text = render_text(findings, summary)
    print(report_text, end="")

    if args.output_json:
        payload = {
            "summary": summary,
            "findings": [asdict(f) for f in findings],
        }
        write_text(Path(args.output_json).expanduser().resolve(), json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.output_text:
        write_text(Path(args.output_text).expanduser().resolve(), report_text)

    error_count = sum(1 for f in findings if f.level == "error")
    if args.strict and error_count > 0:
        return 1
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
