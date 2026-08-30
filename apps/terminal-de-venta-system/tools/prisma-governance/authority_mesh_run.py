#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canonical PRISMA Authority Mesh runner.

Wraps the GovMesh3 engine with two operational guarantees that the raw engine
intentionally does not own:

1. The task output directory is clean before generation, so stale governance
   artifacts can never masquerade as current evidence.
2. Visual/full preflights include a task-scoped snapshot of the tracked
   canonical Layer Map, including provenance and SHA-256 metadata.

The underlying ``authority_mesh.py`` remains the read-mostly analysis engine.
This file is the canonical human/automation entrypoint.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import authority_mesh as engine

CORE_REQUIRED = (
    "AUTHORITY_READSET.lock.json",
    "APP_IMPACT_MATRIX.md",
    "CONTRACT_AND_GATE_MATRIX.json",
    "MISSING_OR_UNMAPPED_RISK.md",
    "AGENT_PROMPT_ENVELOPE.md",
    "AUTHORITY_MESH_REPORT.md",
)

LAYER_REQUIRED = (
    "LAYERS_MAP.json",
    "LAYERS_MAP.md",
    "LAYERS_MAP_SOURCE.json",
)

LAYER_SOURCES = (
    ("docs/visual-layer-map/layer-map.json", "LAYERS_MAP.json"),
    ("docs/visual-layer-map/LAYER_MAP.md", "LAYERS_MAP.md"),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(repo: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _is_descendant(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def clean_output(repo: Path, outdir: Path) -> None:
    """Remove only a governance output directory inside the discovered repo."""
    repo = repo.resolve()
    outdir = outdir.resolve()
    if not _is_descendant(outdir, repo):
        raise RuntimeError(f"refusing to clean output outside repo: {outdir}")
    rel = outdir.relative_to(repo)
    if ".governance" not in rel.parts:
        raise RuntimeError(f"refusing to clean non-governance output: {rel.as_posix()}")
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)


def visual_required(outdir: Path, full: bool) -> bool:
    if full:
        return True
    path = outdir / "VISUAL_CAPABILITY_MATRIX.json"
    if not path.is_file():
        return False
    try:
        return bool(json.loads(path.read_text(encoding="utf-8")).get("visual_required"))
    except Exception:
        return False


def snapshot_layer_map(repo: Path, outdir: Path, task: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for source_rel, target_name in LAYER_SOURCES:
        source = repo / source_rel
        if not source.is_file():
            raise RuntimeError(f"canonical Layer Map source missing: {source_rel}")
        target = outdir / target_name
        shutil.copy2(source, target)
        records.append(
            {
                "source": source_rel,
                "snapshot": target_name,
                "bytes": source.stat().st_size,
                "sha256": sha256_file(source),
            }
        )
    meta = {
        "schema": "prisma.authority-mesh.layer-map-snapshot.v2",
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "task": task,
        "taskScoped": True,
        "sourceCommit": git_head(repo),
        "policy": (
            "Visual/full Authority Mesh runs snapshot the tracked canonical Layer Map "
            "after a clean output reset. Stale .governance/current files are forbidden."
        ),
        "files": records,
    }
    (outdir / "LAYERS_MAP_SOURCE.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return meta


def add_runner_gates(outdir: Path, layer_snapshot: dict[str, Any] | None) -> None:
    matrix_path = outdir / "CONTRACT_AND_GATE_MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    gates = matrix.setdefault("required_gates", [])
    for gate in ("clean_authority_output_required", "no_stale_governance_residue"):
        if gate not in gates:
            gates.append(gate)
    if layer_snapshot:
        for gate in ("layer_map_snapshot_required", "layer_map_provenance_required"):
            if gate not in gates:
                gates.append(gate)
        matrix["layer_map_snapshot"] = layer_snapshot
    matrix_path.write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lock_path = outdir / "AUTHORITY_READSET.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["runner"] = {
        "entrypoint": "tools/prisma-governance/authority_mesh_run.py",
        "cleanOutput": True,
        "staleGovernanceAccepted": False,
        "layerMapSnapshot": layer_snapshot,
    }
    lock_path.write_text(
        json.dumps(lock, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def append_report(outdir: Path, layer_snapshot: dict[str, Any] | None) -> None:
    report = outdir / "AUTHORITY_MESH_REPORT.md"
    with report.open("a", encoding="utf-8") as stream:
        stream.write("\n## Canonical runner guarantees\n\n")
        stream.write("- Output workspace cleaned before generation: `yes`\n")
        stream.write("- Stale governance residue accepted: `no`\n")
        if layer_snapshot:
            stream.write("- Task-scoped Layer Map snapshot: `yes`\n")
            stream.write(f"- Layer Map source commit: `{layer_snapshot.get('sourceCommit')}`\n")
            stream.write("- LAYERS_MAP.json\n- LAYERS_MAP.md\n- LAYERS_MAP_SOURCE.json\n")
        else:
            stream.write("- Task-scoped Layer Map snapshot: `not required for non-visual run`\n")


def verify(outdir: Path, require_layers: bool) -> list[str]:
    missing = [
        name
        for name in CORE_REQUIRED
        if not (outdir / name).is_file() or (outdir / name).stat().st_size == 0
    ]
    if require_layers:
        missing.extend(
            name
            for name in LAYER_REQUIRED
            if not (outdir / name).is_file() or (outdir / name).stat().st_size == 0
        )
    return sorted(set(missing))


def wrapper_selftest() -> int:
    engine_code = engine.selftest()
    if engine_code != 0:
        return engine_code
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        outdir = repo / ".governance" / "current"
        layer_dir = repo / "docs" / "visual-layer-map"
        layer_dir.mkdir(parents=True)
        (layer_dir / "layer-map.json").write_text('{"schema":"test"}\n', encoding="utf-8")
        (layer_dir / "LAYER_MAP.md").write_text("# test\n", encoding="utf-8")
        outdir.mkdir(parents=True)
        (outdir / "STALE.txt").write_text("stale", encoding="utf-8")
        clean_output(repo, outdir)
        assert not (outdir / "STALE.txt").exists()
        meta = snapshot_layer_map(repo, outdir, "selftest visual")
        assert meta["taskScoped"] is True
        assert (outdir / "LAYERS_MAP.json").is_file()
        assert (outdir / "LAYERS_MAP_SOURCE.json").is_file()
    print("AUTHORITY_MESH_RUNNER_SELFTEST_OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical PRISMA Authority Mesh runner")
    parser.add_argument("--task", default="GLOBAL ALL APPS ALL SURFACES AUTHORITY PREFLIGHT")
    parser.add_argument("--repo", default="")
    parser.add_argument("--output", default=".governance/current")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--rules", default="")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument(
        "--keep-output",
        action="store_true",
        help="Debug-only: do not clean output first. Canonical runs must not use this flag.",
    )
    ns = parser.parse_args(argv)
    if ns.selftest:
        return wrapper_selftest()

    start = Path(ns.repo) if ns.repo else Path.cwd()
    repo = engine.discover_repo(start)
    rules_path = (
        Path(ns.rules)
        if ns.rules
        else Path(engine.__file__).with_name("authority_mesh_rules.json")
    )
    outdir = Path(ns.output)
    if not outdir.is_absolute():
        outdir = repo / outdir

    if ns.keep_output:
        outdir.mkdir(parents=True, exist_ok=True)
    else:
        clean_output(repo, outdir)

    result = engine.build_outputs(repo, ns.task, outdir, ns.full, rules_path)
    require_layers = visual_required(outdir, ns.full)
    layer_snapshot = snapshot_layer_map(repo, outdir, ns.task) if require_layers else None
    add_runner_gates(outdir, layer_snapshot)
    append_report(outdir, layer_snapshot)
    missing = verify(outdir, require_layers)

    payload = {
        **result,
        "canonicalRunner": True,
        "cleanOutput": not ns.keep_output,
        "layerMapRequired": require_layers,
        "layerMapSnapshot": layer_snapshot,
        "verification": "PASS" if not missing else "FAIL",
        "missingOutputs": missing,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if missing:
        return 3
    return 0 if result["status"] in {
        "PASS",
        "WARN_AUTHORITY_PATTERNS_MISSING",
        "BLOCKED_CRITICAL_AUTHORITY_MISSING",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
