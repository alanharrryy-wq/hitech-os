#!/usr/bin/env python3
"""Revalidate a previously composed PRISMA Authority Mesh against a newer Git HEAD.

The revalidator is deliberately bounded: it never discovers or promotes new authority.
It proves whether movement since the last authority snapshot intersects task-bound
authority, protected directories, visual layer bindings, or global trust anchors.
Unrelated movement may be rebound to the current HEAD; relevant or unprovable movement
fails closed and requests a full fresh Mesh.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import stat
import subprocess
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

SCHEMA = "prisma.authority_mesh.revalidation.v2"
PASS_NO_RELEVANT_DRIFT = "PASS_NO_RELEVANT_DRIFT"
PASS_ALREADY_CURRENT = "PASS_ALREADY_CURRENT"
BLOCK_RELEVANT_DRIFT = "BLOCKED_RELEVANT_DRIFT"
BLOCK_NON_ANCESTOR = "BLOCKED_NON_ANCESTOR_DRIFT"
BLOCK_INVALID_EVIDENCE = "BLOCKED_INVALID_PRIOR_AUTHORITY"

MAX_ZIP_MEMBERS = 20_000
MAX_ZIP_MEMBER_BYTES = 256 * 1024 * 1024
MAX_ZIP_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_COMPRESSION_RATIO = 2_000.0

TRUST_ANCHORS = {
    ".github/workflows/prisma-remote-automesh.yml",
    ".github/workflows/prisma-remote-automesh-revalidate.yml",
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json",
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_DO_NOT_REBUILD_MAP.json",
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_REGISTRATION_INDEX.json",
    "PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json",
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md",
    "PRISMA Factory Ledger/tools/verify_prisma_anti_rework_gate.py",
    "PRISMA Factory Ledger/tools/verify_change_intelligence_capability_gate.py",
    "tools/code-atlas/CODE_ATLAS_NEUTRALITY_CONTRACT.json",
    "tools/code-atlas/CODE_ATLAS_CHANGE_ASSURANCE_CONTRACT.json",
    "tools/code-atlas/src/code_atlas/motors/prisma_mesh_gateway.py",
    "tools/code-atlas/src/code_atlas/motors/prisma_mesh_revalidation.py",
}
VISUAL_SURFACES = {"tablet", "pc", "mobile", "chart_lab", "shared_ui"}


class RevalidationError(RuntimeError):
    pass


def _norm_digest(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    return raw.removeprefix("sha256:")


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _digest_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _git(repo: Path, *args: str, allow: set[int] | None = None) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(
        ["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", timeout=60, check=False,
    )
    allowed = allow if allow is not None else {0}
    if p.returncode not in allowed:
        raise RevalidationError("GIT_FAILED:" + " ".join(args) + ":" + p.stderr.strip()[:500])
    return p


def _git_bytes(repo: Path, *args: str, allow: set[int] | None = None) -> subprocess.CompletedProcess[bytes]:
    p = subprocess.run(
        ["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=60, check=False,
    )
    allowed = allow if allow is not None else {0}
    if p.returncode not in allowed:
        err = p.stderr.decode("utf-8", errors="replace").strip()[:500]
        raise RevalidationError("GIT_FAILED:" + " ".join(args) + ":" + err)
    return p


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _tree(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()


def _safe_rel(value: str) -> str:
    raw = str(value or "").strip()
    if "\\" in raw:
        raise RevalidationError("UNSAFE_REPOSITORY_PATH:" + raw)
    while raw.startswith("./"):
        raw = raw[2:]
    if not raw or raw.startswith("/") or re.match(r"^[A-Za-z]:/", raw):
        raise RevalidationError("UNSAFE_REPOSITORY_PATH:" + raw)
    p = PurePosixPath(raw)
    if any(part in {"", ".", ".."} for part in p.parts):
        raise RevalidationError("UNSAFE_REPOSITORY_PATH:" + raw)
    return p.as_posix()


def _is_under(path: str, prefix: str) -> bool:
    p = path.rstrip("/")
    d = prefix.rstrip("/")
    return p == d or p.startswith(d + "/")


def _validate_zip(z: zipfile.ZipFile, label: str) -> set[str]:
    infos = z.infolist()
    if len(infos) > MAX_ZIP_MEMBERS:
        raise RevalidationError(f"{label}_TOO_MANY_MEMBERS:{len(infos)}")
    total = 0
    seen_raw: set[str] = set()
    seen_norm: set[str] = set()
    files: set[str] = set()
    for info in infos:
        raw = info.filename
        if raw in seen_raw:
            raise RevalidationError(f"{label}_DUPLICATE_MEMBER:{raw}")
        seen_raw.add(raw)
        trimmed = raw[:-1] if raw.endswith("/") else raw
        if not trimmed:
            continue
        try:
            norm = _safe_rel(trimmed)
        except RevalidationError as exc:
            raise RevalidationError(f"{label}_UNSAFE_MEMBER:{raw}") from exc
        if norm in seen_norm:
            raise RevalidationError(f"{label}_NORMALIZED_COLLISION:{raw}")
        seen_norm.add(norm)
        mode = (info.external_attr >> 16) & 0xFFFF
        if mode and stat.S_ISLNK(mode):
            raise RevalidationError(f"{label}_SYMLINK_MEMBER:{raw}")
        if info.is_dir():
            continue
        if info.file_size < 0 or info.file_size > MAX_ZIP_MEMBER_BYTES:
            raise RevalidationError(f"{label}_MEMBER_SIZE:{raw}:{info.file_size}")
        total += info.file_size
        if total > MAX_ZIP_TOTAL_BYTES:
            raise RevalidationError(f"{label}_TOTAL_SIZE:{total}")
        if info.compress_size == 0:
            if info.file_size > 0:
                raise RevalidationError(f"{label}_INVALID_COMPRESSION:{raw}")
        else:
            ratio = info.file_size / info.compress_size
            if ratio > MAX_COMPRESSION_RATIO:
                raise RevalidationError(f"{label}_COMPRESSION_RATIO:{raw}:{ratio:.1f}")
        files.add(norm)
    return files


def _load_json(z: zipfile.ZipFile, name: str) -> dict[str, Any]:
    try:
        value = json.loads(z.read(name).decode("utf-8"))
    except Exception as exc:
        raise RevalidationError(f"INVALID_JSON:{name}:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise RevalidationError("JSON_OBJECT_REQUIRED:" + name)
    return value


def _open_artifact(path: Path, expected_digest: str) -> tuple[bytes, str, str, str, str]:
    if not path.is_file():
        raise RevalidationError("ARTIFACT_NOT_FOUND:" + str(path))
    outer_bytes = path.read_bytes()
    outer_sha = _sha_bytes(outer_bytes)
    try:
        outer = zipfile.ZipFile(io.BytesIO(outer_bytes))
    except zipfile.BadZipFile as exc:
        raise RevalidationError("ARTIFACT_NOT_ZIP") from exc
    outer_files = _validate_zip(outer, "OUTER_ARTIFACT")
    candidates = [n for n in ("prisma-automesh-composed-result.zip", "prisma-automesh-revalidated-result.zip") if n in outer_files]
    direct = {"PRISMA_MESH_GATEWAY_REPORT.json", "MANIFEST.json"}.issubset(outer_files)
    if len(candidates) > 1 or (candidates and direct):
        raise RevalidationError("AMBIGUOUS_AUTHORITY_ARTIFACT")
    if candidates:
        authority_name = candidates[0]
        composed_bytes = outer.read(authority_name)
    elif direct:
        authority_name = "direct"
        composed_bytes = outer_bytes
    else:
        raise RevalidationError("COMPOSED_AUTHORITY_NOT_FOUND_IN_ARTIFACT")
    composed_sha = _sha_bytes(composed_bytes)
    expected = _norm_digest(expected_digest)
    if not expected:
        raise RevalidationError("EXPECTED_ARTIFACT_DIGEST_REQUIRED")
    if expected == outer_sha:
        matched = "outer"
    elif expected == composed_sha:
        matched = "authority"
    else:
        raise RevalidationError(f"ARTIFACT_DIGEST_MISMATCH:{expected}:{outer_sha}:{composed_sha}")
    return composed_bytes, outer_sha, composed_sha, matched, authority_name


def _verify_composed(composed_bytes: bytes) -> tuple[zipfile.ZipFile, dict[str, Any], dict[str, Any], dict[str, Any]]:
    try:
        z = zipfile.ZipFile(io.BytesIO(composed_bytes))
    except zipfile.BadZipFile as exc:
        raise RevalidationError("COMPOSED_ARTIFACT_NOT_ZIP") from exc
    files = _validate_zip(z, "COMPOSED_ARTIFACT")
    for required in ("MANIFEST.json", "PRISMA_MESH_GATEWAY_REPORT.json", "authority/normalized_request.json"):
        if required not in files:
            raise RevalidationError("COMPOSED_REQUIRED_FILE_MISSING:" + required)
    manifest = _load_json(z, "MANIFEST.json")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise RevalidationError("COMPOSED_MANIFEST_FILES_REQUIRED")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RevalidationError("COMPOSED_MANIFEST_ROW_INVALID")
        name = _safe_rel(str(row.get("path") or ""))
        if name in seen:
            raise RevalidationError("COMPOSED_MANIFEST_DUPLICATE:" + name)
        seen.add(name)
        if name not in files:
            raise RevalidationError("COMPOSED_MANIFEST_FILE_MISSING:" + name)
        data = z.read(name)
        if row.get("sha256") != _sha_bytes(data):
            raise RevalidationError("COMPOSED_MANIFEST_HASH_MISMATCH:" + name)
        if row.get("bytes") != len(data):
            raise RevalidationError("COMPOSED_MANIFEST_SIZE_MISMATCH:" + name)
    unmanifested = sorted(files - seen - {"MANIFEST.json"})
    if unmanifested:
        raise RevalidationError("COMPOSED_UNMANIFESTED_FILE:" + unmanifested[0])
    report = _load_json(z, "PRISMA_MESH_GATEWAY_REPORT.json")
    request = _load_json(z, "authority/normalized_request.json")
    if manifest.get("report") not in (None, report):
        raise RevalidationError("COMPOSED_MANIFEST_REPORT_MISMATCH")
    if report.get("status") != "PASS_COMPOSED_AUTHORITY_MESH":
        raise RevalidationError("PRIOR_MESH_NOT_PASS")
    if report.get("requestDigest") != request.get("requestDigest"):
        raise RevalidationError("PRIOR_REQUEST_DIGEST_MISMATCH")
    if report.get("repoHead") != request.get("expectedHead"):
        revalidation_name = "PRISMA_MESH_REVALIDATION.json"
        if revalidation_name not in files:
            raise RevalidationError("PRIOR_HEAD_REQUEST_MISMATCH")
        revalidation = _load_json(z, revalidation_name)
        recorded_digest = str(revalidation.get("revalidationDigest") or "")
        digest_input = dict(revalidation)
        digest_input.pop("revalidationDigest", None)
        valid_chain = (
            report.get("authorityReusePolicy") == "REVALIDATED_RELEVANT_DRIFT_NOT_STALE_REUSE"
            and report.get("revalidationStatus") in {PASS_NO_RELEVANT_DRIFT, PASS_ALREADY_CURRENT}
            and report.get("revalidationCurrentHead") == report.get("repoHead")
            and revalidation.get("currentHead") == report.get("repoHead")
            and revalidation.get("status") == report.get("revalidationStatus")
            and bool(recorded_digest)
            and recorded_digest == report.get("revalidationDigest")
            and _digest_json(digest_input) == recorded_digest
            and report.get("fullMeshRerun") is False
            and report.get("readOnly") is True
            and report.get("productionCertified") is False
            and revalidation.get("readOnly") is True
            and revalidation.get("productionCertified") is False
        )
        if not valid_chain:
            raise RevalidationError("PRIOR_REVALIDATION_CHAIN_INVALID")
    return z, manifest, report, request


def _walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)


def _collect_binding(z: zipfile.ZipFile, request: dict[str, Any]) -> dict[str, Any]:
    exact: set[str] = set(TRUST_ANCHORS)
    prefixes: set[str] = set()
    pinned: dict[str, str] = {}
    sources: dict[str, set[str]] = {}

    def exact_add(path: str, source: str, sha: str | None = None) -> None:
        try:
            rel = _safe_rel(path)
        except RevalidationError:
            return
        exact.add(rel)
        sources.setdefault(rel, set()).add(source)
        if sha:
            old = pinned.get(rel)
            if old and old.lower() != sha.lower():
                raise RevalidationError("CONTRADICTORY_PINNED_HASH:" + rel)
            pinned[rel] = sha.lower()

    def prefix_add(path: str, source: str) -> None:
        try:
            rel = _safe_rel(path).rstrip("/")
        except RevalidationError:
            return
        prefixes.add(rel)
        sources.setdefault(rel + "/", set()).add(source)

    for p in TRUST_ANCHORS:
        sources.setdefault(p, set()).add("trust-anchor")

    tasks = request.get("tasks") if isinstance(request.get("tasks"), list) else []
    visual = False
    for task in tasks:
        if not isinstance(task, dict):
            continue
        surface = str(task.get("surface") or "")
        domain = str(task.get("domain") or "")
        visual = visual or surface in VISUAL_SURFACES or domain == "visual"
        for p in task.get("requiredAuthorities") or []:
            if isinstance(p, str):
                exact_add(p, "normalized-request:required-authority")
        for p in task.get("requiredDirectories") or []:
            if isinstance(p, str):
                prefix_add(p, "normalized-request:required-directory")

    lane_names = sorted(n for n in z.namelist() if re.fullmatch(r"authority/lanes/[^/]+/AUTHORITY_READSET\.lock\.json", n))
    if not lane_names:
        raise RevalidationError("AUTHORITY_LANE_READSETS_MISSING")
    for name in lane_names:
        lane = _load_json(z, name)
        for p in lane.get("requiredAuthorities") or []:
            if isinstance(p, str):
                exact_add(p, "neutral-readset:required-authority")
        for p in lane.get("requiredDirectories") or []:
            if isinstance(p, str):
                prefix_add(p, "neutral-readset:required-directory")
        for row in lane.get("selected_files") or []:
            if not isinstance(row, dict):
                continue
            if row.get("state") == "SUPPORTED" and row.get("path"):
                exact_add(str(row["path"]), "neutral-readset:supported", str(row.get("sha256") or "") or None)

    names = set(z.namelist())
    legacy_present = "legacy_surface_mesh.zip" in names
    layer_map_present = False
    if visual and not legacy_present:
        raise RevalidationError("VISUAL_LEGACY_SURFACE_MESH_MISSING")
    if legacy_present:
        try:
            legacy = zipfile.ZipFile(io.BytesIO(z.read("legacy_surface_mesh.zip")))
        except zipfile.BadZipFile as exc:
            raise RevalidationError("LEGACY_SURFACE_MESH_INVALID") from exc
        _validate_zip(legacy, "LEGACY_SURFACE_MESH")
        for name in legacy.namelist():
            if not name.endswith("authority_mesh/.governance/current/AUTHORITY_READSET.lock.json"):
                continue
            row = _load_json(legacy, name)
            for p in row.get("explicit_existing_paths") or []:
                if isinstance(p, str):
                    exact_add(p, "legacy-readset:explicit")
            for p in row.get("missing_expected_authority_files") or []:
                if isinstance(p, str):
                    exact_add(p, "legacy-readset:missing-expected")
            visual = visual or bool(row.get("layer_map_required") and str(row.get("surface_argument") or "") in VISUAL_SURFACES)
        if visual:
            layer_names = sorted(n for n in legacy.namelist() if n.endswith("authority_mesh/reports/LAYERS_MAP.json"))
            if not layer_names:
                raise RevalidationError("VISUAL_LAYER_MAP_MISSING")
            layer_map_present = True
            for lname in layer_names:
                layer = _load_json(legacy, lname)
                for value in _walk_strings(layer):
                    if "/" not in value or len(value) > 500:
                        continue
                    cleaned = value.split("#", 1)[0].strip()
                    if not cleaned or cleaned.startswith(("http://", "https://", "/")):
                        continue
                    try:
                        rel = _safe_rel(cleaned)
                    except RevalidationError:
                        continue
                    if re.search(r"\.(?:tsx?|jsx?|css|scss|json|md|prisma|mjs|cjs|py|yml|yaml)$", rel, re.I):
                        exact_add(rel, "visual-layer-map")
    if visual and not layer_map_present:
        raise RevalidationError("VISUAL_LAYER_MAP_MISSING")
    return {"exact": exact, "prefixes": prefixes, "pinned": pinned, "sources": sources, "visual": visual, "layerMapPresent": layer_map_present}


def _changed_paths(repo: Path, base: str, head: str) -> list[str]:
    p = _git(repo, "diff", "--name-status", "-z", "--find-renames", f"{base}..{head}")
    parts = p.stdout.split("\0")
    out: list[str] = []
    i = 0
    while i < len(parts) and parts[i]:
        status_code = parts[i]
        i += 1
        if status_code.startswith(("R", "C")):
            if i + 1 >= len(parts):
                raise RevalidationError("GIT_DIFF_PARSE_ERROR")
            out.extend([_safe_rel(parts[i]), _safe_rel(parts[i + 1])])
            i += 2
        else:
            if i >= len(parts):
                raise RevalidationError("GIT_DIFF_PARSE_ERROR")
            out.append(_safe_rel(parts[i]))
            i += 1
    return sorted(set(out))


def _relevant(paths: list[str], binding: dict[str, Any]) -> tuple[list[str], dict[str, list[str]]]:
    reasons: dict[str, list[str]] = {}
    exact: set[str] = binding["exact"]
    prefixes: set[str] = binding["prefixes"]
    sources: dict[str, set[str]] = binding["sources"]
    for path in paths:
        why: set[str] = set()
        if path in exact:
            why.update(sources.get(path) or {"exact-authority-binding"})
        for prefix in prefixes:
            if _is_under(path, prefix):
                why.update(sources.get(prefix + "/") or {f"required-directory:{prefix}"})
        if why:
            reasons[path] = sorted(why)
    return sorted(reasons), reasons


def _git_blob_sha256(repo: Path, head: str, rel: str) -> tuple[str | None, str | None]:
    tree = _git(repo, "ls-tree", "-z", head, "--", rel)
    raw = tree.stdout
    if not raw:
        return None, "MISSING"
    entry = raw.split("\0", 1)[0]
    meta, sep, path = entry.partition("\t")
    if not sep or path != rel:
        return None, "UNEXPECTED_TREE_ENTRY"
    bits = meta.split()
    if len(bits) != 3 or bits[1] != "blob":
        return None, "NOT_BLOB"
    data = _git_bytes(repo, "cat-file", "blob", bits[2]).stdout
    return _sha_bytes(data), None


def _hash_mismatches(repo: Path, pinned: dict[str, str], head: str) -> tuple[list[dict[str, str]], int]:
    mismatches: list[dict[str, str]] = []
    checked = 0
    for rel, expected in sorted(pinned.items()):
        checked += 1
        actual, reason = _git_blob_sha256(repo, head, rel)
        if reason:
            mismatches.append({"path": rel, "reason": reason, "expected": expected, "actual": actual or ""})
        elif actual and actual.lower() != expected.lower():
            mismatches.append({"path": rel, "reason": "HASH_MISMATCH", "expected": expected, "actual": actual})
    return mismatches, checked


def _fallback_request(request: dict[str, Any], current_head: str) -> dict[str, Any]:
    out = json.loads(json.dumps(request))
    out.pop("requestDigest", None)
    out["schemaVersion"] = "v2"
    out["expectedHead"] = current_head
    return out


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_revalidated_zip(composed: zipfile.ZipFile, prior_report: dict[str, Any], revalidation: dict[str, Any], out_dir: Path) -> Path:
    staging = out_dir / "payload"
    staging.mkdir(parents=True, exist_ok=True)
    for name in composed.namelist():
        if name in {"MANIFEST.json", "PRISMA_MESH_GATEWAY_REPORT.json", "PRIOR_PRISMA_MESH_GATEWAY_REPORT.json", "PRISMA_MESH_REVALIDATION.json"} or name.endswith("/"):
            continue
        target = staging / _safe_rel(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(composed.read(name))
    _write_json(staging / "PRIOR_PRISMA_MESH_GATEWAY_REPORT.json", prior_report)
    _write_json(staging / "PRISMA_MESH_REVALIDATION.json", revalidation)
    report = dict(prior_report)
    report.update({
        "status": "PASS_COMPOSED_AUTHORITY_MESH",
        "repoHead": revalidation["currentHead"],
        "repoTree": revalidation["currentTree"],
        "revalidatedFromHead": revalidation["baseHead"],
        "revalidationCurrentHead": revalidation["currentHead"],
        "revalidationStatus": revalidation["status"],
        "revalidationDigest": revalidation["revalidationDigest"],
        "priorComposedArtifactSha256": revalidation["priorComposedArtifactSha256"],
        "requiredAuthorityCoveragePct": 100,
        "blockers": 0,
        "layerMapPresent": bool(revalidation["visualLayerMapPresent"]),
        "fullMeshRerun": False,
        "authorityReusePolicy": "REVALIDATED_RELEVANT_DRIFT_NOT_STALE_REUSE",
        "readOnly": True,
        "productionCertified": False,
    })
    _write_json(staging / "PRISMA_MESH_GATEWAY_REPORT.json", report)
    rows = []
    for path in sorted(p for p in staging.rglob("*") if p.is_file()):
        rows.append({"path": path.relative_to(staging).as_posix(), "sha256": _sha_file(path), "bytes": path.stat().st_size})
    _write_json(staging / "MANIFEST.json", {"report": report, "files": rows})
    final = out_dir / "prisma-automesh-revalidated-result.zip"
    with zipfile.ZipFile(final, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(p for p in staging.rglob("*") if p.is_file()):
            z.write(path, path.relative_to(staging).as_posix())
    return final


def revalidate(repo: Path, artifact: Path, out_dir: Path, expected_artifact_sha256: str) -> dict[str, Any]:
    started = time.perf_counter()
    repo = repo.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    current = _head(repo)
    current_tree = _tree(repo)
    try:
        composed_bytes, outer_sha, composed_sha, digest_match, authority_name = _open_artifact(artifact, expected_artifact_sha256)
        composed, _manifest, prior, request = _verify_composed(composed_bytes)
        base = str(prior.get("repoHead") or "").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{40}", base):
            raise RevalidationError("PRIOR_BASE_HEAD_INVALID:" + base)
        binding = _collect_binding(composed, request)
        cat = _git(repo, "cat-file", "-e", f"{base}^{{commit}}", allow={0, 1, 128})
        base_exists = cat.returncode == 0
        ancestor = False
        changed: list[str] = []
        relevant: list[str] = []
        reasons: dict[str, list[str]] = {}
        hash_mismatches: list[dict[str, str]] = []
        hash_checked = 0
        if base_exists:
            anc = _git(repo, "merge-base", "--is-ancestor", base, current, allow={0, 1})
            ancestor = anc.returncode == 0
        if base == current:
            status_value = PASS_ALREADY_CURRENT
            ancestor = True
        elif not base_exists or not ancestor:
            status_value = BLOCK_NON_ANCESTOR
        else:
            changed = _changed_paths(repo, base, current)
            relevant, reasons = _relevant(changed, binding)
            hash_mismatches, hash_checked = _hash_mismatches(repo, binding["pinned"], current)
            for row in hash_mismatches:
                path = row["path"]
                reasons.setdefault(path, []).append("pinned-hash-mismatch:" + row["reason"])
                if path not in relevant:
                    relevant.append(path)
            relevant = sorted(set(relevant))
            reasons = {k: sorted(set(v)) for k, v in sorted(reasons.items())}
            status_value = PASS_NO_RELEVANT_DRIFT if not relevant else BLOCK_RELEVANT_DRIFT
        can_fallback = status_value in {BLOCK_RELEVANT_DRIFT, BLOCK_NON_ANCESTOR}
        report = {
            "schemaVersion": SCHEMA,
            "status": status_value,
            "baseHead": base,
            "currentHead": current,
            "baseTree": prior.get("repoTree"),
            "currentTree": current_tree,
            "requestDigest": prior.get("requestDigest"),
            "priorOuterArtifactSha256": outer_sha,
            "priorComposedArtifactSha256": composed_sha,
            "priorAuthorityMember": authority_name,
            "expectedArtifactDigestMatchedAs": digest_match,
            "baseCommitAvailable": base_exists,
            "baseIsAncestorOfCurrent": ancestor,
            "changedPaths": changed,
            "changedCount": len(changed),
            "relevantChangedPaths": sorted(relevant),
            "relevantChangedCount": len(relevant),
            "relevanceReasons": reasons,
            "sensitiveExactPathCount": len(binding["exact"]),
            "sensitiveDirectoryPrefixCount": len(binding["prefixes"]),
            "pinnedHashCount": len(binding["pinned"]),
            "pinnedHashChecked": hash_checked,
            "pinnedHashMismatches": hash_mismatches,
            "pinnedHashSource": "git-object-database",
            "visualTask": bool(binding["visual"]),
            "visualLayerMapPresent": bool(binding["visual"] is False or binding["layerMapPresent"]),
            "fullMeshRerunRequired": status_value in {BLOCK_RELEVANT_DRIFT, BLOCK_NON_ANCESTOR},
            "canFallbackFullMesh": can_fallback,
            "readOnly": True,
            "productionCertified": False,
            "candidateRetrievalIsAuthority": False,
            "policy": "MAIN_MOVEMENT_TRIGGERS_RELEVANT_DRIFT_EVALUATION_NOT_UNCONDITIONAL_AUTHORITY_DESTRUCTION",
        }
        report["revalidationDigest"] = _digest_json(report)
        _write_json(out_dir / "PRISMA_MESH_REVALIDATION.json", report)
        if status_value == PASS_ALREADY_CURRENT:
            final = out_dir / "prisma-automesh-revalidated-result.zip"
            final.write_bytes(composed_bytes)
            report["artifactReuse"] = "VALIDATED_AUTHORITY_BYTES_NO_REPACK"
            report["artifact"] = str(final)
            report["artifactSha256"] = _sha_file(final)
        elif status_value == PASS_NO_RELEVANT_DRIFT:
            final = _build_revalidated_zip(composed, prior, report, out_dir)
            report["artifactReuse"] = "REBOUND_WITH_NEW_ATTESTATION"
            report["artifact"] = str(final)
            report["artifactSha256"] = _sha_file(final)
        elif can_fallback:
            _write_json(out_dir / "fallback_request.json", _fallback_request(request, current))
        report["elapsedMs"] = round((time.perf_counter() - started) * 1000, 3)
        _write_json(out_dir / "PRISMA_MESH_REVALIDATION.json", report)
        return report
    except RevalidationError as exc:
        report = {
            "schemaVersion": SCHEMA,
            "status": BLOCK_INVALID_EVIDENCE,
            "currentHead": current,
            "currentTree": current_tree,
            "error": str(exc),
            "fullMeshRerunRequired": True,
            "canFallbackFullMesh": False,
            "readOnly": True,
            "productionCertified": False,
            "candidateRetrievalIsAuthority": False,
            "elapsedMs": round((time.perf_counter() - started) * 1000, 3),
        }
        report["revalidationDigest"] = _digest_json(report)
        _write_json(out_dir / "PRISMA_MESH_REVALIDATION.json", report)
        return report


def _main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--expected-artifact-sha256", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = revalidate(Path(args.repo), Path(args.artifact), Path(args.out), args.expected_artifact_sha256)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result.get("status") in {PASS_NO_RELEVANT_DRIFT, PASS_ALREADY_CURRENT}:
        return 0
    if result.get("canFallbackFullMesh"):
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(_main())
