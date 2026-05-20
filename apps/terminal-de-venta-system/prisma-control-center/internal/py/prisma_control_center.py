from __future__ import annotations

import argparse
import json
import py_compile
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from cloudflare_supervisor import cloudflare_doctor_commands, collect_cloudflare_health, ensure_cloudflare
from config_loader import (
    CONFIG_ROOT,
    CONTROL_CENTER_PORT,
    CONTROL_ROOT,
    LATEST_ROOT,
    LOG_ROOT,
    REPO_ROOT,
    STATE_FILE,
    TERMINAL_ROOT,
    WEB_ROOT,
    active_health_profile,
    ensure_log_dirs,
    load_cloudflare_config,
    load_health_profiles,
    load_safety_policy,
    load_services_config,
    write_json,
)
from health_checks import check_cloudflare
from local_supervisor import collect_local_health, ensure_local_services
from panel_3150 import run_panel, smoke_panel
from ports_inspector import command_exists, inspect_ports
from report_writer import RunLog, export_support_bundle, public_payload_has_sensitive_data, sanitize_for_public, write_reports
from services_registry import load_services


ASSUMPTIONS = [
    "3110 is treated as PRISMA Web / EIT because the repo documents it as eit.hitechrts.com local origin.",
    "Unknown processes are never stopped. BLOCKED_UNKNOWN_PROCESS is the safe outcome.",
    "Cloudflare stable service mode is preferred over mutating quick tunnel or industrial config.",
    "control.hitechrts.com is optional for local operation and must use PUBLIC_REDACTED without advanced auth.",
]


def _exit_for_status(status: str) -> int:
    return {"PASS": 0, "DEGRADED": 1, "FAIL": 2, "BLOCKED": 3}.get(status, 2)


def _print_report(paths: dict[str, str], payload_path: str) -> None:
    try:
        payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
        print(json.dumps({"overallStatus": payload.get("overallStatus"), "healthScore": payload.get("healthScore"), "reports": paths}, indent=2))
    except Exception:
        print(json.dumps({"reports": paths}, indent=2))


def action_health() -> int:
    run_log = RunLog("health")
    run_log.log("start", "diagnostic-only")
    services = collect_local_health(action="health")
    cloudflare = collect_cloudflare_health(public=True)
    paths = write_reports("health", services, cloudflare, run_log, assumptions=ASSUMPTIONS)
    _print_report(paths, paths["json"])
    payload = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
    return _exit_for_status(str(payload.get("overallStatus", "FAIL")))


def action_local_up() -> int:
    run_log = RunLog("local-up")
    run_log.log("start", "ensure local services")
    services = ensure_local_services(run_log, action="local-up")
    cloudflare = collect_cloudflare_health(public=False)
    paths = write_reports("local-up", services, cloudflare, run_log, assumptions=ASSUMPTIONS)
    _print_report(paths, paths["json"])
    payload = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
    return _exit_for_status(str(payload.get("overallStatus", "FAIL")))


def action_cloudflare_up() -> int:
    run_log = RunLog("cloudflare-up")
    run_log.log("start", "ensure cloudflare")
    services = collect_local_health(action="cloudflare-up")
    cloudflare = ensure_cloudflare(run_log)
    paths = write_reports("cloudflare-up", services, cloudflare, run_log, assumptions=ASSUMPTIONS)
    _print_report(paths, paths["json"])
    payload = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
    return _exit_for_status(str(payload.get("overallStatus", "FAIL")))


def action_all_up() -> int:
    run_log = RunLog("all-up")
    run_log.log("start", "local first, cloudflare second")
    services = ensure_local_services(run_log, action="all-up")
    local_ok = all(not service.get("requiredForLocal") or service.get("status") == "PASS" for service in services)
    if local_ok:
        cloudflare = ensure_cloudflare(run_log)
    else:
        cloudflare = collect_cloudflare_health(public=True)
        cloudflare.setdefault("actionsBlocked", []).append(
            {
                "code": "LOCAL_HEALTH_NOT_CONFIRMED",
                "message": "Cloudflare start/restart was skipped because required local services are not all healthy.",
            }
        )
        run_log.log("skip-cloudflare", cloudflare["actionsBlocked"][-1])
    paths = write_reports("all-up", services, cloudflare, run_log, assumptions=ASSUMPTIONS)
    _print_report(paths, paths["json"])
    payload = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
    return _exit_for_status(str(payload.get("overallStatus", "FAIL")))


