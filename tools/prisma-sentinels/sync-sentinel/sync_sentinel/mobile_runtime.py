from __future__ import annotations

import json
import os
import secrets
import socket
import subprocess
import time
from pathlib import Path

from .model import Check, Verdict
from .registry import APP_REL
from .sandbox import RuntimeCapsule


CANONICAL_MOBILE_PORT = 3140
MOBILE_PASS_TOKENS = (
    "PASS_MOBILE_JOURNEY_M1",
    "PASS_MOBILE_JOURNEY_M2",
    "NOT_APPLICABLE_MOBILE_JOURNEY_M3",
    "PASS_MOBILE_NEGATIVES",
)


def _safe_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _mobile_port() -> tuple[int, bool]:
    if _port_available(CANONICAL_MOBILE_PORT):
        return CANONICAL_MOBILE_PORT, True
    if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
        raise RuntimeError("MOBILE_CANONICAL_PORT_3140_UNAVAILABLE_IN_CI")
    return _safe_port(), False


def _wait_ready_file(proc, ready_path: Path, log_path: Path, label: str, timeout: int = 60) -> dict[str, object]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if ready_path.is_file():
            payload = json.loads(ready_path.read_text(encoding="utf-8"))
            if payload.get("ready") is True and payload.get("port"):
                return payload
        if proc.poll() is not None:
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:] if log_path.is_file() else ""
            raise RuntimeError(f"{label}_EXITED_EARLY:rc={proc.returncode}:{tail}")
        time.sleep(0.2)
    raise RuntimeError(f"{label}_READINESS_TIMEOUT")


def _start_tablet_mobile_bridge(capsule: RuntimeCapsule, tablet_db: Path, token: str):
    assert capsule.worktree is not None and capsule.temp_root is not None and capsule.logs_root is not None
    repo = capsule.worktree
    tablet_app = repo / APP_REL / "products/tablet/app"
    adapter = repo / "tools/prisma-sentinels/sync-sentinel/sync_sentinel/adapters/tablet_mobile_bridge.mts"
    tsx = repo / "node_modules/tsx/dist/cli.mjs"
    ready_path = capsule.temp_root / "tablet-mobile-ready.json"
    log_path = capsule.logs_root / "tablet-mobile-runtime.log"
    env = dict(os.environ)
    env.update({
        "TABLET_DATABASE_PATH": str(tablet_db),
        "TABLET_DATABASE_URL": "file:" + tablet_db.as_posix(),
        "DATABASE_URL": "file:" + tablet_db.as_posix(),
        "TABLET_APP_ROOT": str(tablet_app),
        "SYNC_SENTINEL_TABLET_READY_FILE": str(ready_path),
        "SYNC_SENTINEL_TOKEN": token,
        "NODE_ENV": "test",
    })
    log_fh = log_path.open("w", encoding="utf-8")
    proc = capsule.processes.start(
        ["node", str(tsx), "--tsconfig", str(tablet_app / "tsconfig.json"), str(adapter)],
        cwd=tablet_app,
        env=env,
        stdout=log_fh,
    )
    ready = _wait_ready_file(proc, ready_path, log_path, "TABLET_MOBILE_BRIDGE")
    return proc, log_fh, ready, log_path


