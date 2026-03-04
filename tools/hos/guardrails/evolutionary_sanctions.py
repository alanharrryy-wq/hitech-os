from __future__ import annotations

import argparse
import ast
import datetime as dt
import fnmatch
import hashlib
import json
import math
import os
import re
import sys
import textwrap
import zlib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Optional


# ============================================================
# HITECH-OS Guardrails — Evolutionary Sanctions (Compat + 100x)
# Outputs REQUIRED by validator:
#   - SELF_EVAL_REPORT.json
#   - SANCTION_SCORE.json
#   - SELF_CORRECTION_LOG.jsonl
#
# Score direction:
#   - LOWER sanction_score is BETTER
#
# Extras (non-breaking):
#   - SANCTIONS_RESULT.json
#   - SANCTIONS_REPORT.md
#
# Signals:
#   - Clone detection (winnowing fingerprints)
#   - Near-duplicate detection (SimHash)
#   - Python AST structural duplicates
#   - Entropy + TTR + gzip ratio
#   - Secrets scanning (regex)
#   - Directory explosion / added files concentration (FILES_CHANGED.json)
#   - Single-file bloat (LOC)
#   - Patch LOC delta from DIFF.patch
# ============================================================


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|->|=>|::|[{}()[\].,;:+\-/*%<>]")
WHITESPACE_RE = re.compile(r"\s+")
NON_SOURCE_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
    ".zip", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib",
}

DEFAULT_IGNORES = [
    ".git/*", "**/.git/*",
    "**/node_modules/*",
    "**/dist/*", "**/build/*",
    "**/.next/*", "**/out/*",
    "**/.venv/*", "**/venv/*",
    "**/__pycache__/*",
    "**/.pytest_cache/*",
    "**/coverage/*",
    "**/.cache/*",
    "**/LOGS/*",
]

SECRET_PATTERNS = [
    ("private_key_block", re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"), "SEVERE"),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "SEVERE"),
    ("github_pat", re.compile(r"\bghp_[A-Za-z0-9]{36,}\b"), "SEVERE"),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "SEVERE"),
    ("generic_api_key", re.compile(r"(?i)\b(api[_-]?key|secret|token)\b\s*[:=]\s*['\"][A-Za-z0-9_\-]{24,}['\"]"), "WARN"),
]

DEFAULT_POLICY: dict[str, Any] = {
    "version": "compat-100x",
    "defaults": {
        # scanning limits
        "max_file_bytes": 750_000,          # hard skip
        "max_files_scanned": 5000,          # hard cap
        "max_total_chars": 18_000_000,      # soft cap
        "max_tokens_per_file": 120_000,     # cap tokenization/fingerprints per file (performance)

        # allow/ignore
        "allowed_exts": [
            ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yml", ".yaml", ".md",
            ".css", ".scss", ".html", ".sql", ".txt", ".toml", ".ini", ".env", ".sh", ".ps1",
        ],
        "ignore_globs": DEFAULT_IGNORES,

        # token metrics
        "min_tokens_for_entropy": 1200,
        "min_tokens_for_dup": 900,
        "min_ttr": 0.12,
        "min_entropy_norm": 0.55,
        "min_gzip_ratio": 0.19,

        # winnowing fingerprints (clone detection)
        "winnow_k": 25,
        "winnow_window": 6,
        "dup_pair_threshold": 0.38,
        "dup_ratio_file_warn": 0.22,
        "dup_ratio_file_severe": 0.38,
        "dup_ratio_bundle_warn": 0.10,
        "dup_ratio_bundle_severe": 0.18,

        # near-duplicate simhash
        "simhash_hamming_warn": 8,
        "simhash_hamming_severe": 5,

        # growth / explosion (FILES_CHANGED.json)
        "max_added_files_warn": 140,
        "max_added_files_severe": 280,
        "max_single_dir_added_warn": 65,
        "max_single_dir_added_severe": 110,

        # bloat
        "single_file_loc_warn": 2200,
        "single_file_loc_severe": 4200,

        # sanction thresholds (matches validator fallback semantics)
        "ok_max": 0.6,
        "warn_max": 1.2,

        # weights (tune without code changes)
        "weights": {
            # baseline (FILES_CHANGED-style) contribution already has its own scale; these add-ons push score upward
            "content_entropy": 0.45,
            "content_ttr": 0.18,
            "content_gzip": 0.18,
            "dup_bundle": 0.70,
            "dup_files": 0.35,
            "exact_dups": 0.55,
            "py_ast_dups": 0.18,
            "near_dups": 0.18,
            "dir_explosion": 0.35,
            "added_files": 0.40,
            "single_file_bloat": 0.35,
            "secrets": 2.50,
        },

        # report sizing
        "top_pairs": 20,
        "top_files": 60,
    }
}


# -------------------------
# Models
# -------------------------

@dataclass
class Sanction:
    id: str
    severity: str  # INFO|WARN|SEVERE
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class FileMetrics:
    relpath: str
    bytes: int
    loc: int
    chars: int
    token_count: int
    ttr: float
    entropy_norm: float
    gzip_ratio: float
    fingerprint_count: int
    dup_ratio: float
    simhash64: int
    py_ast_sig: Optional[str] = None
    py_complexity: Optional[int] = None
    secrets_hits: int = 0


@dataclass
class Result100x:
    run_id: str
    worker_id: str
    computed_at_utc: str
    policy_version: str
    sanction_score: float
    sanction_level: str
    vdi: float
    loc_delta: int
    changed_files_count: int
    bundle_metrics: dict[str, Any]
    sanctions: list[Sanction]
    top_duplicate_pairs: list[dict[str, Any]]
    top_files: list[dict[str, Any]]


# -------------------------
# Utils
# -------------------------

def now_utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def to_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def to_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def json_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def jsonl_append(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def rel_norm(root: Path, p: Path) -> str:
    try:
        rp = p.relative_to(root)
    except Exception:
        rp = p
    return str(rp).replace("\\", "/")


def should_ignore(relpath: str, ignore_globs: list[str]) -> bool:
    for g in ignore_globs:
        if fnmatch.fnmatch(relpath, g) or fnmatch.fnmatch("/" + relpath, g):
            return True
    return False


def looks_binary(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in NON_SOURCE_EXT:
        return True
    try:
        with path.open("rb") as f:
            chunk = f.read(2048)
        return b"\x00" in chunk
    except Exception:
        return True


def progress(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _legacy_aliases(policy: dict[str, Any]) -> dict[str, Any]:
    merged = dict(policy)
    defaults_raw = merged.get("defaults", {})
    defaults = dict(defaults_raw) if isinstance(defaults_raw, dict) else {}

    allow_exts = merged.get("allow_extensions", [])
    if "allowed_exts" not in defaults and isinstance(allow_exts, list) and allow_exts:
        defaults["allowed_exts"] = allow_exts

    exclude_globs = merged.get("exclude_globs", [])
    if "ignore_globs" not in defaults and isinstance(exclude_globs, list) and exclude_globs:
        defaults["ignore_globs"] = exclude_globs

    rename_map = {
        "k_tokens": "winnow_k",
        "max_added_files_per_run_warn": "max_added_files_warn",
        "max_added_files_per_run_severe": "max_added_files_severe",
        "max_single_dir_files_added": "max_single_dir_added_warn",
    }
    for old_key, new_key in rename_map.items():
        if old_key in defaults and new_key not in defaults:
            defaults[new_key] = defaults[old_key]

    if "max_single_dir_files_added" in defaults and "max_single_dir_added_severe" not in defaults:
        defaults["max_single_dir_added_severe"] = int(to_int(defaults["max_single_dir_files_added"], 110) * 1.7)

    merged["defaults"] = defaults
    return merged


def load_policy(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return DEFAULT_POLICY
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return DEFAULT_POLICY
        merged = deep_merge(DEFAULT_POLICY, data)
        return _legacy_aliases(merged)
    except Exception:
        return DEFAULT_POLICY


# -------------------------
# Patch LOC delta
# -------------------------

def count_patch_added_loc(patch_path: Path) -> int:
    if not patch_path.exists():
        return 0
    try:
        added = 0
        for line in patch_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("+++ ") or line.startswith("--- ") or line.startswith("@@"):
                continue
            if line.startswith("+") and not line.startswith("++"):
                added += 1
        return added
    except Exception:
        return 0


# -------------------------
# FILES_CHANGED parsing (bundle delta + VDI baseline)
# -------------------------

def read_files_changed(bundle_root: Path) -> dict[str, Any]:
    p = bundle_root / "FILES_CHANGED.json"
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def extract_changes(fc: dict[str, Any]) -> list[dict[str, Any]]:
    # expected common shape in validator fallback: {"changes":[{"path":...}, ...]}
    changes = fc.get("changes", [])
    if isinstance(changes, list):
        return [x for x in changes if isinstance(x, dict)]
    # tolerate other shapes
    files = fc.get("files", [])
    if isinstance(files, list):
        return [x for x in files if isinstance(x, dict)]
    return []


def compute_vdi_from_changes(changes: list[dict[str, Any]]) -> tuple[float, int, float, float, float, float, str, int]:
    """
    Returns:
      vdi, loc_delta, duplication_ratio_new, concentration, structural_div, behavioral_delta, worst_dir, worst_dir_count
    """
    loc_delta = len(changes)
    path_counts: dict[str, int] = {}
    ext_counts: dict[str, int] = {}
    dir_counts: dict[str, int] = {}

    for item in changes:
        path = str(item.get("path", item.get("relpath", ""))).replace("\\", "/").strip()
        if not path:
            continue
        path_counts[path] = path_counts.get(path, 0) + 1
        ext = Path(path).suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        ddir = "/".join(path.strip("/").split("/")[:-1]) or "."
        dir_counts[ddir] = dir_counts.get(ddir, 0) + 1

    unique_paths = len(path_counts)
    behavioral_delta = float(max(1, unique_paths))

    # structural diversity: more extensions + more unique paths relative to loc_delta
    structural_div = clamp01((len(ext_counts) + unique_paths) / max(1.0, float(loc_delta) * 2.0))

    # duplication ratio & concentration as in fallback spirit
    duplication_ratio_new = max(0.0, float(loc_delta - unique_paths)) / max(1.0, float(loc_delta))
    concentration = (max(path_counts.values()) / max(1.0, float(loc_delta))) if path_counts else 1.0

    vdi = clamp01((behavioral_delta * structural_div) / max(1.0, float(loc_delta)) * 0.75)

    worst_dir = "."
    worst_dir_count = 0
    if dir_counts:
        worst_dir, worst_dir_count = max(dir_counts.items(), key=lambda x: x[1])

    return vdi, loc_delta, duplication_ratio_new, concentration, structural_div, behavioral_delta, worst_dir, int(worst_dir_count)


# -------------------------
# Token metrics
# -------------------------

def tokenize(text: str, max_tokens: int) -> list[str]:
    toks = TOKEN_RE.findall(text)
    if max_tokens > 0 and len(toks) > max_tokens:
        return toks[:max_tokens]
    return toks


def token_metrics(tokens: list[str]) -> tuple[int, float, float]:
    n = len(tokens)
    if n == 0:
        return 0, 0.0, 0.0
    uniq = len(set(tokens))
    ttr = uniq / n

    # Shannon entropy over token distribution, normalized by log2(uniq)
    counts: dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1

    H = 0.0
    for c in counts.values():
        p = c / n
        H -= p * math.log(p, 2)

    if uniq <= 1:
        Hn = 0.0
    else:
        Hn = H / math.log(uniq, 2)

    return n, ttr, clamp01(Hn)


def gzip_ratio(text: str) -> float:
    if not text:
        return 0.0
    raw = text.encode("utf-8", errors="ignore")
    comp = zlib.compress(raw)
    return len(comp) / max(1, len(raw))


# -------------------------
# Winnowing fingerprints (clone detection)
# -------------------------

def kgram_hashes(tokens: list[str], k: int) -> list[int]:
    if k <= 0 or len(tokens) < k:
        return []
    out: list[int] = []
    for i in range(0, len(tokens) - k + 1):
        gram = " ".join(tokens[i:i+k])
        h = hashlib.sha1(gram.encode("utf-8", errors="ignore")).digest()
        out.append(int.from_bytes(h[:8], "big", signed=False))
    return out


def winnow_fingerprints(hashes: list[int], window: int) -> list[int]:
    if not hashes:
        return []
    if window <= 1:
        return hashes[:]
    fps: list[int] = []
    min_pos = -1
    min_val = None
    for i in range(0, len(hashes) - window + 1):
        w = hashes[i:i+window]
        m = min(w)
        j = i + (window - 1 - w[::-1].index(m))  # rightmost min
        if j != min_pos or m != min_val:
            fps.append(m)
            min_pos = j
            min_val = m
    return fps


# -------------------------
# SimHash (near duplicates)
# -------------------------

def simhash64(tokens: list[str]) -> int:
    if not tokens:
        return 0
    v = [0] * 64
    for t in tokens:
        h = hashlib.md5(t.encode("utf-8", errors="ignore")).digest()
        x = int.from_bytes(h[:8], "big", signed=False)
        for i in range(64):
            v[i] += 1 if ((x >> i) & 1) else -1
    out = 0
    for i in range(64):
        if v[i] >= 0:
            out |= (1 << i)
    return out


def hamdist64(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def simhash_buckets(x: int) -> list[int]:
    return [
        (x >> 0) & 0xFFFF,
        (x >> 16) & 0xFFFF,
        (x >> 32) & 0xFFFF,
        (x >> 48) & 0xFFFF,
    ]


# -------------------------
# Python AST structural signature
# -------------------------

class PyNormalize(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name) -> ast.AST:
        return ast.copy_location(ast.Name(id="_", ctx=node.ctx), node)

    def visit_arg(self, node: ast.arg) -> ast.AST:
        return ast.copy_location(ast.arg(arg="_", annotation=None, type_comment=None), node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        v = node.value
        if isinstance(v, (int, float, complex)):
            nv = 0
        elif isinstance(v, str):
            nv = ""
        elif isinstance(v, bool):
            nv = False
        else:
            nv = None
        return ast.copy_location(ast.Constant(value=nv), node)


def py_ast_signature(text: str) -> tuple[Optional[str], Optional[int]]:
    try:
        tree = ast.parse(text)
    except Exception:
        return None, None

    norm = PyNormalize().visit(tree)
    ast.fix_missing_locations(norm)

    complexity = 1
    for n in ast.walk(tree):
        if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.BoolOp, ast.IfExp)):
            complexity += 1

    dumped = ast.dump(norm, include_attributes=False)
    sig = sha256_hex(dumped)[:24]
    return sig, complexity


# -------------------------
# Secrets
# -------------------------

def secrets_scan(text: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for sid, rx, sev in SECRET_PATTERNS:
        if rx.search(text):
            hits.append((sid, sev))
    return hits


# -------------------------
# Core scan
# -------------------------

def pick_source_root(bundle_root: Path) -> Path:
    # Prefer FILES/ snapshot if present (that’s the actual “code output”)
    files_dir = bundle_root / "FILES"
    if files_dir.exists() and files_dir.is_dir():
        return files_dir
    return bundle_root


def scan_source_tree(source_root: Path, policy: dict[str, Any]) -> tuple[list[FileMetrics], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[Sanction]]:
    d = policy.get("defaults", {})
    allowed_exts = set([e.lower() for e in d.get("allowed_exts", [])])
    ignore_globs = d.get("ignore_globs", DEFAULT_IGNORES)

    max_files = to_int(d.get("max_files_scanned", 5000), 5000)
    max_file_bytes = to_int(d.get("max_file_bytes", 750_000), 750_000)
    max_total_chars = to_int(d.get("max_total_chars", 18_000_000), 18_000_000)
    max_tokens_per_file = to_int(d.get("max_tokens_per_file", 120_000), 120_000)

    candidates: list[Path] = []
    for p in source_root.rglob("*"):
        if not p.is_file():
            continue
        rp = rel_norm(source_root, p)
        if should_ignore(rp, ignore_globs):
            continue
        ext = p.suffix.lower()
        if ext and allowed_exts and (ext not in allowed_exts):
            if ext != "":
                continue
        if looks_binary(p):
            continue
        candidates.append(p)
        if len(candidates) >= max_files:
            break

    total = len(candidates)
    sanctions: list[Sanction] = []

    if total == 0:
        sanctions.append(Sanction(
            id="no_source_files",
            severity="SEVERE",
            message="No source-like files found to scan.",
            evidence={"source_root": source_root.as_posix()},
        ))
        return [], {"files_scanned": 0}, [], [], sanctions

    progress(f"[evo_sanctions] scanning {total} files under {source_root.as_posix()}")

    file_metrics: list[FileMetrics] = []
    fp_sets: list[set[int]] = []
    fp_index: dict[int, list[int]] = {}
    exact_hash_index: dict[str, list[int]] = {}
    sim_buckets: dict[tuple[int, int], list[int]] = {}
    py_ast_index: dict[str, list[int]] = {}

    total_chars = 0
    total_tokens = 0

    # scan
    for i, p in enumerate(candidates, start=1):
        if i % 40 == 0 or i == total:
            pct = int((i / total) * 100)
            progress(f"[evo_sanctions] {pct:3d}% ({i}/{total}) {rel_norm(source_root, p)}")

        try:
            b = p.stat().st_size
        except Exception:
            continue

        if b > max_file_bytes:
            fm = FileMetrics(
                relpath=rel_norm(source_root, p),
                bytes=b, loc=0, chars=0,
                token_count=0, ttr=0.0, entropy_norm=0.0, gzip_ratio=0.0,
                fingerprint_count=0, dup_ratio=0.0, simhash64=0,
                secrets_hits=0,
            )
            file_metrics.append(fm)
            fp_sets.append(set())
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        total_chars += len(text)
        if total_chars > max_total_chars:
            sanctions.append(Sanction(
                id="max_total_chars_cap",
                severity="WARN",
                message="Reached max_total_chars cap; scan stopped early for performance determinism.",
                evidence={"max_total_chars": max_total_chars},
            ))
            break

        loc = text.count("\n") + 1 if text else 0
        text_norm = WHITESPACE_RE.sub(" ", text).strip()

        toks = tokenize(text, max_tokens_per_file)
        n_tok, ttr, Hn = token_metrics(toks)
        total_tokens += n_tok

        gz = gzip_ratio(text)

        # fingerprints
        k = to_int(d.get("winnow_k", 25), 25)
        w = to_int(d.get("winnow_window", 6), 6)
        hashes = kgram_hashes(toks, k)
        fps = winnow_fingerprints(hashes, w)
        fp_set = set(fps)

        # exact dup hash (normalized)
        norm_hash = sha256_hex(text_norm)
        exact_hash_index.setdefault(norm_hash, []).append(len(file_metrics))

        # simhash buckets
        sh = simhash64(toks)
        for bi, bv in enumerate(simhash_buckets(sh)):
            sim_buckets.setdefault((bi, bv), []).append(len(file_metrics))

        # python AST signature
        py_sig = None
        py_cx = None
        if p.suffix.lower() == ".py":
            py_sig, py_cx = py_ast_signature(text)
            if py_sig:
                py_ast_index.setdefault(py_sig, []).append(len(file_metrics))

        sec_hits = len(secrets_scan(text))

        fm = FileMetrics(
            relpath=rel_norm(source_root, p),
            bytes=b, loc=loc, chars=len(text),
            token_count=n_tok, ttr=ttr, entropy_norm=Hn, gzip_ratio=gz,
            fingerprint_count=len(fp_set), dup_ratio=0.0, simhash64=sh,
            py_ast_sig=py_sig, py_complexity=py_cx,
            secrets_hits=sec_hits,
        )
        file_metrics.append(fm)
        fp_sets.append(fp_set)

        for fp in fp_set:
            fp_index.setdefault(fp, []).append(len(file_metrics) - 1)

    n_files = len(file_metrics)
    if n_files == 0:
        sanctions.append(Sanction(
            id="scan_empty",
            severity="SEVERE",
            message="Scan produced zero readable files after filters/limits.",
            evidence={"source_root": source_root.as_posix()},
        ))
        return [], {"files_scanned": 0}, [], [], sanctions

    # duplication overlap counts via inverted index (avoid full O(n^2))
    overlap_counts: dict[tuple[int, int], int] = {}
    for fp, idxs in fp_index.items():
        if len(idxs) <= 1:
            continue
        idxs_sorted = sorted(idxs)
        for ai in range(len(idxs_sorted)):
            a = idxs_sorted[ai]
            for bi in range(ai + 1, len(idxs_sorted)):
                b = idxs_sorted[bi]
                overlap_counts[(a, b)] = overlap_counts.get((a, b), 0) + 1

    # file dup ratio approximation
    fp_shared_count = [0] * n_files
    for fp, idxs in fp_index.items():
        if len(idxs) <= 1:
            continue
        for idx in idxs:
            fp_shared_count[idx] += 1
    for i in range(n_files):
        denom = max(1, file_metrics[i].fingerprint_count)
        file_metrics[i].dup_ratio = clamp01(fp_shared_count[i] / denom)

    # top duplicate pairs
    pair_threshold = to_float(d.get("dup_pair_threshold", 0.38), 0.38)
    top_pairs_n = to_int(d.get("top_pairs", 20), 20)
    pairs: list[dict[str, Any]] = []
    for (a, b), ov in overlap_counts.items():
        fa = max(1, len(fp_sets[a]))
        fb = max(1, len(fp_sets[b]))
        sim = ov / min(fa, fb)
        if sim >= pair_threshold:
            pairs.append({
                "a": file_metrics[a].relpath,
                "b": file_metrics[b].relpath,
                "overlap": ov,
                "sim_min": round(sim, 4),
                "fa": fa,
                "fb": fb,
            })
    pairs.sort(key=lambda x: (x["sim_min"], x["overlap"]), reverse=True)
    pairs = pairs[:top_pairs_n]

    # exact duplicates
    exact_dups = [idxs for idxs in exact_hash_index.values() if len(idxs) > 1]
    exact_dup_files = sum(len(g) for g in exact_dups)

    # near duplicates (simhash) using bucket candidates
    ham_warn = to_int(d.get("simhash_hamming_warn", 8), 8)
    ham_sev = to_int(d.get("simhash_hamming_severe", 5), 5)
    seen = set()
    near_warn_pairs = 0
    near_sev_pairs = 0
    for _, idxs in sim_buckets.items():
        if len(idxs) <= 1:
            continue
        idxs_sorted = sorted(set(idxs))
        for i in range(len(idxs_sorted)):
            for j in range(i + 1, len(idxs_sorted)):
                a, b = idxs_sorted[i], idxs_sorted[j]
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                hd = hamdist64(file_metrics[a].simhash64, file_metrics[b].simhash64)
                if hd <= ham_sev:
                    near_sev_pairs += 1
                elif hd <= ham_warn:
                    near_warn_pairs += 1

    # python AST duplicates
    py_ast_dups = [idxs for idxs in py_ast_index.values() if len(idxs) > 1]
    py_ast_dup_files = sum(len(g) for g in py_ast_dups)

    # bundle metrics
    avg_ttr = sum(f.ttr for f in file_metrics) / max(1, n_files)
    avg_entropy = sum(f.entropy_norm for f in file_metrics) / max(1, n_files)
    avg_gz = sum(f.gzip_ratio for f in file_metrics) / max(1, n_files)
    max_loc = max((f.loc for f in file_metrics), default=0)

    dup_ratio_bundle = 0.0
    if fp_index:
        shared_fp_total = sum(1 for _, idxs in fp_index.items() if len(idxs) > 1)
        dup_ratio_bundle = shared_fp_total / max(1, len(fp_index))

    secret_files = [f.relpath for f in file_metrics if f.secrets_hits > 0]

    metrics = {
        "files_scanned": n_files,
        "total_chars_scanned": total_chars,
        "total_tokens_scanned": total_tokens,
        "avg_ttr": round(avg_ttr, 4),
        "avg_entropy_norm": round(avg_entropy, 4),
        "avg_gzip_ratio": round(avg_gz, 4),
        "dup_ratio_bundle": round(dup_ratio_bundle, 4),
        "exact_dup_files": int(exact_dup_files),
        "py_ast_dup_files": int(py_ast_dup_files),
        "near_dup_warn_pairs": int(near_warn_pairs),
        "near_dup_severe_pairs": int(near_sev_pairs),
        "max_file_loc": int(max_loc),
        "secret_files_count": len(secret_files),
        "secret_files_sample": secret_files[:10],
    }

    # Top files payload (risk sorted later outside)
    top_files_n = to_int(d.get("top_files", 60), 60)
    top_files_payload = [
        {
            "file": f.relpath,
            "loc": f.loc,
            "tokens": f.token_count,
            "dup_ratio": round(f.dup_ratio, 4),
            "entropy_norm": round(f.entropy_norm, 4),
            "ttr": round(f.ttr, 4),
            "gzip_ratio": round(f.gzip_ratio, 4),
            "secrets_hits": f.secrets_hits,
            "py_ast_sig": f.py_ast_sig,
            "py_complexity": f.py_complexity,
        }
        for f in file_metrics[:top_files_n]
    ]

    return file_metrics, metrics, pairs, top_files_payload, sanctions


# -------------------------
# Scoring (LOWER is better)
# -------------------------

def score_level(score: float, ok_max: float, warn_max: float) -> str:
    if score < ok_max:
        return "OK"
    if score < warn_max:
        return "WARN"
    return "SEVERE"


def normalized_shortfall(value: float, threshold: float) -> float:
    # how far below threshold as 0..1+ (clamped to 1)
    if threshold <= 0:
        return 0.0
    if value >= threshold:
        return 0.0
    return clamp01((threshold - value) / threshold)


def normalized_excess(value: float, warn: float, severe: float) -> float:
    # how far above warn threshold towards severe as 0..1
    if value <= warn:
        return 0.0
    if severe <= warn:
        return 1.0
    return clamp01((value - warn) / (severe - warn))


def compute_sanction_score(
    policy: dict[str, Any],
    changes_vdi: float,
    duplication_ratio_new: float,
    concentration: float,
    structural_div: float,
    behavioral_delta: float,
    loc_delta_changes: int,
    added_files: int,
    worst_dir_count: int,
    metrics: dict[str, Any],
    file_metrics: list[FileMetrics],
) -> tuple[float, list[Sanction], dict[str, Any]]:
    """
    Returns:
      sanction_score (LOWER is better),
      sanctions[],
      score_breakdown
    """
    d = policy.get("defaults", {})
    w = d.get("weights", {})

    sanctions: list[Sanction] = []

    avg_entropy = to_float(metrics.get("avg_entropy_norm"), 0.0)
    avg_ttr = to_float(metrics.get("avg_ttr"), 0.0)
    avg_gz = to_float(metrics.get("avg_gzip_ratio"), 0.0)
    dup_ratio_bundle = to_float(metrics.get("dup_ratio_bundle"), 0.0)
    exact_dup_files = to_int(metrics.get("exact_dup_files"), 0)
    py_ast_dup_files = to_int(metrics.get("py_ast_dup_files"), 0)
    near_warn_pairs = to_int(metrics.get("near_dup_warn_pairs"), 0)
    near_sev_pairs = to_int(metrics.get("near_dup_severe_pairs"), 0)
    max_loc = to_int(metrics.get("max_file_loc"), 0)
    secret_count = to_int(metrics.get("secret_files_count"), 0)

    # --- Baseline "VDI-ish" (validator fallback spirit)
    # Lower is better, so baseline is (1 - vdi) + duplication_ratio_new * concentration
    # We add a tiny stabilizer to avoid exact zero jitter
    baseline = (1.0 - clamp01(changes_vdi)) + (duplication_ratio_new * concentration)
    baseline = max(0.0, baseline)

    # --- Content-based normalized badness
    entropy_bad = normalized_shortfall(avg_entropy, to_float(d.get("min_entropy_norm", 0.55), 0.55))
    ttr_bad = normalized_shortfall(avg_ttr, to_float(d.get("min_ttr", 0.12), 0.12))
    gzip_bad = normalized_shortfall(avg_gz, to_float(d.get("min_gzip_ratio", 0.19), 0.19))

    dup_bundle_bad = normalized_excess(
        dup_ratio_bundle,
        to_float(d.get("dup_ratio_bundle_warn", 0.10), 0.10),
        to_float(d.get("dup_ratio_bundle_severe", 0.18), 0.18),
    )

    # file-level duplication “pressure”: fraction of files over warn/severe
    file_dup_warn_th = to_float(d.get("dup_ratio_file_warn", 0.22), 0.22)
    file_dup_sev_th = to_float(d.get("dup_ratio_file_severe", 0.38), 0.38)

    warn_files = [f for f in file_metrics if f.fingerprint_count > 0 and f.dup_ratio >= file_dup_warn_th]
    sev_files = [f for f in file_metrics if f.fingerprint_count > 0 and f.dup_ratio >= file_dup_sev_th]
    file_dup_bad = 0.0
    if file_metrics:
        file_dup_bad = clamp01((len(warn_files) * 0.6 + len(sev_files) * 1.2) / max(1.0, float(len(file_metrics))) * 1.8)

    # exact dup badness
    exact_bad = 0.0
    if file_metrics:
        exact_bad = clamp01((exact_dup_files / max(1.0, float(len(file_metrics)))) * 6.0)

    # python AST dup badness
    ast_bad = 0.0
    if file_metrics:
        ast_bad = clamp01((py_ast_dup_files / max(1.0, float(len(file_metrics)))) * 4.0)

    # near dup badness
    near_bad = clamp01((near_warn_pairs * 0.03) + (near_sev_pairs * 0.06))

    # growth/explosion badness
    added_warn = to_int(d.get("max_added_files_warn", 140), 140)
    added_sev = to_int(d.get("max_added_files_severe", 280), 280)
    added_bad = normalized_excess(float(added_files), float(added_warn), float(added_sev))

    dir_warn = to_int(d.get("max_single_dir_added_warn", 65), 65)
    dir_sev = to_int(d.get("max_single_dir_added_severe", 110), 110)
    dir_bad = normalized_excess(float(worst_dir_count), float(dir_warn), float(dir_sev))

    # bloat badness
    loc_warn = to_int(d.get("single_file_loc_warn", 2200), 2200)
    loc_sev = to_int(d.get("single_file_loc_severe", 4200), 4200)
    bloat_bad = normalized_excess(float(max_loc), float(loc_warn), float(loc_sev))

    # secrets
    secrets_bad = 1.0 if secret_count > 0 else 0.0

    # --- Weighted sum
    score = baseline
    score += to_float(w.get("content_entropy", 0.45), 0.45) * entropy_bad
    score += to_float(w.get("content_ttr", 0.18), 0.18) * ttr_bad
    score += to_float(w.get("content_gzip", 0.18), 0.18) * gzip_bad
    score += to_float(w.get("dup_bundle", 0.70), 0.70) * dup_bundle_bad
    score += to_float(w.get("dup_files", 0.35), 0.35) * file_dup_bad
    score += to_float(w.get("exact_dups", 0.55), 0.55) * exact_bad
    score += to_float(w.get("py_ast_dups", 0.18), 0.18) * ast_bad
    score += to_float(w.get("near_dups", 0.18), 0.18) * near_bad
    score += to_float(w.get("added_files", 0.40), 0.40) * added_bad
    score += to_float(w.get("dir_explosion", 0.35), 0.35) * dir_bad
    score += to_float(w.get("single_file_bloat", 0.35), 0.35) * bloat_bad
    score += to_float(w.get("secrets", 2.50), 2.50) * secrets_bad

    # --- Sanctions list (human + machine)
    if secrets_bad > 0:
        sanctions.append(Sanction(
            id="secrets_detected",
            severity="SEVERE",
            message="Potential secrets detected in output files.",
            evidence={"secret_files_sample": metrics.get("secret_files_sample", [])},
        ))

    if entropy_bad > 0:
        sanctions.append(Sanction(
            id="low_entropy",
            severity="SEVERE" if entropy_bad >= 0.35 else "WARN",
            message="Low normalized token entropy (output looks overly repetitive).",
            evidence={"avg_entropy_norm": avg_entropy, "threshold": d.get("min_entropy_norm")},
        ))

    if ttr_bad > 0:
        sanctions.append(Sanction(
            id="low_ttr",
            severity="WARN",
            message="Low token type-token ratio (low vocabulary diversity).",
            evidence={"avg_ttr": avg_ttr, "threshold": d.get("min_ttr")},
        ))

    if gzip_bad > 0:
        sanctions.append(Sanction(
            id="low_gzip_ratio",
            severity="WARN",
            message="Low gzip ratio (too compressible => likely template/copy heavy).",
            evidence={"avg_gzip_ratio": avg_gz, "threshold": d.get("min_gzip_ratio")},
        ))

    if dup_bundle_bad > 0:
        sev = "SEVERE" if dup_ratio_bundle >= to_float(d.get("dup_ratio_bundle_severe", 0.18), 0.18) else "WARN"
        sanctions.append(Sanction(
            id="bundle_duplication",
            severity=sev,
            message="Bundle-level duplication detected (shared fingerprints across files).",
            evidence={"dup_ratio_bundle": dup_ratio_bundle},
        ))

    if exact_dup_files > 0:
        sanctions.append(Sanction(
            id="exact_duplicates",
            severity="SEVERE" if exact_dup_files >= 6 else "WARN",
            message="Exact duplicate files detected (normalized content hash).",
            evidence={"exact_dup_files": exact_dup_files},
        ))

    if py_ast_dup_files > 0:
        sanctions.append(Sanction(
            id="python_ast_duplicates",
            severity="WARN",
            message="Python AST structural duplicates detected.",
            evidence={"py_ast_dup_files": py_ast_dup_files},
        ))

    if (near_warn_pairs + near_sev_pairs) > 0:
        sanctions.append(Sanction(
            id="near_duplicates",
            severity="WARN" if near_sev_pairs > 0 else "INFO",
            message="Near-duplicate pairs detected via SimHash.",
            evidence={"near_dup_warn_pairs": near_warn_pairs, "near_dup_severe_pairs": near_sev_pairs},
        ))

    if added_bad > 0:
        sanctions.append(Sanction(
            id="added_files_volume",
            severity="SEVERE" if added_files >= added_sev else "WARN",
            message="High number of added files (possible scaffolding spam).",
            evidence={"added_files": added_files, "warn": added_warn, "severe": added_sev},
        ))

    if dir_bad > 0:
        sanctions.append(Sanction(
            id="dir_explosion",
            severity="SEVERE" if worst_dir_count >= dir_sev else "WARN",
            message="Single directory concentration is high (directory explosion).",
            evidence={"worst_dir_added_count": worst_dir_count, "warn": dir_warn, "severe": dir_sev},
        ))

    if bloat_bad > 0:
        sanctions.append(Sanction(
            id="single_file_bloat",
            severity="SEVERE" if max_loc >= loc_sev else "WARN",
            message="Single-file LOC bloat detected.",
            evidence={"max_file_loc": max_loc, "warn": loc_warn, "severe": loc_sev},
        ))

    breakdown = {
        "baseline": round(baseline, 6),
        "entropy_bad": round(entropy_bad, 6),
        "ttr_bad": round(ttr_bad, 6),
        "gzip_bad": round(gzip_bad, 6),
        "dup_bundle_bad": round(dup_bundle_bad, 6),
        "file_dup_bad": round(file_dup_bad, 6),
        "exact_bad": round(exact_bad, 6),
        "ast_bad": round(ast_bad, 6),
        "near_bad": round(near_bad, 6),
        "added_bad": round(added_bad, 6),
        "dir_bad": round(dir_bad, 6),
        "bloat_bad": round(bloat_bad, 6),
        "secrets_bad": round(secrets_bad, 6),
        "weights": d.get("weights", {}),
    }

    return float(score), sanctions, breakdown


# -------------------------
# Report render
# -------------------------

def render_md(result: Result100x) -> str:
    lines: list[str] = []
    lines.append(f"# Evolutionary Sanctions (Compat 100x) — {result.policy_version}")
    lines.append("")
    lines.append(f"- **computed_at_utc:** {result.computed_at_utc}")
    lines.append(f"- **run_id:** `{result.run_id}`")
    lines.append(f"- **worker_id:** `{result.worker_id}`")
    lines.append(f"- **sanction_score (lower is better):** `{result.sanction_score}`")
    lines.append(f"- **sanction_level:** **{result.sanction_level}**")
    lines.append(f"- **vdi:** `{result.vdi}`")
    lines.append(f"- **loc_delta:** `{result.loc_delta}`")
    lines.append(f"- **changed_files_count:** `{result.changed_files_count}`")
    lines.append("")
    lines.append("## Bundle Metrics")
    for k, v in result.bundle_metrics.items():
        if isinstance(v, dict):
            lines.append(f"- **{k}:**")
            for kk, vv in v.items():
                lines.append(f"  - `{kk}`: `{vv}`")
        else:
            lines.append(f"- **{k}:** `{v}`")
    lines.append("")
    lines.append("## Sanctions")
    if not result.sanctions:
        lines.append("- (none)")
    else:
        for s in result.sanctions:
            lines.append(f"- **[{s.severity}] {s.id}** — {s.message}")
            if s.evidence:
                ev = json.dumps(s.evidence, ensure_ascii=False, indent=2)
                lines.append("  ```json")
                lines.append(textwrap.indent(ev, "  ").strip())
                lines.append("  ```")
    lines.append("")
    lines.append("## Top Duplicate Pairs")
    if not result.top_duplicate_pairs:
        lines.append("- (none)")
    else:
        for p in result.top_duplicate_pairs:
            lines.append(f"- `{p['sim_min']}` overlap `{p['overlap']}` :: **{p['a']}** ↔ **{p['b']}**")
    lines.append("")
    lines.append("## Top Risk Files (sample)")
    if not result.top_files:
        lines.append("- (none)")
    else:
        for f in result.top_files[:30]:
            lines.append(
                f"- **{f['file']}** | loc `{f['loc']}` | dup `{f['dup_ratio']}` | H `{f['entropy_norm']}` | "
                f"TTR `{f['ttr']}` | gz `{f['gzip_ratio']}` | secrets `{f['secrets_hits']}`"
            )
    lines.append("")
    return "\n".join(lines)


# -------------------------
# Main engine
# -------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="Repo root (unused for now but required by contract).")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--worker-id", required=True)
    ap.add_argument("--bundle-dir", required=True, help="Worker bundle root (run_id/worker).")
    ap.add_argument("--policy", required=False, help="Optional guardrails policy.json path.")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    bundle_root = Path(args.bundle_dir).resolve()
    policy = load_policy(Path(args.policy).resolve() if args.policy else None)

    computed_at = now_utc_iso()
    run_id = str(args.run_id)
    worker_id = str(args.worker_id)

    # Always write something (never let validator fall back just because of an exception)
    try:
        # Baseline from FILES_CHANGED (VDI spirit)
        fc = read_files_changed(bundle_root)
        changes = extract_changes(fc)
        vdi, loc_delta_changes, dup_new, concentration, structural_div, behavioral_delta, worst_dir, worst_dir_count = compute_vdi_from_changes(changes)
        changed_files_count = 0
        if changes:
            uniq = set()
            for it in changes:
                p = str(it.get("path", it.get("relpath", ""))).replace("\\", "/").strip()
                if p:
                    uniq.add(p)
            changed_files_count = len(uniq)

        # Prefer patch LOC delta if available (matches validator effective_loc logic)
        patch_loc = count_patch_added_loc(bundle_root / "DIFF.patch")
        loc_delta = max(loc_delta_changes, patch_loc)

        # Added files estimate (FILES_CHANGED shape is not guaranteed; best-effort)
        added_files = 0
        if isinstance(fc.get("added"), list):
            added_files += len(fc["added"])
        # Also infer from changes if they include status
        for it in changes:
            st = str(it.get("status", "")).upper()
            if st.startswith("A"):
                added_files += 1

        # Scan code output
        source_root = pick_source_root(bundle_root)
        files, metrics, pairs, top_files_payload, scan_sanctions = scan_source_tree(source_root, policy)

        # Risk-sort top files payload
        def file_risk(f: FileMetrics) -> float:
            r = 0.0
            r += f.dup_ratio * 2.2
            if f.token_count > 0:
                r += (1.0 - f.entropy_norm) * 1.2
                r += (1.0 - f.ttr) * 0.6
            r += min(2.0, f.secrets_hits * 1.0)
            if f.loc >= to_int(policy["defaults"].get("single_file_loc_warn", 2200), 2200):
                r += 0.8
            if f.loc >= to_int(policy["defaults"].get("single_file_loc_severe", 4200), 4200):
                r += 1.2
            return r

        files_sorted = sorted(files, key=file_risk, reverse=True)
        top_n = to_int(policy["defaults"].get("top_files", 60), 60)
        top_files_payload = [
            {
                "file": f.relpath,
                "loc": f.loc,
                "tokens": f.token_count,
                "dup_ratio": round(f.dup_ratio, 4),
                "entropy_norm": round(f.entropy_norm, 4),
                "ttr": round(f.ttr, 4),
                "gzip_ratio": round(f.gzip_ratio, 4),
                "secrets_hits": f.secrets_hits,
                "py_ast_sig": f.py_ast_sig,
                "py_complexity": f.py_complexity,
            }
            for f in files_sorted[:top_n]
        ]

        # Score
        score, sanctions, breakdown = compute_sanction_score(
            policy=policy,
            changes_vdi=vdi,
            duplication_ratio_new=dup_new,
            concentration=concentration,
            structural_div=structural_div,
            behavioral_delta=behavioral_delta,
            loc_delta_changes=loc_delta_changes,
            added_files=added_files,
            worst_dir_count=worst_dir_count,
            metrics=metrics,
            file_metrics=files,
        )

        # Include scan-time sanctions too
        sanctions = [*scan_sanctions, *sanctions]

        ok_max = to_float(policy["defaults"].get("ok_max", 0.6), 0.6)
        warn_max = to_float(policy["defaults"].get("warn_max", 1.2), 1.2)
        level = score_level(score, ok_max, warn_max)

        bundle_metrics = dict(metrics)
        bundle_metrics["delta"] = {
            "repo_root": repo_root.as_posix(),
            "bundle_root": bundle_root.as_posix(),
            "source_root": source_root.as_posix(),
            "vdi_inputs": {
                "duplication_ratio_new": round(dup_new, 6),
                "concentration": round(concentration, 6),
                "structural_diversity": round(structural_div, 6),
                "behavioral_delta": round(behavioral_delta, 6),
                "worst_dir": worst_dir,
                "worst_dir_count": worst_dir_count,
                "added_files_estimate": int(added_files),
                "loc_delta_changes": int(loc_delta_changes),
                "loc_delta_patch": int(patch_loc),
            },
            "score_breakdown": breakdown,
        }

        result = Result100x(
            run_id=run_id,
            worker_id=worker_id,
            computed_at_utc=computed_at,
            policy_version=str(policy.get("version", "unknown")),
            sanction_score=round(float(score), 6),
            sanction_level=level,
            vdi=round(float(vdi), 6),
            loc_delta=int(loc_delta),
            changed_files_count=int(changed_files_count),
            bundle_metrics=bundle_metrics,
            sanctions=sanctions,
            top_duplicate_pairs=pairs,
            top_files=top_files_payload,
        )

    except Exception as e:
        # Hard fallback: still write required artifacts (engine must not break the validator loop)
        progress(f"[evo_sanctions] ERROR: {e!r} — writing fail-safe artifacts.")
        result = Result100x(
            run_id=run_id,
            worker_id=worker_id,
            computed_at_utc=computed_at,
            policy_version=str(policy.get("version", "unknown")),
            sanction_score=2.0,
            sanction_level="SEVERE",
            vdi=0.0,
            loc_delta=count_patch_added_loc(bundle_root / "DIFF.patch"),
            changed_files_count=0,
            bundle_metrics={"error": repr(e)},
            sanctions=[Sanction(id="engine_exception", severity="SEVERE", message="Engine exception; produced fail-safe outputs.", evidence={"error": repr(e)})],
            top_duplicate_pairs=[],
            top_files=[],
        )

    # -----------------------------
    # Write REQUIRED compat artifacts
    # -----------------------------
    report = {
        "run_id": result.run_id,
        "worker_id": result.worker_id,
        "computed_at_utc": result.computed_at_utc,
        "repo_dir": str(repo_root.as_posix()),
        "bundle_dir": str(bundle_root.as_posix()),
        "loc_delta": int(result.loc_delta),
        "changed_files_count": int(result.changed_files_count),
        "vdi": float(result.vdi),
        "sanction_score": float(result.sanction_score),
        "sanction_level": str(result.sanction_level),
        "bundle_metrics": result.bundle_metrics,
        "sanctions": [asdict(s) for s in result.sanctions],
        "top_duplicate_pairs": result.top_duplicate_pairs,
        "top_files": result.top_files,
        "flags": ["AUTOSANCTION_ENGINE", "AUTOSANCTION_ENGINE_100X"],  # NO "STUB" token here
    }

    score_payload = {
        "run_id": result.run_id,
        "worker_id": result.worker_id,
        "computed_at_utc": result.computed_at_utc,
        "sanction_score": float(result.sanction_score),
        "sanction_level": str(result.sanction_level),
        "vdi": float(result.vdi),
        "loc_delta": int(result.loc_delta),
        "notes": ["AUTOSANCTION_ENGINE", "AUTOSANCTION_ENGINE_100X"],
    }

    json_write(bundle_root / "SELF_EVAL_REPORT.json", report)
    json_write(bundle_root / "SANCTION_SCORE.json", score_payload)

    jsonl_append(
        bundle_root / "SELF_CORRECTION_LOG.jsonl",
        {
            "run_id": result.run_id,
            "worker_id": result.worker_id,
            "computed_at_utc": result.computed_at_utc,
            "sanction_score": float(result.sanction_score),
            "sanction_level": str(result.sanction_level),
            "vdi": float(result.vdi),
            "loc_delta": int(result.loc_delta),
            "flags": ["AUTOSANCTION_ENGINE", "AUTOSANCTION_ENGINE_100X"],
        },
    )

    # -----------------------------
    # Extras (non-breaking)
    # -----------------------------
    json_write(bundle_root / "SANCTIONS_RESULT.json", asdict(result))
    (bundle_root / "SANCTIONS_REPORT.md").write_text(render_md(result), encoding="utf-8", newline="\n")

    progress(f"[evo_sanctions] OK wrote SELF_EVAL_REPORT.json + SANCTION_SCORE.json + SELF_CORRECTION_LOG.jsonl (score={result.sanction_score}, level={result.sanction_level})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
