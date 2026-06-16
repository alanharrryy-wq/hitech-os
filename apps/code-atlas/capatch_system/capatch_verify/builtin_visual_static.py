from __future__ import annotations

"""Static visual verifier with baseline/delta awareness.

This gate is intentionally conservative about *new* visual hazards and forgiving
about legacy debt that already existed before the patch. It is designed for large
CSS files such as PRISMA Tablet POS styles where historical debt should be
reported as warning metadata, not as a hard failure for unrelated surgical edits.
"""

from collections import Counter
import os
import re
from pathlib import Path
from typing import Any

from .base import VerifierResultRow, existing_target_files

IMPORTANT_RE = re.compile(r"!important\b", re.IGNORECASE)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
DECLARATION_RE = re.compile(r"(?P<prop>-{0,2}[A-Za-z_][\w-]*)\s*:\s*(?P<value>[^;{}]+)", re.DOTALL)
DARK_TOKEN_RE = re.compile(r"(?i)(#000(?:000)?\b|#050505\b|#0b0b0b\b|#111\b|\bblack\b)")
VISUAL_SUFFIXES = {".css", ".scss", ".sass", ".tsx", ".jsx"}
DEFAULT_IMPORTANT_ABSOLUTE_LIMIT = 8
DEFAULT_IMPORTANT_DELTA_LIMIT = 2
DEFAULT_LEGACY_IMPORTANT_LIMIT = 50
DEFAULT_LEGACY_LINE_LIMIT = 1000
RISKY_VISUAL_PROPS = {
    "color",
    "background",
    "background-color",
    "background-image",
    "border",
    "border-color",
    "outline",
    "outline-color",
    "box-shadow",
    "text-shadow",
    "fill",
    "stroke",
    "caret-color",
}


def _as_int(value: Any, default: int) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return int(default)


def _ctx_int(ctx: dict[str, Any], key: str, env_key: str, default: int) -> int:
    if key in (ctx or {}):
        return _as_int((ctx or {}).get(key), default)
    return _as_int(os.environ.get(env_key, default), default)


def _strip_comments(text: str) -> str:
    return COMMENT_RE.sub("", text or "")


def _count_important(text: str) -> int:
    return len(IMPORTANT_RE.findall(text or ""))


def _is_tablet_surface(path: Path, ctx: dict[str, Any]) -> bool:
    lowered = path.as_posix().lower().replace("\\", "/")
    if "tablet" in lowered or "products/tablet" in lowered:
        return True
    surface = str((ctx or {}).get("surface") or (ctx or {}).get("capatch_surface") or "").lower()
    return surface == "tablet" or "tablet" in surface


def _is_mask_declaration(prop: str, value: str) -> bool:
    prop_l = str(prop or "").strip().lower()
    value_l = str(value or "").lower()
    return "mask" in prop_l or "-webkit-mask" in prop_l or " mask" in value_l


def _is_risky_visual_prop(prop: str) -> bool:
    prop_l = str(prop or "").strip().lower().lstrip("-")
    if "mask" in prop_l:
        return False
    return (
        prop_l in RISKY_VISUAL_PROPS
        or prop_l.startswith("border-")
        or prop_l.endswith("-color")
        or "shadow" in prop_l
        or prop_l in {"background-size", "background-position"}
    )


def _dark_declaration_hits(text: str) -> tuple[list[str], list[str]]:
    risky: list[str] = []
    ignored_mask: list[str] = []
    source = _strip_comments(text or "")
    for match in DECLARATION_RE.finditer(source):
        prop = str(match.group("prop") or "").strip()
        value = str(match.group("value") or "")
        tokens = [m.group(0) for m in DARK_TOKEN_RE.finditer(value)]
        if not tokens:
            continue
        for token in tokens:
            normalized = f"{prop}:{token}"
            if _is_mask_declaration(prop, value):
                ignored_mask.append(normalized)
            elif _is_risky_visual_prop(prop):
                risky.append(normalized)
    return risky, ignored_mask