def _start_mobile_runtime(capsule: RuntimeCapsule, tablet_bridge: dict[str, object], pc_bridge: dict[str, object], session_secret: str):
    assert capsule.worktree is not None and capsule.logs_root is not None
    repo = capsule.worktree
    mobile_app = repo / APP_REL / "products/mobile/app"
    next_cli = mobile_app / "node_modules/next/dist/bin/next"
    if not next_cli.is_file():
        raise RuntimeError("MOBILE_NEXT_RUNTIME_DEPENDENCY_MISSING")
    port, canonical_port_used = _mobile_port()
    log_path = capsule.logs_root / "mobile-runtime-3140.log"
    env = dict(os.environ)
    env.update({
        "NODE_ENV": "development",
        "PRISMA_MOBILE_SESSION_SECRET": session_secret,
        "PRISMA_MOBILE_DEV_LOOPBACK_CONTEXT": "disabled",
        "PRISMA_MOBILE_TABLET_ORIGIN": f"http://127.0.0.1:{tablet_bridge['port']}",
        "PRISMA_MOBILE_PC_ORIGIN": f"http://127.0.0.1:{pc_bridge['port']}",
        "PRISMA_MOBILE_CONTROL_ORIGIN": "",
        "PRISMA_MOBILE_BLACKBOX_ORIGIN": "",
        "PRISMA_MOBILE_RETRY_COUNT": "1",
        "PRISMA_MOBILE_SOURCE_TIMEOUT_MS": "1200",
        "PRISMA_MOBILE_TABLET_TIMEOUT_MS": "1200",
        "PRISMA_MOBILE_PC_TIMEOUT_MS": "1200",
        "PRISMA_MOBILE_STALE_AFTER_MS": "60000",
    })
    log_fh = log_path.open("w", encoding="utf-8")
    proc = capsule.processes.start(
        ["node", str(next_cli), "dev", "--webpack", "-H", "127.0.0.1", "-p", str(port)],
        cwd=mobile_app,
        env=env,
        stdout=log_fh,
    )
    return proc, log_fh, {
        "port": port,
        "canonicalPort": CANONICAL_MOBILE_PORT,
        "canonicalPortUsed": canonical_port_used,
        "origin": f"http://127.0.0.1:{port}",
    }, log_path


