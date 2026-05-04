from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE = "PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y"
VERSION = "20260504_v01"
DEFAULT_TARGET_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_OUT_DIR = Path(r"F:\descargasf")

ACTIVE_STATUSES = {"blocked", "failed", "error", "fatal", "not_ready"}
READY_STATUSES = {"ready", "ready_with_warnings"}
DOCTOR_GLOB_ORDER = [
    "prisma_show_pos_doctor_smart_00x_*.json",
    "prisma_show_pos_doctor_00u_*.json",
    "prisma_show_pos_scan_*.json",
]


def now_local_stamp() -> str:
    return datetime.now().strftime("%y%m%d_%H%M")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Reporter:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.stamp = now_local_stamp()
        self.log_path = out_dir / f"prisma_show_pos_ai_doctor_00y_{self.stamp}.log"
        self.json_path = out_dir / f"prisma_show_pos_ai_doctor_00y_{self.stamp}.json"
        self.md_path = out_dir / f"prisma_show_pos_ai_doctor_00y_{self.stamp}.md"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("", encoding="utf-8")

    def log(self, msg: str) -> None:
        line = f"[{now_iso()}] {msg}"
        print(line)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def find_latest_report(out_dir: Path, explicit: Path | None = None) -> Path | None:
    if explicit:
        return explicit if explicit.exists() else None
    candidates: list[Path] = []
    for pattern in DOCTOR_GLOB_ORDER:
        candidates.extend(out_dir.glob(pattern))
    if not candidates:
        candidates.extend(out_dir.glob("prisma_*.json"))
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def gate_ok(report: dict[str, Any], gate: str) -> bool | None:
    gates = report.get("gates")
    if isinstance(gates, dict) and gate in gates and isinstance(gates[gate], dict):
        return bool(gates[gate].get("ok"))
    return None


def count_failed_checks(report: dict[str, Any], only_critical: bool | None = None) -> int:
    total = 0
    for check in as_list(report.get("checks")):
        if not isinstance(check, dict):
            continue
        if only_critical is not None and bool(check.get("critical")) != only_critical:
            continue
        if check.get("ok") is False and not check.get("skipped"):
            total += 1
    return total


def extract_failed_check_names(report: dict[str, Any], limit: int = 12) -> list[str]:
    names: list[str] = []
    for check in as_list(report.get("checks")):
        if isinstance(check, dict) and check.get("ok") is False and not check.get("skipped"):
            names.append(str(check.get("name", "unnamed")))
    return names[:limit]


def summarize_report(report: dict[str, Any], report_path: Path) -> dict[str, Any]:
    status = str(report.get("status", "unknown"))
    release_verdict = str(report.get("releaseVerdict", status))
    health = report.get("healthScore")
    critical_failures = as_list(report.get("criticalFailures"))
    warnings = as_list(report.get("warnings"))
    fragile = as_list(report.get("fragilePoints"))
    historical = as_list(report.get("historicalSignals"))
    suppressed = as_list(report.get("suppressedSignals"))
    active_failed_checks = extract_failed_check_names(report)

    gate_summary = {
        "runtime_pos": gate_ok(report, "runtime_pos"),
        "runtime_visual_os": gate_ok(report, "runtime_visual_os"),
        "safe_no_layout": gate_ok(report, "safe_no_layout"),
        "doctor": gate_ok(report, "doctor"),
        "touch_pos": gate_ok(report, "touch_pos"),
    }

    return {
        "sourcePath": str(report_path),
        "package": report.get("package"),
        "version": report.get("version"),
        "createdAt": report.get("createdAt"),
        "status": status,
        "releaseVerdict": release_verdict,
        "healthScore": health,
        "criticalFailureCount": len(critical_failures),
        "warningCount": len(warnings),
        "fragilePointCount": len(fragile),
        "historicalSignalCount": len(historical),
        "suppressedSignalCount": len(suppressed),
        "failedCheckCount": count_failed_checks(report),
        "criticalFailedCheckCount": count_failed_checks(report, True),
        "activeFailedChecks": active_failed_checks,
        "gates": gate_summary,
    }


