from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import time
from pathlib import Path

from .evidence import build_bundle, now_iso
from .fixtures import load_fixture_registry, mandatory_fixture_readiness
from .model import Check, RunReport, Verdict
from .probes import authority_presence, static_probe_suite, sync_source_presence, toolchain_presence
from .progress import Progress
from .registry import APP_REL
from .safety import git_head, git_tree, known_live_db_snapshot, snapshots_equal
from .sandbox import RuntimeCapsule, prepare_isolated_databases


def _process_check(check_id: str, step: dict[str, object], pass_tokens: list[str] | None = None) -> Check:
    text = str(step.get("tail", ""))
    if not step.get("ok"):
        return Check(check_id, Verdict.FAIL, "isolated command failed", {
            "returncode": step.get("returncode"),
            "tail": text[-4000:],
        })
    if pass_tokens and not all(token in text for token in pass_tokens):
        return Check(check_id, Verdict.UNKNOWN, "isolated command exited zero but success markers were incomplete", {
            "returncode": step.get("returncode"),
            "tail": text[-4000:],
        })
    return Check(check_id, Verdict.PASS, "isolated command passed", {
        "returncode": step.get("returncode"),
        "tail": text[-2400:],
    })


def _runtime_preparation_checks(prepared: dict[str, object]) -> list[Check]:
    ids = {
        "pcMigrations": ("pc_temp_db_migrations", ['"pass": true']),
        "pcGenerate": ("pc_temp_prisma_generate", None),
        "tabletGenerate": ("tablet_temp_prisma_generate", None),
        "tabletDbPush": ("tablet_temp_db_push", None),
    }
    steps = prepared.get("steps") or {}
    checks: list[Check] = []
    for key, (check_id, tokens) in ids.items():
        if key not in steps:
            checks.append(Check(check_id, Verdict.BLOCKED, f"runtime preparation did not reach {key}"))
            continue
        checks.append(_process_check(check_id, steps[key], tokens))
    return checks


def _start_pc_bridge(capsule: RuntimeCapsule, pc_db: Path, ready_path: Path, token: str):
    assert capsule.worktree is not None and capsule.temp_root is not None and capsule.logs_root is not None
    repo = capsule.worktree
    pc_app = repo / APP_REL / "products/pc/app"
    adapter = repo / "tools/prisma-sentinels/sync-sentinel/sync_sentinel/adapters/pc_runtime.mts"
    tsx = repo / "node_modules/tsx/dist/cli.mjs"
    env = dict(os.environ)
    env.update({
        "DATABASE_URL": "file:" + pc_db.as_posix(),
        "TV_SYSTEM_ROOT": str(repo / APP_REL),
        "SYNC_SENTINEL_READY_FILE": str(ready_path),
        "SYNC_SENTINEL_TOKEN": token,
        "SYNC_SENTINEL_TEMP_ROOT": str(capsule.temp_root),
        "NODE_ENV": "test",
    })
    log_path = capsule.logs_root / "pc-runtime.log"
    log_fh = log_path.open("w", encoding="utf-8")
    proc = capsule.processes.start(
        ["node", str(tsx), "--tsconfig", str(pc_app / "tsconfig.json"), str(adapter)],
        cwd=pc_app,
        env=env,
        stdout=log_fh,
    )
    deadline = time.time() + 60
    while time.time() < deadline:
        if ready_path.is_file():
            data = json.loads(ready_path.read_text(encoding="utf-8"))
            if data.get("ready") is True and data.get("port"):
                return proc, log_fh, data, log_path
        if proc.poll() is not None:
            log_fh.flush()
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:] if log_path.is_file() else ""
            raise RuntimeError(f"PC_BRIDGE_EXITED_EARLY:rc={proc.returncode}:{tail}")
        time.sleep(0.25)
    raise RuntimeError("PC_BRIDGE_READINESS_TIMEOUT")


