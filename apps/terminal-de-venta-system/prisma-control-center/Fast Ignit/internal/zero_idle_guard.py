#!/usr/bin/env python3
"""PRISMA Zero-Idle Runtime Guard.

Windows-only event driven owner for the Tablet 3120 process tree.  The module
is import-safe on non-Windows hosts so its pure policy and sabotage tests can
run without pretending that Win32 runtime certification occurred.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import datetime as dt
import hashlib
import json
import os
import platform
import queue
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

MiB = 1024 * 1024
SUPPORTED_NODE_LTS_MAJORS = {22, 24}
CERTIFIED_NODE24_VERSION = "24.18.0"
CERTIFIED_NODE24_ROOT = Path(r"F:\PRISMA_CTX\RUNTIMES")
FINGERPRINT_SCHEMA = "prisma-zero-idle-fingerprint/v1"
CERTIFICATION_SCHEMA = "prisma-zero-idle-certification/v1"
LEASE_SCHEMA = "prisma-zero-idle-lease/v1"


class GuardError(RuntimeError):
    pass


def iso_now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def parse_node_version(text: str) -> Tuple[int, int, int]:
    match = re.search(r"\bv?(\d+)\.(\d+)\.(\d+)\b", text or "")
    if not match:
        raise GuardError(f"No pude interpretar la version de Node: {text!r}")
    return tuple(int(match.group(i)) for i in (1, 2, 3))


def assert_supported_node(version_text: str) -> Dict[str, object]:
    major, minor, patch = parse_node_version(version_text)
    if major not in SUPPORTED_NODE_LTS_MAJORS:
        raise GuardError(
            f"NODE_MAJOR_NOT_CERTIFIED: v{major}.{minor}.{patch}; "
            f"permitidos LTS: {sorted(SUPPORTED_NODE_LTS_MAJORS)}"
        )
    return {
        "version": f"{major}.{minor}.{patch}",
        "majorMinor": f"{major}.{minor}",
        "major": major,
        "status": "LTS_ALLOWED",
    }


def resolve_certified_node() -> Tuple[str, Dict[str, object]]:
    """Resolve one explicitly governed Node runtime without scanning the machine.

    The installer provisions an official portable Node 24 build beneath the
    PRISMA toolchain root.  An explicit environment override is accepted for
    controlled testing.  PATH is only a final compatibility fallback.
    """
    candidates: List[Path] = []
    explicit = os.environ.get("PRISMA_NODE24_EXE", "").strip()
    if explicit:
        candidates.append(Path(explicit))
    for arch in ("x64", "arm64"):
        candidates.append(
            CERTIFIED_NODE24_ROOT
            / f"node-v{CERTIFIED_NODE24_VERSION}-win-{arch}"
            / "node.exe"
        )
    path_node = shutil.which("node.exe") or shutil.which("node")
    if path_node:
        candidates.append(Path(path_node))

    attempts: List[Dict[str, object]] = []
    seen = set()
    for candidate in candidates:
        normalized = os.path.normcase(os.path.abspath(str(candidate)))
        if normalized in seen:
            continue
        seen.add(normalized)
        if not candidate.is_file():
            attempts.append({"path": str(candidate), "status": "missing"})
            continue
        try:
            version_text = _run_text([str(candidate), "--version"], timeout=15)
            gate = assert_supported_node(version_text)
            return str(candidate.resolve()), {
                **gate,
                "executable": str(candidate.resolve()),
                "resolution": (
                    "explicit"
                    if explicit and normalized == os.path.normcase(os.path.abspath(explicit))
                    else "prisma-portable"
                    if str(candidate).lower().startswith(str(CERTIFIED_NODE24_ROOT).lower())
                    else "path-fallback"
                ),
            }
        except Exception as exc:
            attempts.append({
                "path": str(candidate),
                "status": "rejected",
                "error": str(exc),
            })
    raise GuardError(
        "CERTIFIED_NODE_LTS_NOT_FOUND: "
        + json.dumps(attempts, ensure_ascii=False)
    )


def _run_text(argv: Sequence[str], cwd: Optional[Path] = None, timeout: int = 20) -> str:
    cp = subprocess.run(
        list(argv),
        cwd=str(cwd) if cwd else None,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if cp.returncode != 0:
        raise GuardError(f"Command failed ({cp.returncode}): {argv!r}\n{cp.stdout[-2000:]}")
    return cp.stdout.strip()


def validate_tablet_package(tablet_root: Path) -> Dict[str, object]:
    package_path = tablet_root / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    scripts = package.get("scripts") or {}
    dev = str(scripts.get("dev") or "")
    dev_webpack = str(scripts.get("dev:webpack") or "")
    joined = "\n".join([dev, dev_webpack]).lower()
    failures: List[str] = []
    if "--webpack" not in dev:
        failures.append("dev script lacks --webpack")
    if "turbopack" in dev.lower() or "--turbo" in dev.lower():
        failures.append("dev script selects Turbopack")
    if "prisma" in joined or "generate" in joined:
        failures.append("dev scripts execute Prisma generation")
    if failures:
        raise GuardError("TABLET_PREFLIGHT_FAILED: " + "; ".join(failures))
    return {
        "package": package.get("name"),
        "version": package.get("version"),
        "next": (package.get("dependencies") or {}).get("next"),
        "dev": dev,
        "devWebpack": dev_webpack,
        "bundler": "webpack",
        "prismaGenerateInDev": False,
    }


def _fingerprint_inputs(repo_root: Path, tablet_root: Path) -> List[Path]:
    candidates = [
        repo_root / "pnpm-lock.yaml",
        tablet_root / "package.json",
        tablet_root / "next.config.mjs",
        tablet_root / "app" / "layout.tsx",
        tablet_root / "generated" / "prisma-visual-runtime" / "prisma-tablet-runtime.css",
        tablet_root / "generated" / "prisma-visual-runtime" / "visual-values.ts",
        tablet_root / "generated" / "prisma-visual-runtime" / "visual-values.tsx",
        tablet_root / "generated" / "prisma-visual-runtime" / "prisma-runtime-root.module.css",
    ]
    selected: List[Path] = []
    for p in candidates:
        if p.exists() and p.is_file() and p not in selected:
            selected.append(p)
    required = candidates[:4]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise GuardError("FINGERPRINT_REQUIRED_INPUT_MISSING: " + ", ".join(missing))
    return selected


def build_fingerprint(repo_root: Path, tablet_root: Path, node_version: str) -> Dict[str, object]:
    node = assert_supported_node(node_version)
    package = validate_tablet_package(tablet_root)
    records = []
    aggregate = hashlib.sha256()
    aggregate.update(FINGERPRINT_SCHEMA.encode())
    aggregate.update(str(node["majorMinor"]).encode())
    aggregate.update(str(package["next"]).encode())
    aggregate.update(b"webpack")
    for path in _fingerprint_inputs(repo_root, tablet_root):
        rel = path.relative_to(repo_root).as_posix()
        digest = sha256_file(path)
        size = path.stat().st_size
        records.append({"path": rel, "sha256": digest, "bytes": size})
        aggregate.update(rel.encode())
        aggregate.update(digest.encode())
    return {
        "schemaVersion": FINGERPRINT_SCHEMA,
        "createdAt": iso_now(),
        "nodeMajorMinor": node["majorMinor"],
        "nextVersion": package["next"],
        "bundler": "webpack",
        "inputs": records,
        "fingerprint": aggregate.hexdigest(),
    }


def prepare_dev_cache(
    repo_root: Path,
    tablet_root: Path,
    fingerprint: Dict[str, object],
    trash_root: Path,
    run_id: str,
) -> Dict[str, object]:
    dev_cache = tablet_root / ".next" / "dev"
    marker = dev_cache / ".prisma-zero-idle-fingerprint.json"
    previous = None
    if marker.is_file():
        try:
            previous = json.loads(marker.read_text(encoding="utf-8"))
        except Exception:
            previous = {"fingerprint": "INVALID_MARKER"}
    same = bool(previous and previous.get("fingerprint") == fingerprint.get("fingerprint"))
    result: Dict[str, object] = {
        "cachePath": str(dev_cache),
        "present": dev_cache.exists(),
        "fingerprintMatch": same,
        "action": "reuse" if same else ("absent" if not dev_cache.exists() else "move-incompatible"),
        "movedTo": None,
    }
    if dev_cache.exists() and not same:
        destination = trash_root / run_id / "tablet-next-dev"
        if destination.exists():
            raise GuardError(f"TRASH_DESTINATION_ALREADY_EXISTS: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        before_files = []
        for p in dev_cache.rglob("*"):
            if p.is_file():
                before_files.append({
                    "relativePath": p.relative_to(dev_cache).as_posix(),
                    "bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                })
        shutil.move(str(dev_cache), str(destination))
        manifest = {
            "schemaVersion": "prisma-trash-manifest/v1",
            "createdAt": iso_now(),
            "reason": "Incompatible Tablet .next/dev fingerprint",
            "originalPath": str(dev_cache),
            "movedPath": str(destination),
            "files": before_files,
            "rollback": {
                "allowedWhen": "Tablet runtime is stopped and target .next/dev is absent",
                "source": str(destination),
                "target": str(dev_cache),
            },
        }
        atomic_json(destination.parent / "manifest.json", manifest)
        (destination.parent / "manifest.md").write_text(
            "# PRISMA cache rollback\n\n"
            f"- Original: `{dev_cache}`\n- Moved: `{destination}`\n"
            f"- Files: `{len(before_files)}`\n- Reason: incompatible `.next/dev` fingerprint.\n",
            encoding="utf-8",
        )
        result["movedTo"] = str(destination)
    return result


def persist_fingerprint(tablet_root: Path, fingerprint: Dict[str, object]) -> Path:
    marker = tablet_root / ".next" / "dev" / ".prisma-zero-idle-fingerprint.json"
    atomic_json(marker, fingerprint)
    return marker


@dataclass
class MemoryIncidentPolicy:
    threshold_bytes: int
    deferred_seconds: float = 15.0
    recoveries_used: int = 0
    incident_open: bool = False

    def notification(self) -> str:
        if self.incident_open:
            return "duplicate-while-open"
        self.incident_open = True
        return "defer-once"

    def persistence_result(self, current_bytes: int) -> str:
        if not self.incident_open:
            raise GuardError("MEMORY_POLICY_NO_OPEN_INCIDENT")
        self.incident_open = False
        if current_bytes <= self.threshold_bytes:
            return "transient-cleared"
        if self.recoveries_used == 0:
            self.recoveries_used = 1
            return "recover-once"
        return "fail-closed-recurrence"


def derive_memory_threshold(cold_peak_bytes: int, steady_baseline_bytes: int) -> int:
    if cold_peak_bytes <= 0 or steady_baseline_bytes <= 0:
        raise GuardError("MEMORY_BASELINE_INVALID")
    return int(max(
        cold_peak_bytes * 1.20,
        steady_baseline_bytes * 1.45,
        cold_peak_bytes + 384 * MiB,
    ))


def validate_chunk_response(url: str, status: int, content_type: str, body: bytes) -> Tuple[bool, str]:
    if status != 200:
        return False, f"HTTP_{status}"
    ctype = (content_type or "").lower()
    if not any(x in ctype for x in ("javascript", "ecmascript")):
        return False, f"WRONG_CONTENT_TYPE:{content_type}"
    if len(body) < 32:
        return False, "BODY_TOO_SMALL"
    head = body[:1024].lstrip().lower()
    if head.startswith(b"<!doctype html") or head.startswith(b"<html"):
        return False, "HTML_INSTEAD_OF_CHUNK"
    signals = (b"webpack", b"self.", b"(self.", b"\"use strict\"", b"(()=>", b"__next")
    if not any(s in body[: min(len(body), 262144)].lower() for s in signals):
        return False, "CONTENT_NOT_JAVASCRIPT_CHUNK"
    if "_next/static/chunks" not in url:
        return False, "NOT_A_CURRENT_CHUNK_URL"
    return True, "PASS"


def _fetch(url: str, timeout: float, max_bytes: int = 16 * MiB) -> Tuple[int, Dict[str, str], bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "PRISMA-Zero-Idle-Guard/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(getattr(response, "status", 200)), dict(response.headers.items()), response.read(max_bytes)
    except urllib.error.HTTPError as exc:
        return int(exc.code), dict(exc.headers.items()) if exc.headers else {}, exc.read(max_bytes)


def _extract_chunk_urls(base_url: str, html: str) -> List[str]:
    found = re.findall(r"""(?:src|href)=["']([^"']*_next/static/chunks/[^"']+)["']""", html, re.I)
    urls = []
    for raw in found:
        if raw.startswith("http://") or raw.startswith("https://"):
            url = raw
        else:
            url = base_url.rstrip("/") + "/" + raw.lstrip("/")
        if url not in urls:
            urls.append(url)
    return urls


