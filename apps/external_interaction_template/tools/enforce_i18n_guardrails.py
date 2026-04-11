#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_ROOT = Path(r"F:\repos\hitech-os\apps\external_interaction_template")
MESSAGE_PATTERN = re.compile(r'"([^"]+)"\s*:\s*"((?:\\.|[^"\\])*)"')
PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")
JSX_TEXT_PATTERN = re.compile(r">\s*([^<{\n][^<>{\n}]*[A-Za-zÁÉÍÓÚáéíóúÑñ][^<>{\n}]*)\s*<")
VISIBLE_PROP_PATTERN = re.compile(r"\b(title|subtitle|description|label|placeholder|helperText|emptyText|tooltip|aria-label)\s*=\s*\"([^\"{][^\"]*[A-Za-zÁÉÍÓÚáéíóúÑñ][^\"]*)\"")
ALLOWED_DIRS = ("app", "components", "src")
IGNORE_DIRS = {"node_modules", ".next", ".turbo", ".git", "coverage", "reports", "storage"}
IGNORE_SUFFIXES = {".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".stories.tsx"}

@dataclass
class Failure:
    code: str
    path: str
    line: int
    detail: str

    @property
    def signature(self) -> str:
        return f"{self.code}|{self.path}|{self.line}|{self.detail}"


def read_messages(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {match.group(1): bytes(match.group(2), "utf-8").decode("unicode_escape") for match in MESSAGE_PATTERN.finditer(text)}


def placeholders(value: str) -> tuple[str, ...]:
    return tuple(sorted(set(PLACEHOLDER_PATTERN.findall(value))))


def iter_code_files(root: Path) -> Iterable[Path]:
    for top in ALLOWED_DIRS:
        base = root / top
        if not base.exists():
            continue
        for current, dirnames, filenames in os.walk(base):
            dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
            current_path = Path(current)
            for name in filenames:
                path = current_path / name
                if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
                    continue
                if any(str(path).endswith(suffix) for suffix in IGNORE_SUFFIXES):
                    continue
                yield path


def find_line(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_message_parity(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    es_path = root / "src" / "lib" / "i18n" / "messages" / "es.ts"
    en_path = root / "src" / "lib" / "i18n" / "messages" / "en.ts"
    es = read_messages(es_path)
    en = read_messages(en_path)

    for missing in sorted(set(es) - set(en)):
        failures.append(Failure("missing-key-in-en", str(en_path.relative_to(root)), 1, missing))
    for missing in sorted(set(en) - set(es)):
        failures.append(Failure("missing-key-in-es", str(es_path.relative_to(root)), 1, missing))

    for key in sorted(set(es) & set(en)):
        if "." not in key:
            failures.append(Failure("non-namespaced-key", str(es_path.relative_to(root)), 1, key))
        if placeholders(es[key]) != placeholders(en[key]):
            failures.append(Failure("placeholder-mismatch", str(es_path.relative_to(root)), 1, f"{key}: es={placeholders(es[key])} en={placeholders(en[key])}"))
    return failures


def looks_like_code_fragment(value: str) -> bool:
    if not value:
        return True
    if value.startswith((")", "(", ";")):
        return True
    code_markers = (
        "===",
        "!==",
        "&&",
        "||",
        "=>",
        " ? ",
        ": return",
        "case ",
        "const ",
        "let ",
        "var ",
        "return ",
        "typeof ",
        "useState",
        "field.",
        "event.",
        "view ===",
        "satisfies Record",
        " as Record",
    )
    if any(marker in value for marker in code_markers):
        return True
    return False


def check_hardcoded_ui(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    for path in iter_code_files(root):
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(root))
        normalized_relative = relative.replace("\\", "/").lower()
        if normalized_relative.startswith("src/lib/adapters/"):
            continue
        for match in JSX_TEXT_PATTERN.finditer(text):
            value = " ".join(match.group(1).split())
            if value.startswith("//") or value.startswith("/*"):
                continue
            if value in {"use client", "GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            if looks_like_code_fragment(value):
                continue
            failures.append(Failure("hardcoded-jsx-text", relative, find_line(text, match.start(1)), value))
        for match in VISIBLE_PROP_PATTERN.finditer(text):
            value = " ".join(match.group(2).split())
            if looks_like_code_fragment(value):
                continue
            failures.append(Failure("hardcoded-visible-prop", relative, find_line(text, match.start(2)), value))
    return failures


def check_contract_registry(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    contracts_dir = root / "src" / "lib" / "i18n" / "feature-contracts"
    if not contracts_dir.exists():
        failures.append(Failure("missing-feature-contracts-dir", "src/lib/i18n/feature-contracts", 1, "directory missing"))
    return failures


def load_baseline(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    raw = payload.get("signatures")
    if not isinstance(raw, list):
        return set()
    return {str(item) for item in raw}


def save_baseline(path: Path, failures: list[Failure]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    signatures = sorted(item.signature for item in failures)
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("signatures") == signatures:
                return
        except Exception:
            pass
    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "signatures": signatures,
        "failures": [asdict(item) for item in failures],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def collect_failures(root: Path) -> list[Failure]:
    return [*check_message_parity(root), *check_contract_registry(root), *check_hardcoded_ui(root)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-fast i18n guardrails for external_interaction_template.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--baseline")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    baseline_path = Path(args.baseline).expanduser().resolve() if args.baseline else root / "tools" / "i18n_guardrails_baseline.json"
    failures = collect_failures(root)

    if args.update_baseline:
        save_baseline(baseline_path, failures)
        print(f"[OK] baseline updated: {baseline_path}")
        return 0

    baseline = load_baseline(baseline_path)
    new_failures = [item for item in failures if item.signature not in baseline]
    payload = {
        "root": str(root),
        "checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "baseline_path": str(baseline_path),
        "failure_count": len(failures),
        "new_failure_count": len(new_failures),
        "failures": [asdict(item) for item in failures],
        "new_failures": [asdict(item) for item in new_failures],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if new_failures:
            for item in new_failures:
                print(f"[FAIL] {item.code}: {item.path}:{item.line} -> {item.detail}")
        else:
            print("[OK] i18n guardrails passed without new violations.")
            if failures:
                print(f"[INFO] existing baseline violations tracked: {len(failures)}")

    return 1 if new_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