def _run_tablet_journeys(capsule: RuntimeCapsule, tablet_db: Path, bridge: dict[str, object], token: str) -> tuple[Check, Path]:
    assert capsule.worktree is not None and capsule.temp_root is not None
    repo = capsule.worktree
    tablet_app = repo / APP_REL / "products/tablet/app"
    adapter = repo / "tools/prisma-sentinels/sync-sentinel/sync_sentinel/adapters/tablet_runner.mts"
    tsx = repo / "node_modules/tsx/dist/cli.mjs"
    out_path = capsule.temp_root / "tablet-journeys.json"
    env = dict(os.environ)
    env.update({
        "TABLET_DATABASE_PATH": str(tablet_db),
        "TABLET_DATABASE_URL": "file:" + tablet_db.as_posix(),
        "DATABASE_URL": "file:" + tablet_db.as_posix(),
        "TABLET_APP_ROOT": str(tablet_app),
        "PRISMA_TABLET_PC_SYNC_ENABLED": "true",
        "PRISMA_TABLET_PC_ORIGIN": f"http://127.0.0.1:{bridge['port']}",
        "PRISMA_TABLET_PC_TIMEOUT_MS": "5000",
        "PRISMA_TABLET_SYNC_ACK_STRICT": "true",
        "SYNC_SENTINEL_TOKEN": token,
        "SYNC_SENTINEL_OUTPUT": str(out_path),
        "NODE_ENV": "test",
    })
    cp = subprocess.run(
        ["node", str(tsx), "--tsconfig", str(tablet_app / "tsconfig.json"), str(adapter)],
        cwd=str(tablet_app), env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=240, check=False,
    )
    text = (cp.stdout or "") + "\n" + (cp.stderr or "")
    step = {"ok": cp.returncode == 0, "returncode": cp.returncode, "tail": text}
    check = _process_check("isolated_real_code_journeys", step, ["PASS_SYNC_JOURNEY_A", "PASS_SYNC_JOURNEY_B"])
    if out_path.is_file():
        try:
            check.evidence["journeys"] = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception:
            check.evidence["journeysRaw"] = out_path.read_text(encoding="utf-8", errors="replace")[-5000:]
    return check, out_path


def _copy_runtime_evidence(paths: list[Path], evidence_dir: Path) -> list[Path]:
    copied: list[Path] = []
    mapping = {
        "pc-runtime.log": "SYNC_PC_RUNTIME.log",
        "tablet-journeys.json": "SYNC_JOURNEYS.json",
    }
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for src in paths:
        if not src.is_file():
            continue
        target = evidence_dir / mapping.get(src.name, f"SYNC_{src.name}")
        shutil.copy2(src, target)
        copied.append(target)
    return copied


def _base_report(mode: str, repo: Path, expected_head: str | None) -> RunReport:
    report = RunReport(mode=mode)
    actual = git_head(repo)
    if expected_head and actual != expected_head:
        report.add(Check("head_lock", Verdict.BLOCKED, "source HEAD does not match requested certification target", {
            "expected": expected_head, "actual": actual,
        }))
    else:
        report.add(Check("head_lock", Verdict.PASS, "source HEAD locked", {"head": actual}))
    report.facts.update({"repoHead": actual, "repoTree": git_tree(repo)})
    return report


def doctor(repo: Path, expected_head: str | None = None, *, keep_work: bool = False) -> RunReport:
    report = _base_report("doctor", repo, expected_head)
    progress = Progress(8)
    progress.step("source HEAD locked")
    report.add(authority_presence(repo)); progress.step("authority presence")
    report.add(sync_source_presence(repo)); progress.step("sync source presence")
    report.add(toolchain_presence()); progress.step("toolchain presence")
    if any(c.verdict != Verdict.PASS for c in report.checks):
        report.finalize()
        return report

    source_head = str(report.facts["repoHead"])
    capsule = RuntimeCapsule(repo, source_head, keep=keep_work)
    live_before = known_live_db_snapshot(repo)
    try:
        setup = capsule.setup()
        report.add(Check(
            "capsule_workspace_install",
            Verdict.PASS if setup.install_ok else Verdict.BLOCKED,
            "frozen workspace installed inside detached capsule" if setup.install_ok else "capsule workspace install failed",
            {"command": "pnpm install --frozen-lockfile --ignore-scripts"},
        ))
        report.add(Check(
            "capsule_dependency_resolution",
            Verdict.PASS if setup.dependency_ok else Verdict.BLOCKED,
            "declared Prisma dependencies resolve exactly inside capsule" if setup.dependency_ok else "Prisma dependency resolution failed closed",
            setup.manifest.get("dependencyResolution", {}),
        ))
        progress.step("capsule and dependency doctor")
        if setup.install_ok and setup.dependency_ok and capsule.worktree and capsule.data_root:
            prepared = prepare_isolated_databases(capsule.worktree, capsule.data_root)
            for check in _runtime_preparation_checks(prepared):
                report.add(check)
            progress.step("Prisma clients and temp DBs")
        else:
            report.add(Check("isolated_runtime_preparation", Verdict.BLOCKED, "dependency doctor blocked runtime preparation"))
            progress.step("runtime preparation blocked")
    except Exception as exc:
        report.add(Check("doctor_runtime", Verdict.FAIL, f"{type(exc).__name__}: {exc}"))
    finally:
        result = capsule.cleanup()
        live_after = known_live_db_snapshot(repo)
        report.add(Check(
            "live_db_unchanged",
            Verdict.PASS if snapshots_equal(live_before, live_after) else Verdict.FAIL,
            "known live DB candidates unchanged" if snapshots_equal(live_before, live_after) else "known live DB candidate changed",
        )); progress.step("live DB guard")
        report.add(Check(
            "capsule_cleanup",
            Verdict.PASS if result.cleanup_pass else Verdict.FAIL,
            "capsule destroyed and source remained stable" if result.cleanup_pass else "capsule cleanup/source guard failed",
            {"cleanup": result.manifest.get("cleanup", {}), "errors": result.errors},
        )); progress.step("capsule cleanup")
        report.facts["sandboxManifest"] = result.manifest
        report.facts["dependencyResolution"] = result.manifest.get("dependencyResolution", {})
        report.facts["liveDbTouched"] = not snapshots_equal(live_before, live_after)
        progress.step("doctor evidence ready")
    report.finalize()
    return report


