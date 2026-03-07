from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


TOOL_VERSION = "2.0.0"
SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}


DEFAULT_CONFIG: dict[str, Any] = {
    "include_extensions": [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"],
    "exclude_dirs": [
        ".git",
        "node_modules",
        ".next",
        ".turbo",
        "dist",
        "build",
        "coverage",
        "_reports",
        "_scaffold",
        "tools/codex/runs",
        "tools/codex/worktrees",
        "scripts/hydration_guard_bundle",
    ],
    "ignore_path_globs": [
        "**/__tests__/**",
        "**/*.test.*",
        "**/*.spec.*",
        "**/*.stories.*",
        "**/*.generated.*",
        "**/*.gen.*",
        "**/*.snap",
        "**/fixtures/**",
        "**/__snapshots__/**",
        "**/vendor/**",
    ],
    "internal_tooling_globs": [
        "apps/keystone/app/dev/**",
        "apps/keystone/components/**/debug/**",
        "apps/keystone/components/**/devtools/**",
        "apps/keystone/components/**/internal-tooling/**",
        "apps/keystone/components/**/scene-studio/**",
        "apps/keystone/app/dev/**/scene-studio/**",
        "tools/**",
        "packages/tooling/**",
    ],
    "allow": {
        "dynamic_ssr_false": [
            "apps/keystone/app/dev/**",
            "apps/keystone/components/**/debug/**",
            "apps/keystone/components/**/devtools/**",
            "apps/keystone/components/**/internal-tooling/**",
        ],
        "suppress_hydration_warning": [
            "apps/keystone/app/dev/**",
            "apps/keystone/components/**/debug/**",
            "apps/keystone/components/**/devtools/**",
        ],
        "use_client_root_route": [
            "apps/keystone/app/dev/**",
        ],
        "server_to_client_import_hint": [
            "apps/keystone/app/dev/**",
            "apps/keystone/components/**/debug/**",
            "apps/keystone/components/**/devtools/**",
        ],
    },
    "browser_api_tokens": [
        "window",
        "document",
        "localStorage",
        "sessionStorage",
        "navigator",
        "matchMedia",
        "requestAnimationFrame",
    ],
    "dom_mutation_signatures": [
        "field_signature",
        "form_signature",
        "alternative_form_signature",
        "visibility_annotation",
    ],
    "baseline_file": "tools/hydration_sentinel/baseline.json",
    "report_top_n": 30,
}


DYNAMIC_SSR_FALSE_RE = re.compile(
    r"dynamic\s*\([\s\S]{0,700}?\{[\s\S]{0,400}?\bssr\s*:\s*false\b",
    re.MULTILINE,
)
SUPPRESS_HYDRATION_RE = re.compile(r"\bsuppressHydrationWarning\b")
HYDRATION_KEYWORD_RE = re.compile(r"\bhydrat(?:e|ion|ing)\b", re.IGNORECASE)
IMPORT_RE = re.compile(
    r"^\s*import(?:[\s\S]*?)from\s*['\"](?P<target>[^'\"]+)['\"]",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Finding:
    key: str
    category: str
    severity: str
    file: str
    line: int
    column: int
    snippet: str
    message: str
    route_scope: str
    allowlisted: bool = False


def detect_repo_root(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).resolve()

    try:
        probe = Path(__file__).resolve()
    except NameError:
        probe = Path.cwd()

    start = probe if probe.is_dir() else probe.parent
    current = start

    markers = ("package.json", "pnpm-workspace.yaml", ".git")
    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent

    return Path.cwd().resolve()


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def matches_any(path_text: str, patterns: list[str]) -> bool:
    normalized = path_text.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pattern.replace("\\", "/")) for pattern in patterns)


def severity_value(severity: str) -> int:
    return SEVERITY_ORDER.get(severity, 0)


def print_progress(current: int, total: int, label: str) -> None:
    total = max(total, 1)
    width = 28
    filled = int(width * (current / total))
    bar = "#" * filled + "." * (width - filled)
    sys.stdout.write(f"\r[{bar}] {current}/{total} {label[:70]}")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")


