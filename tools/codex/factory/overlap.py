from __future__ import annotations

import fnmatch
import hashlib
import re
from collections import defaultdict
from typing import Any

from .common import WORKERS, read_json
from .contracts import bundle_dir
from .path_guard import PathGuardError, PathIssue, canonical_path_key, detect_scope_violations_for_paths, normalize_rel_path


def _load_worker_changes(run_id: str, worker: str) -> list[dict[str, Any]]:
    path = bundle_dir(run_id, worker) / "FILES_CHANGED.json"
    if not path.exists():
        return []
    payload = read_json(path)
    changes = [entry for entry in payload.get("changes", []) if isinstance(entry, dict)]
    normalized: list[dict[str, Any]] = []
    for entry in changes:
        raw_path = str(entry.get("path", ""))
        try:
            path_key = normalize_rel_path(raw_path)
        except PathGuardError:
            path_key = raw_path.strip()
        normalized.append(
            {
                "path": path_key,
                "change_type": str(entry.get("change_type", "modified")),
                "reason": str(entry.get("reason", "")),
                "sha256": str(entry.get("sha256", "")),
            }
        )
    normalized.sort(key=lambda entry: (str(entry.get("path", "")), str(entry.get("change_type", ""))))
    return normalized


def _load_worker_diff(run_id: str, worker: str) -> str:
    path = bundle_dir(run_id, worker) / "DIFF.patch"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _load_scope_lock(run_id: str, worker: str) -> dict[str, Any]:
    path = bundle_dir(run_id, worker) / "SCOPE_LOCK.json"
    if not path.exists():
        return {
            "worker_id": worker,
            "allowed_globs": [],
            "blocked_globs": [],
            "allow_shared_paths": [],
        }
    return read_json(path)


PATCH_PATH_RE = re.compile(r"^(?:\+\+\+ b/|--- a/)(.+)$")


def _extract_patch_paths(diff_text: str) -> list[str]:
    paths: set[str] = set()
    for line in diff_text.splitlines():
        match = PATCH_PATH_RE.match(line.strip())
        if not match:
            continue
        raw = match.group(1).strip()
        if raw == "/dev/null":
            continue
        try:
            paths.add(normalize_rel_path(raw))
        except PathGuardError:
            continue
    return sorted(paths)


