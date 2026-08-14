"""Fail-closed neutrality gate for reusable Code Atlas source.

Every reusable module under the contract's neutral roots must be machine-neutral,
repository-neutral and product-neutral. Product compatibility is permitted only in
explicitly named profile/adapter boundaries and may never be selected implicitly.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".py", ".json", ".jsonc", ".md", ".txt", ".csv", ".ts", ".tsx", ".js", ".mjs", ".mts", ".html", ".css", ".ps1", ".yaml", ".yml", ".toml"}
EXCLUDED_PARTS = {"node_modules", ".git", "__pycache__", ".next", "dist", "build", "coverage", ".pytest_cache"}

# Assemble historical product literals from fragments so this gate does not
# accidentally match its own source while still detecting the real values.
_PRODUCT_REPO = "hitech" + "-os"
_PRODUCT_APP = "terminal" + "-de-venta-system"
_PRODUCT_NAME = "PRI" + "SMA"
_PRODUCT_DOMAIN = "app." + "hitechrts" + ".com"

PATTERNS: dict[str, re.Pattern[str]] = {
    "WINDOWS_ABSOLUTE_PATH": re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Za-z]:(?:[\\/])+[^\s'\"`]+"),
    "POSIX_USER_HOME_PATH": re.compile(r"(?i)(?:['\"`])/(?:home|Users|mnt)/[^\s'\"`]+"),
    "PRODUCT_REPOSITORY": re.compile(re.escape(_PRODUCT_REPO), re.I),
    "PRODUCT_APP_PATH": re.compile(re.escape(_PRODUCT_APP), re.I),
    "PRODUCT_DOMAIN": re.compile(re.escape(_PRODUCT_DOMAIN), re.I),
    "PRODUCT_NAME": re.compile(rf"\b{re.escape(_PRODUCT_NAME)}\b"),
    "FIXED_LOCAL_PORT": re.compile(r"(?i)\b(?:localhost|127\.0\.0\.1):\d{2,5}\b"),
}

DEFAULT_CONTRACT = "CODE_ATLAS_NEUTRALITY_CONTRACT.json"


def _load_contract(root: Path, contract_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(contract_path) if contract_path else root / DEFAULT_CONTRACT
    if not path.is_absolute():
        path = root / path
    if not path.exists():
        raise FileNotFoundError(f"NEUTRALITY_CONTRACT_MISSING:{path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("NEUTRALITY_CONTRACT_MUST_BE_OBJECT")
    return data


def _matches(rel: str, prefixes: list[str], files: list[str]) -> bool:
    rel = rel.replace("\\", "/")
    normalized_files = {item.replace("\\", "/") for item in files}
    if rel in normalized_files:
        return True
    return any(rel.startswith(prefix.replace("\\", "/").rstrip("/") + "/") for prefix in prefixes)


def _iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        yield path


def scan_code_atlas(root: str | Path, contract_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    contract = _load_contract(root, contract_path)
    neutral_prefixes = list(contract.get("neutralRoots") or [])
    neutral_files = list(contract.get("neutralFiles") or [])
    adapter_prefixes = list(contract.get("adapterRoots") or [])
    adapter_files = list(contract.get("adapterFiles") or [])

    findings: list[dict[str, Any]] = []
    scanned = 0
    adapter_scanned = 0
    neutral_scanned = 0
    for path in _iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        is_neutral = _matches(rel, neutral_prefixes, neutral_files)
        is_adapter = _matches(rel, adapter_prefixes, adapter_files)
        if not is_neutral and not is_adapter:
            continue
        scanned += 1
        if is_adapter:
            adapter_scanned += 1
            continue
        neutral_scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for name, rx in PATTERNS.items():
                if rx.search(line):
                    findings.append({
                        "file": rel,
                        "line": line_no,
                        "pattern": name,
                        "classification": "BLOCKING_NEUTRALITY_VIOLATION",
                        "excerpt": line.strip()[:220],
                    })

    status = "PASS_CODE_ATLAS_TOTAL_NEUTRALITY" if not findings else "BLOCKED_CODE_ATLAS_NEUTRALITY_VIOLATION"
    return {
        "schemaVersion": "code_atlas_neutrality_gate.v3",
        "status": status,
        "scannedFileCount": scanned,
        "neutralScannedFileCount": neutral_scanned,
        "explicitAdapterFileCount": adapter_scanned,
        "blockingCount": len(findings),
        "findings": findings,
        "fullReusableSourceBoundary": "src/code_atlas" in neutral_prefixes,
        "adapterBoundaryExplicit": True,
        "productionCertified": False,
        "doesNotProve": [
            "Production readiness.",
            "Correctness for every external repository stack.",
            "Legal or privacy compliance."
        ],
    }


def assert_neutral(root: str | Path, contract_path: str | Path | None = None) -> dict[str, Any]:
    result = scan_code_atlas(root, contract_path)
    if not result.get("fullReusableSourceBoundary"):
        raise RuntimeError("CODE_ATLAS_NEUTRALITY_BLOCKED:FULL_REUSABLE_SOURCE_BOUNDARY_NOT_SCANNED")
    if result["blockingCount"]:
        summary = ", ".join(f"{row['file']}:{row['line']}:{row['pattern']}" for row in result["findings"][:12])
        raise RuntimeError(f"CODE_ATLAS_NEUTRALITY_BLOCKED:{summary}")
    return result
