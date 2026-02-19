from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping

SharedMode = Literal["off", "consume", "publish", "both"]
HashStrategy = Literal["none", "sha256"]

MODE_VALUES: tuple[SharedMode, ...] = ("off", "consume", "publish", "both")
HASH_VALUES: tuple[HashStrategy, ...] = ("none", "sha256")
FACTORY_WORKERS: tuple[str, ...] = ("A_worker", "B_worker", "C_worker", "D_worker", "Z_integrator")
LEGACY_WORKER_ALIASES: Mapping[str, str] = {
    "A_worker": "A_core",
    "B_worker": "B_tooling",
    "C_worker": "C_features",
    "D_worker": "D_validation",
    "Z_integrator": "Z_aggregator",
}

DEFAULT_COPY_EXCLUDES: tuple[str, ...] = (
    "node_modules",
    ".git",
    "tools/codex/worktrees",
    "tools/codex/runs",
    ".pnpm-store",
    "dist",
    "build",
)

IMMUTABLE_DEFAULT_NAMES: tuple[str, ...] = ("IMMUTABLE", ".immutable")
IMMUTABLE_DEFAULT_EXTENSIONS: tuple[str, ...] = (".lock", ".immutable")


@dataclass(frozen=True)
class SharedBridgeFlags:
    mode: SharedMode = "off"
    require_current: bool = False
    strict_schema: bool = False
    hash_strategy: HashStrategy = "sha256"
    dry_run: bool = False
    shared_root_override: str = ""


@dataclass(frozen=True)
class ImmutableRules:
    names: frozenset[str]
    extensions: frozenset[str]
    paths: frozenset[str]