def detect_file_overlaps(
    run_id: str,
    workers: list[str] | None = None,
    *,
    strict_mode: bool = True,
    allow_identical_patch_overlap: bool = False,
) -> dict[str, Any]:
    chosen = list(workers or WORKERS)
    owners: dict[str, list[dict[str, Any]]] = defaultdict(list)
    scope_locks = {worker: _load_scope_lock(run_id, worker) for worker in chosen}
    hidden_overlaps: list[dict[str, Any]] = []
    invalid_paths: list[dict[str, Any]] = []
    patch_hashes: dict[str, str] = {}

    for worker in chosen:
        changes = _load_worker_changes(run_id, worker)
        declared_paths: set[str] = set()
        for entry in changes:
            raw_path = str(entry.get("path", "")).strip()
            if not raw_path:
                continue
            try:
                path = normalize_rel_path(raw_path)
            except PathGuardError as exc:
                invalid_paths.append({"worker": worker, "path": raw_path, "reason": str(exc)})
                continue
            declared_paths.add(path)
            owners[path].append({"worker": worker, "entry": entry})

        diff_text = _load_worker_diff(run_id, worker)
        patch_hashes[worker] = hashlib.sha256(diff_text.encode("utf-8")).hexdigest() if diff_text else ""
        patch_paths = _extract_patch_paths(diff_text)
        for patch_path in patch_paths:
            if patch_path not in declared_paths:
                hidden_overlaps.append(
                    {
                        "worker": worker,
                        "path": patch_path,
                        "reason": "path present in DIFF.patch but missing from FILES_CHANGED",
                    }
                )
            owners[patch_path].append({"worker": worker, "entry": {"path": patch_path, "source": "DIFF.patch"}})

    overlaps: list[dict[str, Any]] = []
    for path, entries in sorted(owners.items()):
        workers_touching = sorted({str(item["worker"]) for item in entries})
        if len(workers_touching) <= 1:
            continue

        shared_allowed = True
        reasons: list[str] = []
        for item in entries:
            lock = scope_locks.get(item["worker"], {})
            allow_shared = set(lock.get("allow_shared_paths", []))
            if path not in allow_shared:
                shared_allowed = False
            blocked_globs = lock.get("blocked_globs", [])
            if any(fnmatch.fnmatch(path, glob) for glob in blocked_globs):
                reasons.append(f"{item['worker']} blocked by scope rule")

        overlap_patch_hashes = sorted({patch_hashes.get(worker, "") for worker in workers_touching if patch_hashes.get(worker, "")})
        identical_patch = len(overlap_patch_hashes) == 1 and len(overlap_patch_hashes[0]) == 64

        if allow_identical_patch_overlap and identical_patch:
            status = "WARN"
            reasons.append("identical_patch_exception")
        elif strict_mode:
            status = "BLOCKED"
        else:
            status = "WARN" if shared_allowed else "BLOCKED"

        overlaps.append(
            {
                "path": path,
                "workers": workers_touching,
                "status": status,
                "reasons": sorted(set(reasons)),
                "identical_patch": identical_patch,
            }
        )

    overlaps.sort(key=lambda entry: (str(entry.get("path", "")), ",".join(entry.get("workers", []))))
    blocked = [entry for entry in overlaps if entry["status"] == "BLOCKED"]
    hidden_overlaps.sort(key=lambda entry: (str(entry.get("path", "")), str(entry.get("worker", ""))))
    invalid_paths.sort(key=lambda entry: (str(entry.get("path", "")), str(entry.get("worker", ""))))
    if hidden_overlaps:
        blocked.extend([{"path": item["path"], "workers": [item["worker"]], "status": "BLOCKED"} for item in hidden_overlaps])
    if invalid_paths:
        blocked.extend([{"path": item["path"], "workers": [item["worker"]], "status": "BLOCKED"} for item in invalid_paths])
    return {
        "run_id": run_id,
        "status": "PASS" if not blocked else "BLOCKED",
        "overlaps": overlaps,
        "hidden_overlaps": hidden_overlaps,
        "invalid_paths": invalid_paths,
        "blocked": len(blocked),
        "strict_mode": bool(strict_mode),
        "allow_identical_patch_overlap": bool(allow_identical_patch_overlap),
    }


def detect_scope_violations(run_id: str, workers: list[str] | None = None) -> dict[str, Any]:
    chosen = list(workers or WORKERS)
    violations: list[dict[str, Any]] = []

    for worker in chosen:
        lock = _load_scope_lock(run_id, worker)
        allowed = list(lock.get("allowed_globs", []))
        blocked_globs = list(lock.get("blocked_globs", []))
        entries = _load_worker_changes(run_id, worker)
        paths = [str(change.get("path", "")) for change in entries if str(change.get("path", "")).strip()]
        scoped_violations = detect_scope_violations_for_paths(
            worker=worker,
            paths=paths,
            allow_globs=allowed,
            deny_globs=blocked_globs,
            enforce_protected=True,
        )
        for item in scoped_violations:
            rule = "allowed_globs"
            detail = item.reason
            if "denylist" in item.reason:
                rule = "blocked_globs"
            if "protected" in item.reason:
                rule = "protected_paths"
            violations.append(
                {
                    "worker": worker,
                    "path": item.path,
                    "rule": rule,
                    "detail": detail,
                }
            )

    violations.sort(key=lambda item: (str(item.get("path", "")), str(item.get("worker", "")), str(item.get("rule", ""))))
    return {
        "run_id": run_id,
        "status": "PASS" if not violations else "BLOCKED",
        "violations": violations,
        "blocked": len(violations),
    }
