#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA Smart AllMesh controller v6.

Streams child progress live, gives every run a private collision-proof workspace,
normalizes nested AutoMesh evidence into one final ZIP, and packages cancellation
or failure fail-closed. Read-only against the repository.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from .prisma_automesh_runtime import (
        ProgressReporter,
        atomic_zip_dir,
        capture_exception,
        extract_zip_verified,
        make_run_id,
        safe_rmtree,
        sha256,
        short_run_id,
        stream_command,
        write_json_atomic,
    )
except ImportError:
    from prisma_automesh_runtime import (
        ProgressReporter,
        atomic_zip_dir,
        capture_exception,
        extract_zip_verified,
        make_run_id,
        safe_rmtree,
        sha256,
        short_run_id,
        stream_command,
        write_json_atomic,
    )

INTENT_TASKS = {
    "auto": (
        "Genera Smart AllMesh inteligente para {surface_label}. El usuario entrega contexto amplio y el motor debe filtrar automaticamente. "
        "Incluye autoridad, layer map, owners, contratos/gates, UI surface target, licencias/tenants/devices/plans, Data PRISMA, Prisma schema, "
        "D1/SQL, APIs, OCR/ingesta visual/documentos/evidencia, NDC/canon/lineage, operational evidence, riesgos, scope guard y readiness. "
        "Read-only: no patch, no process kill, no port free, no dev server, no hot Prisma."
    ),
    "authority": (
        "Genera Authority Mesh previo a patch para {surface_label}. Resolver fuente de autoridad, APP_IMPACT_MATRIX, CONTRACT_AND_GATE_MATRIX, "
        "MISSING_OR_UNMAPPED_RISK, AGENT_PROMPT_ENVELOPE, AUTHORITY_MESH_REPORT, layer map, owners, superficies incluidas/excluidas y riesgos. Read-only."
    ),
    "data_ocr_licenses": (
        "Genera mesh de verdad operativa para {surface_label}: licencias, tenants, plans, devices, permisos, PRISMA data, DB/Prisma schema/D1/SQL, "
        "APIs, runtime evidence, OCR/ingesta visual/documentos/evidencia, lineage, canonical projections, NDC y production readiness. Read-only."
    ),
    "operational": (
        "Genera Operational Evidence Mesh para {surface_label}: ventas, sale lines, tenders, cash sessions, outbox, sync, canonical projection, "
        "customer visible scan, runtime evidence, devices, users/cashiers, stores/terminals, audit completeness, confidence score y production gates. Read-only."
    ),
    "ui_surface": (
        "Genera UI / Surface Target Mesh para {surface_label}: pantalla, layout, botones, dropdowns, paneles, selectors, glass/layers, CSS/TSX owners, "
        "tokens, zero-important gate, fewest containers possible, scope guard y regresiones visuales. Read-only."
    ),
    "ndc_canon": (
        "Genera NDC / Canon / Lineage Mesh para {surface_label}: neutral IDs, ENT/EVT/ACT/STA/MET/CAP/CAN, matrices como vistas, separation meaning vs implementation, "
        "canonical projections, data lineage, schema/API/UI bindings y curation debt. Read-only."
    ),
}

SURFACE_LABELS = {
    "": "superficie inferida",
    "auto": "superficie inferida",
    "all": "Todo PRISMA",
    "global": "Global PRISMA",
    "tablet": "Tablet",
    "pc": "PC Admin",
    "mobile": "App/Mobile",
    "app": "App/Mobile",
    "web": "Web / EIT",
    "cloud-center": "Cloud Center",
    "control-center": "Control Center",
    "chart-lab": "Chart Lab",
}

SURFACE_ARGS = {
    "": "",
    "auto": "",
    "all": "",
    "global": "",
    "tablet": "tablet",
    "pc": "pc",
    "mobile": "mobile",
    "app": "mobile",
    "web": "web",
    "cloud-center": "governance",
    "control-center": "governance",
    "chart-lab": "chart_lab",
}