def _bool_env(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_shared_flags(env: Mapping[str, str] | None = None) -> SharedBridgeFlags:
    """Parse bridge flags from environment variables with defaults OFF."""
    source = dict(env or os.environ)
    mode_raw = str(source.get("HITECH_SHARED_MODE", "off")).strip().lower() or "off"
    mode: SharedMode = "off" if mode_raw not in MODE_VALUES else mode_raw  # type: ignore[assignment]

    hash_raw = str(source.get("HITECH_SHARED_HASH_STRATEGY", "sha256")).strip().lower() or "sha256"
    hash_strategy: HashStrategy = "sha256" if hash_raw not in HASH_VALUES else hash_raw  # type: ignore[assignment]

    return SharedBridgeFlags(
        mode=mode,
        require_current=_bool_env(source.get("HITECH_SHARED_REQUIRE_CURRENT"), default=False),
        strict_schema=_bool_env(source.get("HITECH_SHARED_STRICT_SCHEMA"), default=False),
        hash_strategy=hash_strategy,
        dry_run=_bool_env(source.get("HITECH_SHARED_DRYRUN"), default=False),
        shared_root_override=str(source.get("HITECH_SHARED_ROOT", "")).strip(),
    )


def discover_repo_root(start: Path | None = None) -> Path:
    """
    Resolve repository root by walking upward until `.git` or `KERNEL_CONTEXT.md` exists.
    """
    current = (start or Path.cwd()).resolve(strict=False)
    if current.is_file():
        current = current.parent

    visited: set[Path] = set()
    while True:
        if current in visited:
            break
        visited.add(current)
        if (current / ".git").exists() or (current / "KERNEL_CONTEXT.md").exists():
            return current
        if current.parent == current:
            break
        current = current.parent

    raise FileNotFoundError("unable to resolve repo root via .git or KERNEL_CONTEXT.md")


def resolve_shared_root(
    repo_root: Path,
    *,
    shared_root_override: str = "",
    env: Mapping[str, str] | None = None,
) -> Path | None:
    """
    Resolve shared root:
    1) <repo_root>/tools/codex/shared
    2) HITECH_SHARED_ROOT override
    3) None
    """
    candidate = (repo_root / "tools" / "codex" / "shared").resolve(strict=False)
    if candidate.exists() and candidate.is_dir():
        return candidate

    effective_override = shared_root_override.strip()
    if not effective_override:
        source = dict(env or os.environ)
        effective_override = str(source.get("HITECH_SHARED_ROOT", "")).strip()
    if not effective_override:
        return None

    override_path = Path(effective_override).expanduser().resolve(strict=False)
    if override_path.exists() and override_path.is_dir():
        return override_path
    return None


def _exists_dir_any_case(root: Path, name: str) -> bool:
    exact = root / name
    lower = root / name.lower()
    return (exact.exists() and exact.is_dir()) or (lower.exists() and lower.is_dir())


def _looks_like_current_run_root(candidate: Path) -> bool:
    return (
        _exists_dir_any_case(candidate, "META")
        and _exists_dir_any_case(candidate, "WORKERS")
        and _exists_dir_any_case(candidate, "HEALTH")
    )


def resolve_shared_current_run_root(
    shared_root: Path | None,
    *,
    require_current: bool = False,
) -> Path | None:
    """
    Resolve shared current run root.
    - prefer shared_root/CURRENT
    - fallback to shared_root itself when run-mounted
    """
    if shared_root is None:
        if require_current:
            raise FileNotFoundError("shared root is not available and current run is required")
        return None

    root = shared_root.resolve(strict=False)
    current = (root / "CURRENT").resolve(strict=False)
    if current.exists() and current.is_dir():
        return current

    if _looks_like_current_run_root(root):
        return root

    if require_current:
        raise FileNotFoundError(
            f"shared current run root not found under {root.as_posix()} (expected CURRENT or run-mounted layout)"
        )
    return None


def _is_reparse_point(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
    except OSError:
        return True
    try:
        data = os.lstat(path)
    except OSError:
        return True
    attrs = int(getattr(data, "st_file_attributes", 0))
    reparse_attr = int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    return bool(reparse_attr and attrs & reparse_attr)


def _normalize_excludes(excludes: Iterable[str] | None) -> tuple[str, ...]:
    values = list(excludes or DEFAULT_COPY_EXCLUDES)
    normalized = []
    for item in values:
        token = str(item).strip().replace("\\", "/").strip("/")
        if token:
            normalized.append(token.lower())
    return tuple(sorted(set(normalized)))


def _is_excluded(rel_path: str, excludes: tuple[str, ...]) -> bool:
    rel = rel_path.strip("/").lower()
    if not rel:
        return False
    parts = tuple(part for part in rel.split("/") if part)
    for token in excludes:
        if "/" in token:
            if rel == token or rel.startswith(token + "/"):
                return True
            continue
        if token in parts:
            return True
    return False


def _iter_files_stable(root: Path, *, excludes: tuple[str, ...]) -> list[Path]:
    if not root.exists() or not root.is_dir():
        return []
    if _is_reparse_point(root):
        return []

    output: list[Path] = []

    def _walk(current_abs: Path, current_rel: Path) -> None:
        try:
            entries = sorted(current_abs.iterdir(), key=lambda entry: entry.name)
        except OSError:
            return

        for entry in entries:
            rel = (current_rel / entry.name) if current_rel.as_posix() != "." else Path(entry.name)
            rel_posix = rel.as_posix()
            if _is_excluded(rel_posix, excludes):
                continue
            if _is_reparse_point(entry):
                continue
            if entry.is_dir():
                _walk(entry, rel)
                continue
            if entry.is_file():
                output.append(rel)

    _walk(root, Path("."))
    output.sort(key=lambda item: item.as_posix())
    return output


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _files_equal(source: Path, target: Path) -> bool:
    if not target.exists() or not target.is_file():
        return False
    if source.stat().st_size != target.stat().st_size:
        return False
    with source.open("rb") as left, target.open("rb") as right:
        while True:
            left_chunk = left.read(1024 * 1024)
            right_chunk = right.read(1024 * 1024)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def _atomic_copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as out_handle, source.open("rb") as in_handle:
            while True:
                chunk = in_handle.read(1024 * 1024)
                if not chunk:
                    break
                out_handle.write(chunk)
        os.replace(temp_path, target)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def _load_immutable_rules(shared_current_run_root: Path) -> ImmutableRules:
    names = set(IMMUTABLE_DEFAULT_NAMES)
    extensions = set(IMMUTABLE_DEFAULT_EXTENSIONS)
    paths: set[str] = set()

    manifest = shared_current_run_root / "META" / "IMMUTABLE.json"
    if manifest.exists() and manifest.is_file():
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, Mapping):
            for item in payload.get("immutable_names", []) or []:
                token = str(item).strip()
                if token:
                    names.add(token)
            for item in payload.get("immutable_extensions", []) or []:
                token = str(item).strip()
                if token:
                    extensions.add(token if token.startswith(".") else "." + token)
            for item in payload.get("immutable_paths", []) or []:
                token = str(item).strip().replace("\\", "/").strip("/")
                if token:
                    paths.add(token)

    return ImmutableRules(
        names=frozenset(sorted(names)),
        extensions=frozenset(sorted(ext.lower() for ext in extensions)),
        paths=frozenset(sorted(paths)),
    )


def _is_immutable_destination(rel_path: Path, destination_path: Path, rules: ImmutableRules) -> bool:
    rel = rel_path.as_posix().replace("\\", "/").strip("/")
    name = destination_path.name
    suffix = destination_path.suffix.lower()

    if rel in rules.paths:
        return True
    if name in rules.names:
        return True
    if suffix and suffix in rules.extensions:
        return True

    if (destination_path.parent / ".immutable").exists():
        return True
    if (destination_path.parent / "IMMUTABLE").exists():
        return True
    if destination_path.with_name(destination_path.name + ".immutable").exists():
        return True
    sidecar_meta = destination_path.with_name(destination_path.name + ".meta.json")
    if sidecar_meta.exists():
        try:
            payload = json.loads(sidecar_meta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, Mapping) and bool(payload.get("immutable", False)):
            return True
    return False


def stable_copy_tree(
    source_root: Path,
    destination_root: Path,
    *,
    excludes: Iterable[str] | None = None,
    hash_strategy: HashStrategy = "sha256",
    dry_run: bool = False,
    append_only: bool = False,
    immutable_rules: ImmutableRules | None = None,
) -> dict[str, Any]:
    """
    Copy a tree deterministically without following symlinks/junctions.
    - Stable traversal order
    - Optional hash skip
    - Optional append-only + immutable skip behavior
    """
    if hash_strategy not in HASH_VALUES:
        raise ValueError(f"unsupported hash_strategy: {hash_strategy}")

    source = source_root.resolve(strict=False)
    destination = destination_root.resolve(strict=False)
    exclude_rules = _normalize_excludes(excludes)

    copied: list[str] = []
    unchanged: list[str] = []
    skipped: list[dict[str, str]] = []

    for rel_path in _iter_files_stable(source, excludes=exclude_rules):
        src_path = source / rel_path
        dst_path = destination / rel_path
        rel_posix = rel_path.as_posix()

        destination_exists = dst_path.exists() and dst_path.is_file()
        if append_only and destination_exists and immutable_rules and _is_immutable_destination(rel_path, dst_path, immutable_rules):
            skipped.append({"path": rel_posix, "reason": "immutable"})
            continue

        if hash_strategy == "sha256":
            src_hash = _sha256_file(src_path)
            if destination_exists and _sha256_file(dst_path) == src_hash:
                unchanged.append(rel_posix)
                continue
        else:
            if destination_exists and _files_equal(src_path, dst_path):
                unchanged.append(rel_posix)
                continue

        if not dry_run:
            _atomic_copy_file(src_path, dst_path)
        copied.append(rel_posix)

    copied.sort()
    unchanged.sort()
    skipped = sorted(skipped, key=lambda item: (item.get("path", ""), item.get("reason", "")))

    return {
        "source_root": source.as_posix(),
        "destination_root": destination.as_posix(),
        "copied": copied,
        "unchanged": unchanged,
        "skipped": skipped,
        "hash_strategy": hash_strategy,
        "dry_run": bool(dry_run),
        "append_only": bool(append_only),
    }


def write_ledger_event(
    ledger_path: Path,
    event: Mapping[str, Any],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Append deterministic NDJSON event using stable JSON serialization.
    """
    payload = dict(event)
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if dry_run:
        return {"path": ledger_path.as_posix(), "planned": True, "event": payload}

    target = ledger_path.resolve(strict=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered + "\n")
    return {"path": target.as_posix(), "planned": False, "event": payload}


def _collect_lock_files(root: Path | None) -> list[str]:
    if root is None or not root.exists() or not root.is_dir():
        return []
    lock_files: list[str] = []
    files = _iter_files_stable(root, excludes=())
    for rel_path in files:
        name = rel_path.name.lower()
        if name == "lock" or name.endswith(".lock"):
            lock_files.append((root / rel_path).resolve(strict=False).as_posix())
    return sorted(set(lock_files))


def _resolve_shared_section_dir(shared_current_run_root: Path, section: str) -> Path:
    upper = shared_current_run_root / section
    lower = shared_current_run_root / section.lower()
    if upper.exists() and upper.is_dir():
        return upper
    if lower.exists() and lower.is_dir():
        return lower
    return upper


def _candidate_worker_targets(shared_current_run_root: Path, worker: str) -> list[Path]:
    workers_root = _resolve_shared_section_dir(shared_current_run_root, "WORKERS")
    canonical_direct = workers_root / worker
    canonical_bundle = canonical_direct / "BUNDLE"

    targets: list[Path] = []
    if canonical_bundle.exists() and canonical_bundle.is_dir():
        targets.append(canonical_bundle)
    else:
        targets.append(canonical_direct)

    legacy_alias = str(LEGACY_WORKER_ALIASES.get(worker, "")).strip()
    if legacy_alias:
        legacy_direct = workers_root / legacy_alias
        legacy_bundle = legacy_direct / "BUNDLE"
        if legacy_bundle.exists() and legacy_bundle.is_dir():
            targets.append(legacy_bundle)
        elif legacy_direct.exists() and legacy_direct.is_dir():
            targets.append(legacy_direct)

    unique = {item.resolve(strict=False).as_posix(): item for item in targets}
    return [unique[key] for key in sorted(unique)]


def _copy_canonical_file(
    source: Path,
    destination: Path,
    *,
    rel_path: Path,
    hash_strategy: HashStrategy,
    dry_run: bool,
    immutable_rules: ImmutableRules,
) -> dict[str, Any]:
    if not source.exists() or not source.is_file():
        return {"copied": [], "unchanged": [], "skipped": [{"path": destination.as_posix(), "reason": "missing_source"}]}

    destination_exists = destination.exists() and destination.is_file()
    if destination_exists and _is_immutable_destination(rel_path, destination, immutable_rules):
        return {
            "copied": [],
            "unchanged": [],
            "skipped": [{"path": destination.as_posix(), "reason": "immutable"}],
        }

    if destination_exists:
        if hash_strategy == "sha256":
            if _sha256_file(source) == _sha256_file(destination):
                return {"copied": [], "unchanged": [destination.as_posix()], "skipped": []}
        elif _files_equal(source, destination):
            return {"copied": [], "unchanged": [destination.as_posix()], "skipped": []}

    if not dry_run:
        _atomic_copy_file(source, destination)
    return {"copied": [destination.as_posix()], "unchanged": [], "skipped": []}


def _no_effect_result(run_id: str, mode: SharedMode, reason: str) -> dict[str, Any]:
    return {
        "status": "PASS",
        "run_id": run_id,
        "mode": mode,
        "copied": [],
        "unchanged": [],
        "skipped": [],
        "reason": reason,
    }


def consume_from_shared(
    *,
    run_id: str,
    run_root: Path,
    shared_current_run_root: Path | None,
    mode: SharedMode = "off",
    hash_strategy: HashStrategy = "sha256",
    dry_run: bool = False,
    strict_on_lock: bool = False,
) -> dict[str, Any]:
    """
    Consume shared inputs into canonical `tools/codex/runs/<RUN_ID>/incoming_shared/`.
    """
    if mode not in {"consume", "both"}:
        return _no_effect_result(run_id, mode, "mode does not include consume")
    if shared_current_run_root is None:
        return _no_effect_result(run_id, mode, "shared current run root unavailable")

    canonical_run_root = run_root.resolve(strict=False)
    current_shared_root = shared_current_run_root.resolve(strict=False)
    ledger_path = current_shared_root / "LEDGER" / "BRIDGE_EVENTS.ndjson"

    lock_files = sorted(set(_collect_lock_files(canonical_run_root) + _collect_lock_files(current_shared_root)))
    if lock_files:
        event = {
            "actor": "shared_bridge",
            "event_type": "LOCK_SKIP",
            "run_id": run_id,
            "mode": mode,
            "rc": 2 if strict_on_lock else 0,
            "details": {
                "operation": "consume",
                "lock_files": lock_files,
                "reason": "lock detected; consume skipped",
            },
        }
        ledger_result = write_ledger_event(ledger_path, event, dry_run=dry_run)
        return {
            "status": "BLOCKED" if strict_on_lock else "PASS",
            "run_id": run_id,
            "mode": mode,
            "copied": [],
            "unchanged": [],
            "skipped": [{"path": item, "reason": "lock_detected"} for item in lock_files],
            "lock_files": lock_files,
            "ledger": ledger_result,
            "reason": "lock detected",
        }

    candidates = [
        current_shared_root / "INCOMING" / "FACTORY" / run_id / "incoming_shared",
        current_shared_root / "INCOMING" / "FACTORY" / run_id,
        current_shared_root / "INCOMING",
    ]
    source = next((item for item in candidates if item.exists() and item.is_dir()), None)
    if source is None:
        result = _no_effect_result(run_id, mode, "no shared incoming source found")
        write_ledger_event(
            ledger_path,
            {
                "actor": "shared_bridge",
                "event_type": "CONSUME",
                "run_id": run_id,
                "mode": mode,
                "rc": 0,
                "details": {"copied": [], "unchanged": [], "skipped": [], "source_missing": True},
            },
            dry_run=dry_run,
        )
        return result

    destination = canonical_run_root / "incoming_shared"
    copy_result = stable_copy_tree(
        source,
        destination,
        excludes=DEFAULT_COPY_EXCLUDES,
        hash_strategy=hash_strategy,
        dry_run=dry_run,
        append_only=False,
        immutable_rules=None,
    )

    write_ledger_event(
        ledger_path,
        {
            "actor": "shared_bridge",
            "event_type": "CONSUME",
            "run_id": run_id,
            "mode": mode,
            "rc": 0,
            "details": {
                "source": source.as_posix(),
                "destination": destination.as_posix(),
                "copied": list(copy_result.get("copied", [])),
                "unchanged": list(copy_result.get("unchanged", [])),
                "skipped": list(copy_result.get("skipped", [])),
            },
        },
        dry_run=dry_run,
    )

    return {
        "status": "PASS",
        "run_id": run_id,
        "mode": mode,
        "source": source.as_posix(),
        "destination": destination.as_posix(),
        "copied": list(copy_result.get("copied", [])),
        "unchanged": list(copy_result.get("unchanged", [])),
        "skipped": list(copy_result.get("skipped", [])),
    }


def publish_to_shared(
    *,
    run_id: str,
    run_root: Path,
    shared_current_run_root: Path | None,
    mode: SharedMode = "off",
    hash_strategy: HashStrategy = "sha256",
    dry_run: bool = False,
    strict_on_lock: bool = False,
) -> dict[str, Any]:
    """
    Publish canonical outputs from `tools/codex/runs/<RUN_ID>/` into shared.
    Append-only behavior is enforced: never delete.
    """
    if mode not in {"publish", "both"}:
        return _no_effect_result(run_id, mode, "mode does not include publish")
    if shared_current_run_root is None:
        return _no_effect_result(run_id, mode, "shared current run root unavailable")

    canonical_run_root = run_root.resolve(strict=False)
    current_shared_root = shared_current_run_root.resolve(strict=False)
    ledger_path = current_shared_root / "LEDGER" / "BRIDGE_EVENTS.ndjson"
    immutable_rules = _load_immutable_rules(current_shared_root)

    lock_files = sorted(set(_collect_lock_files(canonical_run_root) + _collect_lock_files(current_shared_root)))
    if lock_files:
        event = {
            "actor": "shared_bridge",
            "event_type": "LOCK_SKIP",
            "run_id": run_id,
            "mode": mode,
            "rc": 2 if strict_on_lock else 0,
            "details": {
                "operation": "publish",
                "lock_files": lock_files,
                "reason": "lock detected; publish skipped",
            },
        }
        ledger_result = write_ledger_event(ledger_path, event, dry_run=dry_run)
        return {
            "status": "BLOCKED" if strict_on_lock else "PASS",
            "run_id": run_id,
            "mode": mode,
            "copied": [],
            "unchanged": [],
            "skipped": [{"path": item, "reason": "lock_detected"} for item in lock_files],
            "lock_files": lock_files,
            "ledger": ledger_result,
            "reason": "lock detected",
        }

    copied: list[str] = []
    unchanged: list[str] = []
    skipped: list[dict[str, str]] = []

    for worker in sorted(FACTORY_WORKERS):
        source_worker = canonical_run_root / worker
        if not source_worker.exists() or not source_worker.is_dir():
            skipped.append({"path": worker, "reason": "missing_worker_bundle"})
            continue
        for destination_worker in _candidate_worker_targets(current_shared_root, worker):
            worker_copy = stable_copy_tree(
                source_worker,
                destination_worker,
                excludes=(),
                hash_strategy=hash_strategy,
                dry_run=dry_run,
                append_only=True,
                immutable_rules=immutable_rules,
            )
            worker_prefix = destination_worker.relative_to(current_shared_root).as_posix().strip("/")
            copied.extend(f"{worker_prefix}/{item}" for item in worker_copy.get("copied", []))
            unchanged.extend(f"{worker_prefix}/{item}" for item in worker_copy.get("unchanged", []))
            skipped.extend(
                {"path": f"{worker_prefix}/{item.get('path', '')}".strip("/"), "reason": str(item.get("reason", ""))}
                for item in worker_copy.get("skipped", [])
            )

    aggregate_root = _resolve_shared_section_dir(current_shared_root, "AGGREGATE")
    manifest_targets = [aggregate_root / "RUN_MANIFEST.json"]
    report_targets = [aggregate_root / "FINAL_REPORT.txt"]

    legacy_meta = current_shared_root / "meta"
    if legacy_meta.exists() and legacy_meta.is_dir():
        manifest_targets.append(legacy_meta / "RUN_MANIFEST.json")
    legacy_artifacts = current_shared_root / "artifacts"
    if legacy_artifacts.exists() and legacy_artifacts.is_dir():
        report_targets.append(legacy_artifacts / "human" / "FINAL_REPORT.txt")

    attestations_source = canonical_run_root / "attestations"
    attestations_targets = [aggregate_root / "attestations"]
    if legacy_artifacts.exists() and legacy_artifacts.is_dir():
        attestations_targets.append(legacy_artifacts / "machine" / "attestations")

    if attestations_source.exists() and attestations_source.is_dir():
        for target_root in attestations_targets:
            attestations_copy = stable_copy_tree(
                attestations_source,
                target_root,
                excludes=(),
                hash_strategy=hash_strategy,
                dry_run=dry_run,
                append_only=True,
                immutable_rules=immutable_rules,
            )
            target_prefix = target_root.relative_to(current_shared_root).as_posix().strip("/")
            copied.extend(f"{target_prefix}/{item}" for item in attestations_copy.get("copied", []))
            unchanged.extend(f"{target_prefix}/{item}" for item in attestations_copy.get("unchanged", []))
            skipped.extend(
                {
                    "path": f"{target_prefix}/{item.get('path', '')}",
                    "reason": str(item.get("reason", "")),
                }
                for item in attestations_copy.get("skipped", [])
            )

    source_manifest = canonical_run_root / "RUN_MANIFEST.json"
    for destination_file in manifest_targets:
        one_result = _copy_canonical_file(
            source_manifest,
            destination_file,
            rel_path=destination_file.relative_to(current_shared_root),
            hash_strategy=hash_strategy,
            dry_run=dry_run,
            immutable_rules=immutable_rules,
        )
        copied.extend(_to_shared_relative_paths(current_shared_root, one_result.get("copied", [])))
        unchanged.extend(_to_shared_relative_paths(current_shared_root, one_result.get("unchanged", [])))
        skipped.extend(_to_shared_relative_skips(current_shared_root, one_result.get("skipped", [])))

    source_report = canonical_run_root / "Z_integrator" / "FINAL_REPORT.txt"
    for destination_file in report_targets:
        one_result = _copy_canonical_file(
            source_report,
            destination_file,
            rel_path=destination_file.relative_to(current_shared_root),
            hash_strategy=hash_strategy,
            dry_run=dry_run,
            immutable_rules=immutable_rules,
        )
        copied.extend(_to_shared_relative_paths(current_shared_root, one_result.get("copied", [])))
        unchanged.extend(_to_shared_relative_paths(current_shared_root, one_result.get("unchanged", [])))
        skipped.extend(_to_shared_relative_skips(current_shared_root, one_result.get("skipped", [])))

    copied = sorted(set(copied))
    unchanged = sorted(set(unchanged))
    skipped = sorted(
        (
            {"path": str(item.get("path", "")).replace("\\", "/"), "reason": str(item.get("reason", ""))}
            for item in skipped
        ),
        key=lambda item: (item.get("path", ""), item.get("reason", "")),
    )

    publish_manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "mode": mode,
        "hash_strategy": hash_strategy,
        "dry_run": bool(dry_run),
        "copied": copied,
        "unchanged": unchanged,
        "skipped": skipped,
    }

    if not dry_run:
        _atomic_write_json(current_shared_root / "HEALTH" / "publish_manifest.json", publish_manifest)

    write_ledger_event(
        ledger_path,
        {
            "actor": "shared_bridge",
            "event_type": "PUBLISH",
            "run_id": run_id,
            "mode": mode,
            "rc": 0,
            "details": {
                "copied": copied,
                "unchanged": unchanged,
                "skipped": skipped,
                "manifest": (current_shared_root / "HEALTH" / "publish_manifest.json").as_posix(),
            },
        },
        dry_run=dry_run,
    )

    return {
        "status": "PASS",
        "run_id": run_id,
        "mode": mode,
        "copied": copied,
        "unchanged": unchanged,
        "skipped": skipped,
        "manifest": publish_manifest,
    }


def _to_shared_relative_paths(shared_root: Path, values: Iterable[str]) -> list[str]:
    output: list[str] = []
    for item in values:
        token = str(item).replace("\\", "/")
        path = Path(token)
        try:
            rel = path.resolve(strict=False).relative_to(shared_root.resolve(strict=False))
            output.append(rel.as_posix())
        except Exception:
            output.append(token)
    return sorted(set(output))


def _to_shared_relative_skips(shared_root: Path, values: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for item in values:
        raw_path = str(item.get("path", "")).replace("\\", "/")
        path = Path(raw_path)
        try:
            rel = path.resolve(strict=False).relative_to(shared_root.resolve(strict=False)).as_posix()
        except Exception:
            rel = raw_path
        output.append({"path": rel, "reason": str(item.get("reason", ""))})
    return sorted(output, key=lambda entry: (entry.get("path", ""), entry.get("reason", "")))


def write_factory_pointer(
    *,
    run_id: str,
    factory_run_root: Path,
    factory_worktrees_root: Path,
    shared_current_run_root: Path,
    mode: SharedMode,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Write `META/FACTORY_POINTER.json` under shared current run root.
    """
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "factory_run_root": factory_run_root.as_posix(),
        "factory_worktrees_root": factory_worktrees_root.as_posix(),
        "shared_current_run_root": shared_current_run_root.as_posix(),
        "mode": mode,
        "dry_run": bool(dry_run),
    }
    target = shared_current_run_root / "META" / "FACTORY_POINTER.json"
    if not dry_run:
        _atomic_write_json(target, payload)
    return {"path": target.as_posix(), "planned": bool(dry_run), "payload": payload}


def write_shared_pointer(
    *,
    run_id: str,
    factory_run_root: Path,
    shared_root: Path,
    shared_current_run_root: Path,
    mode: SharedMode,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Write `SHARED_POINTER.json` under canonical run root.
    """
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "factory_run_root": factory_run_root.as_posix(),
        "shared_root": shared_root.as_posix(),
        "shared_current_run_root": shared_current_run_root.as_posix(),
        "mode": mode,
        "dry_run": bool(dry_run),
    }
    target = factory_run_root / "SHARED_POINTER.json"
    if not dry_run:
        _atomic_write_json(target, payload)
    return {"path": target.as_posix(), "planned": bool(dry_run), "payload": payload}
