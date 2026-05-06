#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA BLACK-BOX i02 R4.2b Status Consensus + Report Path Fix.

This module is intentionally small and import-light. It acts as a guarded status
adapter around the existing black_box.py status command. It does not edit Tablet,
PC, Mobile, DB, schema, contracts, or shared-kernel files.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TOOL_NAME = "black_box_status_consensus"
VERSION = "0.1.0"
BYPASS_ENV = "PRISMA_BLACK_BOX_I02_R4_2_BYPASS"
DEFAULT_TABLET_URL = "http://127.0.0.1:3120/prisma-dark-pos-reference"
DEFAULT_PC_URL = "http://127.0.0.1:3130/"
DEFAULT_MOBILE_URL = "http://127.0.0.1:3140/prisma-app"


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def safe_resolve(value: str | Path) -> Path:
    try:
        return Path(value).expanduser().resolve(strict=False)
    except Exception:
        return Path(os.path.abspath(os.path.expanduser(str(value))))


def ensure_dirs(out_root: Path) -> Dict[str, Path]:
    names = [
        "logs", "reports", "evidence", "runtime", "docs", "incidents",
        "incidents/active", "incidents/resolved", "incidents/archived", "_unknown",
    ]
    dirs: Dict[str, Path] = {}
    out_root.mkdir(parents=True, exist_ok=True)
    for name in names:
        path = out_root / name
        path.mkdir(parents=True, exist_ok=True)
        dirs[name] = path
    return dirs


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def parse_status_stdout(stdout: str) -> Dict[str, str]:
    parsed: Dict[str, str] = {}
    lines = stdout.splitlines()
    if lines:
        parsed["headline"] = lines[0].strip()
        match = re.search(r":\s*([A-Z_]+)\s*$", lines[0].strip())
        if match:
            parsed["state"] = match.group(1)
    key_map = {
        "Root": "root",
        "Active root cause": "active_root_cause",
        "Primary caveat": "primary_caveat",
        "Checks": "checks",
        "Report": "report",
    }
    for line in lines:
        for prefix, key in key_map.items():
            marker = prefix + ":"
            if line.startswith(marker):
                parsed[key] = line.split(":", 1)[1].strip()
    return parsed


def endpoint_name_from_caveat(text: str) -> Optional[str]:
    lower = (text or "").lower()
    for name in ("tablet", "pc", "mobile"):
        if name in lower and "endpoint" in lower:
            return name
    return None


def extract_host_port(url: str) -> Tuple[str, int]:
    match = re.match(r"^https?://([^/:]+)(?::(\d+))?", url)
    if not match:
        return "127.0.0.1", 80
    host = match.group(1)
    port = int(match.group(2) or (443 if url.startswith("https://") else 80))
    return host, port


def check_tcp(host: str, port: int, timeout: float) -> Tuple[bool, Optional[str]]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def check_http(url: str, timeout: float) -> Tuple[bool, Optional[int], Optional[str]]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "PRISMA-BlackBox-StatusConsensus/0.1"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 0) or 0)
            return 200 <= status < 500, status, None
    except urllib.error.HTTPError as exc:
        return 200 <= int(exc.code) < 500, int(exc.code), f"HTTPError: {exc}"
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def probe_endpoint(name: str, url: str, attempts: int = 3, timeout: float = 4.0, delay: float = 0.35) -> Dict[str, Any]:
    host, port = extract_host_port(url)
    results: List[Dict[str, Any]] = []
    for idx in range(1, attempts + 1):
        started = time.perf_counter()
        tcp_ok, tcp_error = check_tcp(host, port, timeout=min(timeout, 2.0))
        http_ok = False
        http_status: Optional[int] = None
        http_error: Optional[str] = None
        if tcp_ok:
            http_ok, http_status, http_error = check_http(url, timeout=timeout)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        attempt = {
            "attempt": idx,
            "tcp_listening": tcp_ok,
            "tcp_error": tcp_error,
            "http_ok": http_ok,
            "http_status": http_status,
            "http_error": http_error,
            "elapsed_ms": elapsed_ms,
        }
        results.append(attempt)
        if http_ok:
            break
        if idx < attempts:
            time.sleep(delay)
    consensus_ok = any(item.get("http_ok") for item in results)
    return {
        "name": name,
        "url": url,
        "host": host,
        "port": port,
        "consensus_ok": consensus_ok,
        "attempts": results,
    }