def classify(summary: dict[str, Any]) -> dict[str, Any]:
    status = str(summary.get("status", "unknown"))
    release_verdict = str(summary.get("releaseVerdict", status))
    health = summary.get("healthScore")
    critical_count = int(summary.get("criticalFailureCount") or 0)
    critical_failed_checks = int(summary.get("criticalFailedCheckCount") or 0)
    warning_count = int(summary.get("warningCount") or 0)
    fragile_count = int(summary.get("fragilePointCount") or 0)
    failed_count = int(summary.get("failedCheckCount") or 0)
    gates = summary.get("gates") or {}

    blockers: list[str] = []
    risks: list[str] = []
    strengths: list[str] = []

    if critical_count:
        blockers.append(f"Hay {critical_count} criticalFailures declaradas.")
    if critical_failed_checks:
        blockers.append(f"Hay {critical_failed_checks} checks críticos fallando.")
    if status in ACTIVE_STATUSES or release_verdict in ACTIVE_STATUSES:
        blockers.append(f"Estado/releaseVerdict bloqueante: status={status}, releaseVerdict={release_verdict}.")

    for gate, ok in gates.items():
        if ok is False:
            blockers.append(f"Gate bloqueado: {gate}.")
        elif ok is True:
            strengths.append(f"Gate OK: {gate}.")

    if failed_count and not blockers:
        risks.append(f"Hay {failed_count} checks no críticos fallando; revisar antes de release externo.")
    if warning_count:
        risks.append(f"Hay {warning_count} warnings activos.")
    if fragile_count:
        risks.append(f"Hay {fragile_count} puntos frágiles activos.")

    if health is not None:
        try:
            score = float(health)
            if score >= 95:
                strengths.append(f"HealthScore alto: {score:g}.")
            elif score >= 80:
                risks.append(f"HealthScore aceptable pero no perfecto: {score:g}.")
            else:
                blockers.append(f"HealthScore bajo: {score:g}.")
        except Exception:
            risks.append(f"HealthScore no numérico: {health}.")

    if not blockers and not risks:
        verdict = "ready"
        action = "Cerrar baseline y avanzar a la siguiente mejora controlada."
        priority = "normal"
    elif not blockers:
        verdict = "ready_with_warnings"
        action = "Atender warnings/frágiles antes de declarar release final externo."
        priority = "medium"
    else:
        verdict = "blocked"
        action = "No avanzar paquete nuevo; corregir blockers primero."
        priority = "high"

    return {
        "aiMode": "offline_rules",
        "verdict": verdict,
        "priority": priority,
        "blockers": blockers,
        "risks": risks,
        "strengths": strengths,
        "nextAction": action,
    }


def propose_next_package(summary: dict[str, Any], classification: dict[str, Any]) -> dict[str, str]:
    failed = " ".join(summary.get("activeFailedChecks") or []).lower()
    gates = summary.get("gates") or {}
    verdict = classification.get("verdict")

    if verdict == "blocked":
        if gates.get("runtime_pos") is False or "route /pos" in failed:
            return {
                "name": "PRISMA_POS_RUNTIME_RECOVERY_00Z",
                "intent": "Recuperar /pos y dejarlo en 200 sin Build Error.",
                "scope": "runtime POS",
            }
        if gates.get("safe_no_layout") is False or "00t" in failed:
            return {
                "name": "PRISMA_VISUAL_OS_SAFE_NO_LAYOUT_REPAIR_00Z",
                "intent": "Reparar 00T safe-no-layout y bloquear CSS que mueva layout.",
                "scope": "visual safety gate",
            }
        if gates.get("touch_pos") is False or "04h" in failed:
            return {
                "name": "PRISMA_POS_TOUCH_ONLY_REPAIR_00Z",
                "intent": "Reparar operación touch-only POS y CTA COBRAR/Tocar.",
                "scope": "touch POS",
            }
        return {
            "name": "PRISMA_SHOW_POS_BLOCKER_REPAIR_00Z",
            "intent": "Corregir blockers detectados por el doctor inteligente.",
            "scope": "release gates",
        }

    if verdict == "ready_with_warnings":
        return {
            "name": "PRISMA_SHOW_POS_WARNING_CLEANUP_00Z",
            "intent": "Eliminar warnings activos sin tocar runtime estable.",
            "scope": "hygiene",
        }

    return {
        "name": "PRISMA_VISUAL_POS_BASELINE_00T_00Y_CLOSEOUT",
        "intent": "Declarar baseline cerrada y preparar siguiente capa de mejora visual QA con screenshots.",
        "scope": "baseline closeout",
    }


