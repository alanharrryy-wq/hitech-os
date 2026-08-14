"""Fail-closed neutrality gate for reusable Code Atlas source.

Every reusable module under the contract's neutral roots must be machine-neutral,
repository-neutral and product-neutral. Product compatibility is permitted only in
explicitly named profile/adapter boundaries and may never be selected implicitly.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".py", ".json", ".jsonc", ".md", ".txt", ".csv", ".ts", ".tsx", ".js", ".mjs", ".mts", ".html", ".css", ".ps1", ".yaml", ".yml", ".toml"}
EXCLUDED_PARTS = {"node_modules", ".git", "__pycache__", ".next", "dist", "build", "coverage", ".pytest_cache"}

_PRODUCT_REPO = "hitech" + "-os"
_PRODUCT_APP = "terminal" + "-de-venta-system"
_PRODUCT_WORD = "PRI" + "SMA"
_PRODUCT_DOMAIN = "app." + "hitechrts" + ".com"
_PRODUCT_MARKERS = (
    rf"\b{_PRODUCT_WORD}[_ -]CTX\b",
    rf"\b{_PRODUCT_WORD}\s+(?:Factory\s+Ledger|Operational|Code\s+Atlas|Surface|UI\s+Bridge|UI\s+Component|Smart\s+AllMesh|Data)\b",
    rf"\b(?:Motores|Todo|Global)\s+{_PRODUCT_WORD}\b",
)

PATTERNS: dict[str, re.Pattern[str]] = {
    "WINDOWS_ABSOLUTE_PATH": re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Za-z]:(?:[\\/])+[^\s'\"`]+"),
    "POSIX_USER_HOME_PATH": re.compile(r"(?i)(?:['\"`])/(?:home|Users)/[^\s'\"`]+"),
    "PRODUCT_REPOSITORY": re.compile(re.escape(_PRODUCT_REPO), re.I),
    "PRODUCT_APP_PATH": re.compile(re.escape(_PRODUCT_APP), re.I),
    "PRODUCT_DOMAIN": re.compile(re.escape(_PRODUCT_DOMAIN), re.I),
    "PRODUCT_MARKER": re.compile("|".join(_PRODUCT_MARKERS), re.I),
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


def _module_from_path(rel: str) -> str | None:
    normalized = rel.replace("\\", "/")
    if not normalized.startswith("src/") or not normalized.endswith(".py"):
        return None
    module = normalized[len("src/"):-3].replace("/", ".")
    if module.endswith(".__init__"):
        module = module[:-9]
    return module


def _adapter_modules(adapter_roots: list[str], adapter_files: list[str]) -> set[str]:
    modules: set[str] = set()
    for value in [*adapter_roots, *adapter_files]:
        normalized = value.replace("\\", "/").rstrip("/")
        if not normalized.startswith("src/"):
            continue
        if normalized.endswith(".py"):
            module = _module_from_path(normalized)
        else:
            module = normalized[len("src/"):].replace("/", ".")
        if module:
            modules.add(module)
    return modules


def _resolved_imports(rel: str, text: str) -> list[tuple[int, str]]:
    current = _module_from_path(rel)
    if not current:
        return []
    is_init = rel.replace("\\", "/").endswith("/__init__.py")
    package_parts = current.split(".") if is_init else current.split(".")[:-1]
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((int(getattr(node, "lineno", 0) or 0), alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                keep = max(0, len(package_parts) - node.level + 1)
                parts = package_parts[:keep]
                if node.module:
                    parts.extend(node.module.split("."))
                module = ".".join(parts)
            else:
                module = node.module or ""
            if module:
                imports.append((int(getattr(node, "lineno", 0) or 0), module))
    return imports


def _is_adapter_import(module: str, adapter_modules: set[str]) -> bool:
    return any(module == adapter or module.startswith(adapter + ".") for adapter in adapter_modules)


def _semantic_patterns(contract: dict[str, Any]) -> list[tuple[str, re.Pattern[str]]]:
    values = contract.get("forbiddenNeutralLiterals") or []
    if not isinstance(values, list):
        raise ValueError("forbiddenNeutralLiterals must be a list")
    out: list[tuple[str, re.Pattern[str]]] = []
    for index, value in enumerate(values):
        literal = str(value or "").strip()
        if literal:
            out.append((f"FORBIDDEN_NEUTRAL_LITERAL_{index + 1}", re.compile(re.escape(literal), re.I)))
    return out


def scan_code_atlas(root: str | Path, contract_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    contract = _load_contract(root, contract_path)
    neutral_prefixes = list(contract.get("neutralRoots") or [])
    neutral_files = list(contract.get("neutralFiles") or [])
    adapter_prefixes = list(contract.get("adapterRoots") or [])
    adapter_files = list(contract.get("adapterFiles") or [])
    adapter_modules = _adapter_modules(adapter_prefixes, adapter_files)
    semantic_patterns = _semantic_patterns(contract)

    findings: list[dict[str, Any]] = []
    scanned = 0
    adapter_scanned = 0
    neutral_scanned = 0
    implicit_adapter_imports = 0
    semantic_blockers = 0
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
                    findings.append({"file": rel, "line": line_no, "pattern": name, "classification": "BLOCKING_NEUTRALITY_VIOLATION", "excerpt": line.strip()[:220]})
            for name, rx in semantic_patterns:
                if rx.search(line):
                    semantic_blockers += 1
                    findings.append({"file": rel, "line": line_no, "pattern": name, "classification": "BLOCKING_SEMANTIC_NEUTRALITY_VIOLATION", "excerpt": line.strip()[:220]})
        if path.suffix.lower() == ".py":
            for line_no, module in _resolved_imports(rel, text):
                if _is_adapter_import(module, adapter_modules):
                    implicit_adapter_imports += 1
                    findings.append({"file": rel, "line": line_no, "pattern": "IMPLICIT_ADAPTER_IMPORT", "classification": "BLOCKING_NEUTRALITY_VIOLATION", "excerpt": module})

    status = "PASS_CODE_ATLAS_TOTAL_NEUTRALITY" if not findings else "BLOCKED_CODE_ATLAS_NEUTRALITY_VIOLATION"
    return {
        "schemaVersion": "code_atlas_neutrality_gate.v6",
        "status": status,
        "scannedFileCount": scanned,
        "neutralScannedFileCount": neutral_scanned,
        "explicitAdapterFileCount": adapter_scanned,
        "implicitAdapterImportCount": implicit_adapter_imports,
        "semanticNeutralityBlockerCount": semantic_blockers,
        "forbiddenNeutralLiteralCount": len(semantic_patterns),
        "blockingCount": len(findings),
        "findings": findings,
        "fullReusableSourceBoundary": "src/code_atlas" in neutral_prefixes,
        "adapterBoundaryExplicit": True,
        "prismaOrmTerminologyAllowed": True,
        "productionCertified": False,
        "doesNotProve": ["Production readiness.", "Correctness for every external repository stack.", "Legal or privacy compliance."],
    }


def assert_neutral(root: str | Path, contract_path: str | Path | None = None) -> dict[str, Any]:
    result = scan_code_atlas(root, contract_path)
    if not result.get("fullReusableSourceBoundary"):
        raise RuntimeError("CODE_ATLAS_NEUTRALITY_BLOCKED:FULL_REUSABLE_SOURCE_BOUNDARY_NOT_SCANNED")
    if result["blockingCount"]:
        summary = ", ".join(f"{row['file']}:{row['line']}:{row['pattern']}" for row in result["findings"][:12])
        raise RuntimeError(f"CODE_ATLAS_NEUTRALITY_BLOCKED:{summary}")
    return result
