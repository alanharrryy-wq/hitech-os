# -*- coding: utf-8 -*-
"""
PRISMA Main README Contract Guard 12E

Validates that the root README.md keeps the canonical PRISMA contract:
- Tablet vende sola.
- PC/App móvil are complementary assets, not sales blockers.
- delivery contract remains governed and reversible.
- licensing, activation, entitlements, offline grace, and 11D signing scan remain visible.

This checker is intentionally contract-based, not byte-for-byte. It allows the
README to evolve without letting the project quietly contradict itself like a
committee meeting with a keyboard.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

PACKAGE = "PRISMA_MAIN_README_CONTRACT_12E"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    detail: str = ""


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = text.replace("\\", "/")
    text = re.sub(r"[`*_>#|]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def heading_title(line: str) -> str:
    value = re.sub(r"^#+\s*", "", line.strip())
    value = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", value)
    return normalize(value)


def load_readme(root: Path) -> str:
    readme = root / "README.md"
    if not readme.exists():
        raise FileNotFoundError(f"README.md no existe en {root}")
    return readme.read_text(encoding="utf-8")


def contains_all(norm_text: str, phrases: Iterable[str]) -> List[str]:
    missing: List[str] = []
    for phrase in phrases:
        if normalize(phrase) not in norm_text:
            missing.append(phrase)
    return missing


def collect_headings(text: str) -> List[str]:
    headings: List[str] = []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s+", line):
            headings.append(heading_title(line))
    return headings


def find_root_readme_noise(root: Path) -> List[str]:
    noise: List[str] = []
    for path in root.glob("README*.md"):
        if path.name != "README.md":
            noise.append(path.name)
    return sorted(noise)


def validate(root: Path, strict_root: bool = False) -> Dict[str, object]:
    root = root.resolve()
    findings: List[Finding] = []

    if not root.exists():
        return {
            "package": PACKAGE,
            "root": str(root),
            "status": "BLOCKED",
            "findings": [asdict(Finding("FAIL", "ROOT_MISSING", "La raíz no existe.", str(root)))],
        }

    try:
        text = load_readme(root)
    except Exception as exc:
        return {
            "package": PACKAGE,
            "root": str(root),
            "status": "BLOCKED",
            "findings": [asdict(Finding("FAIL", "README_MISSING", "No se pudo leer README.md.", str(exc)))],
        }

    norm = normalize(text)
    headings = collect_headings(text)
    heading_set = set(headings)

    required_headings = [
        "Qué es PRISMA",
        "Decisión canónica de producto",
        "Principios no negociables",
        "Estructura operativa esperada",
        "Contrato de entregas",
        "Arquitectura Tablet POS",
        "Arquitectura PC Backoffice",
        "App móvil / Pulso",
        "Licenciamiento, activación y entitlements",
        "KPIs base",
        "Definition of Done",
        "Estado mental correcto del proyecto",
    ]

    missing_headings = [h for h in required_headings if normalize(h) not in heading_set]
    for heading in missing_headings:
        findings.append(Finding("FAIL", "MISSING_REQUIRED_HEADING", "Falta sección canónica en README.md.", heading))

    required_canonical_phrases = [
        "Tablet vende sola",
        "PC y App móvil son assets complementarios",
        "Tablet es el POS autónomo",
        "PC es un asset de backoffice",
        "Ningún asset debe convertirse en requisito para que Tablet venda",
        "Tablet debe vender sola",
        "PC no es permiso para vender",
        "App móvil no es PC chiquita",
        "Toda entrega relevante debe ser reversible",
        "ZIP + instalador .py",
        "--dry-run",
        "--apply",
        "--verify",
        "--rollback",
    ]
    for phrase in contains_all(norm, required_canonical_phrases):
        findings.append(Finding("FAIL", "MISSING_CANONICAL_PHRASE", "Falta frase/regla canónica del README principal.", phrase))

    required_license_terms = [
        "Licenciamiento, activación y entitlements",
        "entitlements",
        "feature keys",
        "TABLET_SOLO",
        "TABLET_PRO",
        "TABLET_PC_REQUIRED",
        "standalone",
        "managed",
        "degraded_managed",
        "offline grace",
        "servidor firma",
        "cliente verifica",
        "docs\\productization\\PRISMA_LICENSES_README.md",
        "PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D.md",
        "local-runtime\\license",
        "local-runtime\\license-server",
        "local-runtime\\license-keys\\dev",
    ]
    for phrase in contains_all(norm, required_license_terms):
        findings.append(Finding("FAIL", "MISSING_LICENSE_CONTRACT", "El README no explica completo el contrato de licencias.", phrase))

    required_paths = [
        Path("docs/productization/PRISMA_LICENSES_README.md"),
        Path("docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D.md"),
        Path("docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D_ACCEPTANCE.md"),
        Path("docs/productization/PRISMA_LICENSE_STATE_MACHINE.md"),
        Path("docs/productization/PRISMA_OFFLINE_GRACE_POLICY.md"),
        Path("docs/productization/PRISMA_LICENSE_OPERATIONS_RUNBOOK.md"),
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            findings.append(Finding("WARN", "REFERENCED_LICENSE_DOC_NOT_FOUND", "Doc de licencias recomendado no existe en el repo.", str(rel)))

    # Banned contradictions. Keep these narrow to avoid punishing valid phrases like
    # "PC no es requisito para vender".
    banned_patterns = [
        (r"tablet\s+depende\s+de\s+pc\s+para\s+vender", "Tablet no debe depender de PC para vender."),
        (r"tablet\s+requiere\s+pc\s+para\s+vender", "Tablet no debe requerir PC para vender."),
        (r"pc\s+bloquea\s+la\s+venta\s+local", "PC no debe bloquear la venta local."),
        (r"app\s+movil\s+es\s+requisito\s+para\s+vender", "App móvil no debe ser requisito para vender."),
        (r"sin\s+internet\s+no\s+se\s+puede\s+vender", "Offline grace debe permitir continuidad operativa según política."),
        (r"shared\s+kernel\s+es\s+basurero", "Shared Kernel no debe ser basurero de utilidades."),
        (r"licencia\s+invalida\s+siempre\s+bloquea\s+venta\s+offline", "La licencia debe respetar gracia offline y política de continuidad."),
    ]
    for pattern, detail in banned_patterns:
        if re.search(pattern, norm):
            findings.append(Finding("FAIL", "BANNED_CONTRADICTION", "El README contiene una contradicción del contrato canónico.", detail))

    noise = find_root_readme_noise(root)
    if noise:
        severity = "FAIL" if strict_root else "WARN"
        findings.append(Finding(severity, "ROOT_README_NOISE", "Hay README alternos en raíz; deben moverse a docs/ o archivarse.", ", ".join(noise)))

    if len(text) < 9000:
        findings.append(Finding("WARN", "README_LOOKS_TOO_SHORT", "El README parece demasiado corto para ser el principal canónico.", f"chars={len(text)}"))

    status = "BLOCKED" if any(f.severity == "FAIL" for f in findings) else "READY"
    return {
        "package": PACKAGE,
        "root": str(root),
        "readme": str(root / "README.md"),
        "status": status,
        "findings": [asdict(f) for f in findings],
        "summary": {
            "failures": sum(1 for f in findings if f.severity == "FAIL"),
            "warnings": sum(1 for f in findings if f.severity == "WARN"),
            "infos": sum(1 for f in findings if f.severity == "INFO"),
            "heading_count": len(headings),
            "readme_chars": len(text),
        },
    }


def print_text(result: Dict[str, object]) -> None:
    print(f"PACKAGE {result['package']}")
    print(f"ROOT {result['root']}")
    print(f"STATUS {result['status']}")
    summary = result.get("summary", {})
    if isinstance(summary, dict):
        print("SUMMARY " + " ".join(f"{k}={v}" for k, v in summary.items()))
    findings = result.get("findings", [])
    if not findings:
        print("OK README principal respeta contrato canónico")
    else:
        for item in findings:
            print(f"{item['severity']} {item['code']} - {item['message']} {item.get('detail','')}")
    print("FINAL " + str(result["status"]))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PRISMA root README.md contract.")
    parser.add_argument("--root", required=True, help="Project root containing README.md")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    parser.add_argument("--text", action="store_true", help="Print human-readable result")
    parser.add_argument("--strict-root", action="store_true", help="Treat alternate root README*.md files as failures")
    parser.add_argument("--report", default="", help="Optional path to write JSON report")
    args = parser.parse_args(argv)

    result = validate(Path(args.root), strict_root=args.strict_root)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_text(result)

    return 0 if result["status"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