def _run_capsule_e2e(repo: Path, evidence_dir: Path, expected_head: str | None, *, keep_work: bool, workers: int, include_certification_gates: bool) -> tuple[RunReport, Path | None]:
    mode = "certify" if include_certification_gates else "e2e"
    report = _base_report(mode, repo, expected_head)
    progress = Progress(12)
    progress.step("source HEAD locked")
    report.add(authority_presence(repo)); progress.step("authority presence")
    report.add(sync_source_presence(repo)); progress.step("sync source presence")
    report.add(toolchain_presence()); progress.step("toolchain presence")
    if any(c.verdict != Verdict.PASS for c in report.checks):
        report.finalize()
        return report, None

    source_head = str(report.facts["repoHead"])
    live_before = known_live_db_snapshot(repo)
    capsule = RuntimeCapsule(repo, source_head, keep=keep_work)
    runtime_evidence: list[Path] = []
    pc_log_fh = None
    try:
        setup = capsule.setup()
        report.add(Check(
            "capsule_workspace_install",
            Verdict.PASS if setup.install_ok else Verdict.BLOCKED,
            "frozen workspace installed inside detached capsule" if setup.install_ok else "capsule workspace install failed",
            {"command": "pnpm install --frozen-lockfile --ignore-scripts"},
        ))
        report.add(Check(
            "capsule_dependency_resolution",
            Verdict.PASS if setup.dependency_ok else Verdict.BLOCKED,
            "Prisma and @prisma/client resolve from declared workspace dependencies" if setup.dependency_ok else "dependency resolution blocked",
            setup.manifest.get("dependencyResolution", {}),
        )); progress.step("capsule dependencies")
        if not setup.install_ok or not setup.dependency_ok or not capsule.worktree or not capsule.data_root or not capsule.temp_root:
            raise RuntimeError("CAPSULE_DEPENDENCY_GATE_BLOCKED")

        prepared = prepare_isolated_databases(capsule.worktree, capsule.data_root)
        for check in _runtime_preparation_checks(prepared):
            report.add(check)
        progress.step("isolated Prisma and SQLite prepared")
        if not prepared.get("ok") or any(c.verdict != Verdict.PASS for c in report.checks):
            raise RuntimeError("ISOLATED_RUNTIME_PREPARATION_FAILED")

        pc_db = Path(str(prepared["pcDb"]))
        tablet_db = Path(str(prepared["tabletDb"]))
        token = secrets.token_hex(24)
        ready = capsule.temp_root / "pc-ready.json"
        proc, pc_log_fh, bridge, pc_log = _start_pc_bridge(capsule, pc_db, ready, token)
        runtime_evidence.append(pc_log)
        report.add(Check("pc_test_bridge", Verdict.PASS, "Sentinel-owned loopback PC bridge ready", {
            "pid": proc.pid,
            "port": bridge.get("port"),
        })); progress.step("real PC service bridge ready")

        journey, journey_path = _run_tablet_journeys(capsule, tablet_db, bridge, token)
        runtime_evidence.append(journey_path)
        report.add(journey); progress.step("Journey A and Journey B")

        for check in static_probe_suite(capsule.worktree, workers=workers):
            report.add(check)
        progress.step("native contract probes")

        fixture_registry = load_fixture_registry(capsule.worktree / "tools/prisma-sentinels/sync-sentinel")
        readiness = mandatory_fixture_readiness(fixture_registry)
        if include_certification_gates:
            report.add(Check(
                "mandatory_fixture_readiness",
                Verdict.PASS if readiness["ready"] else Verdict.BLOCKED,
                "all mandatory positive and negative fixtures are implemented" if readiness["ready"] else "mandatory negative fixtures remain unimplemented",
                readiness,
            ))
        else:
            report.add(Check("fixture_registry_loaded", Verdict.PASS, "versioned fixture registry loaded", readiness))
        progress.step("fixture coverage evaluated")
    except Exception as exc:
        report.add(Check("capsule_runtime", Verdict.FAIL, f"{type(exc).__name__}: {exc}"))
    finally:
        if pc_log_fh is not None:
            try:
                pc_log_fh.flush()
                pc_log_fh.close()
            except Exception:
                pass
        copied = _copy_runtime_evidence(runtime_evidence, evidence_dir)
        result = capsule.cleanup()
        progress.step("owned processes and capsule cleanup")
        live_after = known_live_db_snapshot(repo)
        live_touched = not snapshots_equal(live_before, live_after)
        report.add(Check(
            "live_db_unchanged",
            Verdict.FAIL if live_touched else Verdict.PASS,
            "known live DB candidate changed" if live_touched else "known live DB candidates unchanged",
            {"liveDbTouched": live_touched},
        ))
        report.add(Check(
            "capsule_cleanup",
            Verdict.PASS if result.cleanup_pass else Verdict.FAIL,
            "detached capsule destroyed without source drift or orphan process" if result.cleanup_pass else "capsule cleanup/source guard failed",
            {"cleanup": result.manifest.get("cleanup", {}), "errors": result.errors},
        )); progress.step("source/live guards verified")

        report.facts.update({
            "sandboxManifest": result.manifest,
            "dependencyResolution": result.manifest.get("dependencyResolution", {}),
            "liveDbTouched": live_touched,
            "sourceDrift": result.source_drift,
            "cleanupPass": result.cleanup_pass,
            "orphanProcesses": bool(result.orphan_processes),
        })
        report.finalize()
        success = report.verdict == Verdict.PASS
        payload = report.to_dict() | {
            "schemaVersion": "prisma.sync-sentinel.certification.v2" if include_certification_gates else "prisma.sync-sentinel.e2e.v1",
            "status": "PASS_SYNC_CERTIFICATION" if success and include_certification_gates else ("PASS_SYNC_E2E" if success else f"{report.verdict.value}_{'SYNC_CERTIFICATION' if include_certification_gates else 'SYNC_E2E'}"),
            "generatedAt": now_iso(),
            "repoHead": source_head,
            "liveDbTouched": live_touched,
            "sourceDrift": result.source_drift,
            "cleanupPass": result.cleanup_pass,
            "orphanProcesses": bool(result.orphan_processes),
            "secretFindings": 0,
            "productionCertified": False,
            "doesNotProve": [
                "Hosted/customer production operation",
                "Customer or historical database mutation safety beyond the explicit no-live-DB guards",
                "Future source/dependency/configuration drift",
            ],
        }
        bundle, secret_count, secret_items = build_bundle(evidence_dir, payload, copied)
        if secret_count:
            report.add(Check("evidence_secret_scan", Verdict.FAIL, "secret-like material remained after sanitization", {
                "count": secret_count, "labels": secret_items,
            }))
        else:
            report.add(Check("evidence_secret_scan", Verdict.PASS, "evidence has zero remaining secret findings"))
        report.finalize()
        progress.step("sanitized evidence bundle")
        progress.step("final verdict")
        if report.verdict != Verdict.PASS:
            return report, bundle
    return report, bundle


def e2e(repo: Path, evidence_dir: Path, expected_head: str | None = None, keep_work: bool = False, workers: int = 3) -> tuple[RunReport, Path | None]:
    return _run_capsule_e2e(repo, evidence_dir, expected_head, keep_work=keep_work, workers=workers, include_certification_gates=False)


def certify(repo: Path, evidence_dir: Path, expected_head: str | None = None, keep_work: bool = False, workers: int = 3) -> tuple[RunReport, Path | None]:
    return _run_capsule_e2e(repo, evidence_dir, expected_head, keep_work=keep_work, workers=workers, include_certification_gates=True)
