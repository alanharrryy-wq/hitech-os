#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Violation:
    code: str
    message: str
    path: str | None = None


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_event_constants(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(r'export const ([A-Z0-9_]+)\s*=\s*"([^"]+)";')
    return {match.group(1): match.group(2) for match in pattern.finditer(content)}


def collect_source_files(root: Path) -> list[Path]:
    source_roots = [
        root / "apps/keystone/components/dev-console",
        root / "apps/keystone/components/pitch/debug",
    ]
    files: list[Path] = []
    for source_root in source_roots:
        if not source_root.exists():
            continue
        files.extend(source_root.rglob("*.ts"))
        files.extend(source_root.rglob("*.tsx"))
    return files


def count_symbol_usage(
    source_files: Iterable[Path],
    symbol: str,
    patterns: Iterable[re.Pattern[str]],
) -> int:
    total = 0
    for source_file in source_files:
        content = source_file.read_text(encoding="utf-8")
        for pattern in patterns:
            total += len(list(pattern.finditer(content)))
    return total


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_panel_contracts(repo_root: Path, panel_contracts: list[dict]) -> list[Violation]:
    violations: list[Violation] = []
    valid_domains = {"core", "inspect", "compose"}
    contract_paths: set[str] = set()

    for contract in panel_contracts:
        panel_id = str(contract.get("id", "")).strip()
        domain = str(contract.get("domain", "")).strip()
        relative_file = str(contract.get("file", "")).strip().replace("\\", "/")
        requires_scene_look_model = bool(contract.get("requires_scene_look_model", False))

        if not panel_id:
            violations.append(Violation("LAW-6", "Panel contract missing id"))
            continue

        if domain not in valid_domains:
            violations.append(
                Violation(
                    "LAW-6",
                    f'Panel "{panel_id}" has invalid domain "{domain}"',
                    relative_file or None,
                )
            )

        if not relative_file:
            violations.append(Violation("LAW-6", f'Panel "{panel_id}" missing file path'))
            continue

        contract_paths.add(relative_file)
        file_path = repo_root / relative_file
        if not file_path.exists():
            violations.append(Violation("LAW-6", f'Panel file missing for "{panel_id}"', relative_file))
            continue

        content = read_text(file_path)

        if domain == "inspect":
            inspect_forbidden = [
                re.compile(r"document\.documentElement\.(dataset|style|setAttribute|removeAttribute)"),
                re.compile(r"document\.body\.(append|appendChild|remove|removeChild)"),
                re.compile(r"window\.location\.(assign|replace|reload)\s*\("),
            ]
            for forbidden in inspect_forbidden:
                if forbidden.search(content):
                    violations.append(
                        Violation(
                            "LAW-1",
                            f'Inspect panel "{panel_id}" performs forbidden presentation mutation',
                            relative_file,
                        )
                    )
                    break

        if domain == "compose":
            compose_forbidden = [
                re.compile(r"\bsetDiagnosticsSnapshot\s*\("),
                re.compile(r"\bapplyDiagnosticsSnapshot\s*\("),
                re.compile(r"\bSCENE_STUDIO_REQUEST_DIAGNOSTICS\b"),
                re.compile(r"\bDEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT\b"),
            ]
            for forbidden in compose_forbidden:
                if forbidden.search(content):
                    violations.append(
                        Violation(
                            "LAW-2",
                            f'Compose panel "{panel_id}" mutates diagnostics flow',
                            relative_file,
                        )
                    )
                    break

            if requires_scene_look_model:
                if "sceneLookModel" not in content and "updateSceneLookModel" not in content:
                    violations.append(
                        Violation(
                            "LAW-5",
                            f'Compose panel "{panel_id}" bypasses SceneLookModel contract',
                            relative_file,
                        )
                    )

    discovered_panel_files: set[str] = set()
    scan_roots = [
        repo_root / "apps/keystone/components/dev-console/panels",
        repo_root / "apps/keystone/components/dev-console/domains",
    ]
    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for panel_file in scan_root.rglob("*Panel.tsx"):
            discovered_panel_files.add(str(panel_file.relative_to(repo_root)).replace("\\", "/"))

    missing_contract_files = sorted(discovered_panel_files - contract_paths)
    for missing in missing_contract_files:
        violations.append(
            Violation("LAW-6", "Panel file is not declared in panel contracts", missing)
        )

    return violations


def validate_event_contracts(
    event_contracts: list[dict],
    event_constants: dict[str, str],
    source_files: list[Path],
) -> list[Violation]:
    violations: list[Violation] = []

    for contract in event_contracts:
        symbol = str(contract.get("symbol", "")).strip()
        if not symbol:
            violations.append(Violation("LAW-4", "Event contract missing symbol"))
            continue

        if symbol not in event_constants:
            violations.append(Violation("LAW-4", f'Event symbol "{symbol}" is not declared in dev-console-events.ts'))
            continue

        emitter_patterns = [
            re.compile(rf"CustomEvent(?:<[^>]+>)?\(\s*{re.escape(symbol)}\b"),
            re.compile(rf"dispatchConsoleEvent\(\s*{re.escape(symbol)}\b"),
            re.compile(rf"emit\(\s*{re.escape(symbol)}\b"),
        ]
        listener_patterns = [
            re.compile(rf"addEventListener\(\s*{re.escape(symbol)}\b"),
            re.compile(rf"registerConsoleEventListener\(\s*{re.escape(symbol)}\b"),
        ]

        emitter_hits = count_symbol_usage(source_files, symbol, emitter_patterns)
        listener_hits = count_symbol_usage(source_files, symbol, listener_patterns)

        must_have_emitter = bool(contract.get("must_have_emitter", False))
        must_have_listener = bool(contract.get("must_have_listener", False))

        if must_have_emitter and emitter_hits == 0:
            violations.append(Violation("LAW-4", f'Contract event "{symbol}" has no emitter usage'))
        if must_have_listener and listener_hits == 0:
            violations.append(Violation("LAW-4", f'Contract event "{symbol}" has no listener usage'))
        if emitter_hits > 0 and listener_hits == 0 and must_have_listener:
            violations.append(Violation("LAW-4", f'Event "{symbol}" is emitted without consumer listeners'))

    return violations


def build_report(violations: list[Violation]) -> str:
    lines = ["DEV CONSOLE ARCHITECTURE GUARD REPORT", ""]
    if not violations:
        lines.append("status: PASS")
        lines.append("violations: 0")
        return "\n".join(lines)

    lines.append("status: FAIL")
    lines.append(f"violations: {len(violations)}")
    lines.append("")
    for violation in violations:
        if violation.path:
            lines.append(f"- [{violation.code}] {violation.message} ({violation.path})")
        else:
            lines.append(f"- [{violation.code}] {violation.message}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev Console architecture guard")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on violations")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    events_contract_path = repo_root / "docs/dev-console/contracts/events.json"
    panels_contract_path = repo_root / "docs/dev-console/contracts/panels.json"
    events_source_path = repo_root / "apps/keystone/components/dev-console/dev-console-events.ts"

    missing_paths = [
        path
        for path in [events_contract_path, panels_contract_path, events_source_path]
        if not path.exists()
    ]
    if missing_paths:
        for missing in missing_paths:
            print(f"[ARCH_GUARD_ERROR] missing required file: {missing}", file=sys.stderr)
        return 2

    event_contracts_raw = load_json(events_contract_path)
    panel_contracts_raw = load_json(panels_contract_path)
    event_constants = parse_event_constants(events_source_path)
    source_files = collect_source_files(repo_root)

    panel_contracts = list(panel_contracts_raw.get("panels", []))
    event_contracts = list(event_contracts_raw.get("events", []))

    violations: list[Violation] = []
    violations.extend(validate_panel_contracts(repo_root, panel_contracts))
    violations.extend(validate_event_contracts(event_contracts, event_constants, source_files))

    report = build_report(violations)
    print(report)

    if violations and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
