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
            "guardianIntervalSec": int(
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
    :root {
      --bg: #060912;
      --panel: rgba(12, 18, 33, 0.78);
      --line: rgba(129, 172, 255, 0.18);
      --line-strong: rgba(129, 172, 255, 0.33);
      --text: #e8f2ff;
      --muted: #91a8c9;
      --ok: #20df9c;
      --warn: #ffb347;
      --bad: #ff6a6a;
      --accent: #6cd0ff;
      --accent-2: #63ffa8;
    }

    * { box-sizing: border-box; }
    html, body { min-height: 100%; }
    body {
      margin: 0;
      color: var(--text);
      font-family: "Bahnschrift", "Franklin Gothic Medium", "Trebuchet MS", sans-serif;
      background:
        radial-gradient(1200px 900px at -8% -10%, rgba(66, 163, 255, 0.22), transparent 62%),
        radial-gradient(900px 700px at 112% 12%, rgba(38, 255, 188, 0.16), transparent 52%),
        radial-gradient(900px 700px at 40% 120%, rgba(35, 99, 255, 0.24), transparent 55%),
        linear-gradient(165deg, #04060d 0%, #0a1020 42%, #03060f 100%);
      padding: 22px;
      letter-spacing: 0.2px;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        repeating-linear-gradient(90deg, rgba(255,255,255,0.02) 0, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 120px),
        repeating-linear-gradient(0deg, rgba(255,255,255,0.015) 0, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 120px);
      mix-blend-mode: screen;
      opacity: 0.23;
    }

    .shell {
      width: min(1800px, 100%);
      margin: 0 auto;
      display: grid;
      gap: 14px;
      animation: reveal 500ms ease;
    }

    @keyframes reveal {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .hero {
      background: linear-gradient(145deg, rgba(14, 22, 41, 0.86), rgba(8, 12, 23, 0.9));
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 22px 44px rgba(0, 0, 0, 0.38);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      position: relative;
      overflow: hidden;
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, transparent, rgba(114, 196, 255, 0.12), transparent);
      transform: translateX(-100%);
      animation: sweep 5s linear infinite;
      pointer-events: none;
    }

    @keyframes sweep {
      to { transform: translateX(100%); }
    }

    .title-wrap h1 {
      margin: 0;
      font-size: clamp(28px, 3vw, 42px);
      line-height: 1.04;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      font-family: "Impact", "Haettenschweiler", "Franklin Gothic Heavy", sans-serif;
      text-shadow: 0 0 20px rgba(93, 184, 255, 0.35);
    }

    .title-wrap p {
      margin: 8px 0 0;
      font-size: 13px;
      color: var(--muted);
      font-family: "Consolas", "Lucida Console", monospace;
      max-width: 860px;
      word-break: break-word;
    }

    .hero-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      position: relative;
      z-index: 2;
      flex-wrap: wrap;
    }

    .pill {
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(8, 13, 24, 0.85);
      padding: 7px 12px;
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }

    .status-pill {
      color: #dff8ff;
      border-color: rgba(103, 255, 198, 0.55);
      box-shadow: inset 0 0 0 1px rgba(103, 255, 198, 0.2);
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--accent-2);
      display: inline-block;
      margin-right: 8px;
      box-shadow: 0 0 0 0 rgba(99, 255, 168, 0.65);
      animation: pulse 2s infinite;
      vertical-align: middle;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(99, 255, 168, 0.65); }
      70% { box-shadow: 0 0 0 10px rgba(99, 255, 168, 0); }
      100% { box-shadow: 0 0 0 0 rgba(99, 255, 168, 0); }
    }

    button {
      border: 1px solid rgba(141, 201, 255, 0.34);
      color: #e8f8ff;
      border-radius: 12px;
      padding: 9px 14px;
      font-family: "Bahnschrift", "Trebuchet MS", sans-serif;
      font-weight: 700;
      letter-spacing: 0.4px;
      text-transform: uppercase;
      background: linear-gradient(130deg, rgba(26, 62, 116, 0.95), rgba(13, 148, 112, 0.84));
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
      cursor: pointer;
      transition: transform 140ms ease, filter 140ms ease, box-shadow 140ms ease;
    }

    button:hover {
      transform: translateY(-1px);
      filter: brightness(1.08);
      box-shadow: 0 14px 28px rgba(0, 0, 0, 0.42);
    }

    button:active {
      transform: translateY(0);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px 14px;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
      min-height: 94px;
      position: relative;
      overflow: hidden;
    }

    .card::before {
      content: "";
      position: absolute;
      inset: -1px;
      background: linear-gradient(130deg, rgba(120, 192, 255, 0.2), transparent 40%, rgba(98, 255, 172, 0.14));
      opacity: 0;
      transition: opacity 180ms ease;
      pointer-events: none;
    }

    .card:hover::before { opacity: 1; }
    .card .label {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 700;
    }

    .card .value {
      font-size: clamp(22px, 2.2vw, 32px);
      font-weight: 800;
      margin-top: 6px;
      line-height: 1.1;
      font-family: "Franklin Gothic Heavy", "Bahnschrift", sans-serif;
      text-shadow: 0 0 16px rgba(94, 175, 255, 0.22);
    }

    .card .sub {
      margin-top: 4px;
      color: #7f95b8;
      font-size: 11px;
    }

    .panel-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
    }

    .section h2 {
      margin: 0 0 10px;
      font-size: 13px;
      letter-spacing: 1px;
      text-transform: uppercase;
      font-family: "Franklin Gothic Demi", "Bahnschrift", sans-serif;
      color: #d8e9ff;
    }

    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    th, td {
      border-bottom: 1px solid rgba(128, 170, 245, 0.14);
      padding: 7px 8px;
      text-align: left;
      vertical-align: top;
      font-size: 12px;
      word-break: break-word;
    }

    th {
      color: #a8bddb;
      font-weight: 700;
      width: 44%;
      letter-spacing: 0.3px;
    }

    .findings th { width: auto; }
    .findings td { font-family: "Consolas", "Lucida Console", monospace; font-size: 11px; }
    .findings td:nth-child(3), .findings td:nth-child(5) { color: #c8dbf6; }

    pre {
      margin: 10px 0 0;
      background: rgba(6, 10, 18, 0.85);
      border: 1px dashed rgba(255, 130, 130, 0.35);
      color: #ffdede;
      border-radius: 10px;
      padding: 9px;
      white-space: pre-wrap;
      word-break: break-word;
      min-height: 34px;
      font-family: "Consolas", "Lucida Console", monospace;
      font-size: 11px;
    }

    .ok { color: var(--ok); font-weight: 700; }
    .warn { color: var(--warn); font-weight: 700; }
    .bad { color: var(--bad); font-weight: 700; }

    @media (max-width: 1200px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .panel-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 680px) {
      body { padding: 12px; }
      .grid { grid-template-columns: 1fr; }
      .hero { padding: 14px; }
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
        <span class="pill status-pill"><span class="dot"></span>Live Guardian</span>
        <span class="pill" id="refreshClock">refresh in 60s</span>
        <button onclick="refresh()">Refresh now</button>
      </div>
    </header>

    <section class="grid" id="cards"></section>

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
    </div>

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

    function refreshClockTick() {
      nextRefresh -= 1;
      if (nextRefresh < 0) nextRefresh = 0;
      const clock = document.getElementById("refreshClock");
      if (clock) clock.textContent = `refresh in ${nextRefresh}s`;
    }

    function renderCards(cards) {
      const rows = [
        ["Health Score", `${cards.healthScore} (${cards.healthStatus})`, statusClass(cards.healthStatus), "overall repository hygiene"],
        ["Security Findings", cards.securityFindings, cards.securityFindings > 0 ? "warn" : "ok", "active findings after suppression"],
        ["False Positive Rate", fmtRate(cards.falsePositiveRate), cards.falsePositiveRate > 0.2 ? "warn" : "ok", "suppressed / total findings"],
        ["Security Eval F1", `${cards.securityEvalF1} (${cards.securityEvalPassed})`, cards.securityEvalPassed ? "ok" : "bad", "golden-set detector quality"],
        ["CI Gate", String(cards.ciGatePassed), cards.ciGatePassed ? "ok" : "bad", "incremental diff gate"],
        ["Guardian", `${cards.guardianCycles} cycles`, "", `interval ${fmtInterval(cards.guardianIntervalSec)}`],
      ];
      document.getElementById("cards").innerHTML = rows.map(([label, value, cls, sub]) =>
        `<div class="card"><div class="label">${esc(label)}</div><div class="value ${cls}">${esc(value)}</div><div class="sub">${esc(sub)}</div></div>`
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
      nextRefresh = REFRESH_MS / 1000;
    }

    refresh().catch(err => { document.getElementById("meta").textContent = `error=${err}`; });
    setInterval(() => refresh().catch(() => {}), REFRESH_MS);
    setInterval(refreshClockTick, 1000);
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