def _expected_structure() -> list[Path]:
    base = CONTROL_ROOT
    return [
        base / "01_LEVANTAR_TODO_LOCAL.cmd",
        base / "02_LEVANTAR_TODO_CLOUDFLARE.cmd",
        base / "03_LEVANTAR_TODO_LOCAL_Y_CLOUDFLARE.cmd",
        base / "04_DIAGNOSTICO_LOCAL_Y_CLOUDFLARE.cmd",
        base / "07_ABRIR_PANEL_CONTROL_3150.cmd",
        base / "README_OPERADOR.md",
        base / "internal" / "py" / "prisma_control_center.py",
        base / "internal" / "py" / "services_registry.py",
        base / "internal" / "py" / "ports_inspector.py",
        base / "internal" / "py" / "process_classifier.py",
        base / "internal" / "py" / "local_supervisor.py",
        base / "internal" / "py" / "cloudflare_supervisor.py",
        base / "internal" / "py" / "health_checks.py",
        base / "internal" / "py" / "panel_3150.py",
        base / "internal" / "py" / "report_writer.py",
        base / "internal" / "py" / "safe_actions.py",
        base / "internal" / "py" / "config_loader.py",
        base / "internal" / "config" / "services.json",
        base / "internal" / "config" / "cloudflare.json",
        base / "internal" / "config" / "health_profiles.json",
        base / "internal" / "config" / "safety_policy.json",
        base / "internal" / "wrappers" / "local_up.ps1",
        base / "internal" / "wrappers" / "cloudflare_up.ps1",
        base / "internal" / "wrappers" / "health.ps1",
        base / "internal" / "wrappers" / "all_up.ps1",
        base / "internal" / "wrappers" / "panel_3150.ps1",
        base / "internal" / "web" / "index.html",
        base / "internal" / "web" / "app.js",
        base / "internal" / "web" / "styles.css",
        base / "internal" / "web" / "quality_bay.css",
        base / "internal" / "web" / "quality_bay.js",
        base / "internal" / "templates" / "report.html",
        base / "internal" / "templates" / "report.txt",
        base / "internal" / "templates" / "runbook.md",
    ]


def run_self_test() -> tuple[list[dict[str, Any]], bool]:
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: Any = "") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    missing = [str(path) for path in _expected_structure() if not path.exists()]
    add("structure", not missing, {"missing": missing})
    for loader_name, loader in [
        ("services.json", load_services_config),
        ("cloudflare.json", load_cloudflare_config),
        ("health_profiles.json", load_health_profiles),
        ("safety_policy.json", load_safety_policy),
    ]:
        try:
            loader()
            add(f"json-parse-{loader_name}", True)
        except Exception as exc:  # noqa: BLE001 - self-test reports exact parser failure.
            add(f"json-parse-{loader_name}", False, str(exc))

    compile_failures = []
    compile_root = LOG_ROOT / "_py_compile"
    compile_root.mkdir(parents=True, exist_ok=True)
    for path in sorted((CONTROL_ROOT / "internal" / "py").glob("*.py")):
        try:
            py_compile.compile(str(path), cfile=str(compile_root / f"{path.stem}.pyc"), doraise=True)
        except py_compile.PyCompileError as exc:
            compile_failures.append({"path": str(path), "error": str(exc)})
    add("python-py-compile", not compile_failures, compile_failures)

    policy = load_safety_policy()
    forbidden = set(int(x) for x in policy.get("forbiddenPortsForNewServices", []))
    add("control-port-not-forbidden", CONTROL_CENTER_PORT not in forbidden, {"controlCenterPort": CONTROL_CENTER_PORT, "forbidden": sorted(forbidden)})

    try:
        ensure_log_dirs()
        probe = LOG_ROOT / "self_test_write_probe.txt"
        probe.write_text("ok\n", encoding="utf-8", newline="\n")
        add("report-writer-can-write-logs", probe.exists(), str(probe))
    except Exception as exc:
        add("report-writer-can-write-logs", False, str(exc))

    try:
        services = collect_local_health(action="self-test", include_lan=False)
        add("health-runs-with-failing-endpoints", isinstance(services, list), {"services": len(services)})
    except Exception as exc:
        add("health-runs-with-failing-endpoints", False, str(exc))

    try:
        profile = active_health_profile()
        add("health-profile-active", True, profile.get("name"))
    except Exception as exc:
        add("health-profile-active", False, str(exc))

    try:
        sample = {
            "overallStatus": "PASS",
            "healthScore": 100,
            "services": [{"port": 3150, "owners": [{"pid": 123, "commandLine": "python F:\\repos\\hitech-os\\secret.env"}]}],
            "cloudflare": {"config": {"rawPreview": "credentials-file: C:\\Users\\alanh\\.cloudflared\\secret.json"}},
            "control_center": {"public_url": "https://control.hitechrts.com/"},
        }
        public_sample = sanitize_for_public(sample)
        add("public-sanitizer-removes-sensitive-fields", public_payload_has_sensitive_data(public_sample)["safe"], public_payload_has_sensitive_data(public_sample))
    except Exception as exc:
        add("public-sanitizer-removes-sensitive-fields", False, str(exc))

    public_latest = LATEST_ROOT / "public-health.json"
    add("public-health-json-path-targeted", str(public_latest).endswith("public-health.json"), str(public_latest))

    all_ok = all(item["ok"] for item in checks)
    return checks, all_ok