def _counter_delta(after_items: list[str], before_items: list[str]) -> list[str]:
    before = Counter(before_items or [])
    added: list[str] = []
    for item, count in Counter(after_items or []).items():
        extra = count - before.get(item, 0)
        if extra > 0:
            added.extend([item] * extra)
    return sorted(added)


def _normalize_key(path: Path, root_dir: Path | None) -> list[str]:
    keys = [path.as_posix(), str(path), path.name]
    try:
        if root_dir is not None:
            keys.append(path.resolve().relative_to(root_dir.resolve()).as_posix())
    except Exception:
        pass
    return list(dict.fromkeys(keys))


def _read_mapping_baseline(path: Path, root_dir: Path | None, ctx: dict[str, Any]) -> str | None:
    map_names = (
        "visual_baseline_by_target",
        "baseline_text_by_target",
        "before_content_by_target",
        "before_text_by_target",
    )
    keys = _normalize_key(path, root_dir)
    for map_name in map_names:
        mapping = (ctx or {}).get(map_name)
        if not isinstance(mapping, dict):
            continue
        for key in keys:
            if key in mapping:
                value = mapping.get(key)
                if value is not None:
                    return str(value)
    return None


def _read_checkpoint_baseline(path: Path, root_dir: Path | None, ctx: dict[str, Any]) -> str | None:
    checkpoint_value = str((ctx or {}).get("checkpoint_dir") or "").strip()
    if not checkpoint_value or root_dir is None:
        return None
    try:
        checkpoint_dir = Path(checkpoint_value).expanduser().resolve()
        relative = path.resolve().relative_to(root_dir.resolve())
        candidate = checkpoint_dir / relative
        if candidate.exists() and candidate.is_file():
            return candidate.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    return None


def _baseline_text(path: Path, ctx: dict[str, Any]) -> str | None:
    root_value = str((ctx or {}).get("root_dir") or "").strip()
    root_dir = Path(root_value).expanduser().resolve() if root_value else None
    mapped = _read_mapping_baseline(path, root_dir, ctx)
    if mapped is not None:
        return mapped
    return _read_checkpoint_baseline(path, root_dir, ctx)


def _is_legacy_debt(text: str, important_count: int, ctx: dict[str, Any]) -> bool:
    legacy_important_limit = _ctx_int(ctx, "visual_legacy_important_limit", "CAPATCH_VISUAL_LEGACY_IMPORTANT_LIMIT", DEFAULT_LEGACY_IMPORTANT_LIMIT)
    legacy_line_limit = _ctx_int(ctx, "visual_legacy_line_limit", "CAPATCH_VISUAL_LEGACY_LINE_LIMIT", DEFAULT_LEGACY_LINE_LIMIT)
    return important_count >= legacy_important_limit or len((text or "").splitlines()) >= legacy_line_limit