@dataclass
class StartupCertifier:
    base_url: str
    tablet_root: Path
    memory_reader: Callable[[], Tuple[int, int]]
    dist_root: Optional[Path] = None
    request_count: int = 0
    probes_active: bool = True

    def request(self, path_or_url: str, timeout: float = 120.0) -> Tuple[int, Dict[str, str], bytes]:
        if not self.probes_active:
            raise GuardError("ACTIVE_PROBE_AFTER_CERTIFIED")
        url = path_or_url if path_or_url.startswith("http") else self.base_url.rstrip("/") + "/" + path_or_url.lstrip("/")
        self.request_count += 1
        return _fetch(url, timeout)

    def certify(self) -> Dict[str, object]:
        started = time.monotonic()
        routes = ["/", "/pos", "/sales/today", "/settings/export", "/settings/license", "/offline"]
        route_evidence = []
        chunk_urls: List[str] = []
        cold_samples: List[int] = []
        for route in routes:
            status, headers, body = self.request(route)
            ok = status == 200 and len(body) > 32
            route_evidence.append({
                "route": route,
                "status": status,
                "ok": ok,
                "bytes": len(body),
                "sha256": sha256_bytes(body),
            })
            if not ok:
                raise GuardError(f"CRITICAL_ROUTE_FAILED:{route}:HTTP_{status}")
            chunk_urls.extend(x for x in _extract_chunk_urls(self.base_url, body.decode("utf-8", "replace")) if x not in chunk_urls)
            current, peak = self.memory_reader()
            cold_samples.extend([current, peak])
        static_root = (
            self.dist_root
            if self.dist_root is not None
            else self.tablet_root / ".next" / "dev"
        ) / "static" / "chunks"
        if static_root.is_dir():
            for path in static_root.rglob("*.js"):
                rel = path.relative_to(static_root.parent).as_posix()
                url = self.base_url.rstrip("/") + "/_next/static/" + rel
                if url not in chunk_urls:
                    chunk_urls.append(url)
        if not chunk_urls:
            raise GuardError("NO_EMITTED_CHUNKS_DISCOVERED")
        chunk_evidence = []
        for url in chunk_urls[:128]:
            status, headers, body = self.request(url, timeout=35.0)
            ctype = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
            ok, reason = validate_chunk_response(url, status, ctype, body)
            chunk_evidence.append({
                "url": url,
                "status": status,
                "contentType": ctype,
                "bytes": len(body),
                "sha256": sha256_bytes(body),
                "ok": ok,
                "reason": reason,
            })
            if not ok:
                raise GuardError(f"CHUNK_VALIDATION_FAILED:{url}:{reason}")
        steady_samples: List[int] = []
        for _ in range(10):
            current, peak = self.memory_reader()
            steady_samples.append(current)
            cold_samples.append(peak)
            time.sleep(2.0)
        health = []
        for _ in range(3):
            status, headers, body = self.request("/api/health", timeout=12.0)
            text = body.decode("utf-8", "replace").lower()
            ok = status == 200 and "prisma" in text and ("\"status\":\"ok\"" in text.replace(" ", "") or '"status": "ok"' in text)
            health.append({"status": status, "ok": ok, "sha256": sha256_bytes(body)})
            if not ok:
                raise GuardError("HEALTH_3_OF_3_FAILED")
            time.sleep(1.0)
        cold_peak = max(cold_samples)
        steady_baseline = int(statistics.median(steady_samples))
        threshold = derive_memory_threshold(cold_peak, steady_baseline)
        before_freeze = self.request_count
        self.probes_active = False
        time.sleep(3.0)
        if self.request_count != before_freeze:
            raise GuardError("ACTIVE_HTTP_AFTER_CERTIFIED")
        return {
            "schemaVersion": CERTIFICATION_SCHEMA,
            "status": "CERTIFIED",
            "certifiedAt": iso_now(),
            "elapsedSec": round(time.monotonic() - started, 3),
            "bundler": "webpack",
            "routes": route_evidence,
            "chunks": chunk_evidence,
            "health": health,
            "healthConsecutive": 3,
            "memoryMetric": "Windows Job committed memory bytes",
            "coldPeakMB": round(cold_peak / MiB, 2),
            "steadyBaselineMB": round(steady_baseline / MiB, 2),
            "notificationThresholdMB": round(threshold / MiB, 2),
            "notificationThresholdBytes": threshold,
            "activeProbesAfterCertified": 0,
            "httpRequestsPerHourAfterCertified": 0,
            "browserAutomationResident": 0,
            "wmiPeriodic": 0,
        }