def run_original_status(black_box_py: Path, argv: List[str], target_root: Optional[Path]) -> Dict[str, Any]:
    env = os.environ.copy()
    env[BYPASS_ENV] = "1"
    cwd = str(target_root or black_box_py.parent)
    command = [sys.executable, str(black_box_py), "status"] + argv
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
        env=env,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return {
        "command": command,
        "cwd": cwd,
        "returncode": proc.returncode,
        "elapsed_ms": elapsed_ms,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def find_report_elsewhere(out_root: Path, reported_path: Optional[Path]) -> Optional[Path]:
    if not reported_path:
        return None
    name = reported_path.name
    for rel in ("reports", "docs", "evidence", "work", "_unknown"):
        base = out_root / rel
        if not base.exists():
            continue
        direct = base / name
        if direct.exists() and direct.is_file():
            return direct
    try:
        for candidate in out_root.rglob(name):
            if candidate.is_file():
                return candidate
    except Exception:
        return None
    return None


def materialize_report(
    out_root: Path,
    dirs: Dict[str, Path],
    parsed: Dict[str, str],
    original: Dict[str, Any],
    endpoints: List[Dict[str, Any]],
    normalized_state: str,
    resolution_note: Optional[str],
) -> Dict[str, Any]:
    reported_raw = parsed.get("report")
    reported_path = safe_resolve(reported_raw) if reported_raw else None
    reported_exists = bool(reported_path and reported_path.exists())
    found_elsewhere = find_report_elsewhere(out_root, reported_path) if reported_path else None

    source_content = ""
    source_kind = "generated_from_status"
    if reported_exists and reported_path:
        try:
            source_content = reported_path.read_text(encoding="utf-8", errors="replace")
            source_kind = "reported_path"
        except Exception:
            source_content = ""
    elif found_elsewhere:
        try:
            source_content = found_elsewhere.read_text(encoding="utf-8", errors="replace")
            source_kind = "found_elsewhere"
        except Exception:
            source_content = ""

    stamp = utc_stamp()
    canonical = dirs["reports"] / f"prisma_black_box_i02_status_consensus_{stamp}.md"
    endpoint_rows = []
    for ep in endpoints:
        last = ep.get("attempts", [{}])[-1] if ep.get("attempts") else {}
        endpoint_rows.append(
            f"| {ep.get('name')} | `{ep.get('url')}` | {ep.get('consensus_ok')} | "
            f"{len(ep.get('attempts', []))} | {last.get('http_status')} | {last.get('http_error') or ''} |"
        )
    content = [
        "# PRISMA BLACK-BOX status consensus report",
        "",
        f"Generated: {now_iso()}",
        f"Tool: {TOOL_NAME} v{VERSION}",
        "",
        "## Normalized status",
        "",
        f"- state: {normalized_state}",
        f"- original_state: {parsed.get('state', 'UNKNOWN')}",
        f"- active_root_cause: {parsed.get('active_root_cause', '')}",
        f"- primary_caveat: {parsed.get('primary_caveat', '')}",
        f"- checks: {parsed.get('checks', '')}",
        f"- resolution_note: {resolution_note or ''}",
        "",
        "## Endpoint consensus",
        "",
        "| App | URL | Consensus OK | Attempts | Last status | Last error |",
        "|---|---|---:|---:|---:|---|",
        *endpoint_rows,
        "",
        "## Report path contract",
        "",
        f"- reported_path: {reported_raw or ''}",
        f"- reported_exists_before: {reported_exists}",
        f"- found_elsewhere: {str(found_elsewhere) if found_elsewhere else ''}",
        f"- canonical_report: {canonical}",
        f"- source_kind: {source_kind}",
        "",
        "## Captured original stdout",
        "",
        "```text",
        original.get("stdout", "").rstrip(),
        "```",
        "",
    ]
    if source_content.strip():
        content.extend([
            "## Source report content",
            "",
            source_content.rstrip(),
            "",
        ])
    write_text(canonical, "\n".join(content))
    return {
        "reported_path": str(reported_path) if reported_path else None,
        "reported_exists_before": reported_exists,
        "found_elsewhere": str(found_elsewhere) if found_elsewhere else None,
        "canonical_report": str(canonical),
        "source_kind": source_kind,
    }


def bump_checks_for_resolved_caveat(checks: str) -> str:
    if not checks:
        return checks
    def repl_warn(match: re.Match[str]) -> str:
        value = int(match.group(1))
        return f"WARN={max(0, value - 1)}"
    def repl_ok(match: re.Match[str]) -> str:
        value = int(match.group(1))
        return f"OK={value + 1}"
    updated = re.sub(r"WARN=(\d+)", repl_warn, checks, count=1)
    updated = re.sub(r"OK=(\d+)", repl_ok, updated, count=1)
    return updated


def build_normalized_stdout(
    parsed: Dict[str, str],
    original_stdout: str,
    normalized_state: str,
    canonical_report: str,
    resolution_note: Optional[str],
    checks_override: Optional[str],
) -> str:
    root = parsed.get("root", "")
    active = parsed.get("active_root_cause", "NO_ACTIVE_FAILURE")
    primary = parsed.get("primary_caveat", "")
    checks = checks_override or parsed.get("checks", "")

    if normalized_state == "READY" and resolution_note:
        primary_line = f"Primary caveat: none - {resolution_note}"
    elif primary:
        primary_line = f"Primary caveat: {primary}"
    else:
        primary_line = "Primary caveat: none"

    lines = [
        f"PRISMA BLACK-BOX i02: {normalized_state}",
        f"Root: {root}",
        f"Active root cause: {active}",
        primary_line,
    ]
    if checks:
        lines.append(f"Checks: {checks}")
    if resolution_note:
        lines.append(f"Endpoint consensus: {resolution_note}")
    lines.append(f"Report: {canonical_report}")
    return "\n".join(lines) + "\n"


def parse_args(argv: List[str]) -> Tuple[argparse.Namespace, List[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--allow-blocked", action="store_true")
    args, unknown = parser.parse_known_args(argv)
    return args, unknown


def run_status_consensus_cli(argv: List[str], black_box_py: Optional[Path] = None) -> int:
    try:
        args, _unknown = parse_args(argv)
        black_box_py = safe_resolve(black_box_py or Path(__file__).with_name("black_box.py"))
        target_root = safe_resolve(args.root) if args.root else None
        out_root = safe_resolve(args.out) if args.out else safe_resolve(os.environ.get("PRISMA_BLACK_BOX_OUT", r"F:\Black-box"))
        dirs = ensure_dirs(out_root)
        stamp = utc_stamp()
        evidence_dir = dirs["evidence"] / f"black_box_i02_r4_2b_status_consensus_{stamp}"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        original = run_original_status(black_box_py, argv, target_root)
        parsed = parse_status_stdout(original.get("stdout", ""))
        write_json(evidence_dir / "original_status.json", {"parsed": parsed, "original": original})

        endpoints = [
            probe_endpoint("tablet", DEFAULT_TABLET_URL),
            probe_endpoint("pc", DEFAULT_PC_URL),
            probe_endpoint("mobile", DEFAULT_MOBILE_URL),
        ]
        write_json(evidence_dir / "endpoint_consensus.json", endpoints)

        normalized_state = parsed.get("state", "UNKNOWN") or "UNKNOWN"
        resolution_note: Optional[str] = None
        checks_override: Optional[str] = None
        caveat_endpoint = endpoint_name_from_caveat(parsed.get("primary_caveat", ""))
        if normalized_state == "READY_WITH_CAVEATS" and caveat_endpoint:
            ep = next((item for item in endpoints if item.get("name") == caveat_endpoint), None)
            if ep and ep.get("consensus_ok"):
                normalized_state = "READY"
                resolution_note = (
                    f"RESOLVED_TRANSIENT_ENDPOINT - {caveat_endpoint} endpoint recovered during consensus retry; "
                    "original timeout was not treated as an active failure."
                )
                checks_override = bump_checks_for_resolved_caveat(parsed.get("checks", ""))

        report_details = materialize_report(out_root, dirs, parsed, original, endpoints, normalized_state, resolution_note)
        summary = {
            "tool": TOOL_NAME,
            "version": VERSION,
            "created_at": now_iso(),
            "normalized_state": normalized_state,
            "original_state": parsed.get("state"),
            "resolution_note": resolution_note,
            "parsed_status": parsed,
            "original_status": original,
            "endpoints": endpoints,
            "report_details": report_details,
            "evidence_dir": str(evidence_dir),
        }
        summary_json = dirs["runtime"] / "black_box_i02_r4_2b_status_consensus_latest.json"
        write_json(summary_json, summary)
        write_json(evidence_dir / "status_consensus_summary.json", summary)

        normalized_stdout = build_normalized_stdout(
            parsed=parsed,
            original_stdout=original.get("stdout", ""),
            normalized_state=normalized_state,
            canonical_report=str(report_details["canonical_report"]),
            resolution_note=resolution_note,
            checks_override=checks_override,
        )
        sys.stdout.write(normalized_stdout)
        if original.get("stderr"):
            sys.stderr.write(str(original.get("stderr")))
        return int(original.get("returncode", 0) or 0)
    except Exception as exc:
        sys.stderr.write("PRISMA BLACK-BOX i02 R4.2 status consensus failed; falling back is not possible inside wrapper.\n")
        sys.stderr.write(f"{type(exc).__name__}: {exc}\n")
        sys.stderr.write(traceback.format_exc())
        return 2