def is_page_layout_template(rel_path: str) -> bool:
    return bool(
        re.search(r"(^|/)app/.+/(page|layout|template)\.(ts|tsx|js|jsx|mjs|cjs)$", rel_path)
    )


def has_use_client(text: str) -> bool:
    allowed = {"'use client'", '"use client"', "'use client';", '"use client";'}
    for raw_line in text.splitlines()[:20]:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("//") or line.startswith("/*") or line.startswith("*"):
            continue
        return line in allowed
    return False


def line_col_for_offset(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    last_newline = text.rfind("\n", 0, offset)
    column = (offset + 1) if last_newline == -1 else (offset - last_newline)
    return line, column


def build_key(
    category: str,
    severity: str,
    file_path: str,
    line: int,
    message: str,
    snippet: str,
) -> str:
    raw = f"{category}|{severity}|{file_path}|{line}|{message}|{snippet}".encode("utf-8", "ignore")
    return hashlib.sha1(raw).hexdigest()


def classify_route_scope(rel_path: str, config: dict[str, Any]) -> str:
    if matches_any(rel_path, config["internal_tooling_globs"]):
        return "internal-tooling"
    if "/app/" in rel_path or rel_path.startswith("apps/"):
        return "app-surface"
    return "neutral"


def allowlisted(category: str, rel_path: str, config: dict[str, Any]) -> bool:
    patterns = config.get("allow", {}).get(category, [])
    return matches_any(rel_path, patterns)


def browser_api_hits(text: str, tokens: list[str]) -> list[tuple[str, int]]:
    hits: list[tuple[str, int]] = []
    for token in tokens:
        pattern = re.compile(rf"\b{re.escape(token)}\b")
        for match in pattern.finditer(text):
            hits.append((token, match.start()))
    hits.sort(key=lambda item: item[1])
    return hits


def discover_files(root: Path, config: dict[str, Any], max_files: int | None = None) -> tuple[list[Path], int]:
    include_extensions = set(config["include_extensions"])
    skipped = 0
    collected: list[Path] = []

    for current_root, dirs, files in os.walk(root):
        current_path = Path(current_root)
        rel_dir = rel_posix(current_path, root) if current_path != root else ""
        normalized_dir = rel_dir.replace("\\", "/")

        pruned: list[str] = []
        for directory in dirs:
            candidate_rel = f"{normalized_dir}/{directory}".strip("/")
            if any(
                candidate_rel == ex or candidate_rel.startswith(f"{ex}/")
                for ex in [d.replace("\\", "/") for d in config["exclude_dirs"]]
            ):
                skipped += 1
                continue
            pruned.append(directory)
        dirs[:] = pruned

        for file_name in files:
            full_path = current_path / file_name
            rel_path = rel_posix(full_path, root)

            if full_path.suffix not in include_extensions:
                skipped += 1
                continue
            if matches_any(rel_path, config["ignore_path_globs"]):
                skipped += 1
                continue

            collected.append(full_path)
            if max_files and len(collected) >= max_files:
                return sorted(collected), skipped

    return sorted(collected), skipped


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def build_client_index(files: list[Path], root: Path) -> dict[str, bool]:
    index: dict[str, bool] = {}
    total = len(files)
    for idx, file_path in enumerate(files, start=1):
        if idx == 1 or idx == total or idx % 250 == 0:
            print_progress(idx, total, f"Indexando client files: {rel_posix(file_path, root)}")
        text = read_text(file_path)
        index[rel_posix(file_path, root)] = has_use_client(text)
    return index


def resolve_relative_import(source_rel: str, target: str, root: Path, config: dict[str, Any]) -> str | None:
    if not target.startswith("."):
        return None

    source_dir = (root / source_rel).parent
    candidate_base = (source_dir / target).resolve()

    extensions = config["include_extensions"]
    candidates: list[Path] = [candidate_base]

    if candidate_base.suffix == "":
        for ext in extensions:
            candidates.append(candidate_base.with_suffix(ext))
        for ext in extensions:
            candidates.append(candidate_base / f"index{ext}")

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return rel_posix(candidate, root)

    return None


def make_finding(
    findings: list[Finding],
    category: str,
    severity: str,
    rel_path: str,
    line: int,
    column: int,
    snippet: str,
    message: str,
    route_scope: str,
    allowlist_hit: bool = False,
) -> None:
    normalized_snippet = " ".join(snippet.strip().split())
    key = build_key(category, severity, rel_path, line, message, normalized_snippet)
    findings.append(
        Finding(
            key=key,
            category=category,
            severity=severity,
            file=rel_path,
            line=line,
            column=column,
            snippet=normalized_snippet[:260],
            message=message,
            route_scope=route_scope,
            allowlisted=allowlist_hit,
        )
    )


def analyze_file(
    file_path: Path,
    root: Path,
    text: str,
    config: dict[str, Any],
    client_index: dict[str, bool],
    findings: list[Finding],
) -> None:
    rel_path = rel_posix(file_path, root)
    route_scope = classify_route_scope(rel_path, config)
    is_client_file = client_index.get(rel_path, False)
    pageish = is_page_layout_template(rel_path)
    internal = route_scope == "internal-tooling"

    for match in DYNAMIC_SSR_FALSE_RE.finditer(text):
        line, col = line_col_for_offset(text, match.start())
        allowlist_hit = allowlisted("dynamic_ssr_false", rel_path, config)
        severity = "low" if allowlist_hit else ("high" if pageish else "medium")
        message = (
            "dynamic(..., { ssr:false }) detectado. Confirma que el scope sea estrecho y solo para tooling interno."
        )
        make_finding(
            findings,
            "dynamic_ssr_false",
            severity,
            rel_path,
            line,
            col,
            match.group(0),
            message,
            route_scope,
            allowlist_hit,
        )
        if pageish and not allowlist_hit:
            make_finding(
                findings,
                "risky_broad_workaround",
                "high",
                rel_path,
                line,
                col,
                match.group(0),
                "ssr:false en page/layout/template. Esto huele a workaround ancho. Revísalo con lupa.",
                route_scope,
                False,
            )

    for match in SUPPRESS_HYDRATION_RE.finditer(text):
        line, col = line_col_for_offset(text, match.start())
        allowlist_hit = allowlisted("suppress_hydration_warning", rel_path, config)
        severity = "low" if allowlist_hit else ("high" if pageish else "medium")
        message = (
            "suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado."
        )
        make_finding(
            findings,
            "suppress_hydration_warning",
            severity,
            rel_path,
            line,
            col,
            match.group(0),
            message,
            route_scope,
            allowlist_hit,
        )
        if pageish and not allowlist_hit:
            make_finding(
                findings,
                "risky_broad_workaround",
                "high",
                rel_path,
                line,
                col,
                match.group(0),
                "suppressHydrationWarning en page/layout/template. Esto puede esconder mismatch real.",
                route_scope,
                False,
            )

    if is_client_file and pageish:
        allowlist_hit = allowlisted("use_client_root_route", rel_path, config)
        severity = "low" if allowlist_hit else "medium"
        make_finding(
            findings,
            "use_client_root_route",
            severity,
            rel_path,
            1,
            1,
            "'use client'",
            "'use client' en page/layout/template. Verifica si de verdad necesitas subir el boundary tan arriba.",
            route_scope,
            allowlist_hit,
        )

    for token, offset in browser_api_hits(text, config["browser_api_tokens"]):
        if is_client_file:
            continue
        line, col = line_col_for_offset(text, offset)
        severity = "medium" if (pageish or internal) else "low"
        make_finding(
            findings,
            "browser_api_in_non_client",
            severity,
            rel_path,
            line,
            col,
            token,
            f"Uso de browser API `{token}` en archivo sin 'use client'. Revisa boundary y flujo SSR/CSR.",
            route_scope,
            False,
        )
        if internal:
            make_finding(
                findings,
                "client_boundary_hint",
                "low",
                rel_path,
                line,
                col,
                token,
                "Tooling interno con browser API en archivo no-client. Candidato a boundary client-only estrecho.",
                route_scope,
                False,
            )

    for keyword_match in HYDRATION_KEYWORD_RE.finditer(text):
        line, col = line_col_for_offset(text, keyword_match.start())
        make_finding(
            findings,
            "hydration_keyword",
            "info",
            rel_path,
            line,
            col,
            keyword_match.group(0),
            "Keyword de hydration encontrado. Señal de revisión, no fallo por sí sola.",
            route_scope,
            False,
        )

    for signature in config["dom_mutation_signatures"]:
        signature_re = re.compile(rf"\b{re.escape(signature)}\b")
        for match in signature_re.finditer(text):
            line, col = line_col_for_offset(text, match.start())
            make_finding(
                findings,
                "dom_mutation_signature",
                "medium" if internal else "low",
                rel_path,
                line,
                col,
                match.group(0),
                "Firma asociada a mutación del DOM antes de hydration. Suele apuntar a extensiones/autofill/password managers.",
                route_scope,
                False,
            )
            if internal:
                make_finding(
                    findings,
                    "client_boundary_hint",
                    "low",
                    rel_path,
                    line,
                    col,
                    match.group(0),
                    "Firma de mutación externa en tooling interno. Evalúa aislamiento client-only local.",
                    route_scope,
                    False,
                )

    if not is_client_file:
        for import_match in IMPORT_RE.finditer(text):
            target = import_match.group("target")
            resolved = resolve_relative_import(rel_path, target, root, config)
            if not resolved:
                continue
            if not client_index.get(resolved, False):
                continue

            line, col = line_col_for_offset(text, import_match.start())
            allowlist_hit = allowlisted("server_to_client_import_hint", rel_path, config)
            severity = "low" if allowlist_hit else ("medium" if pageish else "low")
            make_finding(
                findings,
                "server_to_client_import_hint",
                severity,
                rel_path,
                line,
                col,
                target,
                (
                    f"Import relativo hacia archivo client `{resolved}` desde archivo sin 'use client'. "
                    "En Next esto puede ser válido, pero conviene revisar boundary, props serializables y scope."
                ),
                route_scope,
                allowlist_hit,
            )


def dedupe_findings(findings: list[Finding]) -> list[Finding]:
    unique: dict[str, Finding] = {}
    for finding in findings:
        unique[finding.key] = finding
    return sorted(
        unique.values(),
        key=lambda item: (-severity_value(item.severity), item.file, item.line, item.column, item.category),
    )


def load_baseline(root: Path, config: dict[str, Any]) -> set[str]:
    baseline_path = root / config["baseline_file"]
    payload = load_json(baseline_path, {"ignore_keys": []})
    keys = payload.get("ignore_keys", []) if isinstance(payload, dict) else []
    return set(keys)


def update_baseline(root: Path, config: dict[str, Any], findings: list[Finding]) -> Path:
    baseline_path = root / config["baseline_file"]
    payload = {
        "tool_version": TOOL_VERSION,
        "ignore_keys": sorted(f.key for f in findings),
    }
    write_json(baseline_path, payload)
    return baseline_path


def build_summary(
    root: Path,
    scanned_files: list[Path],
    skipped_files: int,
    findings: list[Finding],
    baseline_ignored: int,
) -> dict[str, Any]:
    by_category: dict[str, int] = {}
    by_severity: dict[str, int] = {}

    for finding in findings:
        by_category[finding.category] = by_category.get(finding.category, 0) + 1
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1

    return {
        "tool_version": TOOL_VERSION,
        "repo_root": str(root),
        "files_scanned": len(scanned_files),
        "files_skipped": skipped_files,
        "total_findings": len(findings),
        "baseline_ignored": baseline_ignored,
        "by_category": dict(sorted(by_category.items())),
        "by_severity": dict(sorted(by_severity.items(), key=lambda item: severity_value(item[0]))),
    }


def build_recommendations(findings: list[Finding]) -> list[dict[str, str]]:
    categories = {finding.category for finding in findings}
    recs: list[dict[str, str]] = []

    if "risky_broad_workaround" in categories:
        recs.append({
            "priority": "high",
            "title": "Eliminar workarounds anchos en route trees",
            "detail": "Hay señales de ssr:false o suppressHydrationWarning en page/layout/template. Revisa y baja el boundary.",
        })

    if "browser_api_in_non_client" in categories:
        recs.append({
            "priority": "high",
            "title": "Aislar browser APIs fuera de client files",
            "detail": "Se detectaron window/document/localStorage/sessionStorage en archivos sin 'use client'.",
        })

    if "dynamic_ssr_false" in categories:
        recs.append({
            "priority": "medium",
            "title": "Revisar dynamic(..., { ssr:false })",
            "detail": "Confirma que se use solo en tooling interno y con scope estrecho.",
        })

    if "suppress_hydration_warning" in categories:
        recs.append({
            "priority": "medium",
            "title": "Limitar suppressHydrationWarning",
            "detail": "Prefiere root cause local antes que silenciar hydration mismatch a lo bruto.",
        })

    if "client_boundary_hint" in categories or "dom_mutation_signature" in categories:
        recs.append({
            "priority": "medium",
            "title": "Aplicar client-only boundary estrecho en tooling interno con mutación externa",
            "detail": "Ideal para debug panels, HUDs y dev surfaces propensas a mutación pre-hydration.",
        })

    if "use_client_root_route" in categories:
        recs.append({
            "priority": "low",
            "title": "Revisar 'use client' en rutas raíz",
            "detail": "No siempre es malo, pero puede subir demasiado el boundary y ensanchar el costo cliente.",
        })

    if "server_to_client_import_hint" in categories:
        recs.append({
            "priority": "low",
            "title": "Revisar imports server-ish hacia client files",
            "detail": "En Next puede ser válido, pero revisa serialización de props, bundle cost y boundary clarity.",
        })

    if not recs:
        recs.append({
            "priority": "low",
            "title": "Sin alertas fuertes",
            "detail": "No se detectaron patrones graves con las reglas actuales.",
        })

    return recs


def write_markdown_report(
    output_dir: Path,
    summary: dict[str, Any],
    findings: list[Finding],
    recommendations: list[dict[str, str]],
    config: dict[str, Any],
) -> Path:
    top_n = int(config.get("report_top_n", 30))
    risky_paths = sorted({f.file for f in findings if f.category == "risky_broad_workaround"})
    likely_internal_paths = sorted({f.file for f in findings if f.route_scope == "internal-tooling"})[:top_n]

    lines: list[str] = [
        "# Hydration Sentinel Report",
        "",
        f"- Repo root: `{summary['repo_root']}`",
        f"- Files scanned: **{summary['files_scanned']}**",
        f"- Files skipped: **{summary['files_skipped']}**",
        f"- Total findings: **{summary['total_findings']}**",
        f"- Baseline ignored: **{summary['baseline_ignored']}**",
        f"- Tool version: **{summary['tool_version']}**",
        "",
        "## Findings by category",
        "",
    ]

    for category, count in summary["by_category"].items():
        lines.append(f"- `{category}`: {count}")

    lines.extend(["", "## Findings by severity", ""])
    for severity, count in summary["by_severity"].items():
        lines.append(f"- `{severity}`: {count}")

    lines.extend(["", "## Recommendations", ""])
    for rec in recommendations:
        lines.append(f"- **{rec['priority'].upper()}** {rec['title']} -> {rec['detail']}")

    lines.extend(["", "## Likely internal tooling paths", ""])
    if likely_internal_paths:
        for path in likely_internal_paths:
            lines.append(f"- `{path}`")
    else:
        lines.append("- None detected")

    lines.extend(["", "## Risky broad workaround paths", ""])
    if risky_paths:
        for path in risky_paths:
            lines.append(f"- `{path}`")
    else:
        lines.append("- None detected from current heuristics.")

    lines.extend(["", "## Sample findings", ""])
    if findings:
        for finding in findings[:top_n]:
            lines.append(
                f"- **{finding.severity.upper()}** `{finding.category}` in `{finding.file}:{finding.line}` "
                f"-> `{finding.snippet}` | {finding.message}"
            )
    else:
        lines.append("- No findings after baseline filtering.")

    report_path = output_dir / "hydration_sentinel_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return report_path


def save_outputs(
    output_dir: Path,
    summary: dict[str, Any],
    findings: list[Finding],
    recommendations: list[dict[str, str]],
    config: dict[str, Any],
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    findings_path = output_dir / "hydration_sentinel_findings.json"
    summary_path = output_dir / "hydration_sentinel_summary.json"
    recommendations_path = output_dir / "hydration_sentinel_recommendations.json"

    write_json(findings_path, [asdict(finding) for finding in findings])
    write_json(summary_path, summary)
    write_json(recommendations_path, recommendations)
    report_path = write_markdown_report(output_dir, summary, findings, recommendations, config)

    return {
        "report": report_path,
        "summary": summary_path,
        "findings": findings_path,
        "recommendations": recommendations_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hydration Sentinel for HITECH-OS")
    parser.add_argument("--repo-root", default=None, help="Ruta explícita del repo root")
    parser.add_argument("--output-dir", default="_reports/hydration_sentinel", help="Directorio de salida")
    parser.add_argument("--config", default="tools/hydration_sentinel/config.json", help="Ruta del config JSON")
    parser.add_argument("--strict", action="store_true", help="Falla si encuentra medium/high")
    parser.add_argument(
        "--fail-on",
        default="none",
        choices=["none", "low", "medium", "high"],
        help="Umbral mínimo para salir con código distinto de 0",
    )
    parser.add_argument("--update-baseline", action="store_true", help="Escribe baseline con findings actuales")
    parser.add_argument("--max-files", type=int, default=None, help="Limita archivos para smoke testing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    root = detect_repo_root(args.repo_root)
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = root / config_path

    config = deep_merge(DEFAULT_CONFIG, load_json(config_path, {}))
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    print(f"[Hydration Sentinel] repo: {root}")
    print(f"[Hydration Sentinel] config: {config_path}")
    print(f"[Hydration Sentinel] output: {output_dir}")

    files, skipped = discover_files(root, config, max_files=args.max_files)
    print(f"[Hydration Sentinel] archivos a escanear: {len(files)} | omitidos: {skipped}")

    print("[Hydration Sentinel] construyendo índice de client files...")
    client_index = build_client_index(files, root)

    findings: list[Finding] = []
    total = len(files)
    print("[Hydration Sentinel] escaneando reglas...")
    for idx, file_path in enumerate(files, start=1):
        if idx == 1 or idx == total or idx % 200 == 0:
            print_progress(idx, total, f"Analizando: {rel_posix(file_path, root)}")
        text = read_text(file_path)
        analyze_file(file_path, root, text, config, client_index, findings)

    findings = dedupe_findings(findings)

    baseline_keys = load_baseline(root, config)
    baseline_ignored = 0
    if baseline_keys:
        before = len(findings)
        findings = [finding for finding in findings if finding.key not in baseline_keys]
        baseline_ignored = before - len(findings)

    if args.update_baseline:
        baseline_path = update_baseline(root, config, findings)
        print(f"[Hydration Sentinel] baseline actualizada: {baseline_path}")

    recommendations = build_recommendations(findings)
    summary = build_summary(root, files, skipped, findings, baseline_ignored)
    outputs = save_outputs(output_dir, summary, findings, recommendations, config)

    print("")
    print("[Hydration Sentinel] salidas:")
    for name, path in outputs.items():
        print(f"  - {name}: {path}")

    threshold = "medium" if args.strict and args.fail_on == "none" else args.fail_on
    if threshold != "none":
        matches_threshold = [
            finding for finding in findings if severity_value(finding.severity) >= severity_value(threshold)
        ]
        if matches_threshold:
            print(
                f"[Hydration Sentinel] threshold alcanzado: {threshold} | findings: {len(matches_threshold)}",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