if os.name == "nt":
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    HANDLE = wt.HANDLE
    SIZE_T = ctypes.c_size_t
    ULONG_PTR = SIZE_T
    DWORD64 = ctypes.c_ulonglong

    CREATE_SUSPENDED = 0x00000004
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    CREATE_UNICODE_ENVIRONMENT = 0x00000400
    STARTF_USESTDHANDLES = 0x00000100
    HANDLE_FLAG_INHERIT = 0x00000001
    INFINITE = 0xFFFFFFFF
    WT_EXECUTEONLYONCE = 0x00000008
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
    JobObjectExtendedLimitInformation = 9
    JobObjectAssociateCompletionPortInformation = 7
    JobObjectNotificationLimitInformation = 12
    JobObjectLimitViolationInformation = 13
    JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO = 4
    JOB_OBJECT_MSG_NOTIFICATION_LIMIT = 11
    STILL_ACTIVE = 259

    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("nLength", wt.DWORD), ("lpSecurityDescriptor", wt.LPVOID), ("bInheritHandle", wt.BOOL)]

    class STARTUPINFOW(ctypes.Structure):
        _fields_ = [
            ("cb", wt.DWORD), ("lpReserved", wt.LPWSTR), ("lpDesktop", wt.LPWSTR), ("lpTitle", wt.LPWSTR),
            ("dwX", wt.DWORD), ("dwY", wt.DWORD), ("dwXSize", wt.DWORD), ("dwYSize", wt.DWORD),
            ("dwXCountChars", wt.DWORD), ("dwYCountChars", wt.DWORD), ("dwFillAttribute", wt.DWORD),
            ("dwFlags", wt.DWORD), ("wShowWindow", wt.WORD), ("cbReserved2", wt.WORD),
            ("lpReserved2", ctypes.POINTER(ctypes.c_ubyte)), ("hStdInput", HANDLE),
            ("hStdOutput", HANDLE), ("hStdError", HANDLE),
        ]

    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [("hProcess", HANDLE), ("hThread", HANDLE), ("dwProcessId", wt.DWORD), ("dwThreadId", wt.DWORD)]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", DWORD64), ("WriteOperationCount", DWORD64), ("OtherOperationCount", DWORD64),
            ("ReadTransferCount", DWORD64), ("WriteTransferCount", DWORD64), ("OtherTransferCount", DWORD64),
        ]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wt.DWORD), ("MinimumWorkingSetSize", SIZE_T), ("MaximumWorkingSetSize", SIZE_T),
            ("ActiveProcessLimit", wt.DWORD), ("Affinity", ULONG_PTR), ("PriorityClass", wt.DWORD),
            ("SchedulingClass", wt.DWORD),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION), ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", SIZE_T), ("JobMemoryLimit", SIZE_T),
            ("PeakProcessMemoryUsed", SIZE_T), ("PeakJobMemoryUsed", SIZE_T),
        ]

    class JOBOBJECT_ASSOCIATE_COMPLETION_PORT(ctypes.Structure):
        _fields_ = [("CompletionKey", wt.LPVOID), ("CompletionPort", HANDLE)]

    class JOBOBJECT_NOTIFICATION_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("IoReadBytesLimit", DWORD64), ("IoWriteBytesLimit", DWORD64),
            ("PerJobUserTimeLimit", ctypes.c_longlong), ("JobMemoryLimit", DWORD64),
            ("RateControlTolerance", ctypes.c_int), ("RateControlToleranceInterval", ctypes.c_int),
            ("LimitFlags", wt.DWORD),
        ]

    class JOBOBJECT_LIMIT_VIOLATION_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("LimitFlags", wt.DWORD), ("ViolationLimitFlags", wt.DWORD),
            ("IoReadBytes", DWORD64), ("IoReadBytesLimit", DWORD64),
            ("IoWriteBytes", DWORD64), ("IoWriteBytesLimit", DWORD64),
            ("PerJobUserTime", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("JobMemory", DWORD64), ("JobMemoryLimit", DWORD64),
            ("RateControlTolerance", ctypes.c_int), ("RateControlToleranceLimit", ctypes.c_int),
        ]

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wt.DWORD), ("dwHighDateTime", wt.DWORD)]

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
            ("PeakWorkingSetSize", SIZE_T), ("WorkingSetSize", SIZE_T),
            ("QuotaPeakPagedPoolUsage", SIZE_T), ("QuotaPagedPoolUsage", SIZE_T),
            ("QuotaPeakNonPagedPoolUsage", SIZE_T), ("QuotaNonPagedPoolUsage", SIZE_T),
            ("PagefileUsage", SIZE_T), ("PeakPagefileUsage", SIZE_T),
        ]

    class THREADENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ThreadID", wt.DWORD),
            ("th32OwnerProcessID", wt.DWORD), ("tpBasePri", ctypes.c_long),
            ("tpDeltaPri", ctypes.c_long), ("dwFlags", wt.DWORD),
        ]

    WAIT_CALLBACK = ctypes.WINFUNCTYPE(None, wt.LPVOID, wt.BOOLEAN)

    kernel32.CreateJobObjectW.argtypes = [ctypes.POINTER(SECURITY_ATTRIBUTES), wt.LPCWSTR]
    kernel32.CreateJobObjectW.restype = HANDLE
    kernel32.SetInformationJobObject.argtypes = [HANDLE, ctypes.c_int, wt.LPVOID, wt.DWORD]
    kernel32.SetInformationJobObject.restype = wt.BOOL
    kernel32.QueryInformationJobObject.argtypes = [HANDLE, ctypes.c_int, wt.LPVOID, wt.DWORD, ctypes.POINTER(wt.DWORD)]
    kernel32.QueryInformationJobObject.restype = wt.BOOL
    kernel32.AssignProcessToJobObject.argtypes = [HANDLE, HANDLE]
    kernel32.AssignProcessToJobObject.restype = wt.BOOL
    kernel32.CreateIoCompletionPort.argtypes = [HANDLE, HANDLE, ULONG_PTR, wt.DWORD]
    kernel32.CreateIoCompletionPort.restype = HANDLE
    kernel32.GetQueuedCompletionStatus.argtypes = [
        HANDLE, ctypes.POINTER(wt.DWORD), ctypes.POINTER(ULONG_PTR),
        ctypes.POINTER(wt.LPVOID), wt.DWORD,
    ]
    kernel32.GetQueuedCompletionStatus.restype = wt.BOOL
    kernel32.PostQueuedCompletionStatus.argtypes = [HANDLE, wt.DWORD, ULONG_PTR, wt.LPVOID]
    kernel32.PostQueuedCompletionStatus.restype = wt.BOOL
    kernel32.CreateProcessW.argtypes = [
        wt.LPCWSTR, wt.LPWSTR, ctypes.POINTER(SECURITY_ATTRIBUTES), ctypes.POINTER(SECURITY_ATTRIBUTES),
        wt.BOOL, wt.DWORD, wt.LPVOID, wt.LPCWSTR, ctypes.POINTER(STARTUPINFOW),
        ctypes.POINTER(PROCESS_INFORMATION),
    ]
    kernel32.CreateProcessW.restype = wt.BOOL
    kernel32.CreateFileW.argtypes = [
        wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.POINTER(SECURITY_ATTRIBUTES),
        wt.DWORD, wt.DWORD, HANDLE,
    ]
    kernel32.CreateFileW.restype = HANDLE
    kernel32.SetHandleInformation.argtypes = [HANDLE, wt.DWORD, wt.DWORD]
    kernel32.SetHandleInformation.restype = wt.BOOL
    kernel32.ResumeThread.argtypes = [HANDLE]
    kernel32.ResumeThread.restype = wt.DWORD
    kernel32.CloseHandle.argtypes = [HANDLE]
    kernel32.CloseHandle.restype = wt.BOOL
    kernel32.GetExitCodeProcess.argtypes = [HANDLE, ctypes.POINTER(wt.DWORD)]
    kernel32.GetExitCodeProcess.restype = wt.BOOL
    kernel32.TerminateJobObject.argtypes = [HANDLE, wt.UINT]
    kernel32.TerminateJobObject.restype = wt.BOOL
    kernel32.TerminateProcess.argtypes = [HANDLE, wt.UINT]
    kernel32.TerminateProcess.restype = wt.BOOL
    kernel32.RegisterWaitForSingleObject.argtypes = [
        ctypes.POINTER(HANDLE), HANDLE, WAIT_CALLBACK, wt.LPVOID, wt.ULONG, wt.ULONG,
    ]
    kernel32.RegisterWaitForSingleObject.restype = wt.BOOL
    kernel32.UnregisterWaitEx.argtypes = [HANDLE, HANDLE]
    kernel32.UnregisterWaitEx.restype = wt.BOOL
    kernel32.GetCurrentProcess.restype = HANDLE
    kernel32.GetProcessHandleCount.argtypes = [HANDLE, ctypes.POINTER(wt.DWORD)]
    kernel32.GetProcessHandleCount.restype = wt.BOOL
    kernel32.GetProcessTimes.argtypes = [
        HANDLE, ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wt.BOOL
    kernel32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = HANDLE
    kernel32.Thread32First.argtypes = [HANDLE, ctypes.POINTER(THREADENTRY32)]
    kernel32.Thread32First.restype = wt.BOOL
    kernel32.Thread32Next.argtypes = [HANDLE, ctypes.POINTER(THREADENTRY32)]
    kernel32.Thread32Next.restype = wt.BOOL

    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wt.DWORD]
    psapi.GetProcessMemoryInfo.restype = wt.BOOL


