from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .evidence import build_bundle, now_iso
from .model import Check, RunReport, Verdict
from .probes import authority_presence, head_check, static_probe_suite, sync_source_presence, toolchain_presence
from .progress import Progress
from .registry import APP_REL
from .safety import (
    ensure_temp_db,
    git_head,
    git_tree,
    known_live_db_snapshot,
    repo_clean_for_certification,
    run,
    snapshots_equal,
    stop_owned_process,
    tracked_diff,
)


def _result_from_process(check_id: str, cp: subprocess.CompletedProcess[str], pass_tokens: list[str] | None = None) -> Check:
    text = (cp.stdout or "") + "\n" + (cp.stderr or "")
    if cp.returncode != 0:
        return Check(check_id, Verdict.FAIL, "command failed", {"returncode": cp.returncode, "tail": text[-4000:]})
    if pass_tokens and not all(token in text for token in pass_tokens):
        return Check(check_id, Verdict.UNKNOWN, "command exited zero but canonical success markers were incomplete", {"tail": text[-4000:]})
    return Check(check_id, Verdict.PASS, "command passed", {"returncode": cp.returncode, "tail": text[-2400:]})


def scan(repo: Path, expected_head: str | None = None, workers: int = 3) -> RunReport:
    report = RunReport(mode="scan")
    progress = Progress(5)
    report.add(head_check(repo, expected_head)); progress.step("HEAD lock")
    report.add(authority_presence(repo)); progress.step("authority presence")
    report.add(sync_source_presence(repo)); progress.step("sync source presence")
    report.add(toolchain_presence()); progress.step("toolchain presence")
    for check in static_probe_suite(repo, workers=workers):
        report.add(check)
    progress.step("native static probes")
    report.facts.update({"repoHead": git_head(repo), "repoTree": git_tree(repo)})
    report.finalize()
    return report


def diagnose(repo: Path, expected_head: str | None = None) -> RunReport:
    report = RunReport(mode="diagnose")
    progress = Progress(4)
    report.add(head_check(repo, expected_head)); progress.step("HEAD lock")
    clean, detail = repo_clean_for_certification(repo)
    report.add(Check("worktree_clean", Verdict.PASS if clean else Verdict.BLOCKED, "worktree is clean for isolated certification" if clean else "worktree has non-Sentinel drift", detail)); progress.step("worktree state")
    live = known_live_db_snapshot(repo)
    report.add(Check("known_live_db_inventory", Verdict.PASS, "known live DB candidates inventoried read-only", {"candidates": live}, ["Does not discover arbitrary DBs outside the repository or operator-specific paths."])); progress.step("live DB inventory")
    report.add(sync_source_presence(repo)); progress.step("sync source map")
    report.facts.update({"repoHead": git_head(repo), "repoTree": git_tree(repo), "knownLiveDbBefore": live})
    report.finalize()
    return report


def _prepare_temp_databases(repo: Path, temp_root: Path, pc_db: Path, tablet_db: Path) -> list[Check]:
    checks: list[Check] = []
    app = repo / APP_REL
    env_pc = dict(os.environ)
    env_pc["DATABASE_URL"] = "file:" + pc_db.as_posix()
    env_pc["PRISMA_GENERATE_SKIP_AUTOINSTALL"] = "true"
    cp = run(["python", str(app / "tooling/scripts/migrate_prisma_canonical.py")], cwd=app, env=env_pc, timeout=240)
    checks.append(_result_from_process("pc_temp_db_migrations", cp, ['"pass": true']))
    if checks[-1].verdict != Verdict.PASS:
        return checks

    cp = run(["python", str(app / "tooling/scripts/generate_prisma_canonical.py"), "pc"], cwd=app, env=env_pc, timeout=300)
    checks.append(_result_from_process("pc_temp_prisma_generate", cp))
    if checks[-1].verdict != Verdict.PASS:
        return checks

    # Tablet owns a custom Prisma client output (prisma/.generated/prisma-client).
    # Do not call scripts/tablet-db.mjs here: its operational init path imports the
    # package-default @prisma/client after generation and may also seed demo data.
    # Sentinel needs only the canonical Tablet schema on a disposable DB; the
    # journey adapter seeds the minimum synthetic scope itself.
    tablet_app = app / "products/tablet/app"
    tablet_schema = tablet_app / "prisma/schema.prisma"
    env_tab = dict(os.environ)
    env_tab["TABLET_DATABASE_PATH"] = str(tablet_db)
    env_tab["TABLET_DATABASE_URL"] = "file:" + tablet_db.as_posix()
    env_tab["DATABASE_URL"] = "file:" + tablet_db.as_posix()
    env_tab["PRISMA_GENERATE_SKIP_AUTOINSTALL"] = "true"

    cp = run(["pnpm", "exec", "prisma", "generate", "--schema", str(tablet_schema)], cwd=tablet_app, env=env_tab, timeout=300)
    checks.append(_result_from_process("tablet_temp_prisma_generate", cp))
    if checks[-1].verdict != Verdict.PASS:
        return checks

    cp = run(["pnpm", "exec", "prisma", "db", "push", "--schema", str(tablet_schema), "--skip-generate"], cwd=tablet_app, env=env_tab, timeout=300)
    checks.append(_result_from_process("tablet_temp_db_push", cp))
    return checks


