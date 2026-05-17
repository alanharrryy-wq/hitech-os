from __future__ import annotations

from pathlib import Path
from typing import Any

from config_loader import CONTROL_ROOT, TERMINAL_ROOT, load_safety_policy, load_state


def _norm(value: str | None) -> str:
    return str(value or "").replace("/", "\\").lower()


def _managed_entry(pid: int, service_id: str | None = None) -> dict[str, Any] | None:
    state = load_state()
    for item in state.get("managedProcesses", []):
        try:
            item_pid = int(item.get("pid", 0))
        except (TypeError, ValueError):
            item_pid = 0
        if item_pid == int(pid) and (not service_id or item.get("serviceId") == service_id):
            return item
    return None


def classify_process(owner: dict[str, Any] | None, action: str = "health", service_id: str | None = None) -> dict[str, Any]:
    if not owner:
        return {
            "classification": "NO_PROCESS",
            "recognized": False,
            "allowedToStop": False,
            "reason": "No listening process was found.",
        }

    policy = load_safety_policy()
    pid = int(owner.get("pid") or owner.get("ProcessId") or 0)
    name = _norm(owner.get("processName") or owner.get("Name"))
    command_line = _norm(owner.get("commandLine") or owner.get("CommandLine"))
    executable_path = _norm(owner.get("executablePath") or owner.get("ExecutablePath"))
    cwd = _norm(owner.get("cwd"))
    terminal_root = _norm(str(TERMINAL_ROOT))
    control_root = _norm(str(CONTROL_ROOT))
    blocked_names = {_norm(x) for x in policy.get("processBlocklist", {}).get("names", [])}
    blocked_needles = [_norm(x) for x in policy.get("processBlocklist", {}).get("commandLineContains", [])]
    allow_names = {_norm(x) for x in policy.get("processAllowlist", {}).get("names", [])}
    cloudflare_names = {_norm(x) for x in policy.get("processAllowlist", {}).get("cloudflareNames", [])}
    managed = _managed_entry(pid, service_id)

    if name in blocked_names or any(needle and needle in command_line for needle in blocked_needles):
        return {
            "classification": "BLOCKLISTED_PROCESS",
            "recognized": False,
            "allowedToStop": False,
            "reason": "Process matched safety blocklist.",
            "managedState": managed,
        }

    if managed:
        return {
            "classification": "PRISMA_CONTROL_CENTER_MANAGED",
            "recognized": True,
            "allowedToStop": True,
            "reason": "PID is registered in Control Center state.",
            "managedState": managed,
        }

    in_terminal_tree = terminal_root in command_line or terminal_root in executable_path or terminal_root in cwd
    in_control_tree = control_root in command_line or control_root in executable_path or control_root in cwd
    prisma_runtime = name in allow_names and in_terminal_tree

    if in_control_tree:
        return {
            "classification": "PRISMA_CONTROL_CENTER_PROCESS",
            "recognized": True,
            "allowedToStop": action in {"panel"},
            "reason": "Process points to prisma-control-center.",
            "managedState": managed,
        }

    if prisma_runtime:
        return {
            "classification": "PRISMA_RECOGNIZED_PROCESS",
            "recognized": True,
            "allowedToStop": True,
            "reason": "Allowed runtime process points inside terminal-de-venta-system.",
            "managedState": managed,
        }

    if name in cloudflare_names and action in {"cloudflare-up", "all-up"}:
        return {
            "classification": "CLOUDFLARE_RECOGNIZED_PROCESS",
            "recognized": True,
            "allowedToStop": True,
            "reason": "cloudflared is recognized only inside Cloudflare actions.",
            "managedState": managed,
        }

    inferred_cwd = ""
    for token in (str(TERMINAL_ROOT), str(CONTROL_ROOT), str(Path.cwd())):
        if _norm(token) in command_line:
            inferred_cwd = token
            break

    return {
        "classification": "UNKNOWN_PROCESS",
        "recognized": False,
        "allowedToStop": bool(policy.get("forceUnknown", False)),
        "reason": "Process did not match the PRISMA allowlist.",
        "managedState": managed,
        "inferredCwd": inferred_cwd,
    }


def classify_owners(port_report: dict[str, Any], action: str, service_id: str | None = None) -> list[dict[str, Any]]:
    classified = []
    for owner in port_report.get("owners", []):
        item = dict(owner)
        item["classification"] = classify_process(owner, action=action, service_id=service_id)
        classified.append(item)
    return classified