def _win_error(label: str) -> GuardError:
    return GuardError(f"{label}: WinError {ctypes.get_last_error()}: {ctypes.WinError(ctypes.get_last_error())}")


def process_metrics() -> Dict[str, float]:
    if os.name != "nt":
        return {
            "workingSetMB": 0.0,
            "privateCommitMB": 0.0,
            "handles": 0,
            "threads": threading.active_count(),
            "cpuSeconds": time.process_time(),
        }
    process = kernel32.GetCurrentProcess()
    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
        raise _win_error("GetProcessMemoryInfo")
    handles = wt.DWORD()
    if not kernel32.GetProcessHandleCount(process, ctypes.byref(handles)):
        raise _win_error("GetProcessHandleCount")
    created, exited, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
    if not kernel32.GetProcessTimes(
        process, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)
    ):
        raise _win_error("GetProcessTimes")
    to_ticks = lambda ft: (int(ft.dwHighDateTime) << 32) | int(ft.dwLowDateTime)
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, 0)  # TH32CS_SNAPTHREAD
    thread_count = 0
    if snapshot and snapshot != INVALID_HANDLE_VALUE:
        try:
            entry = THREADENTRY32()
            entry.dwSize = ctypes.sizeof(entry)
            ok = kernel32.Thread32First(snapshot, ctypes.byref(entry))
            pid = os.getpid()
            while ok:
                if int(entry.th32OwnerProcessID) == pid:
                    thread_count += 1
                ok = kernel32.Thread32Next(snapshot, ctypes.byref(entry))
        finally:
            kernel32.CloseHandle(snapshot)
    return {
        "workingSetMB": round(int(counters.WorkingSetSize) / MiB, 3),
        "privateCommitMB": round(int(counters.PagefileUsage) / MiB, 3),
        "handles": int(handles.value),
        "threads": thread_count,
        "cpuSeconds": (to_ticks(kernel) + to_ticks(user)) / 10_000_000.0,
    }


