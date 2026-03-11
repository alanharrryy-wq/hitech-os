#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import webbrowser
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
from tools.hos.git_sentinel.config import SentinelConfig, build_config  # noqa: E402
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


def collect_dashboard_state(config: SentinelConfig) -> dict[str, Any]:
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
  <title>Git Sentinel Dashboard</title>
  <style>
    body { font-family: "Segoe UI", Arial, sans-serif; margin: 0; padding: 16px; background: #0f1218; color: #e5e7eb; }
    h1 { margin: 0 0 12px; font-size: 22px; }
    .meta { color: #9ca3af; font-size: 12px; margin-bottom: 12px; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
    .card { background: #171b22; border: 1px solid #263041; border-radius: 8px; padding: 10px; }
    .card .label { color: #9ca3af; font-size: 12px; }
    .card .value { font-size: 20px; font-weight: 700; margin-top: 4px; }
    .section { background: #171b22; border: 1px solid #263041; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
    .section h2 { margin: 0 0 8px; font-size: 14px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid #253042; padding: 6px 8px; text-align: left; font-size: 12px; vertical-align: top; }
    th { color: #9ca3af; font-weight: 600; }
    pre { margin: 0; white-space: pre-wrap; word-break: break-word; font-size: 12px; }
    .ok { color: #22c55e; }
    .warn { color: #f59e0b; }
    .bad { color: #ef4444; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    button { background: #1f2937; border: 1px solid #374151; color: #e5e7eb; border-radius: 6px; padding: 6px 10px; cursor: pointer; }
  </style>
</head>
<body>
  <h1>Git Sentinel Dashboard</h1>
  <div class="meta" id="meta">loading...</div>
  <div style="margin-bottom:10px"><button onclick="refresh()">Refresh now</button></div>

  <div class="grid" id="cards"></div>

  <div class="row">
    <div class="section">
      <h2>Security Severity</h2>
      <table><tbody id="securitySeverity"></tbody></table>
    </div>
    <div class="section">
      <h2>CI Gate</h2>
      <table><tbody id="ciGate"></tbody></table>
      <pre id="ciGateFailures"></pre>
    </div>
  </div>

  <div class="row">
    <div class="section">
      <h2>Security Eval</h2>
      <table><tbody id="securityEval"></tbody></table>
    </div>
    <div class="section">
      <h2>Suppressions</h2>
      <table><tbody id="suppressions"></tbody></table>
    </div>
  </div>

  <div class="section">
    <h2>Top Security Findings</h2>
    <table>
      <thead><tr><th>severity</th><th>kind</th><th>path</th><th>line</th><th>snippet</th></tr></thead>
      <tbody id="topFindings"></tbody>
    </table>
  </div>

  <script>
    const REFRESH_MS = 60000;
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
    function renderCards(cards) {
      const rows = [
        ["Health Score", `${cards.healthScore} (${cards.healthStatus})`, statusClass(cards.healthStatus)],
        ["Security Findings", cards.securityFindings, cards.securityFindings > 0 ? "warn" : "ok"],
        ["False Positive Rate", cards.falsePositiveRate, cards.falsePositiveRate > 0.2 ? "warn" : "ok"],
        ["Security Eval F1", `${cards.securityEvalF1} (${cards.securityEvalPassed})`, cards.securityEvalPassed ? "ok" : "bad"],
        ["CI Gate", String(cards.ciGatePassed), cards.ciGatePassed ? "ok" : "bad"],
        ["Guardian Cycles", cards.guardianCycles, ""],
      ];
      document.getElementById("cards").innerHTML = rows.map(([label, value, cls]) =>
        `<div class="card"><div class="label">${esc(label)}</div><div class="value ${cls}">${esc(value)}</div></div>`
      ).join("");
    }
    function renderSeverity(security) {
      const counts = security.severityCounts || {};
      const keys = Object.keys(counts).sort();
      document.getElementById("securitySeverity").innerHTML = keys.map(k => tr(k, counts[k], statusClass(k))).join("");
    }
    function renderCIGate(ciGate) {
      const summary = ciGate.summary || {};
      document.getElementById("ciGate").innerHTML = ""
        + tr("baseRef", ciGate.baseRef || "")
        + tr("changedPathCount", ciGate.changedPathCount || 0)
        + tr("mode", summary.mode || "")
        + tr("severityCounts", JSON.stringify(summary.severityCounts || {}))
        + tr("passed", String(!(ciGate.failures || []).length), (ciGate.failures || []).length ? "bad" : "ok");
      document.getElementById("ciGateFailures").textContent = (ciGate.failures || []).join("\\n");
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
    async function refresh() {
      const r = await fetch("/api/state");
      if (!r.ok) throw new Error(`http_${r.status}`);
      const data = await r.json();
      document.getElementById("meta").textContent = `timestamp=${data.timestamp} repo=${data.repoRoot}`;
      renderCards(data.cards || {});
      renderSeverity(data.security || {});
      renderCIGate(data.ciGate || {});
      renderSecurityEval(data.securityEval || {});
      renderSuppressions(data.falsePositive || {});
      renderFindings(data.securityFindingsTop || []);
    }
    refresh().catch(err => { document.getElementById("meta").textContent = `error=${err}`; });
    setInterval(() => refresh().catch(() => {}), REFRESH_MS);
  </script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    state_provider = None

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
    if args.dump_state:
        print(dump_json(collect_dashboard_state(config=config)), end="")
        return 0

    _Handler.state_provider = lambda: collect_dashboard_state(config=config)
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