def render_markdown(result: dict[str, Any]) -> str:
    summary = result["sourceSummary"]
    cls = result["classification"]
    next_pkg = result["nextPackage"]
    generated = result["generatedAt"]

    blockers = cls.get("blockers") or []
    risks = cls.get("risks") or []
    strengths = cls.get("strengths") or []

    def bullet(items: list[str]) -> str:
        if not items:
            return "- Ninguno."
        return "\n".join(f"- {x}" for x in items)

    gates = summary.get("gates") or {}
    gates_md = "\n".join(f"- `{k}`: `{v}`" for k, v in gates.items())

    return f"""# PRISMA Show POS AI Doctor 00Y - Diagnóstico offline

**Generado:** `{generated}`  
**Modo:** `offline_rules`  
**Fuente:** `{summary.get('sourcePath')}`

## Veredicto

`{cls.get('verdict')}`

## Lectura ejecutiva

- `status`: `{summary.get('status')}`
- `releaseVerdict`: `{summary.get('releaseVerdict')}`
- `healthScore`: `{summary.get('healthScore')}`
- `criticalFailures`: `{summary.get('criticalFailureCount')}`
- `warnings`: `{summary.get('warningCount')}`
- `fragilePoints`: `{summary.get('fragilePointCount')}`
- `historicalSignals`: `{summary.get('historicalSignalCount')}`
- `suppressedSignals`: `{summary.get('suppressedSignalCount')}`

## Gates

{gates_md or '- Sin gates estructurados.'}

## Fortalezas

{bullet(strengths)}

## Bloqueos

{bullet(blockers)}

## Riesgos

{bullet(risks)}

## Siguiente paquete recomendado

- **Nombre:** `{next_pkg.get('name')}`
- **Intención:** {next_pkg.get('intent')}
- **Scope:** `{next_pkg.get('scope')}`

## Acción siguiente

{cls.get('nextAction')}

## Nota operativa

Este doctor no llama APIs, no cuesta dinero, no modifica el POS y no toma decisiones por su cuenta. Lee evidencia y produce diagnóstico. O sea, por fin alguien en esta novela técnica usa los recibos antes de opinar.
"""


def build_result(report: dict[str, Any], report_path: Path, reporter: Reporter) -> dict[str, Any]:
    reporter.log(f"Reading source report: {report_path}")
    summary = summarize_report(report, report_path)
    classification = classify(summary)
    next_package = propose_next_package(summary, classification)
    return {
        "package": PACKAGE,
        "version": VERSION,
        "generatedAt": utc_now_iso(),
        "mode": "offline_rules",
        "cost": "zero_api_cost",
        "sourceSummary": summary,
        "classification": classification,
        "nextPackage": next_package,
        "outputs": {
            "log": str(reporter.log_path),
            "json": str(reporter.json_path),
            "markdown": str(reporter.md_path),
        },
    }