def _start_pc_bridge(repo: Path, temp_root: Path, pc_db: Path, ready_path: Path, token: str):
    pc_app = repo / APP_REL / "products/pc/app"
    adapter = repo / "tools/prisma-sentinels/sync-sentinel/sync_sentinel/adapters/pc_runtime.mts"
    tsx = repo / "node_modules/tsx/dist/cli.mjs"
    env = dict(os.environ)
    env.update({
        "DATABASE_URL": "file:" + pc_db.as_posix(),
        "TV_SYSTEM_ROOT": str(repo / APP_REL),
        "SYNC_SENTINEL_READY_FILE": str(ready_path),
        "SYNC_SENTINEL_TOKEN": token,
        "SYNC_SENTINEL_TEMP_ROOT": str(temp_root),
        "NODE_ENV": "test",
    })
    cmd = ["node", str(tsx), "--tsconfig", str(pc_app / "tsconfig.json"), str(adapter)]
    log_path = temp_root / "pc-runtime.log"
    log_fh = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(cmd, cwd=str(pc_app), env=env, stdout=log_fh, stderr=subprocess.STDOUT, text=True)
    deadline = time.time() + 45
    while time.time() < deadline:
        if ready_path.is_file():
            data = json.loads(ready_path.read_text(encoding="utf-8"))
            if data.get("ready") is True and data.get("port"):
                return proc, log_fh, data, log_path
        if proc.poll() is not None:
            log_fh.flush()
            raise RuntimeError(f"PC bridge exited early rc={proc.returncode}: {log_path.read_text(encoding='utf-8', errors='replace')[-4000:]}")
        time.sleep(0.25)
    raise RuntimeError("PC bridge readiness timeout")


def _run_tablet_journeys(repo: Path, temp_root: Path, tablet_db: Path, bridge: dict, token: str) -> Check:
    tablet_app = repo / APP_REL / "products/tablet/app"
    adapter = repo / "tools/prisma-sentinels/sync-sentinel/sync_sentinel/adapters/tablet_runner.mts"
    tsx = repo / "node_modules/tsx/dist/cli.mjs"
    out_path = temp_root / "tablet-journeys.json"
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
    cp = run(["node", str(tsx), "--tsconfig", str(tablet_app / "tsconfig.json"), str(adapter)], cwd=tablet_app, env=env, timeout=180)
    check = _result_from_process("isolated_real_code_journeys", cp, ["PASS_SYNC_JOURNEY_A", "PASS_SYNC_JOURNEY_B"])
    if out_path.is_file():
        try:
            check.evidence["journeys"] = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception:
            check.evidence["journeysRaw"] = out_path.read_text(encoding="utf-8", errors="replace")[-5000:]
    return check


