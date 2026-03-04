from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import zlib
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")

DEFAULT_POLICY: dict[str, Any] = {
    "version": "1.0",
    "defaults": {
        "max_file_chars": 120000,
        "max_file_loc": 2000,
        "k_tokens": 25,
        "winnow_window": 6,
        "dup_ratio_file_warn": 0.2,
        "dup_ratio_file_severe": 0.35,
        "dup_ratio_new_warn": 0.08,
        "dup_ratio_new_severe": 0.15,
        "min_gzip_ratio": 0.18,
        "min_ttr": 0.12,
        "min_tokens_for_entropy": 1500,
        "min_tokens_for_dup": 800,
        "max_added_files_per_run_warn": 120,
        "max_added_files_per_run_severe": 250,
        "max_single_dir_files_added": 60,
        "scaling_constant_K": 1200.0,
        "penalties": {
            "entropy_severe": 0.75,
            "blind_severe": 0.9,
            "caps_severe": 1.1,
        },
    },
}


def _now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _read_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def _normalize_rel(path_value: str) -> str:
    path = str(path_value or "").replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return path.strip("/")


def _load_policy(policy_path: Path | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    defaults = dict(DEFAULT_POLICY.get("defaults", {}))
    penalties = dict(defaults.get("penalties", {}))
    payload = _read_json_dict(policy_path) if policy_path else {}
    if not payload:
        merged["defaults"] = defaults
        defaults["penalties"] = penalties
        return merged
    payload_defaults = payload.get("defaults", {}) if isinstance(payload.get("defaults", {}), dict) else {}
    for key, value in payload_defaults.items():
        if key == "penalties" and isinstance(value, dict):
            for p_key, p_value in value.items():
                penalties[p_key] = p_value
        else:
            defaults[key] = value
    defaults["penalties"] = penalties
    merged.update(payload)
    merged["defaults"] = defaults
    return merged


def _parse_files_changed(bundle_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    payload = _read_json_dict(bundle_dir / "FILES_CHANGED.json")
    changes_raw = payload.get("changes", [])
    changes: list[dict[str, Any]] = []
    paths: list[str] = []
    if isinstance(changes_raw, list):
        for item in changes_raw:
            if not isinstance(item, dict):
                continue
            safe = _normalize_rel(str(item.get("path", "")))
            if not safe:
                continue
            normalized = dict(item)
            normalized["path"] = safe
            changes.append(normalized)
            paths.append(safe)
    return changes, paths


def _parse_patch(bundle_dir: Path) -> tuple[dict[str, list[str]], list[str]]:
    patch_path = bundle_dir / "DIFF.patch"
    if not patch_path.exists() or not patch_path.is_file():
        return {}, []
    try:
        text = patch_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}, []
    by_path: dict[str, list[str]] = {}
    current_path = ""
    all_added: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                right = parts[3]
                if right.startswith("b/"):
                    current_path = _normalize_rel(right[2:])
            continue
        if line.startswith("+++ b/"):
            current_path = _normalize_rel(line[6:])
            continue
        if line.startswith("+") and not line.startswith("+++"):
            if not current_path:
                continue
            content = line[1:]
            by_path.setdefault(current_path, []).append(content)
            all_added.append(content)
    return by_path, all_added


def _gzip_ratio(text: str) -> float:
    if not text:
        return 1.0
    raw = text.encode("utf-8", errors="ignore")
    if not raw:
        return 1.0
    compressed = zlib.compress(raw, level=9)
    return float(len(compressed)) / max(1.0, float(len(raw)))


def _token_metrics(lines: list[str]) -> tuple[int, float]:
    if not lines:
        return 0, 1.0
    tokens: list[str] = []
    for line in lines:
        tokens.extend(TOKEN_RE.findall(line))
    total = len(tokens)
    if total == 0:
        return 0, 1.0
    ttr = float(len(set(tokens))) / float(total)
    return total, ttr


def _score_bundle(
    *,
    run_id: str,
    worker_id: str,
    bundle_dir: Path,
    policy: dict[str, Any],
    base_ref: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    defaults = policy.get("defaults", {}) if isinstance(policy.get("defaults", {}), dict) else {}
    penalties = defaults.get("penalties", {}) if isinstance(defaults.get("penalties", {}), dict) else {}

    max_file_chars = max(1, _to_int(defaults.get("max_file_chars"), 120000))
    max_file_loc = max(1, _to_int(defaults.get("max_file_loc"), 2000))
    min_gzip_ratio = _to_float(defaults.get("min_gzip_ratio"), 0.18)
    min_ttr = _to_float(defaults.get("min_ttr"), 0.12)
    min_tokens_for_entropy = max(1, _to_int(defaults.get("min_tokens_for_entropy"), 1500))
    max_added_files_per_run_warn = max(1, _to_int(defaults.get("max_added_files_per_run_warn"), 120))
    max_added_files_per_run_severe = max(1, _to_int(defaults.get("max_added_files_per_run_severe"), 250))
    max_single_dir_files_added = max(1, _to_int(defaults.get("max_single_dir_files_added"), 60))
    entropy_penalty_value = _to_float(penalties.get("entropy_severe"), 0.75)
    blind_penalty_value = _to_float(penalties.get("blind_severe"), 0.9)
    caps_penalty_value = _to_float(penalties.get("caps_severe"), 1.1)

    files_changed_entries, files_changed_paths = _parse_files_changed(bundle_dir)
    patch_by_path, all_added_lines = _parse_patch(bundle_dir)

    if not patch_by_path:
        for path in files_changed_paths:
            patch_by_path.setdefault(path, ["__fallback_change_marker__"])
            all_added_lines.append("__fallback_change_marker__")

    path_counts: dict[str, int] = {path: len(lines) for path, lines in sorted(patch_by_path.items())}
    loc_delta = int(sum(path_counts.values()))
    unique_paths = len(path_counts)

    ext_counts: dict[str, int] = {}
    dir_counts: dict[str, int] = {}
    for path, count in path_counts.items():
        suffix = Path(path).suffix.lower()
        ext_counts[suffix] = ext_counts.get(suffix, 0) + count
        parent = str(Path(path).parent).replace("\\", "/")
        dir_counts[parent] = dir_counts.get(parent, 0) + 1
    unique_dirs = len(dir_counts)

    behavioral_delta = float(unique_dirs + max(1, unique_paths))
    structural_diversity = _clamp01((len(ext_counts) + unique_dirs) / max(1.0, float(loc_delta) * 2.0))
    vdi = _clamp01((behavioral_delta * structural_diversity) / max(1.0, float(loc_delta)) * 0.85)

    non_empty_lines = [line for line in all_added_lines if line.strip()]
    normalized_lines = [line.strip() for line in non_empty_lines]
    unique_line_count = len(set(normalized_lines))
    duplicate_ratio = (
        max(0, len(normalized_lines) - unique_line_count) / max(1.0, float(len(normalized_lines)))
        if normalized_lines
        else 0.0
    )
    concentration = max(path_counts.values()) / max(1.0, float(loc_delta)) if path_counts else 1.0
    dup_penalty = duplicate_ratio * concentration

    joined_all = "\n".join(non_empty_lines)
    gzip_ratio_min = _gzip_ratio(joined_all)
    token_count, ttr_min = _token_metrics(non_empty_lines)
    entropy_flag = bool(token_count >= min_tokens_for_entropy and (gzip_ratio_min < min_gzip_ratio or ttr_min < min_ttr))
    blinded_flag = bool(behavioral_delta <= 1.0 and loc_delta >= 4)

    file_entries: list[dict[str, Any]] = []
    cap_hits: list[str] = []
    dir_file_counts: dict[str, int] = {}
    for path, lines in sorted(patch_by_path.items()):
        loc = len(lines)
        text = "\n".join(lines)
        chars = len(text)
        ratio = _gzip_ratio(text)
        _, ttr = _token_metrics(lines)
        file_entries.append(
            {
                "path": path,
                "loc": int(loc),
                "chars": int(chars),
                "gzip_ratio": ratio,
                "ttr": ttr,
            }
        )
        if loc > max_file_loc:
            cap_hits.append(f"max_file_loc:{path}:{loc}>{max_file_loc}")
        if chars > max_file_chars:
            cap_hits.append(f"max_file_chars:{path}:{chars}>{max_file_chars}")
        parent = str(Path(path).parent).replace("\\", "/")
        dir_file_counts[parent] = dir_file_counts.get(parent, 0) + 1

    added_files_count = len(path_counts)
    if added_files_count > max_added_files_per_run_severe:
        cap_hits.append(f"max_added_files_per_run_severe:{added_files_count}>{max_added_files_per_run_severe}")
    elif added_files_count > max_added_files_per_run_warn:
        cap_hits.append(f"max_added_files_per_run_warn:{added_files_count}>{max_added_files_per_run_warn}")
    for directory, count in sorted(dir_file_counts.items()):
        if count > max_single_dir_files_added:
            cap_hits.append(f"max_single_dir_files_added:{directory}:{count}>{max_single_dir_files_added}")

    entropy_penalty = entropy_penalty_value if entropy_flag else 0.0
    blind_penalty = blind_penalty_value if blinded_flag else 0.0
    caps_penalty = caps_penalty_value if cap_hits else 0.0
    sanction_score = (1.0 - vdi) + dup_penalty + entropy_penalty + blind_penalty + caps_penalty
    sanction_level = "OK" if sanction_score < 0.6 else ("WARN" if sanction_score < 1.2 else "SEVERE")

    flags: list[str] = []
    if entropy_flag:
        flags.append("LOW_ENTROPY")
    if blinded_flag:
        flags.append("BLINDED_PATTERN")
    if cap_hits:
        flags.append("CAPS_EXCEEDED")
    if not (bundle_dir / "DIFF.patch").exists():
        flags.append("PATCH_MISSING_FALLBACK")

    top_offenders = [
        {"path": path, "score_proxy": float(count)}
        for path, count in sorted(path_counts.items(), key=lambda row: row[1], reverse=True)[:25]
    ]

    computed_at = _now_utc()
    report = {
        "run_id": run_id,
        "worker_id": worker_id,
        "computed_at_utc": computed_at,
        "bundle_dir": bundle_dir.as_posix(),
        "base_ref": str(base_ref or "HEAD"),
        "loc_delta": int(loc_delta),
        "loc_removed": 0,
        "changed_files_count": int(unique_paths),
        "added_files_count": int(added_files_count),
        "behavioral_delta": behavioral_delta,
        "behavioral_density": behavioral_delta / max(1.0, float(loc_delta)),
        "structural_diversity": structural_diversity,
        "duplication_ratio_new": duplicate_ratio,
        "file_concentration_ratio": concentration,
        "gzip_ratio_min": float(gzip_ratio_min),
        "ttr_min": float(ttr_min),
        "flags": sorted(flags),
        "vdi": float(vdi),
        "sanction_score": float(sanction_score),
        "sanction_level": sanction_level,
        "duplicate_clusters": [],
        "blinded_suspects": [{"reason": "heuristic_trigger", "details": {}}] if blinded_flag else [],
        "top_offenders": top_offenders,
        "per_file": file_entries,
        "cap_hits": cap_hits,
        "policy_used": policy,
    }

    score = {
        "run_id": run_id,
        "worker_id": worker_id,
        "computed_at_utc": computed_at,
        "sanction_score": float(sanction_score),
        "sanction_level": sanction_level,
        "vdi": float(vdi),
        "loc_delta": int(loc_delta),
        "notes": sorted(flags),
    }
    return report, score


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic evolutionary sanctions engine")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--run-id", default="UNKNOWN_RUN")
    parser.add_argument("--worker-id", default="UNKNOWN_WORKER")
    parser.add_argument("--bundle-dir", default=None)
    parser.add_argument("--base-ref", default=None)
    parser.add_argument("--policy", default=None)
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    bundle_dir = Path(args.bundle_dir).resolve() if args.bundle_dir else repo_root
    bundle_dir.mkdir(parents=True, exist_ok=True)

    policy_path = Path(args.policy).resolve() if args.policy else None
    policy = _load_policy(policy_path)
    report, score = _score_bundle(
        run_id=str(args.run_id),
        worker_id=str(args.worker_id),
        bundle_dir=bundle_dir,
        policy=policy,
        base_ref=args.base_ref,
    )

    _write_json(bundle_dir / "SELF_EVAL_REPORT.json", report)
    _write_json(bundle_dir / "SANCTION_SCORE.json", score)
    _append_jsonl(
        bundle_dir / "SELF_CORRECTION_LOG.jsonl",
        {
            "run_id": score["run_id"],
            "worker_id": score["worker_id"],
            "computed_at_utc": score["computed_at_utc"],
            "sanction_score": score["sanction_score"],
            "sanction_level": score["sanction_level"],
            "vdi": score["vdi"],
            "loc_delta": score["loc_delta"],
            "flags": report.get("flags", []),
        },
    )
    print("OK evolutionary_sanctions completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