def _runner_check(step: subprocess.CompletedProcess[str], output_path: Path) -> Check:
    text = (step.stdout or "") + "\n" + (step.stderr or "")
    if step.returncode != 0:
        evidence: dict[str, object] = {"returncode": step.returncode, "tail": text[-6000:]}
        if output_path.is_file():
            try:
                evidence["mobileRuntime"] = json.loads(output_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return Check("mobile_runtime_3140_journeys", Verdict.FAIL, "Mobile runtime journey runner failed", evidence)
    missing = [token for token in MOBILE_PASS_TOKENS if token not in text]
    if missing:
        return Check(
            "mobile_runtime_3140_journeys",
            Verdict.UNKNOWN,
            "Mobile runner exited zero without all fail-closed success markers",
            {"missingTokens": missing, "tail": text[-6000:]},
        )
    if not output_path.is_file():
        return Check("mobile_runtime_3140_journeys", Verdict.UNKNOWN, "Mobile runner did not produce structured evidence")
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    if payload.get("ok") is not True:
        return Check("mobile_runtime_3140_journeys", Verdict.FAIL, "Mobile structured runtime evidence is not PASS", {"mobileRuntime": payload})
    journeys = payload.get("journeys") if isinstance(payload.get("journeys"), dict) else {}
    negatives = payload.get("negativeFixtures") if isinstance(payload.get("negativeFixtures"), dict) else {}
    if journeys.get("M1", {}).get("status") != "PASS" or journeys.get("M2", {}).get("status") != "PASS":
        return Check("mobile_runtime_3140_journeys", Verdict.FAIL, "Mobile M1/M2 did not PASS", {"mobileRuntime": payload})
    if journeys.get("M3", {}).get("status") != "NOT_APPLICABLE":
        return Check("mobile_runtime_3140_journeys", Verdict.FAIL, "Mobile M3 disposition is not governed NOT_APPLICABLE", {"mobileRuntime": payload})
    failed_negatives = [name for name, row in negatives.items() if not isinstance(row, dict) or row.get("status") != "PASS"]
    if len(negatives) < 12 or failed_negatives:
        return Check(
            "mobile_runtime_3140_journeys",
            Verdict.FAIL,
            "Mobile negative matrix is incomplete or failed",
            {"negativeCount": len(negatives), "failedNegatives": failed_negatives, "mobileRuntime": payload},
        )
    return Check(
        "mobile_runtime_3140_journeys",
        Verdict.PASS,
        "Mobile canonical 3140 read-side runtime, M1/M2, M3 disposition and negative matrix passed",
        {"mobileRuntime": payload, "returncode": step.returncode},
    )


def run_mobile_runtime_extension(
    capsule: RuntimeCapsule,
    tablet_db: Path,
    pc_bridge: dict[str, object],
    control_token: str,
) -> tuple[Check, list[Path], dict[str, object]]:
    assert capsule.worktree is not None and capsule.temp_root is not None
    repo = capsule.worktree
    root_tsx = repo / "node_modules/tsx/dist/cli.mjs"
    tablet_log_fh = None
    mobile_log_fh = None
    paths: list[Path] = []
    facts: dict[str, object] = {
        "canonicalRuntime": "3140",
        "canonicalTabletRuntime": "3120",
        "canonicalPcRuntime": "3130",
        "productionCertified": False,
    }
    try:
        tablet_proc, tablet_log_fh, tablet_bridge, tablet_log = _start_tablet_mobile_bridge(capsule, tablet_db, control_token)
        paths.append(tablet_log)
        facts["tabletOwnerBridge"] = {"pid": tablet_proc.pid, "port": tablet_bridge.get("port"), "canonicalRuntime": "3120"}

        session_secret = secrets.token_urlsafe(48)
        mobile_proc, mobile_log_fh, mobile_runtime, mobile_log = _start_mobile_runtime(capsule, tablet_bridge, pc_bridge, session_secret)
        paths.append(mobile_log)
        facts["mobileRuntime"] = {
            "pid": mobile_proc.pid,
            "boundPort": mobile_runtime["port"],
            "canonicalPort": mobile_runtime["canonicalPort"],
            "canonicalPortUsed": mobile_runtime["canonicalPortUsed"],
            "loopbackOnly": True,
        }

        output_path = capsule.temp_root / "mobile-journeys.json"
        adapter = repo / "tools/prisma-sentinels/sync-sentinel/sync_sentinel/adapters/mobile_runner.mts"
        env = dict(os.environ)
        env.update({
            "SYNC_SENTINEL_MOBILE_ORIGIN": str(mobile_runtime["origin"]),
            "SYNC_SENTINEL_TABLET_ORIGIN": f"http://127.0.0.1:{tablet_bridge['port']}",
            "SYNC_SENTINEL_PC_ORIGIN": f"http://127.0.0.1:{pc_bridge['port']}",
            "SYNC_SENTINEL_TOKEN": control_token,
            "SYNC_SENTINEL_MOBILE_SESSION_SECRET": session_secret,
            "SYNC_SENTINEL_MOBILE_OUTPUT": str(output_path),
            "NODE_ENV": "test",
        })
        step = subprocess.run(
            ["node", str(root_tsx), str(adapter)],
            cwd=str(repo),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=420,
            check=False,
        )
        paths.append(output_path)
        check = _runner_check(step, output_path)
        if output_path.is_file():
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            facts.update({
                "journeys": {name: row.get("status") for name, row in (payload.get("journeys") or {}).items() if isinstance(row, dict)},
                "negativeCount": len(payload.get("negativeFixtures") or {}),
                "faultZones": payload.get("faultZones") or [],
                "dispositions": payload.get("dispositions") or {},
            })
            truth_path = capsule.temp_root / "mobile-truth-map.json"
            truth_path.write_text(json.dumps({
                "schemaVersion": "prisma.sync-sentinel.mobile-truth-map.v1",
                "canonicalRuntime": "3140",
                "canonicalTabletRuntime": "3120",
                "canonicalPcRuntime": "3130",
                "truthMap": payload.get("truthMap") or {},
                "journeys": facts.get("journeys"),
                "faultZones": facts.get("faultZones"),
                "dispositions": facts.get("dispositions"),
                "productionCertified": False,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            paths.append(truth_path)
        return check, paths, facts
    except subprocess.TimeoutExpired as exc:
        return Check(
            "mobile_runtime_3140_journeys",
            Verdict.FAIL,
            "Mobile runtime journey runner timed out",
            {"timeout": exc.timeout},
        ), paths, facts
    except Exception as exc:
        return Check(
            "mobile_runtime_3140_journeys",
            Verdict.FAIL,
            f"{type(exc).__name__}: {exc}",
        ), paths, facts
    finally:
        for handle in (tablet_log_fh, mobile_log_fh):
            if handle is not None:
                try:
                    handle.flush()
                    handle.close()
                except Exception:
                    pass