def certify(repo: Path, evidence_dir: Path, expected_head: str | None = None, keep_work: bool = False, workers: int = 3) -> tuple[RunReport, Path | None]:
    report = RunReport(mode="certify")
    progress = Progress(12)
    start_head = git_head(repo)
    report.facts.update({"repoHead": start_head, "repoTree": git_tree(repo)})
    if expected_head and start_head != expected_head:
        report.add(Check("head_lock", Verdict.BLOCKED, "certification HEAD mismatch", {"expected": expected_head, "actual": start_head}))
        report.finalize()
        return report, None
    report.add(Check("head_lock", Verdict.PASS, "certification HEAD locked", {"head": start_head})); progress.step("HEAD locked")

    clean, clean_detail = repo_clean_for_certification(repo)
    report.add(Check("worktree_clean", Verdict.PASS if clean else Verdict.BLOCKED, "clean worktree" if clean else "non-Sentinel worktree drift", clean_detail)); progress.step("worktree checked")
    if not clean:
        report.finalize(); return report, None

    report.add(authority_presence(repo)); progress.step("authority checked")
    report.add(sync_source_presence(repo)); progress.step("sync source checked")
    report.add(toolchain_presence()); progress.step("toolchain checked")
    if any(c.verdict != Verdict.PASS for c in report.checks):
        report.finalize(); return report, None

    before_live = known_live_db_snapshot(repo)
    before_diff = tracked_diff(repo)
    progress.step("live DB and source baseline captured")

    temp_root = Path(tempfile.mkdtemp(prefix="prisma-sync-sentinel-"))
    pc_db = ensure_temp_db(temp_root / "pc/canonical.db", temp_root, "pc")
    tablet_db = ensure_temp_db(temp_root / "tablet/tablet-pos.db", temp_root, "tablet")
    token = os.urandom(18).hex()
    report.facts["tempRoot"] = str(temp_root)
    proc = None
    log_fh = None
    extra_files: list[Path] = []
    cleanup = {"process": None, "tempRemoved": False}
    bundle: Path | None = None
    live_touched = False
    source_drift = False
    head_drift = False
    orphan = False
    try:
        for check in _prepare_temp_databases(repo, temp_root, pc_db, tablet_db):
            report.add(check)
            if check.verdict != Verdict.PASS:
                break
        progress.step("isolated temp databases initialized")
        if any(c.verdict != Verdict.PASS for c in report.checks):
            raise RuntimeError("isolated DB preparation failed")

        ready = temp_root / "pc-ready.json"
        proc, log_fh, bridge, pc_log = _start_pc_bridge(repo, temp_root, pc_db, ready, token)
        extra_files.extend([ready, pc_log])
        report.add(Check("pc_test_bridge", Verdict.PASS, "Sentinel-owned loopback PC bridge is ready", {"pid": proc.pid, "port": bridge.get("port")}))
        progress.step("Sentinel PC bridge ready")

        journey = _run_tablet_journeys(repo, temp_root, tablet_db, bridge, token)
        report.add(journey)
        jpath = temp_root / "tablet-journeys.json"
        if jpath.is_file(): extra_files.append(jpath)
        progress.step("Journey A and Journey B executed")

        for check in static_probe_suite(repo, workers=workers):
            report.add(check)
        progress.step("native contract probes executed")

    except Exception as exc:
        report.add(Check("certification_runtime", Verdict.FAIL, f"{type(exc).__name__}: {exc}"))
    finally:
        if log_fh:
            try: log_fh.flush()
            except Exception: pass
        if proc is not None:
            cleanup["process"] = stop_owned_process(proc)
        if log_fh:
            try: log_fh.close()
            except Exception: pass
        progress.step("Sentinel-owned process cleanup")

        after_live = known_live_db_snapshot(repo)
        live_touched = not snapshots_equal(before_live, after_live)
        after_diff = tracked_diff(repo)
        source_drift = before_diff != after_diff or bool(after_diff)
        current_head = git_head(repo)
        head_drift = current_head != start_head
        report.add(Check("live_db_unchanged", Verdict.FAIL if live_touched else Verdict.PASS, "known live DB candidates changed" if live_touched else "known live DB candidates unchanged", {"before": before_live, "after": after_live}))
        report.add(Check("source_drift", Verdict.FAIL if source_drift or head_drift else Verdict.PASS, "source/HEAD drift detected during certification" if source_drift or head_drift else "tracked source and HEAD remained stable", {"beforeDiff": before_diff, "afterDiff": after_diff, "startHead": start_head, "endHead": current_head}))
        progress.step("live DB and source drift verified")

        orphan = bool(proc is not None and proc.poll() is None)
        report.add(Check("owned_process_cleanup", Verdict.FAIL if orphan else Verdict.PASS, "Sentinel-owned process remains alive" if orphan else "no Sentinel-owned orphan process remains", cleanup))
        progress.step("orphan process check")

        report.finalize()
        success = report.verdict == Verdict.PASS
        result = report.to_dict()
        result.update({
            "schemaVersion": "prisma.sync-sentinel.certification.v1",
            "status": "PASS_SYNC_CERTIFICATION" if success else f"{report.verdict.value}_SYNC_CERTIFICATION",
            "generatedAt": now_iso(),
            "repoHead": start_head,
            "repoTree": git_tree(repo),
            "liveDbTouched": live_touched,
            "sourceDrift": source_drift or head_drift,
            "cleanupPass": not orphan,
            "orphanProcesses": orphan,
            "secretFindings": 0,
            "productionCertified": False,
            "doesNotProve": [
                "Hosted/customer production operation",
                "Arbitrary external databases outside the known repository candidates",
                "Future source or configuration drift",
            ],
        })
        bundle, secret_count, secret_items = build_bundle(evidence_dir, result, extra_files)
        if secret_count:
            report.add(Check("evidence_secret_scan", Verdict.FAIL, "evidence still contains secret-like material after sanitization", {"count": secret_count, "labels": secret_items}))
        else:
            report.add(Check("evidence_secret_scan", Verdict.PASS, "evidence text has zero detected secret patterns after sanitization"))
        report.finalize()
        progress.step("sanitized evidence bundle built")

        if not keep_work:
            try:
                shutil.rmtree(temp_root)
                cleanup["tempRemoved"] = not temp_root.exists()
            except Exception as exc:
                cleanup["tempCleanupError"] = str(exc)
                report.add(Check("temp_workspace_cleanup", Verdict.FAIL, "temporary workspace cleanup failed", {"error": str(exc)}))
                report.finalize()
        else:
            cleanup["tempRemoved"] = False
        progress.step("temporary workspace cleanup")

    return report, bundle