def _analyze_file(path: Path, ctx: dict[str, Any]) -> dict[str, Any]:
    after_text = path.read_text(encoding="utf-8", errors="replace")
    before_text = _baseline_text(path, ctx)
    after_imp = _count_important(after_text)
    before_imp = _count_important(before_text) if before_text is not None else None
    important_delta = after_imp - before_imp if before_imp is not None else None
    after_dark, after_mask_ignored = _dark_declaration_hits(after_text)
    before_dark, _before_mask_ignored = _dark_declaration_hits(before_text or "") if before_text is not None else ([], [])
    new_dark = _counter_delta(after_dark, before_dark) if before_text is not None else list(after_dark)
    delta_limit = _ctx_int(ctx, "visual_important_delta_limit", "CAPATCH_VISUAL_IMPORTANT_DELTA_LIMIT", DEFAULT_IMPORTANT_DELTA_LIMIT)
    absolute_limit = _ctx_int(ctx, "visual_important_absolute_limit", "CAPATCH_VISUAL_IMPORTANT_ABSOLUTE_LIMIT", DEFAULT_IMPORTANT_ABSOLUTE_LIMIT)
    issues: list[str] = []
    warnings: list[str] = []
    legacy = _is_legacy_debt(after_text, after_imp, ctx)

    if before_text is not None:
        if before_imp and before_imp > absolute_limit:
            warnings.append(f"legacy !important debt already existed: {before_imp}")
        if important_delta is not None and important_delta > delta_limit:
            issues.append(f"too many new !important declarations: +{important_delta} (limit {delta_limit})")
    else:
        if after_imp > absolute_limit:
            if legacy:
                warnings.append(f"legacy visual debt without baseline: {after_imp} !important declarations")
            else:
                issues.append(f"too many !important declarations without baseline: {after_imp}")

    if _is_tablet_surface(path, ctx):
        if before_text is not None:
            if new_dark:
                issues.append("new risky dark Tablet theme tokens: " + ", ".join(sorted(set(new_dark))[:8]))
            elif after_dark:
                warnings.append("legacy risky dark Tablet tokens already existed: " + ", ".join(sorted(set(after_dark))[:8]))
        elif after_dark:
            if legacy:
                warnings.append("legacy risky dark Tablet tokens without baseline: " + ", ".join(sorted(set(after_dark))[:8]))
            else:
                issues.append("possible accidental dark Tablet theme tokens: " + ", ".join(sorted(set(after_dark))[:8]))

    if after_mask_ignored:
        warnings.append(f"ignored mask-only dark tokens: {len(after_mask_ignored)}")

    return {
        "ok": not issues,
        "issues": issues,
        "warnings": warnings,
        "baseline_available": before_text is not None,
        "important_count": after_imp,
        "baseline_important_count": before_imp,
        "important_delta": important_delta,
        "important_delta_limit": delta_limit,
        "dark_hits": sorted(set(after_dark))[:50],
        "new_dark_hits": sorted(set(new_dark))[:50],
        "mask_dark_hits_ignored": sorted(set(after_mask_ignored))[:50],
        "legacy_debt": legacy,
        "line_count": len((after_text or "").splitlines()),
    }


def run_visual_static_gates(target_files: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() not in VISUAL_SUFFIXES:
            continue
        analysis = _analyze_file(path, dict(ctx or {}))
        issues = list(analysis.get("issues") or [])
        warnings = list(analysis.get("warnings") or [])
        ok = bool(analysis.get("ok"))
        if issues:
            detail = "; ".join(issues)
        elif warnings:
            detail = "warnings: " + "; ".join(warnings)
        else:
            detail = "Visual static gates passed"
        rows.append(
            VerifierResultRow(
                "visual-static-gates",
                ok,
                f"Visual static gates {'OK' if ok else 'failed'}: {path.name}",
                detail,
                metrics={
                    "file": str(path),
                    "baseline_available": analysis.get("baseline_available"),
                    "important_count": analysis.get("important_count"),
                    "baseline_important_count": analysis.get("baseline_important_count"),
                    "important_delta": analysis.get("important_delta"),
                    "important_delta_limit": analysis.get("important_delta_limit"),
                    "legacy_debt": analysis.get("legacy_debt"),
                    "warnings": warnings,
                    "issues": issues,
                    "dark_hits": analysis.get("dark_hits"),
                    "new_dark_hits": analysis.get("new_dark_hits"),
                    "mask_dark_hits_ignored": analysis.get("mask_dark_hits_ignored"),
                    "line_count": analysis.get("line_count"),
                    "mode": "delta" if analysis.get("baseline_available") else "absolute-or-legacy-warning",
                },
                severity_if_failed="error",
            ).to_dict()
        )
    if not rows:
        rows.append(
            VerifierResultRow(
                "visual-static-gates",
                True,
                "Visual static gates skipped",
                "No visual target files were provided.",
                severity_if_failed="warning",
            ).to_dict()
        )
    return rows