def find_repo(root_path: str | None, fallback: str | None) -> Path:
    candidates: list[Path] = []
    if root_path:
        candidate = Path(root_path)
        if candidate.is_file():
            candidate = candidate.parent
        candidates.append(candidate)
    if fallback:
        candidates.append(Path(fallback))
    candidates.extend([Path(r"F:\repos\hitech-os"), Path.cwd()])

    seen: set[str] = set()
    for candidate in candidates:
        try:
            candidate = candidate.expanduser().resolve()
        except Exception:
            continue
        for path in [candidate] + list(candidate.parents):
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            if (path / ".git").exists():
                return path
    for candidate in candidates:
        try:
            if candidate.exists():
                return candidate.resolve()
        except Exception:
            pass
    raise RuntimeError("NO_REPO: no encontré repo Git")


def copy_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists() or not source.is_file():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def controller_self_test() -> int:
    first = make_run_id("allmesh")
    second = make_run_id("allmesh")
    assert first != second
    with tempfile.TemporaryDirectory(prefix="smart_allmesh_selftest_") as temporary:
        root = Path(temporary)
        source = root / "source"
        source.mkdir()
        (source / "hello.txt").write_text("hola\n", encoding="utf-8")
        target = root / "result.zip"
        result = atomic_zip_dir(source, target)
        assert target.exists()
        assert result["entries"] == 1
    print("SMART ALLMESH CONTROLLER V6 SELFTEST OK: unique-run atomic-zip live-stream-ready")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Atlas Smart AllMesh controller v6")
    parser.add_argument("--root-path", default="")
    parser.add_argument("--surface", default="auto")
    parser.add_argument("--intent", default="auto", choices=sorted(INTENT_TASKS))
    parser.add_argument("--repo", default=os.environ.get("ALLMESH_REPO", r"F:\repos\hitech-os"))
    parser.add_argument("--out-root", default=os.environ.get("ALLMESH_OUT_ROOT", r"F:\descargasf"))
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--shards", type=int, default=72)
    parser.add_argument("--max-files", type=int, default=360)
    parser.add_argument("--max-mb", type=int, default=140)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return controller_self_test()

    args.workers = max(1, min(18, int(args.workers)))
    args.shards = max(args.workers, min(216, int(args.shards)))
    args.max_files = max(1, int(args.max_files))
    args.max_mb = max(1, int(args.max_mb))

    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    repo = find_repo(args.root_path, args.repo)
    run_id = args.run_id.strip() or make_run_id("allmesh")
    short_id = short_run_id(run_id)
    human_stamp = dt.datetime.now().strftime("%d%m %H%M%S")

    work_root = out_root / ".allmesh_work" / run_id
    stage = work_root / "staging"
    final_payload = work_root / "final_payload"
    automesh_out = stage / "automesh_out"
    log_path = stage / "smart_allmesh.log"
    progress_jsonl = stage / "controller_progress.jsonl"
    child_progress_jsonl = stage / "automesh_progress.jsonl"
    stage.mkdir(parents=True, exist_ok=False)
    final_payload.mkdir(parents=True, exist_ok=False)
    automesh_out.mkdir(parents=True, exist_ok=False)

    reporter = ProgressReporter(
        run_id=run_id,
        jsonl_path=progress_jsonl,
        width=34,
        component="smart-allmesh-controller",
    )
    reporter.start_heartbeat(5.0)

    surface_key = (args.surface or "auto").strip().lower()
    surface_arg = SURFACE_ARGS.get(
        surface_key,
        surface_key if surface_key not in {"auto", "all", "global"} else "",
    )
    surface_label = SURFACE_LABELS.get(surface_key, args.surface or "superficie inferida")
    task = INTENT_TASKS[args.intent].format(surface_label=surface_label)

    report: dict[str, Any] = {
        "kind": "CODE_ATLAS_SMART_ALLMESH_CONTROLLER",
        "version": "v6",
        "created_at": dt.datetime.now().isoformat(),
        "run_id": run_id,
        "status": "PENDING",
        "root_path": args.root_path,
        "repo": str(repo),
        "out_root": str(out_root),
        "surface": args.surface,
        "surface_arg": surface_arg,
        "intent": args.intent,
        "task": task,
        "workers_local_cap": args.workers,
        "shards": args.shards,
        "rules": {
            "read_only": True,
            "no_patch": True,
            "no_process_kill": True,
            "no_port_free": True,
            "no_dev_server_start": True,
            "no_hot_prisma": True,
            "one_loose_final_zip": True,
            "atomic_zip_publication": True,
            "live_child_output": True,
            "collision_proof_private_stage": True,
            "global_worker_budget": 18,
        },
    }

    final_zip: Path | None = None
    exit_code = 1
    try:
        reporter.emit(2, "preflight Smart AllMesh", details={"repo": str(repo)})
        automesh = Path(__file__).resolve().with_name("smart_allmesh_automesh.py")
        if not automesh.exists():
            raise RuntimeError(f"NO_AUTOMESH: {automesh}")

        reporter.emit(8, "automesh self-test")
        self_test = stream_command(
            [sys.executable, str(automesh), "--self-test"],
            cwd=None,
            log_path=log_path,
            reporter=reporter,
            heartbeat_label="self-test AutoMesh trabajando",
        )
        report["self_test"] = self_test
        if self_test["returncode"] != 0:
            raise RuntimeError("FAIL_AUTOMESH_SELF_TEST")

        reporter.emit(15, "generando mesh inteligente con salida viva")
        command = [
            sys.executable,
            str(automesh),
            "--task",
            task,
            "--repo",
            str(repo),
            "--out",
            str(automesh_out),
            "--workers",
            str(args.workers),
            "--shards",
            str(args.shards),
            "--max-files",
            str(args.max_files),
            "--max-mb",
            str(args.max_mb),
            "--run-id",
            run_id,
            "--progress-jsonl",
            str(child_progress_jsonl),
        ]
        if surface_arg:
            command += ["--surface", surface_arg]

        child = stream_command(
            command,
            cwd=None,
            log_path=log_path,
            reporter=reporter,
            heartbeat_label="AutoMesh sigue vivo; esperando siguiente evento",
        )
        report["automesh_returncode"] = child["returncode"]
        report["automesh_markers"] = child["markers"]
        report["automesh_tail"] = child["tail"]

        marker_name = "OK_RESULT_ZIP" if child["returncode"] == 0 else "FAIL_ZIP"
        marker_path = child["markers"].get(marker_name)
        if not marker_path:
            raise RuntimeError(
                f"AUTOMESH_DID_NOT_REPORT_EXACT_ZIP: expected {marker_name}"
            )
        child_zip = Path(marker_path)
        if not child_zip.exists():
            raise RuntimeError(f"AUTOMESH_ZIP_MISSING: {child_zip}")

        reporter.emit(82, "normalizando evidencia sin ZIP anidado")
        extraction = extract_zip_verified(child_zip, final_payload / "authority_mesh")
        report["automesh_zip_source"] = extraction
        report["automesh_zip_name"] = child_zip.name

        report["status"] = "PASS" if child["returncode"] == 0 else "FAIL"
        copy_if_exists(log_path, final_payload / "smart_allmesh.log")
        copy_if_exists(progress_jsonl, final_payload / "controller_progress.jsonl")
        copy_if_exists(child_progress_jsonl, final_payload / "automesh_progress.jsonl")
        write_json_atomic(final_payload / "SMART_ALLMESH_REPORT.json", report)
        (final_payload / "SMART_ALLMESH_REPORT.md").write_text(
            "# Smart AllMesh v6\n\n"
            f"- Status: `{report['status']}`\n"
            f"- Run ID: `{run_id}`\n"
            f"- Surface: `{args.surface}`\n"
            f"- Intent: `{args.intent}`\n"
            f"- Repo: `{repo}`\n"
            f"- Global worker budget: `18`\n"
            f"- Local worker cap: `{args.workers}`\n\n"
            "## Task\n\n"
            f"{task}\n",
            encoding="utf-8",
        )
        (final_payload / "CONTINUATION.md").write_text(
            "# Smart AllMesh continuation\n\n"
            f"Status: {report['status']}\n"
            f"Run ID: {run_id}\n"
            "The child AutoMesh output was streamed live and normalized into this single ZIP.\n",
            encoding="utf-8",
        )

        status_word = "result" if child["returncode"] == 0 else "fail"
        final_zip = out_root / f"allmesh {human_stamp} {short_id} {status_word}.zip"
        report["final_zip_path"] = str(final_zip)
        write_json_atomic(final_payload / "SMART_ALLMESH_REPORT.json", report)
        reporter.emit(94, "publicando ZIP final atómico")
        zip_report = atomic_zip_dir(final_payload, final_zip)

        exit_code = 0 if child["returncode"] == 0 else 1
        reporter.emit(
            100,
            "Smart AllMesh terminado",
            status="PASS" if exit_code == 0 else "FAIL",
            details={"zip": str(final_zip)},
        )
        if exit_code == 0:
            print(f"FINAL_RESULT_ZIP={final_zip}", flush=True)
        else:
            print(f"FINAL_FAIL_ZIP={final_zip}", flush=True)
        return exit_code

    except KeyboardInterrupt as exc:
        exit_code = 130
        report["status"] = "CANCELLED"
        report["error"] = capture_exception(exc)
    except Exception as exc:
        exit_code = 1
        report["status"] = "FAIL"
        report["error"] = capture_exception(exc)
    finally:
        if exit_code != 0 and report.get("status") in {"FAIL", "CANCELLED"}:
            try:
                reporter.emit(
                    96,
                    "empaquetando diagnóstico fail-closed",
                    status=report["status"],
                )
                diagnostics = final_payload / "diagnostics"
                diagnostics.mkdir(parents=True, exist_ok=True)
                copy_if_exists(log_path, diagnostics / "smart_allmesh.log")
                copy_if_exists(progress_jsonl, diagnostics / "controller_progress.jsonl")
                copy_if_exists(child_progress_jsonl, diagnostics / "automesh_progress.jsonl")
                if automesh_out.exists():
                    partial = diagnostics / "partial_automesh_out"
                    shutil.copytree(automesh_out, partial, dirs_exist_ok=True)
                write_json_atomic(final_payload / "SMART_ALLMESH_REPORT.json", report)
                (final_payload / "ERROR.txt").write_text(
                    json.dumps(report.get("error", {}), indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                (final_payload / "CONTINUATION.md").write_text(
                    "# Smart AllMesh fail continuation\n\n"
                    f"Status: {report.get('status')}\n"
                    f"Run ID: {run_id}\n"
                    "Review ERROR.txt, logs, progress JSONL and partial AutoMesh evidence.\n",
                    encoding="utf-8",
                )
                final_zip = out_root / f"allmesh {human_stamp} {short_id} fail.zip"
                atomic_zip_dir(final_payload, final_zip)
                reporter.emit(
                    100,
                    "diagnóstico fail-closed listo",
                    status=report.get("status", "FAIL"),
                    details={"zip": str(final_zip)},
                )
                print(f"FINAL_FAIL_ZIP={final_zip}", flush=True)
            except Exception as packaging_exc:
                print(
                    "SMART_ALLMESH_FATAL_PACKAGING_ERROR="
                    + json.dumps(capture_exception(packaging_exc), ensure_ascii=False),
                    flush=True,
                )
                print(f"SMART_ALLMESH_WORK_ROOT_PRESERVED={work_root}", flush=True)
        reporter.stop_heartbeat()
        if final_zip is not None and final_zip.exists():
            safe_rmtree(work_root)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