def action_self_test() -> int:
    run_log = RunLog("self-test")
    run_log.log("start", "self-test")
    checks, ok = run_self_test()
    services = collect_local_health(action="self-test", include_lan=False)
    cloudflare = collect_cloudflare_health(public=False)
    extra = {"selfTest": {"ok": ok, "checks": checks}}
    paths = write_reports("self-test", services, cloudflare, run_log, assumptions=ASSUMPTIONS, extra=extra)
    print(json.dumps({"selfTestOk": ok, "checks": checks, "reports": paths}, indent=2))
    return 0 if ok else 2


def action_doctor() -> int:
    run_log = RunLog("doctor")
    run_log.log("start", "deep diagnostic no destructive fixes")
    services = collect_local_health(action="doctor")
    cloudflare = collect_cloudflare_health(public=True)
    ports = inspect_ports([3110, 3120, 3130, 3140, 3150])
    commands = [
        {"name": "python", "status": command_exists("python")},
        {"name": "pnpm", "status": command_exists("pnpm")},
        {"name": "cloudflared", "status": command_exists("cloudflared")},
    ]
    commands.extend(cloudflare_doctor_commands())
    suggestions = []
    for service in services:
        if service.get("status") == "BLOCKED":
            suggestions.append(f"Port {service.get('port')} is blocked by an unknown process. Resolve manually before restart.")
        elif service.get("status") == "FAIL":
            suggestions.append(f"Review start command and app logs for {service.get('name')} on {service.get('port')}.")
    if cloudflare.get("status") != "PASS":
        suggestions.append("Review cloudflared binary, Windows service, config drift, DNS, and public endpoint probes.")
    extra = {"doctor": {"ports": ports, "commands": commands, "suggestions": suggestions}}
    paths = write_reports("doctor", services, cloudflare, run_log, assumptions=ASSUMPTIONS, commands_executed=commands, extra=extra)
    print(json.dumps({"doctor": extra["doctor"], "reports": paths}, indent=2))
    payload = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
    return _exit_for_status(str(payload.get("overallStatus", "FAIL")))


def action_export_support_bundle() -> int:
    ensure_log_dirs()
    result = export_support_bundle()
    print(json.dumps(result, indent=2))
    return 0 if Path(result["bundle"]).exists() else 2


def action_panel(open_browser: bool = False, smoke: bool = False) -> int:
    if smoke:
        result = smoke_panel()
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 2
    return run_panel(open_browser=open_browser)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PRISMA Control Center")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("local-up")
    sub.add_parser("cloudflare-up")
    sub.add_parser("all-up")
    panel = sub.add_parser("panel")
    panel.add_argument("--open-browser", action="store_true")
    panel.add_argument("--smoke", action="store_true")
    sub.add_parser("doctor")
    sub.add_parser("self-test")
    sub.add_parser("export-support-bundle")
    args = parser.parse_args(argv)

    ensure_log_dirs()
    if args.command == "health":
        return action_health()
    if args.command == "local-up":
        return action_local_up()
    if args.command == "cloudflare-up":
        return action_cloudflare_up()
    if args.command == "all-up":
        return action_all_up()
    if args.command == "panel":
        return action_panel(open_browser=args.open_browser, smoke=args.smoke)
    if args.command == "doctor":
        return action_doctor()
    if args.command == "self-test":
        return action_self_test()
    if args.command == "export-support-bundle":
        return action_export_support_bundle()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
