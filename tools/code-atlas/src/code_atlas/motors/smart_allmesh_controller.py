#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

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


def progress(done: int, total: int, label: str) -> None:
    pct = int(done * 100 / max(total, 1))
    fill = int(34 * pct / 100)
    print(f"[{'█' * fill}{'░' * (34 - fill)}] {pct:3d}% | falta {100 - pct:3d}% | {label}", flush=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        dst.unlink()
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(src).as_posix())


def run(cmd: list[str], cwd: Path | None, log_path: Path) -> dict[str, Any]:
    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        log.write("\n\n$ " + " ".join(map(str, cmd)) + "\n")
        log.flush()
        try:
            p = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
            log.write(p.stdout)
            if p.stderr:
                log.write("\n[stderr]\n" + p.stderr)
            log.write(f"\n[returncode] {p.returncode}\n")
            return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "cmd": cmd}
        except Exception as exc:
            log.write("\n[exception] " + repr(exc) + "\n")
            return {"returncode": 999, "stdout": "", "stderr": repr(exc), "cmd": cmd}


def find_repo(root_path: str | None, fallback: str | None) -> Path:
    candidates: list[Path] = []
    if root_path:
        p = Path(root_path)
        if p.is_file():
            p = p.parent
        candidates.append(p)
    if fallback:
        candidates.append(Path(fallback))
    candidates.append(Path(r"F:\repos\hitech-os"))
    candidates.append(Path.cwd())
    seen: set[str] = set()
    for c in candidates:
        try:
            c = c.expanduser().resolve()
        except Exception:
            continue
        for p in [c] + list(c.parents):
            key = str(p).lower()
            if key in seen:
                continue
            seen.add(key)
            if (p / ".git").exists():
                return p
    for c in candidates:
        try:
            if c.exists():
                return c.resolve()
        except Exception:
            pass
    return Path(r"F:\repos\hitech-os")


def newest_zip(folder: Path, status: str) -> Path | None:
    candidates = [p for p in folder.rglob("*.zip") if p.name.lower().endswith(f" {status}.zip")]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Atlas Smart AllMesh controller")
    parser.add_argument("--root-path", default="")
    parser.add_argument("--surface", default="auto")
    parser.add_argument("--intent", default="auto", choices=sorted(INTENT_TASKS))
    parser.add_argument("--repo", default=os.environ.get("ALLMESH_REPO", r"F:\repos\hitech-os"))
    parser.add_argument("--out-root", default=os.environ.get("ALLMESH_OUT_ROOT", r"F:\descargasf"))
    parser.add_argument("--workers", default="18")
    parser.add_argument("--shards", default="72")
    parser.add_argument("--max-files", default="360")
    parser.add_argument("--max-mb", default="140")
    args = parser.parse_args()

    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    repo = find_repo(args.root_path, args.repo)
    stamp = dt.datetime.now().strftime("%d%m %H%M")
    stage = out_root / f"allmesh {stamp} staging"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True, exist_ok=True)
    log_path = stage / "smart_allmesh.log"

    surface_key = (args.surface or "auto").strip().lower()
    surface_arg = SURFACE_ARGS.get(surface_key, surface_key if surface_key not in {"auto", "all", "global"} else "")
    surface_label = SURFACE_LABELS.get(surface_key, args.surface or "superficie inferida")
    task = INTENT_TASKS[args.intent].format(surface_label=surface_label)

    report: dict[str, Any] = {
        "kind": "CODE_ATLAS_SMART_ALLMESH_CONTROLLER",
        "created_at": dt.datetime.now().isoformat(),
        "status": "PENDING",
        "root_path": args.root_path,
        "repo": str(repo),
        "out_root": str(out_root),
        "surface": args.surface,
        "surface_arg": surface_arg,
        "intent": args.intent,
        "task": task,
        "rules": {
            "read_only": True,
            "no_patch": True,
            "no_process_kill": True,
            "no_port_free": True,
            "no_dev_server_start": True,
            "no_hot_prisma": True,
            "auto_filter_context": True,
            "one_dropdown_one_button": True,
        },
    }

    progress(0, 5, "preflight Smart AllMesh")
    if not repo.exists():
        raise SystemExit(f"NO_REPO: {repo}")

    automesh = Path(__file__).resolve().with_name("smart_allmesh_automesh.py")
    if not automesh.exists():
        raise SystemExit(f"NO_AUTOMESH: {automesh}")

    progress(1, 5, "automesh self-test")
    p = run([sys.executable, str(automesh), "--self-test"], None, log_path)
    if p["returncode"] != 0:
        report["status"] = "FAIL_SELF_TEST"
        report["self_test"] = p
        final_dir = stage / f"allmesh {stamp} fail"
        final_dir.mkdir(parents=True, exist_ok=True)
        (final_dir / "SMART_ALLMESH_REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        shutil.copy2(log_path, final_dir / "smart_allmesh.log")
        final_zip = out_root / f"allmesh {stamp} fail.zip"
        zip_dir(final_dir, final_zip)
        print(f"FINAL_FAIL_ZIP={final_zip}", flush=True)
        return 1

    progress(2, 5, "generando mesh inteligente")
    automesh_out = stage / "automesh_out"
    automesh_out.mkdir(parents=True, exist_ok=True)
    cmd = [
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
    ]
    if surface_arg:
        cmd += ["--surface", surface_arg]
    p = run(cmd, None, log_path)
    status = "result" if p["returncode"] == 0 else "fail"
    src = newest_zip(automesh_out, status)

    progress(3, 5, "normalizando evidencia")
    final_dir = stage / f"allmesh {stamp} {status}"
    final_dir.mkdir(parents=True, exist_ok=True)
    report["status"] = "PASS" if status == "result" else "FAIL"
    report["automesh_returncode"] = p["returncode"]
    report["automesh_zip"] = str(src) if src else None
    if src and src.exists():
        report["automesh_sha256"] = sha256(src)
        shutil.copy2(src, final_dir / src.name)
    else:
        (final_dir / "ERROR.txt").write_text("AutoMesh did not produce expected zip. See smart_allmesh.log.\n", encoding="utf-8")
    (final_dir / "SMART_ALLMESH_REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (final_dir / "SMART_ALLMESH_REPORT.md").write_text(
        "# Smart AllMesh\n\n"
        f"- Status: `{report['status']}`\n"
        f"- Surface: `{args.surface}`\n"
        f"- Intent: `{args.intent}`\n"
        f"- Repo: `{repo}`\n\n"
        "## Task\n\n"
        f"{task}\n",
        encoding="utf-8",
    )
    shutil.copy2(log_path, final_dir / "smart_allmesh.log")
    progress(4, 5, "empaquetando zip final")
    final_zip = out_root / f"allmesh {stamp} {status}.zip"
    zip_dir(final_dir, final_zip)
    progress(5, 5, "listo")
    print((f"FINAL_RESULT_ZIP={final_zip}" if status == "result" else f"FINAL_FAIL_ZIP={final_zip}"), flush=True)
    return 0 if status == "result" else 1


if __name__ == "__main__":
    raise SystemExit(main())
