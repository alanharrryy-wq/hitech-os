from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

SOURCE = "prisma-quality-bay-api"
SCHEMA_VERSION = "1.0"

QUALITY_ACTIONS: dict[str, dict[str, Any]] = {
    "self-test": {
        "label": "Self-Test",
        "kind": "flag",
        "args": ["--self-test"],
        "timeout": 180,
        "description": "Valida integridad interna de PRISMA Quality.",
    },
    "list": {
        "label": "Listar perfiles",
        "kind": "flag",
        "args": ["--list-profiles"],
        "timeout": 90,
        "description": "Lista perfiles disponibles de Quality.",
    },
    "first-run": {
        "label": "Instalacion nueva",
        "profile": "first-run",
        "timeout": 240,
        "description": "Verifica minimo operativo de primer arranque.",
    },
    "client-readiness": {
        "label": "Cliente listo",
        "profile": "client-readiness",
        "timeout": 240,
        "description": "Confirma readiness para mostrar o promover con cliente.",
    },
    "demo": {
        "label": "Demo segura",
        "profile": "demo",
        "timeout": 240,
        "description": "Busca riesgos antes de demo o presentacion.",
    },
    "support-pack": {
        "label": "Paquete soporte",
        "profile": "support-pack",
        "timeout": 300,
        "description": "Genera evidencia exportable para soporte.",
    },
    "upgrade": {
        "label": "Upgrade check",
        "profile": "upgrade",
        "timeout": 260,
        "description": "Valida preparacion para upgrade y rollback conceptual.",
    },
    "pilot": {
        "label": "Piloto cliente",
        "profile": "pilot",
        "timeout": 260,
        "description": "Valida estado para piloto controlado con cliente.",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _control_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _repo_root() -> Path:
    return _control_root().parent


def _quality_root() -> Path:
    return _repo_root() / "quality"


def _logs_root() -> Path:
    return _repo_root() / "tools" / "_local" / "logs" / "prisma-control-center" / "quality-bay"


def _default_out_dir() -> Path:
    configured = os.environ.get("PRISMA_QUALITY_OUT_DIR") or os.environ.get("PRISMA_OUT_DIR")
    if configured:
        return Path(configured)
    if os.name == "nt":
        return Path(r"F:\descargasf")
    return _repo_root() / "_quality_out"


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _read_text(path: Path, fallback: str = "") -> str:
    try:
        if not path.exists():
            return fallback
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return fallback


def _path_status(path: Path, public: bool = False) -> dict[str, Any]:
    try:
        exists = path.exists()
        stat = path.stat() if exists else None
        return {
            "path": "<redacted>" if public else str(path),
            "name": path.name,
            "exists": exists,
            "isFile": path.is_file() if exists else False,
            "isDir": path.is_dir() if exists else False,
            "size": stat.st_size if stat and path.is_file() else None,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds") if stat else None,
        }
    except Exception as exc:
        return {"path": "<redacted>" if public else str(path), "exists": False, "error": str(exc)}


def _redact(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, val in value.items():
            low = str(key).lower()
            if any(token in low for token in ["path", "root", "command", "cmd", "stdout", "stderr", "log", "pid", "token", "secret"]):
                out[key] = "<redacted>"
            else:
                out[key] = _redact(val)
        return out
    if isinstance(value, str) and (":\\" in value or ":/" in value):
        return "<redacted>"
    return value


def _node_executable() -> str:
    for candidate in ["node.exe", "node"]:
        found = shutil.which(candidate)
        if found:
            return found
    return "node.exe" if os.name == "nt" else "node"


def _latest_run_dir(out_dir: Path) -> Path | None:
    try:
        candidates = [p for p in out_dir.glob("PRISMA_QUALITY_OS_*") if p.is_dir()]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)
    except Exception:
        return None


def _run_dir_from_stdout(stdout: str, out_dir: Path) -> Path | None:
    match = re.search(r"Run dir:\s*(.+)", stdout or "")
    if match:
        candidate = Path(match.group(1).strip().strip('"'))
        if candidate.exists():
            return candidate
    return _latest_run_dir(out_dir)


def _summarize_run_dir(run_dir: Path | None, public: bool = False) -> dict[str, Any]:
    if run_dir is None or not run_dir.exists():
        return {"available": False}
    machine = _read_json(run_dir / "QUALITY_MACHINE_SUMMARY.json", {})
    decision = _read_json(run_dir / "QUALITY_DECISION.json", {})
    report = _read_json(run_dir / "QUALITY_REPORT.json", {})
    blockers = decision.get("blockers") if isinstance(decision, dict) else []
    warnings = decision.get("warnings") if isinstance(decision, dict) else []
    findings = report.get("findings") if isinstance(report, dict) else []
    artifacts = {
        "runDir": _path_status(run_dir, public),
        "decision": _path_status(run_dir / "QUALITY_DECISION.json", public),
        "summary": _path_status(run_dir / "QUALITY_MACHINE_SUMMARY.json", public),
        "reportMd": _path_status(run_dir / "QUALITY_REPORT.md", public),
        "blockersMd": _path_status(run_dir / "QUALITY_BLOCKERS.md", public),
        "warningsMd": _path_status(run_dir / "QUALITY_WARNINGS.md", public),
        "manifest": _path_status(run_dir / "QUALITY_RUN_MANIFEST.json", public),
        "ledger": _path_status(run_dir / "CUSTOMER_EVIDENCE_LEDGER.json", public),
    }
    summary = {
        "available": True,
        "runId": machine.get("runId") or report.get("runId") or run_dir.name.replace("PRISMA_QUALITY_OS_", ""),
        "profile": machine.get("profile") or report.get("profile") or decision.get("profile"),
        "decision": machine.get("decision") or decision.get("decision") or "UNKNOWN",
        "status": decision.get("status") or machine.get("decision") or "UNKNOWN",
        "exitCode": machine.get("exitCode") if "exitCode" in machine else decision.get("exitCode"),
        "blockerCount": machine.get("blockerCount") if "blockerCount" in machine else decision.get("blockerCount", len(blockers or [])),
        "warningCount": machine.get("warningCount") if "warningCount" in machine else decision.get("warningCount", len(warnings or [])),
        "gateCount": machine.get("gateCount") or (len(report.get("gates", [])) if isinstance(report.get("gates"), list) else None),
        "blockedGates": machine.get("blockedGates", []),
        "warningGates": machine.get("warningGates", []),
        "topBlockers": (blockers or [])[:5],
        "topWarnings": (warnings or [])[:5],
        "findingsPreview": (findings or [])[:8] if isinstance(findings, list) else [],
        "artifacts": artifacts,
    }
    return _redact(summary) if public else summary


def _latest_payload(public: bool = False) -> dict[str, Any]:
    out_dir = _default_out_dir()
    run_dir = _latest_run_dir(out_dir)
    root = _repo_root()
    quality = _quality_root()
    payload = {
        "ok": True,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "repoRoot": str(root),
        "qualityRoot": str(quality),
        "outDir": str(out_dir),
        "installed": {
            "qualityRoot": quality.exists(),
            "cli": (quality / "bin" / "prisma-quality.mjs").exists(),
            "profiles": (quality / "profiles").exists(),
            "contracts": (quality / "contracts").exists(),
            "gates": (quality / "gates").exists(),
        },
        "actions": _actions_payload(public=False)["actions"],
        "latestRun": _summarize_run_dir(run_dir, public=public),
    }
    return _redact(payload) if public else payload


def _actions_payload(public: bool = False) -> dict[str, Any]:
    actions = []
    for key, spec in QUALITY_ACTIONS.items():
        actions.append({
            "id": key,
            "label": spec.get("label"),
            "description": spec.get("description"),
            "profile": spec.get("profile"),
            "url": f"/api/quality/run/{key}",
            "localOnly": True,
            "danger": False,
        })
    return {
        "ok": True,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "actions": actions,
    }


def _build_command(action: str, spec: dict[str, Any], out_dir: Path) -> list[str]:
    cli = _quality_root() / "bin" / "prisma-quality.mjs"
    node = _node_executable()
    base = [node, str(cli)]
    if spec.get("kind") == "flag":
        return base + list(spec.get("args", [])) + ["--repo-root", str(_repo_root())]
    profile = str(spec.get("profile") or action)
    return base + ["--profile", profile, "--repo-root", str(_repo_root()), "--out-dir", str(out_dir)]


def _run_action(action: str, public: bool = False) -> dict[str, Any]:
    if public:
        return {"ok": False, "status": "FORBIDDEN", "reason": "quality actions are local-only", "source": SOURCE, "action": action}
    spec = QUALITY_ACTIONS.get(action)
    if not spec:
        return {"ok": False, "status": "UNKNOWN_ACTION", "source": SOURCE, "action": action, "availableActions": sorted(QUALITY_ACTIONS)}
    cli = _quality_root() / "bin" / "prisma-quality.mjs"
    if not cli.exists():
        return {"ok": False, "status": "QUALITY_CLI_MISSING", "source": SOURCE, "action": action, "cli": str(cli)}

    out_dir = _default_out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    logs = _logs_root()
    logs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    action_log = logs / f"quality_{action}_{stamp}.log"
    cmd = _build_command(action, spec, out_dir)
    env = os.environ.copy()
    env["PRISMA_CONTROL_CENTER"] = "1"
    env["NODE_DISABLE_COLORS"] = "1"
    started = _now()
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(_repo_root()),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=int(spec.get("timeout", 240)),
        )
        action_log.write_text(
            "PRISMA Quality Bay action\n"
            f"ACTION: {action}\n"
            f"LABEL: {spec.get('label')}\n"
            "COMMAND: " + " ".join(cmd) + "\n"
            f"STARTED: {started}\n"
            f"FINISHED: {_now()}\n"
            f"RETURN_CODE: {completed.returncode}\n\n"
            "STDOUT:\n" + completed.stdout + "\n\n"
            "STDERR:\n" + completed.stderr + "\n",
            encoding="utf-8",
            newline="\n",
        )
        run_dir = _run_dir_from_stdout(completed.stdout, out_dir)
        summary = _summarize_run_dir(run_dir, public=False)
        stdout_text = completed.stdout or ""
        stderr_text = completed.stderr or ""
        decision = summary.get("decision") if isinstance(summary, dict) else None
        ok = completed.returncode == 0 or decision in {"READY_FOR_CUSTOMER_PROMOTION", "READY", "PASS"}
        # Quality uses non-zero exits for useful blocked/warning evidence. Keep payload usable.
        return {
            "ok": ok,
            "status": "COMPLETED" if completed.returncode == 0 else "COMPLETED_WITH_FINDINGS",
            "source": SOURCE,
            "action": action,
            "label": spec.get("label"),
            "startedAt": started,
            "finishedAt": _now(),
            "returnCode": completed.returncode,
            "log": str(action_log),
            "stdoutSample": stdout_text[-3500:],
            "stderrSample": stderr_text[-1800:],
            "summary": summary,
            "latest": _latest_payload(public=False),
        }
    except subprocess.TimeoutExpired as exc:
        action_log.write_text(
            "PRISMA Quality Bay action timeout\n"
            f"ACTION: {action}\n"
            "COMMAND: " + " ".join(cmd) + "\n"
            f"STARTED: {started}\n"
            f"TIMEOUT: {spec.get('timeout', 240)}\n"
            f"ERROR: {exc}\n",
            encoding="utf-8",
            newline="\n",
        )
        return {"ok": False, "status": "TIMEOUT", "source": SOURCE, "action": action, "error": str(exc), "log": str(action_log)}
    except Exception as exc:
        return {"ok": False, "status": "START_FAILED", "source": SOURCE, "action": action, "error": str(exc), "log": str(action_log)}


def quality_command_payload(path_text: str, public: bool = False) -> dict[str, Any]:
    parsed = urlparse(path_text)
    path = parsed.path.rstrip("/") or "/api/quality/latest"
    _ = parse_qs(parsed.query)
    if path == "/api/quality/actions":
        return _actions_payload(public=public)
    if path == "/api/quality/latest":
        return _latest_payload(public=public)
    if path.startswith("/api/quality/run/"):
        action = path.rsplit("/", 1)[-1].strip().lower()
        return _run_action(action, public=public)
    return _latest_payload(public=public)
