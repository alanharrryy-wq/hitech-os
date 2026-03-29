#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import threading
import webbrowser
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        continue

from tools.hos._core.stable_json import dump_json, load_json  # noqa: E402
from tools.hos.git_sentinel.ci_gate import run_ci_gate  # noqa: E402
from tools.hos.git_sentinel.config import SentinelConfig, build_config  # noqa: E402
from tools.hos.git_sentinel.git_utils import (  # noqa: E402
    git_deleted_tracked_files,
    git_modified_tracked_files,
    git_untracked_files,
)
from tools.hos.git_sentinel.learning_engine import read_telemetry_history  # noqa: E402
from tools.hos.git_sentinel.sentinel import SentinelRunOptions, run_sentinel_cycle  # noqa: E402
from tools.hos.git_sentinel.utils import now_utc_iso  # noqa: E402


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = load_json(path)
    except (OSError, ValueError):
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def _path_from_config(config: SentinelConfig, raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate.resolve()
    return (config.repo_root / raw).resolve()


def _latest_guardian_summary(config: SentinelConfig) -> dict[str, Any]:
    if not config.log_dir.exists():
        return {}
    candidates = sorted(
        [path for path in config.log_dir.glob("guardian_summary_*.json") if path.is_file()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return {}
    return _read_json(candidates[0])


def _changed_paths(config: SentinelConfig) -> list[str]:
    runtime_prefixes: set[str] = {
        str(item).replace("\\", "/").strip("/")
        for item in config.runtime_artifact_dirs
        if str(item).strip()
    }
    try:
        runtime_prefixes.add(config.output_root.resolve().relative_to(config.repo_root.resolve()).as_posix().strip("/"))
    except ValueError:
        pass

    def _is_runtime_noise(path: str) -> bool:
        normalized = str(path).replace("\\", "/").strip("/")
        if not normalized:
            return False
        for prefix in runtime_prefixes:
            if not prefix:
                continue
            if normalized == prefix or normalized.startswith(prefix + "/"):
                return True
        return False

    changed = set(git_modified_tracked_files(config.repo_root))
    changed.update(git_untracked_files(config.repo_root))
    changed.update(git_deleted_tracked_files(config.repo_root))
    return sorted([path for path in changed if not _is_runtime_noise(path)])


def _parse_iso_utc(raw: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _learning_progress(config: SentinelConfig) -> dict[str, Any]:
    history = read_telemetry_history(config=config, limit=120)
    if not history:
        return {
            "historyPoints": 0,
            "healthDelta7d": 0,
            "healthDelta30d": 0,
            "artifactDelta30d": 0,
            "securityFindingDelta30d": 0,
            "falsePositiveRateDelta30d": 0.0,
            "latestHealthScore": 0,
            "latestSecurityFindings": 0,
            "latestArtifactCount": 0,
            "latestFalsePositiveRate": 0.0,
        }

    end = history[-1]
    end_ts = _parse_iso_utc(str(end.get("timestamp", ""))) or datetime.now(UTC)

    def _window_start(days: int) -> dict[str, Any]:
        cutoff = end_ts - timedelta(days=max(1, int(days)))
        selected = history[0]
        for row in history:
            row_ts = _parse_iso_utc(str(row.get("timestamp", "")))
            if row_ts is None:
                continue
            if row_ts >= cutoff:
                selected = row
                break
        return selected

    start_7 = _window_start(7)
    start_30 = _window_start(30)

    def _n(payload: dict[str, Any], key: str) -> float:
        raw = payload.get(key, 0)
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    progress = {
        "historyPoints": len(history),
        "healthDelta7d": round(_n(end, "healthScore") - _n(start_7, "healthScore"), 2),
        "healthDelta30d": round(_n(end, "healthScore") - _n(start_30, "healthScore"), 2),
        "artifactDelta30d": round(_n(end, "artifactCount") - _n(start_30, "artifactCount"), 2),
        "securityFindingDelta30d": round(
            _n(end, "securityFindingCount") - _n(start_30, "securityFindingCount"),
            2,
        ),
        "falsePositiveRateDelta30d": round(
            _n(end, "securityFalsePositiveRate") - _n(start_30, "securityFalsePositiveRate"),
            4,
        ),
        "latestHealthScore": int(_n(end, "healthScore")),
        "latestSecurityFindings": int(_n(end, "securityFindingCount")),
        "latestArtifactCount": int(_n(end, "artifactCount")),
        "latestFalsePositiveRate": round(_n(end, "securityFalsePositiveRate"), 4),
    }
    return progress


class ActionController:
    def __init__(self, config: SentinelConfig) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._state: dict[str, Any] = {
            "running": False,
            "runningAction": "",
            "lastStartedAt": "",
            "lastFinishedAt": "",
            "lastStatus": "idle",
            "lastError": "",
            "lastHealthScore": 0,
            "lastCiGatePassed": None,
            "lastReportJson": "",
            "lastCiGateReport": "",
            "lastTrigger": "",
            "lastAction": "",
            "lastSummary": "",
        }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def trigger(self, action: str, trigger_source: str = "dashboard") -> dict[str, Any]:
        normalized_action = str(action or "").strip().lower()
        if normalized_action not in {"scan", "fix", "ci_gate", "to_healthy"}:
            return {
                "accepted": False,
                "reason": "unknown_action",
                "manualCycle": self.snapshot(),
            }
        if normalized_action in {"fix", "to_healthy"}:
            changed_paths = _changed_paths(config=self._config)
            if not changed_paths:
                return {
                    "accepted": False,
                    "reason": "empty_cycle_blocked",
                    "manualCycle": self.snapshot(),
                }
        with self._lock:
            if bool(self._state.get("running", False)):
                return {
                    "accepted": False,
                    "reason": "already_running",
                    "manualCycle": dict(self._state),
                }
            self._state["running"] = True
            self._state["runningAction"] = normalized_action
            self._state["lastStartedAt"] = now_utc_iso()
            self._state["lastStatus"] = "running"
            self._state["lastError"] = ""
            self._state["lastTrigger"] = str(trigger_source)
            self._state["lastAction"] = normalized_action
            self._state["lastSummary"] = f"{normalized_action} queued"

        worker = threading.Thread(
            target=self._run_action,
            args=(normalized_action,),
            name=f"git-sentinel-action-{normalized_action}",
            daemon=True,
        )
        worker.start()
        return {
            "accepted": True,
            "reason": "started",
            "manualCycle": self.snapshot(),
        }

    def _run_action(self, action: str) -> None:
        status = "ok"
        error = ""
        health_score = 0
        report_json = ""
        ci_gate_passed: bool | None = None
        ci_gate_report = ""
        summary = ""
        try:
            if action == "scan":
                payload = run_sentinel_cycle(
                    config=self._config,
                    options=SentinelRunOptions(
                        apply=False,
                        update_ignore=False,
                        enable_cleanup=False,
                        enable_repair=False,
                        scan_only=True,
                    ),
                )
                health_score = int(payload.get("health", {}).get("score", 0))
                report_json = str(payload.get("files", {}).get("reportJson", ""))
                summary = f"scan complete health={health_score}"
            elif action == "ci_gate":
                payload = run_ci_gate(config=self._config, base_ref=None, run_security_eval=True)
                ci_gate_passed = bool(payload.get("passed", False))
                ci_gate_report = str(payload.get("files", {}).get("latest", ""))
                summary = f"ci_gate passed={ci_gate_passed} failures={len(payload.get('failures', []))}"
            elif action == "to_healthy":
                target_score = 85
                max_passes = 3
                pass_summaries: list[str] = []
                latest_health = 0
                latest_gate = False
                for idx in range(1, max_passes + 1):
                    if idx > 1 and not _changed_paths(config=self._config):
                        pass_summaries.append(f"pass{idx}:skipped_empty_workspace")
                        break
                    _fix_payload = run_sentinel_cycle(
                        config=self._config,
                        options=SentinelRunOptions(
                            apply=True,
                            apply_cleanup=True,
                            apply_repair=True,
                            update_ignore=False,
                        ),
                    )
                    _scan_payload = run_sentinel_cycle(
                        config=self._config,
                        options=SentinelRunOptions(
                            apply=False,
                            update_ignore=False,
                            enable_cleanup=False,
                            enable_repair=False,
                            scan_only=True,
                        ),
                    )
                    _gate_payload = run_ci_gate(config=self._config, base_ref=None, run_security_eval=True)

                    latest_health = int(_scan_payload.get("health", {}).get("score", 0))
                    health_score = latest_health
                    report_json = str(_scan_payload.get("files", {}).get("reportJson", ""))
                    if not report_json:
                        report_json = str(_fix_payload.get("files", {}).get("reportJson", ""))

                    latest_gate = bool(_gate_payload.get("passed", False))
                    ci_gate_passed = latest_gate
                    ci_gate_report = str(_gate_payload.get("files", {}).get("latest", ""))
                    pass_summaries.append(f"pass{idx}:health={latest_health},gate={latest_gate}")
                    if latest_health >= target_score and latest_gate:
                        break

                status_word = "ok" if latest_health >= target_score and latest_gate else "partial"
                status = status_word
                summary = f"to_healthy {status_word} {' | '.join(pass_summaries)}"
            else:
                payload = run_sentinel_cycle(
                    config=self._config,
                    options=SentinelRunOptions(
                        apply=True,
                        apply_cleanup=True,
                        apply_repair=True,
                        update_ignore=False,
                    ),
                )
                health_score = int(payload.get("health", {}).get("score", 0))
                report_json = str(payload.get("files", {}).get("reportJson", ""))
                summary = f"fix complete health={health_score} errors={len(payload.get('errors', []))}"
        except Exception as exc:  # pragma: no cover
            status = "error"
            error = f"{exc.__class__.__name__}: {exc}"
            summary = f"{action} failed"
        finally:
            finished = now_utc_iso()
            with self._lock:
                self._state["running"] = False
                self._state["runningAction"] = ""
                self._state["lastFinishedAt"] = finished
                self._state["lastStatus"] = status
                self._state["lastError"] = error
                self._state["lastHealthScore"] = health_score
                self._state["lastReportJson"] = report_json
                self._state["lastCiGatePassed"] = ci_gate_passed
                self._state["lastCiGateReport"] = ci_gate_report
                self._state["lastSummary"] = summary


def collect_dashboard_state(config: SentinelConfig, action_controller: ActionController | None = None) -> dict[str, Any]:
    report = _read_json((config.report_dir / "git_sentinel_report_latest.json").resolve())
    telemetry = _read_json((config.telemetry_dir / "telemetry_latest.json").resolve())
    security_eval = _read_json((config.telemetry_dir / "security_eval_latest.json").resolve())
    ci_gate = _read_json((config.telemetry_dir / "ci_gate_latest.json").resolve())
    false_positive_metrics = _read_json((config.telemetry_dir / "false_positive_metrics_latest.json").resolve())
    dashboard_payload = _read_json((config.dashboard_dir / "dashboard_data.json").resolve())
    guardian_summary = _latest_guardian_summary(config=config)
    false_positive_audit = _read_json(_path_from_config(config=config, raw=config.false_positive_audit_path))

    health = report.get("health", {})
    security_summary = report.get("security", {})
    security_eval_metrics = security_eval.get("metrics", {})
    ci_gate_security = ci_gate.get("security", {}).get("summary", {})
    ci_gate_failures = ci_gate.get("failures", [])

    return {
        "timestamp": now_utc_iso(),
        "repoRoot": config.repo_root.as_posix(),
        "cards": {
            "healthScore": int(health.get("score", 0)),
            "healthStatus": str(health.get("status", "unknown")),
            "securityFindings": int(security_summary.get("findingCount", 0)),
            "falsePositiveRate": float(security_summary.get("falsePositiveRate", 0.0)),
            "securityEvalF1": float(security_eval_metrics.get("f1", 0.0)),
            "securityEvalPassed": bool(security_eval.get("passed", False)),
            "ciGatePassed": bool(ci_gate.get("passed", True)),
            "guardianCycles": int(guardian_summary.get("cycles", 0)),
            "guardianIntervalSec": int(
                guardian_summary.get(
                    "intervalSecondsStart",
                    guardian_summary.get("intervalSecondsFinal", guardian_summary.get("intervalSeconds", 0)),
                )
                or 0
            ),
            "guardianDynamicIntervalSec": int(
                guardian_summary.get(
                    "intervalSecondsFinal",
                    guardian_summary.get("intervalSeconds", 0),
                )
                or 0
            ),
        },
        "health": health,
        "security": security_summary,
        "securityFindingsTop": report.get("dashboard", {}).get("alerts", [])[:25],
        "securityEval": security_eval,
        "ciGate": {
            "summary": ci_gate_security,
            "baseRef": ci_gate.get("baseRef", ""),
            "changedPathCount": int(ci_gate.get("changedPathCount", 0)),
            "failures": ci_gate_failures,
        },
        "guardian": {
            "summary": guardian_summary,
            "lockPath": _path_from_config(config=config, raw=config.lock_path).as_posix(),
            "lockPresent": _path_from_config(config=config, raw=config.lock_path).exists(),
        },
        "retention": report.get("retention", {}),
        "alertsDispatch": report.get("alertsDispatch", {}),
        "falsePositive": {
            "metrics": false_positive_metrics,
            "audit": false_positive_audit,
        },
        "dashboardData": dashboard_payload,
        "learningProgress": _learning_progress(config=config),
        "manualCycle": action_controller.snapshot() if action_controller else {},
        "actionRunner": action_controller.snapshot() if action_controller else {},
        "files": {
            "reportLatest": (config.report_dir / "git_sentinel_report_latest.json").resolve().as_posix(),
            "telemetryLatest": (config.telemetry_dir / "telemetry_latest.json").resolve().as_posix(),
            "securityEvalLatest": (config.telemetry_dir / "security_eval_latest.json").resolve().as_posix(),
            "ciGateLatest": (config.telemetry_dir / "ci_gate_latest.json").resolve().as_posix(),
            "falsePositiveAudit": _path_from_config(config=config, raw=config.false_positive_audit_path).as_posix(),
        },
    }


_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Git Sentinel Control Deck</title>
  <style>
    :root {
      --radius: 16px;
      --text: #e6f0ff;
      --muted: #9bb1d4;
      --ok: #1ee4a0;
      --warn: #ffbe57;
      --bad: #ff6b6b;
      --panel: rgba(10, 18, 36, 0.8);
      --line: rgba(125, 170, 255, 0.2);
      --line-strong: rgba(125, 170, 255, 0.38);
      --pill-bg: rgba(8, 13, 27, 0.85);
      --table-line: rgba(118, 156, 226, 0.18);
      --button-bg: linear-gradient(140deg, #1957a8, #0f9e8a);
      --button-fg: #f6fbff;
      --panel-solid: #0a1530;
      --frost-tint: rgba(113, 168, 255, 0.12);
      --hero-bg: linear-gradient(145deg, rgba(15, 24, 47, 0.92), rgba(8, 13, 28, 0.9));
      --shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
      --pre-bg: rgba(8, 13, 26, 0.72);
      --bg-layer-1: radial-gradient(1100px 800px at -8% -12%, rgba(80, 147, 255, 0.25), transparent 62%);
      --bg-layer-2: radial-gradient(860px 760px at 108% 10%, rgba(49, 255, 203, 0.16), transparent 56%);
      --bg-layer-3: radial-gradient(760px 620px at 44% 116%, rgba(35, 95, 255, 0.2), transparent 56%);
      --bg-layer-4: linear-gradient(160deg, #04070f 0%, #091227 48%, #040911 100%);
    }

    * { box-sizing: border-box; }
    html, body { min-height: 100%; }
    body {
      margin: 0;
      color: var(--text);
      font-family: "Bahnschrift", "Trebuchet MS", "Franklin Gothic Medium", sans-serif;
      letter-spacing: 0.2px;
      padding: 20px;
      background: var(--bg-layer-1), var(--bg-layer-2), var(--bg-layer-3), var(--bg-layer-4);
      transition: background 300ms ease, color 300ms ease;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.24;
      background-image:
        repeating-linear-gradient(90deg, rgba(255,255,255,0.02) 0, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 122px),
        repeating-linear-gradient(0deg, rgba(255,255,255,0.015) 0, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 122px);
      mix-blend-mode: screen;
    }

    body::after {
      content: "";
      position: fixed;
      inset: -20% -10% auto auto;
      width: 520px;
      height: 520px;
      pointer-events: none;
      background: radial-gradient(circle at center, rgba(126, 185, 255, 0.38), rgba(126, 185, 255, 0.02) 62%, transparent 70%);
      filter: blur(32px);
      opacity: 0.7;
      z-index: 0;
    }

    body[data-theme="cloud"] {
      --text: #0e1c35;
      --muted: #5d6f8d;
      --ok: #0f9b63;
      --warn: #d58b0f;
      --bad: #cc4242;
      --panel: rgba(255, 255, 255, 0.58);
      --line: rgba(92, 126, 195, 0.2);
      --line-strong: rgba(90, 134, 219, 0.45);
      --pill-bg: rgba(255, 255, 255, 0.64);
      --table-line: rgba(141, 161, 205, 0.24);
      --button-bg: linear-gradient(135deg, #6d98ff, #52c9ff);
      --button-fg: #072347;
      --panel-solid: #f3f7ff;
      --frost-tint: rgba(128, 175, 255, 0.2);
      --hero-bg: linear-gradient(138deg, rgba(255, 255, 255, 0.74), rgba(241, 248, 255, 0.66));
      --shadow: 0 18px 40px rgba(78, 118, 186, 0.2);
      --pre-bg: rgba(255, 255, 255, 0.55);
      --bg-layer-1: radial-gradient(1100px 900px at -8% -14%, rgba(90, 183, 255, 0.4), transparent 58%);
      --bg-layer-2: radial-gradient(860px 760px at 110% 8%, rgba(149, 225, 255, 0.42), transparent 58%);
      --bg-layer-3: radial-gradient(760px 620px at 38% 118%, rgba(255, 180, 214, 0.26), transparent 58%);
      --bg-layer-4: linear-gradient(165deg, #f6faff 0%, #eef4ff 50%, #f8fcff 100%);
    }

    body[data-theme="cloud"]::before {
      opacity: 0.28;
      mix-blend-mode: multiply;
    }

    body[data-theme="cloud"]::after {
      background: radial-gradient(circle at center, rgba(104, 160, 255, 0.26), rgba(255, 176, 218, 0.28) 46%, rgba(255, 255, 255, 0.06) 68%, transparent 76%);
      filter: blur(50px);
      opacity: 0.92;
    }

    .shell {
      width: min(1840px, 100%);
      margin: 0 auto;
      display: grid;
      gap: 12px;
      animation: rise 420ms ease;
      position: relative;
      z-index: 1;
    }

    @keyframes rise {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .hero {
      border: 1px solid transparent;
      border-radius: calc(var(--radius) + 4px);
      padding: 16px;
      box-shadow: var(--shadow), inset 0 0 0 1px rgba(255,255,255,0.04);
      background:
        linear-gradient(var(--hero-bg), var(--hero-bg)) padding-box,
        linear-gradient(124deg, rgba(111, 175, 255, 0.48), rgba(123, 255, 217, 0.25), rgba(132, 163, 255, 0.42)) border-box;
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(14px) saturate(135%);
      -webkit-backdrop-filter: blur(14px) saturate(135%);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(100deg, transparent, rgba(120, 196, 255, 0.14), transparent);
      transform: translateX(-110%);
      animation: sweep 7s linear infinite;
      pointer-events: none;
    }

    .hero::before {
      content: "";
      position: absolute;
      width: 420px;
      height: 420px;
      top: -240px;
      right: -110px;
      border-radius: 999px;
      background: radial-gradient(circle at center, rgba(120, 184, 255, 0.42), rgba(120, 184, 255, 0.04) 66%, transparent 74%);
      filter: blur(20px);
      pointer-events: none;
      opacity: 0.9;
    }

    body[data-theme="cloud"] .hero::before {
      background: radial-gradient(circle at center, rgba(127, 186, 255, 0.48), rgba(255, 190, 224, 0.35) 46%, rgba(255, 255, 255, 0.12) 66%, transparent 76%);
      filter: blur(28px);
      opacity: 1;
    }

    @keyframes sweep {
      to { transform: translateX(110%); }
    }

    .title-wrap {
      position: relative;
      z-index: 2;
      max-width: 920px;
    }

    .title-wrap h1 {
      margin: 0;
      font-size: clamp(28px, 2.8vw, 46px);
      line-height: 1.03;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      font-family: "Impact", "Haettenschweiler", "Franklin Gothic Heavy", sans-serif;
      text-shadow: 0 0 22px rgba(82, 164, 255, 0.24);
    }

    .title-wrap p {
      margin: 8px 0 0;
      font-size: 13px;
      color: var(--muted);
      font-family: "Consolas", "Lucida Console", monospace;
      word-break: break-word;
    }

    .hero-actions {
      position: relative;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;
      flex-wrap: wrap;
    }

    .pill {
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--pill-bg);
      padding: 7px 12px;
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
    }

    .status-pill {
      color: var(--text);
      border-color: rgba(87, 235, 174, 0.45);
      box-shadow: inset 0 0 0 1px rgba(87, 235, 174, 0.26);
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: #3effb9;
      display: inline-block;
      margin-right: 8px;
      animation: pulse 2s infinite;
      vertical-align: middle;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(62, 255, 185, 0.7); }
      70% { box-shadow: 0 0 0 10px rgba(62, 255, 185, 0); }
      100% { box-shadow: 0 0 0 0 rgba(62, 255, 185, 0); }
    }

    .skin-wrap {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 6px 10px;
      background: var(--pill-bg);
      color: var(--muted);
      font-size: 12px;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
    }

    .skin-wrap select {
      border: 1px solid var(--line-strong);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      font-size: 12px;
      font-family: inherit;
      padding: 4px 8px;
      outline: none;
      transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
    }

    .skin-wrap select:hover {
      transform: translateY(-1px);
      border-color: rgba(132, 188, 255, 0.75);
      box-shadow: 0 0 0 2px rgba(120, 175, 255, 0.2);
    }

    body[data-theme="cloud"] .skin-wrap select {
      background: rgba(255, 255, 255, 0.75);
      color: #163056;
    }

    button {
      border: 1px solid transparent;
      border-radius: 12px;
      padding: 9px 13px;
      font-family: inherit;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.4px;
      text-transform: uppercase;
      color: var(--button-fg);
      background:
        linear-gradient(var(--button-bg), var(--button-bg)) padding-box,
        linear-gradient(120deg, rgba(255,255,255,0.58), rgba(255,255,255,0.06), rgba(255,255,255,0.4)) border-box;
      box-shadow: 0 10px 22px rgba(25, 61, 130, 0.28), inset 0 1px 0 rgba(255,255,255,0.25);
      cursor: pointer;
      transition: transform 180ms cubic-bezier(0.2, 0.8, 0.2, 1), filter 180ms ease, box-shadow 180ms ease;
      white-space: nowrap;
      position: relative;
      overflow: hidden;
      isolation: isolate;
    }

    button::before {
      content: "";
      position: absolute;
      top: -40%;
      left: -35%;
      width: 45%;
      height: 180%;
      background: linear-gradient(110deg, rgba(255,255,255,0), rgba(255,255,255,0.42), rgba(255,255,255,0));
      transform: translateX(-180%) rotate(14deg);
      transition: transform 620ms ease;
      pointer-events: none;
      z-index: 2;
    }

    button::after {
      content: "";
      position: absolute;
      left: 14%;
      right: 14%;
      bottom: -18px;
      height: 18px;
      border-radius: 999px;
      background: rgba(61, 117, 255, 0.46);
      filter: blur(14px);
      opacity: 0.36;
      transition: opacity 180ms ease, transform 180ms ease;
      pointer-events: none;
      z-index: 0;
    }

    button:hover {
      transform: translateY(-2px) scale(1.03);
      filter: brightness(1.07) saturate(1.05);
      box-shadow: 0 18px 30px rgba(22, 59, 129, 0.34), 0 0 0 1px rgba(255,255,255,0.28) inset;
    }

    button:hover::before {
      transform: translateX(380%) rotate(14deg);
    }

    button:hover::after {
      opacity: 0.62;
      transform: scaleX(1.08);
    }

    button:active {
      transform: translateY(0) scale(0.995);
    }

    button:focus-visible {
      outline: 2px solid rgba(122, 186, 255, 0.75);
      outline-offset: 2px;
    }

    button.btn-fix {
      background:
        linear-gradient(136deg, #c25e26, #deaa25) padding-box,
        linear-gradient(118deg, rgba(255,243,220,0.8), rgba(255,229,177,0.16), rgba(255,248,231,0.72)) border-box;
      color: #fff9f1;
    }

    button.btn-gate {
      background:
        linear-gradient(136deg, #2f66cc, #2c4da2) padding-box,
        linear-gradient(118deg, rgba(219,236,255,0.82), rgba(184,210,255,0.12), rgba(240,246,255,0.76)) border-box;
      color: #eaf1ff;
    }

    button.btn-toggle {
      background:
        linear-gradient(136deg, #4f5d74, #39475f) padding-box,
        linear-gradient(118deg, rgba(224,235,255,0.5), rgba(194,209,244,0.12), rgba(227,235,255,0.45)) border-box;
      color: #e2ebff;
    }

    body[data-theme="cloud"] button.btn-toggle {
      background:
        linear-gradient(136deg, #d5e4ff, #c2d8ff) padding-box,
        linear-gradient(118deg, rgba(255,255,255,0.92), rgba(228,239,255,0.56), rgba(255,255,255,0.9)) border-box;
      color: #173256;
    }

    body[data-theme="cloud"] button {
      box-shadow: 0 10px 24px rgba(112, 148, 221, 0.26), inset 0 1px 0 rgba(255,255,255,0.78);
    }

    body[data-theme="cloud"] button:hover {
      box-shadow: 0 18px 30px rgba(100, 138, 210, 0.34), 0 0 0 1px rgba(255,255,255,0.92) inset;
    }

    button:disabled {
      opacity: 0.58;
      cursor: not-allowed;
      transform: none;
      filter: grayscale(0.25);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .card,
    .section {
      border: 1px solid transparent;
      border-radius: var(--radius);
      background:
        linear-gradient(var(--panel), var(--panel)) padding-box,
        linear-gradient(125deg, rgba(117, 176, 255, 0.45), rgba(101, 240, 189, 0.18), rgba(120, 154, 255, 0.38)) border-box;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03), 0 12px 26px rgba(7, 14, 29, 0.38);
      backdrop-filter: blur(11px) saturate(130%);
      -webkit-backdrop-filter: blur(11px) saturate(130%);
      transition: transform 170ms ease, box-shadow 170ms ease, border-color 170ms ease;
    }

    .card:hover,
    .section:hover {
      transform: translateY(-2px);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08), 0 18px 34px rgba(8, 20, 41, 0.42);
    }

    .card {
      padding: 12px 14px;
      min-height: 94px;
      position: relative;
      overflow: hidden;
    }

    .card::before {
      content: "";
      position: absolute;
      inset: -1px;
      pointer-events: none;
      opacity: 0;
      transition: opacity 170ms ease;
      background: linear-gradient(120deg, rgba(113, 180, 255, 0.22), transparent 42%, rgba(104, 255, 190, 0.16));
    }

    .card:hover::before { opacity: 1; }

    .card::after {
      content: "";
      position: absolute;
      width: 240px;
      height: 160px;
      right: -120px;
      top: -90px;
      border-radius: 999px;
      pointer-events: none;
      background: radial-gradient(circle at center, rgba(131, 186, 255, 0.3), rgba(131, 186, 255, 0.04) 64%, transparent 72%);
      filter: blur(18px);
      opacity: 0.72;
    }

    .card .label {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 700;
    }

    .card .value {
      margin-top: 6px;
      font-size: clamp(24px, 2.2vw, 33px);
      font-family: "Franklin Gothic Heavy", "Bahnschrift", sans-serif;
      line-height: 1.1;
      text-shadow: 0 0 14px rgba(98, 173, 255, 0.2);
      font-weight: 800;
    }

    .card .sub {
      margin-top: 4px;
      color: #7f95b8;
      font-size: 11px;
    }

    body[data-theme="cloud"] .card .sub { color: #587097; }

    body[data-theme="cloud"] .card,
    body[data-theme="cloud"] .section {
      background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.68), rgba(250, 253, 255, 0.46)) padding-box,
        linear-gradient(128deg, rgba(115, 173, 255, 0.58), rgba(255, 174, 213, 0.46), rgba(92, 214, 255, 0.56)) border-box;
      box-shadow:
        inset 0 0 0 1px rgba(255,255,255,0.62),
        0 22px 42px rgba(103, 137, 199, 0.26),
        0 5px 10px rgba(148, 175, 227, 0.22);
    }

    body[data-theme="cloud"] .card::after {
      background: radial-gradient(circle at center, rgba(124, 188, 255, 0.34), rgba(255, 199, 226, 0.28) 45%, rgba(255,255,255,0.08) 66%, transparent 74%);
      filter: blur(22px);
      opacity: 0.88;
    }

    .panel-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .intent-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(280px, 0.6fr) minmax(0, 1fr);
      gap: 18px;
      align-items: stretch;
    }

    .section {
      padding: 12px;
      position: relative;
      overflow: hidden;
    }

    .recovery-hub {
      display: grid;
      grid-template-rows: auto auto auto;
      gap: 10px;
      align-content: start;
      background:
        linear-gradient(140deg, rgba(11, 25, 52, 0.9), rgba(8, 16, 34, 0.9)) padding-box,
        linear-gradient(125deg, rgba(131, 186, 255, 0.72), rgba(99, 255, 201, 0.4), rgba(120, 155, 255, 0.62)) border-box;
    }

    body[data-theme="cloud"] .recovery-hub {
      background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.84), rgba(244, 249, 255, 0.64)) padding-box,
        linear-gradient(126deg, rgba(116, 180, 255, 0.74), rgba(255, 177, 215, 0.6), rgba(101, 205, 255, 0.72)) border-box;
    }

    .hub-sub {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .hub-status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 10px;
      border-radius: 999px;
      border: 1px solid var(--line-strong);
      font-size: 12px;
      color: var(--muted);
      width: fit-content;
      background: rgba(10, 18, 38, 0.52);
    }

    body[data-theme="cloud"] .hub-status {
      background: rgba(255, 255, 255, 0.62);
    }

    .hub-actions {
      display: grid;
      gap: 8px;
    }

    .hub-actions button {
      width: 100%;
      justify-content: center;
    }

    button.btn-scan {
      background:
        linear-gradient(136deg, #1f68b8, #1198a3) padding-box,
        linear-gradient(118deg, rgba(216, 242, 255, 0.78), rgba(175, 236, 255, 0.2), rgba(236, 248, 255, 0.74)) border-box;
      color: #eaf8ff;
    }

    button.btn-healthy {
      background:
        linear-gradient(136deg, #1a8f5e, #45b87c) padding-box,
        linear-gradient(118deg, rgba(230, 255, 241, 0.85), rgba(181, 255, 214, 0.24), rgba(236, 255, 244, 0.78)) border-box;
      color: #f2fff7;
    }

    body[data-theme="cloud"] button.btn-healthy {
      color: #073f28;
    }

    .hub-tip {
      margin: 0;
      font-size: 11px;
      color: var(--muted);
      line-height: 1.35;
    }

    body[data-theme="cloud"] .section {
      box-shadow:
        inset 0 0 0 1px rgba(255,255,255,0.35),
        0 14px 28px rgba(70, 115, 190, 0.12);
    }

    @supports not ((backdrop-filter: blur(2px)) or (-webkit-backdrop-filter: blur(2px))) {
      .hero,
      .card,
      .section,
      .pill,
      .skin-wrap {
        background: var(--panel-solid);
      }

      .hero {
        border-color: var(--line-strong);
      }

      .card,
      .section {
        border-color: var(--line);
        box-shadow: 0 12px 24px rgba(9, 16, 30, 0.28);
      }

      body[data-theme="cloud"] .hero,
      body[data-theme="cloud"] .card,
      body[data-theme="cloud"] .section,
      body[data-theme="cloud"] .pill,
      body[data-theme="cloud"] .skin-wrap {
        background:
          linear-gradient(140deg, rgba(255,255,255,0.9), rgba(241,247,255,0.9)) padding-box,
          linear-gradient(120deg, rgba(110,170,255,0.55), rgba(255,184,222,0.4), rgba(101,205,255,0.5)) border-box;
      }
    }

    .section h2 {
      margin: 0 0 10px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text);
      font-family: "Franklin Gothic Demi", "Bahnschrift", sans-serif;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }

    th, td {
      border-bottom: 1px solid var(--table-line);
      padding: 7px 8px;
      font-size: 12px;
      text-align: left;
      vertical-align: top;
      word-break: break-word;
    }

    th {
      width: 44%;
      color: var(--muted);
      font-weight: 700;
    }

    .findings th { width: auto; }
    .findings td { font-family: "Consolas", "Lucida Console", monospace; font-size: 11px; }

    pre {
      margin: 8px 0 0;
      background: var(--pre-bg);
      border: 1px dashed var(--table-line);
      color: var(--muted);
      border-radius: 10px;
      padding: 8px 9px;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "Consolas", "Lucida Console", monospace;
      font-size: 11px;
      display: none;
    }

    pre.has-errors {
      display: block;
      border-color: rgba(255, 130, 130, 0.45);
      color: #ffdede;
    }

    .insights {
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .insights li strong { color: var(--text); }

    .ok { color: var(--ok); font-weight: 700; }
    .warn { color: var(--warn); font-weight: 700; }
    .bad { color: var(--bad); font-weight: 700; }

    @media (max-width: 1200px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .panel-grid { grid-template-columns: 1fr; }
      .intent-grid { grid-template-columns: 1fr; gap: 10px; }
    }

    @media (max-width: 760px) {
      body { padding: 12px; }
      .grid { grid-template-columns: 1fr; }
      .hero { padding: 14px; }
      .hero-actions { justify-content: flex-start; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="hero">
      <div class="title-wrap">
        <h1>Git Sentinel Control Deck</h1>
        <p id="meta">loading...</p>
      </div>
      <div class="hero-actions">
        <label class="skin-wrap">Skin
          <select id="skinSelect" onchange="setSkin(this.value)">
            <option value="night">Neon Night</option>
            <option value="cloud">Cloud Glass</option>
          </select>
        </label>
        <span class="pill status-pill"><span class="dot"></span>Live Guardian</span>
        <span class="pill" id="runnerStatus">idle</span>
        <span class="pill" id="refreshClock">refresh in 60s</span>
        <button class="btn-toggle" id="toggleRefreshButton" onclick="toggleAutoRefresh()">Pause auto</button>
        <button onclick="refresh()">Refresh now</button>
      </div>
    </header>

    <section class="grid" id="cards"></section>

    <section class="section">
      <h2>Learning Progress</h2>
      <table><tbody id="learningProgress"></tbody></table>
    </section>

    <section class="intent-grid">
      <div class="section">
        <h2>What This Means</h2>
        <ul id="meaningList" class="insights"></ul>
      </div>
      <div class="section recovery-hub">
        <h2>Recovery Console</h2>
        <p class="hub-sub">Usa estos botones para recuperar salud sin correr comandos en terminal.</p>
        <div id="healthyStatus" class="hub-status">target: healthy >= 85 + ci gate pass</div>
        <div class="hub-actions">
          <button class="btn-scan" data-action="scan" data-default="Run scan" data-running="Scanning..." onclick="runAction('scan')">Run scan</button>
          <button class="btn-fix" data-action="fix" data-default="Run fix cycle" data-running="Fixing..." onclick="runAction('fix')">Run fix cycle</button>
          <button class="btn-gate" data-action="ci_gate" data-default="Run CI gate" data-running="Running gate..." onclick="runAction('ci_gate')">Run CI gate</button>
          <button class="btn-healthy" data-action="to_healthy" data-default="Run to Healthy" data-running="Optimizing..." onclick="runAction('to_healthy')">Run to Healthy</button>
        </div>
        <p class="hub-tip">Run to Healthy ejecuta fix + scan + ci gate en secuencia (hasta 3 pasadas) y bloquea ciclos vacios.</p>
      </div>
      <div class="section">
        <h2>Next Best Actions</h2>
        <ol id="actionList" class="insights"></ol>
      </div>
    </section>

    <section class="panel-grid">
      <div class="section">
        <h2>Security Severity</h2>
        <table><tbody id="securitySeverity"></tbody></table>
      </div>
      <div class="section">
        <h2>CI Gate</h2>
        <table><tbody id="ciGate"></tbody></table>
        <pre id="ciGateFailures"></pre>
      </div>
    </section>

    <section class="panel-grid">
      <div class="section">
        <h2>Security Eval</h2>
        <table><tbody id="securityEval"></tbody></table>
      </div>
      <div class="section">
        <h2>Suppressions</h2>
        <table><tbody id="suppressions"></tbody></table>
      </div>
    </section>

    <section class="section">
      <h2>Top Security Findings</h2>
      <table class="findings">
        <thead><tr><th>severity</th><th>kind</th><th>path</th><th>line</th><th>snippet</th></tr></thead>
        <tbody id="topFindings"></tbody>
      </table>
    </section>
  </div>

  <script>
    const REFRESH_MS = 60000;
    let nextRefresh = REFRESH_MS / 1000;
    let autoRefreshEnabled = true;

    function esc(v) {
      if (v === null || v === undefined) return "";
      return String(v).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
    }

    function tr(k, v, cls="") { return `<tr><th>${esc(k)}</th><td class="${cls}">${esc(v)}</td></tr>`; }

    function statusClass(v) {
      const s = String(v).toLowerCase();
      if (["true", "passed", "healthy", "ok", "ready"].includes(s)) return "ok";
      if (["warning", "warn"].includes(s)) return "warn";
      if (["false", "failed", "critical", "error"].includes(s)) return "bad";
      return "";
    }

    function fmtRate(v) {
      const n = Number(v || 0);
      return `${(n * 100).toFixed(1)}%`;
    }

    function fmtInterval(sec) {
      const n = Number(sec || 0);
      if (!n || n <= 0) return "n/a";
      if (n < 60) return `${n}s`;
      const m = Math.floor(n / 60);
      const s = n % 60;
      if (!s) return `${m}m`;
      return `${m}m ${s}s`;
    }

    function fmtSigned(n, digits = 0) {
      const value = Number(n || 0);
      const fixed = digits > 0 ? value.toFixed(digits) : Math.round(value).toString();
      return `${value > 0 ? "+" : ""}${fixed}`;
    }

    function setSkin(theme) {
      const normalized = theme === "cloud" ? "cloud" : "night";
      document.body.setAttribute("data-theme", normalized);
      try {
        localStorage.setItem("gitSentinelSkin", normalized);
      } catch (_err) {}
      const select = document.getElementById("skinSelect");
      if (select && select.value !== normalized) select.value = normalized;
    }

    function initSkin() {
      let saved = "night";
      try {
        saved = localStorage.getItem("gitSentinelSkin") || "night";
      } catch (_err) {}
      setSkin(saved);
    }

    function refreshClockTick() {
      if (!autoRefreshEnabled) return;
      nextRefresh -= 1;
      if (nextRefresh < 0) nextRefresh = 0;
      const clock = document.getElementById("refreshClock");
      if (clock) clock.textContent = `refresh in ${nextRefresh}s`;
    }

    function toggleAutoRefresh() {
      autoRefreshEnabled = !autoRefreshEnabled;
      const button = document.getElementById("toggleRefreshButton");
      const clock = document.getElementById("refreshClock");
      if (button) button.textContent = autoRefreshEnabled ? "Pause auto" : "Resume auto";
      if (!autoRefreshEnabled) {
        if (clock) clock.textContent = "auto refresh paused";
      } else {
        nextRefresh = REFRESH_MS / 1000;
      }
    }

    function renderCards(cards) {
      const rows = [
        ["Health Score", `${cards.healthScore} (${cards.healthStatus})`, statusClass(cards.healthStatus), "overall repository hygiene"],
        ["Security Findings", cards.securityFindings, cards.securityFindings > 0 ? "warn" : "ok", "active findings after suppression"],
        ["False Positive Rate", fmtRate(cards.falsePositiveRate), cards.falsePositiveRate > 0.2 ? "warn" : "ok", "suppressed / total findings"],
        ["Security Eval F1", `${cards.securityEvalF1} (${cards.securityEvalPassed})`, cards.securityEvalPassed ? "ok" : "bad", "golden-set detector quality"],
        ["CI Gate", String(cards.ciGatePassed), cards.ciGatePassed ? "ok" : "bad", "incremental diff gate"],
        [
          "Guardian",
          `${cards.guardianCycles} cycles`,
          "",
          `schedule ${fmtInterval(cards.guardianIntervalSec)} | loop ${fmtInterval(cards.guardianDynamicIntervalSec)}`,
        ],
      ];
      document.getElementById("cards").innerHTML = rows.map(([label, value, cls, sub]) =>
        `<div class="card"><div class="label">${esc(label)}</div><div class="value ${cls}">${esc(value)}</div><div class="sub">${esc(sub)}</div></div>`
      ).join("");
    }

    function renderLearningProgress(progress) {
      const health7 = Number(progress.healthDelta7d || 0);
      const health30 = Number(progress.healthDelta30d || 0);
      const findings30 = Number(progress.securityFindingDelta30d || 0);
      const artifacts30 = Number(progress.artifactDelta30d || 0);
      const fp30 = Number(progress.falsePositiveRateDelta30d || 0);

      const findingsClass = findings30 <= 0 ? "ok" : "warn";
      const artifactsClass = artifacts30 <= 0 ? "ok" : "warn";
      const fpClass = fp30 <= 0 ? "ok" : "warn";

      document.getElementById("learningProgress").innerHTML = ""
        + tr("historyPoints", progress.historyPoints || 0)
        + tr("healthDelta7d", fmtSigned(health7), health7 >= 0 ? "ok" : "bad")
        + tr("healthDelta30d", fmtSigned(health30), health30 >= 0 ? "ok" : "bad")
        + tr("securityFindingDelta30d", fmtSigned(findings30), findingsClass)
        + tr("artifactDelta30d", fmtSigned(artifacts30), artifactsClass)
        + tr("falsePositiveRateDelta30d", `${fmtSigned(fp30, 4)}`, fpClass)
        + tr("latestHealthScore", progress.latestHealthScore || 0, (progress.latestHealthScore || 0) >= 85 ? "ok" : "warn")
        + tr("latestSecurityFindings", progress.latestSecurityFindings || 0, (progress.latestSecurityFindings || 0) === 0 ? "ok" : "warn")
        + tr("latestArtifactCount", progress.latestArtifactCount || 0, (progress.latestArtifactCount || 0) <= 0 ? "ok" : "warn");
    }

    function renderSeverity(security) {
      const counts = security.severityCounts || {};
      const keys = Object.keys(counts).sort();
      document.getElementById("securitySeverity").innerHTML = keys.map(k => tr(k, counts[k], statusClass(k))).join("");
    }

    function renderCIGate(ciGate) {
      const summary = ciGate.summary || {};
      const failures = ciGate.failures || [];
      document.getElementById("ciGate").innerHTML = ""
        + tr("baseRef", ciGate.baseRef || "")
        + tr("changedPathCount", ciGate.changedPathCount || 0)
        + tr("mode", summary.mode || "")
        + tr("severityCounts", JSON.stringify(summary.severityCounts || {}))
        + tr("passed", String(!failures.length), failures.length ? "bad" : "ok");
      const failureNode = document.getElementById("ciGateFailures");
      if (!failures.length) {
        failureNode.textContent = "";
        failureNode.classList.remove("has-errors");
        failureNode.style.display = "none";
        return;
      }
      failureNode.textContent = failures.join("\\n");
      failureNode.classList.add("has-errors");
      failureNode.style.display = "block";
    }

    function renderSecurityEval(securityEval) {
      const metrics = securityEval.metrics || {};
      const thresholds = securityEval.thresholds || {};
      document.getElementById("securityEval").innerHTML = ""
        + tr("status", securityEval.status || "")
        + tr("passed", String(!!securityEval.passed), securityEval.passed ? "ok" : "bad")
        + tr("precision", `${metrics.precision} (min ${thresholds.minPrecision})`, (metrics.precision || 0) >= (thresholds.minPrecision || 0) ? "ok" : "bad")
        + tr("recall", `${metrics.recall} (min ${thresholds.minRecall})`, (metrics.recall || 0) >= (thresholds.minRecall || 0) ? "ok" : "bad")
        + tr("f1", `${metrics.f1} (min ${thresholds.minF1})`, (metrics.f1 || 0) >= (thresholds.minF1 || 0) ? "ok" : "bad")
        + tr("tp/fp/fn", `${metrics.tp}/${metrics.fp}/${metrics.fn}`);
    }

    function renderSuppressions(falsePositive) {
      const metrics = (falsePositive.metrics || {}).summary || {};
      const audit = (falsePositive.audit || {});
      document.getElementById("suppressions").innerHTML = ""
        + tr("suppressionCount", metrics.suppressionCount || 0)
        + tr("expiredSuppressionCount", metrics.expiredSuppressionCount || 0, (metrics.expiredSuppressionCount || 0) > 0 ? "warn" : "ok")
        + tr("suppressedFindingCount", metrics.suppressedFindingCount || 0)
        + tr("activeSuppressionCount(audit)", audit.activeSuppressionCount || 0);
    }

    function renderFindings(items) {
      const rows = (items || []).slice(0, 20).map(row =>
        `<tr><td class="${statusClass(row.severity)}">${esc(row.severity)}</td><td>${esc(row.kind)}</td><td>${esc(row.path)}</td><td>${esc(row.line)}</td><td>${esc(row.snippet)}</td></tr>`
      );
      document.getElementById("topFindings").innerHTML = rows.join("");
    }

    function renderGuidance(data) {
      const cards = data.cards || {};
      const security = data.security || {};
      const ciGate = data.ciGate || {};
      const health = Number(cards.healthScore || 0);
      const status = String(cards.healthStatus || "unknown");
      const findings = Number(cards.securityFindings || 0);
      const severityCounts = security.severityCounts || {};
      const medium = Number(severityCounts.medium || 0);
      const low = Number(severityCounts.low || 0);
      const gatePassed = !!cards.ciGatePassed;
      const fpRate = Number(cards.falsePositiveRate || 0);

      const meaning = [
        `<strong>Health Score</strong> resume la higiene general del repo: ${health} (${status}).`,
        `<strong>Security Findings</strong> son hallazgos detectados después de filtros: ${findings} (medium=${medium}, low=${low}).`,
        `<strong>CI Gate</strong> valida cambios incrementales contra ${esc(ciGate.baseRef || "base ref")}: ${gatePassed ? "passed" : "failed"}.`,
        `<strong>False Positive Rate</strong> mide ruido del escaneo: ${fmtRate(fpRate)}.`,
      ];
      document.getElementById("meaningList").innerHTML = meaning.map((row) => `<li>${row}</li>`).join("");

      const actions = [];
      if (!gatePassed) actions.push("Presiona <strong>Run CI gate</strong> y atiende primero los failures de ese panel.");
      if (health < 85) actions.push("Usa <strong>Run to Healthy</strong> para ejecutar fix + scan + ci gate automáticamente.");
      if (health < 85) actions.push("Si no llega en una pasada, repite <strong>Run to Healthy</strong> para estabilizar tendencia.");
      if (findings > 0) actions.push("Revisa <strong>Top Security Findings</strong> y elimina riesgos runtime primero.");
      if (fpRate > 0.2) actions.push("Ajusta suppressions para reducir falsos positivos sin ocultar hallazgos reales.");
      if (!actions.length) actions.push("Todo está estable; usa <strong>Run scan</strong> para chequeo bajo demanda y mantén monitoreo.");
      document.getElementById("actionList").innerHTML = actions.map((row) => `<li>${row}</li>`).join("");

      const targetNode = document.getElementById("healthyStatus");
      if (targetNode) {
        const targetReached = health >= 85 && gatePassed;
        targetNode.textContent = targetReached
          ? `healthy target reached: health=${health}, ci_gate=pass`
          : `target pending: health=${health}/85, ci_gate=${gatePassed ? "pass" : "fail"}`;
        targetNode.classList.remove("ok", "warn", "bad");
        targetNode.classList.add(targetReached ? "ok" : (health >= 75 ? "warn" : "bad"));
      }
    }

    function renderRunner(state) {
      const statusNode = document.getElementById("runnerStatus");
      const running = !!state.running;
      const runningAction = String(state.runningAction || "");
      const lastStatus = String(state.lastStatus || "idle");
      const lastAction = String(state.lastAction || "");
      const lastSummary = String(state.lastSummary || "");
      statusNode.classList.remove("ok", "warn", "bad");

      if (running) {
        statusNode.textContent = `running: ${runningAction || "action"}`;
        statusNode.classList.add("status-pill");
      } else {
        statusNode.classList.remove("status-pill");
        if (lastStatus === "error") {
          statusNode.textContent = `last ${lastAction || "action"}: error`;
          statusNode.classList.add("bad");
        } else if (lastStatus === "ok") {
          statusNode.textContent = `last ${lastAction || "action"}: ok`;
          statusNode.classList.add("ok");
        } else if (lastStatus === "partial") {
          statusNode.textContent = `last ${lastAction || "action"}: partial`;
          statusNode.classList.add("warn");
        } else {
          statusNode.textContent = "idle";
        }
      }

      const actionButtons = document.querySelectorAll("button[data-action]");
      actionButtons.forEach((btn) => {
        const btnAction = String(btn.getAttribute("data-action") || "");
        const defaultLabel = String(btn.getAttribute("data-default") || btn.textContent || "");
        const runningLabel = String(btn.getAttribute("data-running") || "Running...");
        btn.disabled = running;
        btn.textContent = running && btnAction === runningAction ? runningLabel : defaultLabel;
      });

      if (!running && lastSummary) {
        statusNode.title = lastSummary;
      }
    }

    async function runAction(action) {
      try {
        const r = await fetch("/api/actions/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action }),
        });
        const payload = await r.json().catch(() => ({}));
        if (!payload.accepted) {
          if (payload.reason === "empty_cycle_blocked") {
            throw new Error("empty_cycle_blocked (no changed paths)");
          }
          throw new Error(payload.reason || `http_${r.status}`);
        }
        await refresh();
      } catch (err) {
        const statusNode = document.getElementById("runnerStatus");
        statusNode.textContent = `action error: ${err}`;
        statusNode.classList.remove("ok", "warn");
        statusNode.classList.add("bad");
      }
    }

    async function refresh() {
      const r = await fetch("/api/state");
      if (!r.ok) throw new Error(`http_${r.status}`);
      const data = await r.json();
      document.getElementById("meta").textContent = `timestamp=${data.timestamp} repo=${data.repoRoot}`;
      renderCards(data.cards || {});
      renderLearningProgress(data.learningProgress || {});
      renderSeverity(data.security || {});
      renderCIGate(data.ciGate || {});
      renderSecurityEval(data.securityEval || {});
      renderSuppressions(data.falsePositive || {});
      renderFindings(data.securityFindingsTop || []);
      renderGuidance(data);
      renderRunner(data.actionRunner || data.manualCycle || {});
      nextRefresh = REFRESH_MS / 1000;
    }

    initSkin();
    refresh().catch(err => { document.getElementById("meta").textContent = `error=${err}`; });
    setInterval(() => {
      if (autoRefreshEnabled) refresh().catch(() => {});
    }, REFRESH_MS);
    setInterval(refreshClockTick, 1000);
  </script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    state_provider = None
    action_controller = None

    def _json(self, payload: dict[str, Any], status: int = 200) -> None:
        rendered = dump_json(payload)
        body = rendered.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self) -> dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        try:
            parsed = json.loads(raw.decode("utf-8", errors="replace"))
        except ValueError:
            return {}
        if isinstance(parsed, dict):
            return parsed
        return {}

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            self._html(_HTML)
            return
        if self.path.startswith("/api/state"):
            try:
                payload = _Handler.state_provider()
            except Exception as exc:  # pragma: no cover
                self._json({"error": str(exc)}, status=500)
                return
            self._json(payload)
            return
        self._json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.startswith("/api/actions/run"):
            controller = _Handler.action_controller
            if controller is None:
                self._json({"accepted": False, "reason": "action_controller_unavailable"}, status=503)
                return
            body = self._json_body()
            action = str(body.get("action", "")).strip().lower()
            result = controller.trigger(action=action, trigger_source="dashboard")
            self._json(result, status=202 if bool(result.get("accepted", False)) else 409)
            return
        if self.path.startswith("/api/guardian/run"):
            controller = _Handler.action_controller
            if controller is None:
                self._json({"accepted": False, "reason": "action_controller_unavailable"}, status=503)
                return
            result = controller.trigger(action="fix", trigger_source="dashboard_legacy")
            self._json(result, status=202 if bool(result.get("accepted", False)) else 409)
            return
        self._json({"error": "not_found"}, status=404)

    def log_message(self, _format: str, *_args: Any) -> None:  # noqa: A003
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Git Sentinel local dashboard server.")
    parser.add_argument("--repo-root", default=None, help="Absolute or relative repository root.")
    parser.add_argument("--config", default=None, help="Optional JSON config override path.")
    parser.add_argument(
        "--profile",
        default=None,
        choices=("safe", "strict", "aggressive"),
        help="Optional sentinel profile override.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host binding.")
    parser.add_argument("--port", type=int, default=8787, help="Dashboard port.")
    parser.add_argument("--open-browser", action="store_true", help="Open default browser on start.")
    parser.add_argument("--dump-state", action="store_true", help="Print one JSON payload and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = build_config(repo_root=args.repo_root, config_path=args.config, profile=args.profile)
    config.ensure_layout()
    action_controller = ActionController(config=config)
    if args.dump_state:
        print(dump_json(collect_dashboard_state(config=config, action_controller=action_controller)), end="")
        return 0

    _Handler.action_controller = action_controller
    _Handler.state_provider = lambda: collect_dashboard_state(config=config, action_controller=action_controller)
    server = ThreadingHTTPServer((args.host, int(args.port)), _Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"[git-sentinel-dashboard] url={url}")
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