@dataclass
class GuardedProcess:
    pid: int
    handle: object
    returncode: Optional[int] = None
    stdout: object = None
    exit_event: threading.Event = field(default_factory=threading.Event)

    def poll(self) -> Optional[int]:
        if self.returncode is not None:
            return self.returncode
        if not self.exit_event.is_set() or os.name != "nt":
            return None
        code = wt.DWORD()
        if not kernel32.GetExitCodeProcess(self.handle, ctypes.byref(code)):
            raise _win_error("GetExitCodeProcess")
        if code.value != STILL_ACTIVE:
            self.returncode = int(code.value)
        return self.returncode


class WindowsJobGuard:
    def __init__(self, evidence_dir: Path, run_id: str, deferred_seconds: float = 15.0):
        if os.name != "nt":
            raise GuardError("WINDOWS_JOB_OBJECT_REQUIRED")
        self.evidence_dir = evidence_dir
        self.run_id = run_id
        self.deferred_seconds = deferred_seconds
        self.job = None
        self.iocp = None
        self.process: Optional[GuardedProcess] = None
        self.wait_handle = HANDLE()
        self.wait_callback = None
        self.events: "queue.Queue[Dict[str, object]]" = queue.Queue()
        self.iocp_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.job_empty_event = threading.Event()
        self.policy: Optional[MemoryIncidentPolicy] = None
        self.incidents: List[Dict[str, object]] = []
        self.certification: Dict[str, object] = {}
        self.overhead_before = process_metrics()
        self._open_job()

    def _set_info(self, info_class: int, value: ctypes.Structure) -> None:
        if not kernel32.SetInformationJobObject(self.job, info_class, ctypes.byref(value), ctypes.sizeof(value)):
            raise _win_error(f"SetInformationJobObject({info_class})")

    def _open_job(self) -> None:
        self.job = kernel32.CreateJobObjectW(None, f"PRISMA.ZeroIdle.Tablet.{self.run_id}")
        if not self.job:
            raise _win_error("CreateJobObjectW")
        limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        self._set_info(JobObjectExtendedLimitInformation, limits)
        self.iocp = kernel32.CreateIoCompletionPort(HANDLE(INVALID_HANDLE_VALUE), None, 0, 1)
        if not self.iocp:
            raise _win_error("CreateIoCompletionPort")
        association = JOBOBJECT_ASSOCIATE_COMPLETION_PORT()
        association.CompletionKey = ctypes.c_void_p(id(self))
        association.CompletionPort = self.iocp
        self._set_info(JobObjectAssociateCompletionPortInformation, association)

    def _set_memory_notification(self, threshold_bytes: int) -> None:
        info = JOBOBJECT_NOTIFICATION_LIMIT_INFORMATION()
        info.JobMemoryLimit = int(threshold_bytes)
        info.LimitFlags = JOB_OBJECT_LIMIT_JOB_MEMORY
        self._set_info(JobObjectNotificationLimitInformation, info)

    def _query_memory(self) -> Tuple[int, int]:
        violation = JOBOBJECT_LIMIT_VIOLATION_INFORMATION()
        if not kernel32.QueryInformationJobObject(
            self.job, JobObjectLimitViolationInformation, ctypes.byref(violation),
            ctypes.sizeof(violation), None,
        ):
            raise _win_error("QueryInformationJobObject(Violation)")
        limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        if not kernel32.QueryInformationJobObject(
            self.job, JobObjectExtendedLimitInformation, ctypes.byref(limits),
            ctypes.sizeof(limits), None,
        ):
            raise _win_error("QueryInformationJobObject(Extended)")
        return int(violation.JobMemory), int(limits.PeakJobMemoryUsed)

    def _environment_block(self, env: Dict[str, str]) -> ctypes.Array:
        text = "\0".join(f"{k}={v}" for k, v in sorted(env.items(), key=lambda item: item[0].upper())) + "\0\0"
        return ctypes.create_unicode_buffer(text)

    def launch(self, argv: Sequence[str], cwd: Path, env: Dict[str, str], log_path: Path) -> GuardedProcess:
        if self.process is not None:
            raise GuardError("GUARD_ALREADY_LAUNCHED")
        command = list(argv)
        if command and command[0].lower().endswith((".cmd", ".bat")):
            comspec = os.environ.get("ComSpec", r"C:\Windows\System32\cmd.exe")
            command = [comspec, "/d", "/s", "/c", subprocess.list2cmdline(command)]
        cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = log_path.open("ab", buffering=0)
        import msvcrt
        log_handle = HANDLE(msvcrt.get_osfhandle(log_file.fileno()))
        kernel32.SetHandleInformation(log_handle, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT)
        nul = kernel32.CreateFileW("NUL", 0x80000000, 0x00000001 | 0x00000002, None, 3, 0x80, None)
        startup = STARTUPINFOW()
        startup.cb = ctypes.sizeof(startup)
        startup.dwFlags = STARTF_USESTDHANDLES
        startup.hStdInput = nul
        startup.hStdOutput = log_handle
        startup.hStdError = log_handle
        proc_sa = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, False)
        thread_sa = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, False)
        pi = PROCESS_INFORMATION()
        env_block = self._environment_block(env)
        flags = CREATE_SUSPENDED | CREATE_NEW_PROCESS_GROUP | CREATE_UNICODE_ENVIRONMENT
        try:
            ok = kernel32.CreateProcessW(
                None, cmdline, ctypes.byref(proc_sa), ctypes.byref(thread_sa), True, flags,
                env_block, str(cwd), ctypes.byref(startup), ctypes.byref(pi),
            )
            if not ok:
                raise _win_error("CreateProcessW(CREATE_SUSPENDED)")
            if not kernel32.AssignProcessToJobObject(self.job, pi.hProcess):
                kernel32.TerminateProcess(pi.hProcess, 97)
                raise _win_error("AssignProcessToJobObject")
            process = GuardedProcess(pid=int(pi.dwProcessId), handle=pi.hProcess)
            self.process = process

            @WAIT_CALLBACK
            def on_exit(context, timed_out):
                process.exit_event.set()
                self.events.put({"type": "root-exit", "pid": process.pid, "at": iso_now()})

            self.wait_callback = on_exit
            if not kernel32.RegisterWaitForSingleObject(
                ctypes.byref(self.wait_handle), pi.hProcess, on_exit, None, INFINITE, WT_EXECUTEONLYONCE,
            ):
                raise _win_error("RegisterWaitForSingleObject")
            if kernel32.ResumeThread(pi.hThread) == 0xFFFFFFFF:
                raise _win_error("ResumeThread")
            kernel32.CloseHandle(pi.hThread)
            self._set_memory_notification(8 * 1024 * MiB)
            self.iocp_thread = threading.Thread(target=self._completion_loop, name="prisma-zero-idle-iocp", daemon=True)
            self.iocp_thread.start()
            return process
        finally:
            log_file.close()
            if nul:
                kernel32.CloseHandle(nul)

    def _completion_loop(self) -> None:
        while not self.stop_event.is_set():
            transferred = wt.DWORD()
            key = ULONG_PTR()
            overlapped = wt.LPVOID()
            ok = kernel32.GetQueuedCompletionStatus(
                self.iocp, ctypes.byref(transferred), ctypes.byref(key), ctypes.byref(overlapped), INFINITE,
            )
            if self.stop_event.is_set():
                return
            message = int(transferred.value)
            if message == JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO:
                self.job_empty_event.set()
                self.events.put({"type": "job-empty", "at": iso_now()})
                continue
            if message != JOB_OBJECT_MSG_NOTIFICATION_LIMIT:
                continue
            try:
                current, peak = self._query_memory()
                incident = {
                    "type": "memory-notification",
                    "at": iso_now(),
                    "currentMB": round(current / MiB, 2),
                    "peakMB": round(peak / MiB, 2),
                }
                self.incidents.append(incident)
                if self.policy is None:
                    continue
                action = self.policy.notification()
                incident["action"] = action
                if action == "defer-once":
                    timer = threading.Timer(self.policy.deferred_seconds, self._memory_persistence_check)
                    timer.daemon = True
                    timer.start()
            except Exception as exc:
                self.events.put({"type": "fail-closed", "reason": f"memory-handler:{exc}", "at": iso_now()})

    def _memory_persistence_check(self) -> None:
        try:
            current, peak = self._query_memory()
            if self.policy is None:
                return
            action = self.policy.persistence_result(current)
            record = {
                "type": "memory-persistence-check",
                "at": iso_now(),
                "currentMB": round(current / MiB, 2),
                "peakMB": round(peak / MiB, 2),
                "thresholdMB": round(self.policy.threshold_bytes / MiB, 2),
                "action": action,
            }
            self.incidents.append(record)
            self.events.put(record)
        except Exception as exc:
            self.events.put({"type": "fail-closed", "reason": f"memory-persistence:{exc}", "at": iso_now()})

    def certify(
        self,
        base_url: str,
        tablet_root: Path,
        dist_root: Optional[Path] = None,
    ) -> Dict[str, object]:
        certifier = StartupCertifier(
            base_url=base_url,
            tablet_root=tablet_root,
            memory_reader=self._query_memory,
            dist_root=dist_root,
        )
        report = certifier.certify()
        threshold = int(report["notificationThresholdBytes"])
        self.policy = MemoryIncidentPolicy(threshold_bytes=threshold, deferred_seconds=self.deferred_seconds)
        self._set_memory_notification(threshold)
        idle_start = process_metrics()
        time.sleep(3.0)
        idle_end = process_metrics()
        cpu_delta = max(0.0, idle_end["cpuSeconds"] - idle_start["cpuSeconds"])
        cpu_percent = (cpu_delta / 3.0 / max(os.cpu_count() or 1, 1)) * 100.0
        report["overhead"] = {
            "ramWorkingSetAddedMB": round(idle_end["workingSetMB"] - self.overhead_before["workingSetMB"], 3),
            "privateCommitAddedMB": round(idle_end["privateCommitMB"] - self.overhead_before["privateCommitMB"], 3),
            "handlesAdded": int(idle_end["handles"] - self.overhead_before["handles"]),
            "threadsAdded": int(idle_end["threads"] - self.overhead_before["threads"]),
            "idleCpuPercent": round(cpu_percent, 6),
            "idleMeasurementSeconds": 3.0,
            "residentAdditionalProcesses": 0,
            "httpRequestsPerHourAfterCertified": 0,
            "wmiRequestsPerHourAfterCertified": 0,
            "browserAutomationResident": 0,
        }
        self.certification = report
        return report

    def next_event(self, timeout: Optional[float] = None) -> Dict[str, object]:
        return self.events.get(timeout=timeout)

    def terminate(self, exit_code: int = 0x5A1D) -> None:
        if self.job and not kernel32.TerminateJobObject(self.job, exit_code):
            raise _win_error("TerminateJobObject")

    def close(self, kill: bool = True, wait_timeout: float = 30.0) -> None:
        # Shutdown is event-driven. In normal guarded shutdown, TerminateJobObject
        # is followed by root-exit and ACTIVE_PROCESS_ZERO events. The kill=False
        # branch deliberately tests JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE by closing
        # the final Job handle first and awaiting the registered root-exit event.
        deadline = time.monotonic() + max(0.0, wait_timeout)
        job_closed_for_kill_on_close = False
        if self.job:
            if kill:
                if not kernel32.TerminateJobObject(self.job, 0x5A1D):
                    error = ctypes.get_last_error()
                    if error not in (0, 5):
                        raise _win_error("TerminateJobObject")
            else:
                kernel32.CloseHandle(self.job)
                self.job = None
                job_closed_for_kill_on_close = True
        if self.process is not None:
            remaining = max(0.0, deadline - time.monotonic())
            if not self.process.exit_event.wait(remaining):
                raise GuardError("ROOT_PROCESS_EXIT_EVENT_TIMEOUT")
        if kill and self.job is not None:
            remaining = max(0.0, deadline - time.monotonic())
            if not self.job_empty_event.wait(remaining):
                raise GuardError("JOB_ACTIVE_PROCESS_ZERO_EVENT_TIMEOUT")
        self.stop_event.set()
        if self.iocp:
            kernel32.PostQueuedCompletionStatus(self.iocp, 0, 0, None)
        if self.wait_handle:
            try:
                kernel32.UnregisterWaitEx(self.wait_handle, HANDLE(INVALID_HANDLE_VALUE))
            except Exception:
                pass
        if self.process and self.process.handle:
            kernel32.CloseHandle(self.process.handle)
            self.process.handle = None
        if self.job:
            kernel32.CloseHandle(self.job)
            self.job = None
        if self.iocp_thread and self.iocp_thread.is_alive():
            self.iocp_thread.join(timeout=5.0)
        if self.iocp:
            kernel32.CloseHandle(self.iocp)
            self.iocp = None