def self_check(target_root: Path, out_dir: Path, reporter: Reporter) -> int:
    system = target_root / "apps" / "terminal-de-venta-system"
    doctor = system / "tools" / "prisma-visual-os" / "ai_doctor_prisma_show_pos_00y.py"
    policy = system / "config" / "prisma-visual-os" / "ai-doctor-policy-00y.json"
    ok = True
    for name, path in [("system root", system), ("ai doctor", doctor), ("policy", policy)]:
        exists = path.exists()
        reporter.log(("OK" if exists else "FAIL") + f" {name}: {path}")
        ok = ok and exists
    result = {
        "package": PACKAGE,
        "version": VERSION,
        "mode": "self-check",
        "status": "ready" if ok else "blocked",
        "targetRoot": str(target_root),
        "systemRoot": str(system),
        "outputs": {"log": str(reporter.log_path), "json": str(reporter.json_path), "markdown": str(reporter.md_path)},
    }
    write_json(reporter.json_path, result)
    reporter.md_path.write_text(render_self_check_md(result), encoding="utf-8")
    return 0 if ok else 2


def render_self_check_md(result: dict[str, Any]) -> str:
    return f"""# PRISMA Show POS AI Doctor 00Y - Self-check

- `package`: `{result.get('package')}`
- `version`: `{result.get('version')}`
- `status`: `{result.get('status')}`
- `targetRoot`: `{result.get('targetRoot')}`
- `systemRoot`: `{result.get('systemRoot')}`
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai_doctor_prisma_show_pos_00y.py",
        description="PRISMA offline AI doctor. Reads doctor 00X reports and emits actionable diagnosis without API cost.",
    )
    parser.add_argument("--target-root", default=str(DEFAULT_TARGET_ROOT))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--input-json", default="", help="Optional explicit doctor JSON report to interpret.")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--ai-provider", default="none", choices=["none"], help="Only offline rules are enabled in 00Y v01.")
    args = parser.parse_args(argv)

    target_root = Path(args.target_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    reporter = Reporter(out_dir)
    reporter.log(f"START {PACKAGE} {VERSION}")

    if args.self_check:
        return self_check(target_root, out_dir, reporter)

    explicit = Path(args.input_json).resolve() if args.input_json else None
    source = find_latest_report(out_dir, explicit)
    if not source:
        reporter.log("FAIL no doctor report found")
        result = {
            "package": PACKAGE,
            "version": VERSION,
            "status": "blocked",
            "classification": {
                "verdict": "blocked",
                "blockers": ["No se encontró reporte JSON del doctor 00X/00U en out-dir."],
                "nextAction": "Ejecutar primero run_prisma_show_pos_doctor.cmd.",
            },
            "outputs": {"log": str(reporter.log_path), "json": str(reporter.json_path), "markdown": str(reporter.md_path)},
        }
        write_json(reporter.json_path, result)
        reporter.md_path.write_text(render_markdown({
            "generatedAt": utc_now_iso(),
            "sourceSummary": {"sourcePath": "none", "status": "missing", "releaseVerdict": "blocked", "healthScore": None, "criticalFailureCount": 1, "warningCount": 0, "fragilePointCount": 0, "historicalSignalCount": 0, "suppressedSignalCount": 0, "gates": {}},
            "classification": result["classification"],
            "nextPackage": {"name": "PRISMA_SHOW_POS_DOCTOR_REPORT_REQUIRED", "intent": "Generar reporte base del doctor 00X.", "scope": "diagnostics"},
        }), encoding="utf-8")
        return 2

    try:
        report = read_json(source)
    except Exception as exc:
        reporter.log(f"FAIL invalid json: {source} :: {exc}")
        return 2

    result = build_result(report, source, reporter)
    write_json(reporter.json_path, result)
    reporter.md_path.write_text(render_markdown(result), encoding="utf-8")
    reporter.log(f"JSON {reporter.json_path}")
    reporter.log(f"MARKDOWN {reporter.md_path}")
    reporter.log(f"VERDICT {result['classification']['verdict']}")
    return 0 if result["classification"]["verdict"] in {"ready", "ready_with_warnings"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