def passive_beacon_contract() -> Dict[str, object]:
    return {
        "signals": ["ChunkLoadError", "Failed to load chunk", "_next/static/chunks"],
        "events": ["window.error", "unhandledrejection"],
        "timers": 0,
        "polling": 0,
        "maxBeaconsPerBrowserSession": 1,
        "maxReloadRecoveriesPerBrowserSession": 1,
        "pii": False,
        "salesData": False,
    }


def run_pure_sabotage_tests() -> Dict[str, object]:
    tests = []

    def record(name: str, fn: Callable[[], None]) -> None:
        try:
            fn()
            tests.append({"name": name, "status": "PASS"})
        except Exception as exc:
            tests.append({"name": name, "status": "FAIL", "error": str(exc)})

    def eol_node() -> None:
        try:
            assert_supported_node("v20.19.4")
        except GuardError:
            return
        raise AssertionError("Node 20 was accepted")

    def odd_eol_node() -> None:
        try:
            assert_supported_node("v25.6.0")
        except GuardError:
            return
        raise AssertionError("Node 25 was accepted")

    def bad_chunk_404() -> None:
        ok, _ = validate_chunk_response("http://x/_next/static/chunks/a.js", 404, "text/plain", b"missing")
        assert not ok

    def bad_chunk_200() -> None:
        ok, _ = validate_chunk_response(
            "http://x/_next/static/chunks/a.js", 200, "text/html", b"<!doctype html><html>wrong</html>"
        )
        assert not ok

    def memory_transient() -> None:
        p = MemoryIncidentPolicy(100)
        assert p.notification() == "defer-once"
        assert p.persistence_result(80) == "transient-cleared"

    def memory_persistent_once() -> None:
        p = MemoryIncidentPolicy(100)
        p.notification()
        assert p.persistence_result(120) == "recover-once"

    def memory_recurrence() -> None:
        p = MemoryIncidentPolicy(100)
        p.notification()
        assert p.persistence_result(120) == "recover-once"
        p.notification()
        assert p.persistence_result(130) == "fail-closed-recurrence"

    def webpack_required() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "package.json").write_text(json.dumps({
                "name": "sabotage",
                "version": "1",
                "scripts": {"dev": "next dev -p 3120", "dev:webpack": "next dev -p 3120"},
                "dependencies": {"next": "16.1.6"},
            }), encoding="utf-8")
            try:
                validate_tablet_package(root)
            except GuardError:
                return
            raise AssertionError("next dev without --webpack was accepted")

    def incompatible_fingerprint_moves_dev_only() -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            tablet = root / "tablet"
            dev = tablet / ".next" / "dev"
            dev.mkdir(parents=True)
            (dev / "current.js").write_text("webpack", encoding="utf-8")
            (dev / ".prisma-zero-idle-fingerprint.json").write_text(
                json.dumps({"fingerprint": "old"}), encoding="utf-8"
            )
            (tablet / ".next" / "keep.txt").write_text("keep", encoding="utf-8")
            trash = Path(td) / "trash"
            result = prepare_dev_cache(
                root, tablet, {"fingerprint": "new"}, trash, "sabotage-fingerprint"
            )
            assert result["action"] == "move-incompatible"
            assert not dev.exists()
            assert (tablet / ".next" / "keep.txt").read_text() == "keep"
            assert (trash / "sabotage-fingerprint" / "tablet-next-dev" / "current.js").exists()

    record("node-major-eol-blocked", eol_node)
    record("node-25-eol-blocked", odd_eol_node)
    record("next-dev-without-webpack-blocked", webpack_required)
    record("fingerprint-incompatible-moves-only-next-dev", incompatible_fingerprint_moves_dev_only)
    record("chunk-404-blocked", bad_chunk_404)
    record("chunk-200-wrong-content-blocked", bad_chunk_200)
    record("memory-spike-then-falls", memory_transient)
    record("memory-persists-one-recovery", memory_persistent_once)
    record("two-memory-incidents-fail-closed", memory_recurrence)
    record("beacon-contract-one-per-session", lambda: (
        None if passive_beacon_contract()["maxBeaconsPerBrowserSession"] == 1 else (_ for _ in ()).throw(AssertionError())
    ))
    return {
        "status": "PASS" if all(t["status"] == "PASS" for t in tests) else "FAIL",
        "tests": tests,
    }
