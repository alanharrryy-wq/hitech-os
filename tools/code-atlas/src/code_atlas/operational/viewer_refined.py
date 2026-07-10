# DB_EVIDENCE_CONFIDENCE_SCORE_V01
from __future__ import annotations

import csv
import html
import json
import os
import re
from pathlib import Path
from typing import Any

MAX_EMBED_ROWS_PER_SECTION = int(os.environ.get("DB_EVIDENCE_VIEWER_MAX_ROWS", "750") or "750")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(_read_text(path))
    except Exception:
        return None


def _find_file(root: Path, name: str) -> Path | None:
    for path in root.rglob("*"):
        if path.is_file() and path.name.lower() == name.lower():
            return path
    return None


def _find_csv(root: Path, fragment: str) -> Path | None:
    frag = fragment.lower()
    for path in root.rglob("*.csv"):
        if frag in path.name.lower():
            return path
    return None


def _flatten(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            full = f"{prefix}.{key}" if prefix else str(key)
            rows.append((full, value))
            rows.extend(_flatten(value, full))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            full = f"{prefix}[{index}]"
            rows.append((full, value))
            rows.extend(_flatten(value, full))
    return rows


def _find_numeric(json_items: list[tuple[str, Any]], keys: set[str], default: int = 0) -> int:
    lowered = {k.lower() for k in keys}
    for _, obj in json_items:
        for key, value in _flatten(obj):
            tail = re.split(r"[.\[\]]+", key)[-1].lower()
            if tail in lowered and isinstance(value, (int, float)) and not isinstance(value, bool):
                return int(value)
    return default


def _find_token_files(root: Path, token: str) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".html", ".txt", ".csv"}:
            continue
        try:
            text = _read_text(path)
        except Exception:
            continue
        if token in text:
            try:
                hits.append(str(path.relative_to(root)).replace("\\", "/"))
            except Exception:
                hits.append(path.name)
    return hits[:24]


def _csv_rows(path: Path | None) -> tuple[list[str], list[dict[str, str]], int]:
    if path is None or not path.exists():
        return [], [], 0
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows: list[dict[str, str]] = []
        total = 0
        for row in reader:
            total += 1
            if len(rows) < MAX_EMBED_ROWS_PER_SECTION:
                rows.append({str(k): str(v) for k, v in dict(row).items()})
    return fieldnames, rows, total


def _html_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _coerce_report_root(*args: Any, **kwargs: Any) -> Path:
    candidate_keys = (
        "report_root", "output_dir", "out_dir", "root", "report_dir", "bundle_dir",
        "target_dir", "directory", "path", "output_root"
    )
    for key in candidate_keys:
        value = kwargs.get(key)
        if value:
            path = Path(str(value)).expanduser()
            return path.parent if path.suffix.lower() == ".zip" else path
    for value in args:
        if value:
            path = Path(str(value)).expanduser()
            return path.parent if path.suffix.lower() == ".zip" else path
    return Path.cwd()


def _section(label: str, fragment: str, root: Path, icon: str) -> dict[str, Any]:
    csv_path = _find_csv(root, fragment)
    columns, rows, total = _csv_rows(csv_path)
    return {
        "id": re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-"),
        "label": label,
        "icon": icon,
        "source": str(csv_path.relative_to(root)).replace("\\", "/") if csv_path else "",
        "columns": columns,
        "rows": rows,
        "totalRows": total,
        "embeddedRows": len(rows),
    }




def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "pass", "ok"}


def _row_text(row: dict[str, Any]) -> str:
    return " ".join(str(v) for v in row.values()).lower()


def _parse_fields_json(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("fields") or row.get("payload") or row.get("json") or ""
    if not raw:
        return {}
    try:
        obj = json.loads(str(raw))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _status_value(row: dict[str, Any]) -> str:
    return str(row.get("status") or row.get("rule") or row.get("trustLevel") or "").strip()


def _confidence_for_row(section_label: str, row: dict[str, Any]) -> dict[str, Any]:
    """Assign a pragmatic, explainable evidence confidence score.

    This is not a production certificate. It is a quality lens over the report rows:
    provenance, scope, source strength, validity, recency and blocking signals.
    """
    label = section_label.lower()
    text = _row_text(row)
    fields = _parse_fields_json(row)
    status = _status_value(row)
    status_lower = status.lower()

    score = 50
    reasons: list[str] = []
    dimensions: list[str] = []
    hard_block = False

    # Source strength / traceability.
    if str(row.get("trustLevel", "")).lower() == "row-level-sanitized":
        score += 16
        reasons.append("row-level sanitized evidence")
        dimensions.append("source=row-level-sanitized")
    if str(row.get("sourceLevel", "")).lower() == "sqlite":
        score += 8
        reasons.append("SQLite source detected")
        dimensions.append("sourceLevel=sqlite")
    if row.get("sourceDb") or row.get("db"):
        score += 5
        dimensions.append("sourceDb=present")
    if row.get("sourceTable") or row.get("table"):
        score += 5
        dimensions.append("sourceTable=present")

    # Scope / tenant containment.
    scope_keys = {"businessId", "clientId", "tenantId", "licenseId", "deviceId", "storeId", "terminalId"}
    has_scope = bool(scope_keys.intersection(set(fields.keys()))) or _truthy(row.get("hasScopeKeys")) or "scope_authority" in status_lower or "pass_scope" in status_lower
    if has_scope:
        score += 14
        reasons.append("scope/tenant key evidence present")
        dimensions.append("scope=present")
    elif any(k in label for k in ["client", "license", "device", "sale", "lineage", "scope", "tenant"]):
        score -= 12
        reasons.append("scope key evidence not obvious")
        dimensions.append("scope=weak")

    # Positive status signals.
    if status_lower == "pass" or status_lower.startswith("pass_"):
        score += 14
        reasons.append(f"status {status}")
        dimensions.append("validity=pass")
    if "source_ready" in status_lower:
        score += 4
        reasons.append("source-ready signal")
        dimensions.append("readiness=source-ready")

    # Provenance / lineage.
    if _truthy(row.get("hasRelatedLineage")) or "full_provenance" in status_lower or "confirmed_provenance" in status_lower:
        score += 22
        reasons.append("related lineage/provenance present")
        dimensions.append("provenance=confirmed")
    if "inferred_provenance" in status_lower or "inferred_provenance" in text:
        score -= 18
        reasons.append("provenance is inferred, not certifying")
        dimensions.append("provenance=inferred")
    if "unknown_missing_provenance" in text:
        score -= 22
        reasons.append("unknown/missing provenance rule present")
        dimensions.append("provenance=unknown_missing")

    # Blocking/risk signals.
    if "blocked" in status_lower or "blocked" in text:
        hard_block = True
        score -= 42
        reasons.append("blocked evidence state")
        dimensions.append("blocker=blocked")
    if status_lower.startswith("orphan") or "orphan" in status_lower or "orphan_scope" in text:
        hard_block = True
        score -= 36
        reasons.append("orphan/scope-unknown evidence")
        dimensions.append("blocker=orphan")
    if "duplicate" in status_lower or "duplicate" in text:
        score -= 28
        reasons.append("duplicate finding")
        dimensions.append("quality=duplicate")
    if "drift" in status_lower or "drift" in label:
        score -= 28
        reasons.append("schema drift finding")
        dimensions.append("quality=schema-drift")
    if row.get("error"):
        score -= 24
        reasons.append("row has parse/error signal")
        dimensions.append("validity=error")
    if str(row.get("payloadParsed", "")).lower() == "true":
        score += 14
        reasons.append("JSON payload parsed")
        dimensions.append("payload=parsed")
    elif "payload" in label and row.get("payloadParsed"):
        score -= 18
        reasons.append("JSON payload did not parse")
        dimensions.append("payload=parse-failed")
    if "stale" in status_lower or "no_timestamp" in status_lower or "no timestamp" in text:
        score -= 18
        reasons.append("staleness/timestamp weakness")
        dimensions.append("timeliness=weak")

    # Section-specific adjustments.
    if label == "device claims" and status_lower == "pass":
        score += 12
        reasons.append("device claim crosscheck passed")
    if label == "sales lineage" and "inferred_provenance" in status_lower:
        # Medium diagnostic confidence, but not production certification.
        score = min(score, 62)
    if label == "golden path" and "no green" in text:
        score = min(score, 50)
        reasons.append("golden-path rule blocks green certification")
    if label in {"runtime links", "snapshot diff", "operational timeline"} and ("blocked" in text or "no_result" in text):
        hard_block = True
        score = min(score, 25)

    score = max(0, min(100, int(score)))
    if hard_block or score < 35:
        level = "BLOCKED"
    elif score < 55:
        level = "LOW"
    elif score < 80:
        level = "MEDIUM"
    else:
        level = "HIGH"

    if not reasons:
        reasons.append("generic evidence row; insufficient special signals")
    if not dimensions:
        dimensions.append("dimension=generic")

    return {
        "level": level,
        "score": score,
        "reasons": reasons[:6],
        "dimensions": dimensions[:8],
    }


def _apply_confidence_to_sections(sections: list[dict[str, Any]]) -> dict[str, Any]:
    level_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "BLOCKED": 3}
    totals = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "BLOCKED": 0}
    scores: list[int] = []
    section_rows: list[dict[str, str]] = []

    for section in sections:
        label = str(section.get("label") or "Evidence")
        rows = section.get("rows") or []
        local = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "BLOCKED": 0}
        local_scores: list[int] = []
        dominant_reasons: dict[str, int] = {}

        for row in rows:
            if not isinstance(row, dict):
                continue
            c = _confidence_for_row(label, row)
            row["confidenceLevel"] = c["level"]
            row["confidenceScore"] = str(c["score"])
            row["confidenceReasons"] = " | ".join(c["reasons"])
            row["confidenceDimensions"] = " | ".join(c["dimensions"])
            totals[c["level"]] += 1
            local[c["level"]] += 1
            scores.append(c["score"])
            local_scores.append(c["score"])
            if c["reasons"]:
                dominant_reasons[c["reasons"][0]] = dominant_reasons.get(c["reasons"][0], 0) + 1

        columns = list(section.get("columns") or [])
        for extra in ["confidenceLevel", "confidenceScore", "confidenceReasons", "confidenceDimensions"]:
            if extra not in columns:
                columns.append(extra)
        section["columns"] = columns

        total_rows = int(section.get("totalRows") or len(rows) or 0)
        avg = round(sum(local_scores) / len(local_scores), 1) if local_scores else 0
        dominant = sorted(dominant_reasons.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] if dominant_reasons else "no embedded rows analyzed"
        section_rows.append({
            "section": label,
            "totalRows": str(total_rows),
            "embeddedRowsScored": str(len(local_scores)),
            "avgConfidenceScore": str(avg),
            "high": str(local["HIGH"]),
            "medium": str(local["MEDIUM"]),
            "low": str(local["LOW"]),
            "blocked": str(local["BLOCKED"]),
            "dominantReason": dominant,
        })

    total_scored = sum(totals.values())
    avg_all = round(sum(scores) / len(scores), 1) if scores else 0
    certifiable_sales = 0
    for section in sections:
        if str(section.get("label", "")).lower() == "sales lineage":
            for row in section.get("rows") or []:
                if isinstance(row, dict) and row.get("confidenceLevel") == "HIGH" and "inferred_provenance" not in _row_text(row):
                    certifiable_sales += 1

    confidence_section = {
        "id": "evidence-confidence-score",
        "label": "Evidence Confidence",
        "icon": "◈",
        "source": "generated:evidence-confidence-score",
        "columns": ["section", "totalRows", "embeddedRowsScored", "avgConfidenceScore", "high", "medium", "low", "blocked", "dominantReason"],
        "rows": section_rows,
        "totalRows": len(section_rows),
        "embeddedRows": len(section_rows),
    }
    sections.insert(0, confidence_section)

    return {
        "totalRowsScored": total_scored,
        "averageScore": avg_all,
        "high": totals["HIGH"],
        "medium": totals["MEDIUM"],
        "low": totals["LOW"],
        "blocked": totals["BLOCKED"],
        "productionCertifiableSales": certifiable_sales,
        "method": "score based on provenance, scope, source level, validity, drift, duplicate/orphan, payload parse and runtime blockers",
        "levels": {
            "HIGH": "row-level and/or passed crosschecks with strong source/scope/provenance signals",
            "MEDIUM": "usable diagnostic evidence, often inferred or missing one hard confirmation",
            "LOW": "weak/partial evidence, drift, duplicate, staleness or parse concern",
            "BLOCKED": "blocked, orphan, missing provenance, missing runtime/comparable evidence, or hard gate issue",
        },
    }

def build_refined_operational_html(report_root: str | Path) -> str:
    root = Path(report_root).expanduser().resolve()
    manifest = _load_json(_find_file(root, "ATLAS_MANIFEST_PLUS.json") or Path("__missing__"))
    atlas = _load_json(_find_file(root, "operational_evidence_atlas.json") or Path("__missing__"))
    ledger = _load_json(_find_file(root, "placeholder_ledger.json") or Path("__missing__"))
    json_items = [("manifest", manifest), ("atlas", atlas), ("placeholder_ledger", ledger)]
    json_items = [(name, obj) for name, obj in json_items if obj is not None]

    sections = [
        _section("Clients", "clients", root, "◌"),
        _section("Licenses", "licenses", root, "◆"),
        _section("Devices", "devices", root, "▣"),
        _section("Sales", "sales", root, "◧"),
        _section("Sales Lineage", "salesLineage", root, "⌁"),
        _section("Schema Drift", "schemaDriftGuard", root, "△"),
        _section("Device Claims", "deviceClaimCrosscheck", root, "◇"),
        _section("Runtime Links", "runtimeEvidenceLinks", root, "↗"),
        _section("Payload JSON", "payloadJsonIndex", root, "{}"),
        _section("Data Lineage", "dataLineageGraph", root, "⟐"),
        _section("Scope Guard", "multiTenantLeakageGuard", root, "◎"),
        _section("Golden Path", "goldenPathComparator", root, "✓"),
        # SUPPORT_RESOLVER_VIEWER_SECTIONS_START
        _section("Support Summary", "supportResolverSummary", root, "SR"),
        _section("Support Capabilities", "supportCapabilityMatrix", root, "SC"),
        _section("Support Error Codes", "supportErrorCodeCoverage", root, "68"),
        _section("Support Actions", "supportActionCoverage", root, "SA"),
        _section("Support UI Routes", "supportUiRouteMap", root, "UI"),
        _section("Support E2E", "supportE2eCoverage", root, "E2E"),
        _section("Support Duplicates", "supportDuplicateImplementations", root, "DUP"),
        _section("Support Do Not Rebuild", "supportDoNotRebuildMap", root, "DNR"),
        _section("Support Contracts", "supportContractCoverage", root, "CT"),
        _section("Support Security", "supportSecurityRisks", root, "SEC"),
        # SUPPORT_RESOLVER_VIEWER_SECTIONS_END
    ]
    sections = [s for s in sections if s["source"] or s["totalRows"] > 0]
    if not sections:
        sections = [{"id":"evidence","label":"Evidence","icon":"◌","source":"","columns":["message"],"rows":[{"message":"No CSV evidence files were found in this bundle."}],"totalRows":1,"embeddedRows":1}]

    confidence_summary = _apply_confidence_to_sections(sections)

    feature_count = _find_numeric(json_items, {"featureCount", "feature_count", "featuresCount", "features_count"}, 0)
    placeholders = _find_numeric(json_items, {"placeholdersRemaining", "placeholders_remaining", "remainingPlaceholders"}, 0)
    detectors = _find_numeric(json_items, {"detectorsConverted", "detectors_converted", "convertedDetectors"}, 0)
    sales_total = next((s["totalRows"] for s in sections if s["label"] == "Sales"), 0)
    devices_total = next((s["totalRows"] for s in sections if s["label"] == "Devices"), 0)
    clients_total = next((s["totalRows"] for s in sections if s["label"] == "Clients"), 0)
    licenses_total = next((s["totalRows"] for s in sections if s["label"] == "Licenses"), 0)

    negative_gate_hits = _find_token_files(root, "NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED")
    inferred_hits = _find_token_files(root, "INFERRED_PROVENANCE")
    gate_status = "NO PASS" if negative_gate_hits or inferred_hits else "SOURCE READY"
    gate_tone = "danger" if gate_status == "NO PASS" else "ok"
    gate_reason = "Production certification stays blocked because provenance is not fully certified." if gate_status == "NO PASS" else "No explicit blocking production token was found in this bundle."

    payload = {
        "generatedAt": "__GENERATED_AT__",
        "summary": {
            "featureCount": feature_count,
            "placeholdersRemaining": placeholders,
            "detectorsConverted": detectors,
            "clients": clients_total,
            "licenses": licenses_total,
            "devices": devices_total,
            "sales": sales_total,
            "gateStatus": gate_status,
            "gateTone": gate_tone,
            "gateReason": gate_reason,
            "confidenceAverage": confidence_summary.get("averageScore", 0),
            "confidenceHigh": confidence_summary.get("high", 0),
            "confidenceMedium": confidence_summary.get("medium", 0),
            "confidenceLow": confidence_summary.get("low", 0),
            "confidenceBlocked": confidence_summary.get("blocked", 0),
            "confidenceRowsScored": confidence_summary.get("totalRowsScored", 0),
            "productionCertifiableSales": confidence_summary.get("productionCertifiableSales", 0),
            "confidenceMethod": confidence_summary.get("method", ""),
            "confidenceLevels": confidence_summary.get("levels", {}),
            "negativeGateFiles": negative_gate_hits,
            "inferredProvenanceFiles": inferred_hits,
        },
        "sections": sections,
    }
    payload["generatedAt"] = ""  # JS fills visual date from document timestamp if needed.
    data_json = _html_json(payload)

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DB Evidence Atlas</title>
  <style>
    :root {{
      color-scheme: light;
      --ink:#172033;
      --muted:#536175;
      --soft:#708095;
      --line:rgba(22,32,51,.125);
      --line-strong:rgba(22,32,51,.20);
      --glass:rgba(255,255,255,.44);
      --glass-strong:rgba(255,255,255,.58);
      --glass-faint:rgba(255,255,255,.30);
      --blue:#2563eb;
      --blue-soft:#dff4ff;
      --sky:#0ea5e9;
      --aqua:#06b6d4;
      --indigo:#6366f1;
      --violet:#8b5cf6;
      --mint:#10b981;
      --rose:#e11d48;
      --coral:#f97378;
      --green:#087a55;
      --slate:#334155;
      --red:#b42318;
      --shadow:0 26px 76px rgba(22,32,51,.145), 0 2px 12px rgba(22,32,51,.06);
      --inner:inset 0 1px 0 rgba(255,255,255,.76), inset 0 -1px 0 rgba(255,255,255,.22);
      --radius:24px;
      --mono:"SFMono-Regular","Cascadia Mono",Consolas,monospace;
      --sans:"Aptos","Segoe UI Variable","Inter",-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",system-ui,sans-serif;
    }}
    *{{box-sizing:border-box}}
    html,body{{min-height:100%;margin:0}}
    body{{
      font-family:var(--sans);
      color:var(--ink);
      background:
        radial-gradient(circle at 14% 8%, rgba(125,211,252,.74), transparent 29rem),
        radial-gradient(circle at 78% 14%, rgba(99,102,241,.24), transparent 30rem),
        radial-gradient(circle at 88% 36%, rgba(139,92,246,.18), transparent 31rem),
        radial-gradient(circle at 24% 88%, rgba(16,185,129,.22), transparent 30rem),
        radial-gradient(circle at 54% 96%, rgba(225,29,72,.12), transparent 34rem),
        linear-gradient(135deg,#eef7ff 0%, #f7fbff 38%, #edf2ff 72%, #eef9f6 100%);
      overflow-x:hidden;
    }}
    body::before{{
      content:"";
      position:fixed;
      inset:-18%;
      pointer-events:none;
      z-index:-2;
      background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1600' height='1100' viewBox='0 0 1600 1100'%3E%3Cdefs%3E%3ClinearGradient id='silk' x1='0' x2='1' y1='0' y2='1'%3E%3Cstop stop-color='%23ffffff' stop-opacity='.42'/%3E%3Cstop offset='.45' stop-color='%23d7e9ff' stop-opacity='.28'/%3E%3Cstop offset='1' stop-color='%23dbeafe' stop-opacity='.25'/%3E%3C/linearGradient%3E%3Cfilter id='blur'%3E%3CfeGaussianBlur stdDeviation='36'/%3E%3C/filter%3E%3C/defs%3E%3Cg filter='url(%23blur)' opacity='.95'%3E%3Cpath d='M-80 260 C260 80 360 420 630 230 C930 20 1040 360 1450 160 C1650 64 1720 360 1480 520 C1120 760 990 470 690 660 C400 845 270 610 -50 835Z' fill='url(%23silk)'/%3E%3Cpath d='M220 980 C510 720 740 920 950 705 C1160 490 1390 590 1660 430 L1700 1180 L160 1180Z' fill='%23ffffff' opacity='.38'/%3E%3C/g%3E%3C/svg%3E"),
        radial-gradient(circle at 30% 18%, rgba(255,255,255,.72), transparent 22rem),
        radial-gradient(circle at 72% 22%, rgba(14,165,233,.22), transparent 24rem),
        radial-gradient(circle at 48% 70%, rgba(139,92,246,.12), transparent 30rem);
      background-size:cover, auto, auto;
      transform:rotate(-2deg) scale(1.02);
    }}
    body::after{{
      content:"";
      position:fixed;
      inset:0;
      pointer-events:none;
      z-index:-1;
      background-image:radial-gradient(rgba(17,24,39,.055) .55px, transparent .65px);
      background-size:18px 18px;
      mask-image:linear-gradient(to bottom, rgba(0,0,0,.42), transparent 75%);
      opacity:.50;
    }}
    .shell{{width:min(1480px, calc(100vw - 40px)); margin:0 auto; padding:34px 0 46px;}}
    .hero{{
      position:relative;
      overflow:hidden;
      border:1px solid rgba(255,255,255,.62);
      border-radius:34px;
      padding:32px;
      background:linear-gradient(135deg, rgba(255,255,255,.54), rgba(255,255,255,.30));
      -webkit-backdrop-filter: blur(30px) saturate(1.32);
      backdrop-filter: blur(30px) saturate(1.32);
      box-shadow:var(--shadow), var(--inner);
    }}
    .hero::before{{content:"";position:absolute;inset:0;background:linear-gradient(110deg, rgba(255,255,255,.72), transparent 32%, rgba(255,255,255,.32) 72%, transparent);opacity:.55;pointer-events:none}}
    .hero-grid{{position:relative;display:grid;grid-template-columns:1.2fr .8fr;gap:22px;align-items:end}}
    .eyebrow{{margin:0 0 10px;color:var(--sky);font-weight:620;font-size:12px;letter-spacing:.16em;text-transform:uppercase}}
    h1{{margin:0;font-size:clamp(38px,5vw,68px);letter-spacing:-.06em;line-height:.93}}
    .subtitle{{margin:16px 0 0;max-width:780px;color:var(--muted);font-size:17px;line-height:1.55}}
    .hero-actions{{display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap}}
    button,.pill{{font-family:var(--sans)}}
    .btn{{
      border:1px solid rgba(17,24,39,.11);border-radius:999px;background:rgba(255,255,255,.50);
      -webkit-backdrop-filter: blur(18px) saturate(1.18);backdrop-filter: blur(18px) saturate(1.18);
      padding:10px 14px;color:var(--ink);font-weight:600;box-shadow:0 8px 22px rgba(31,41,55,.07), inset 0 1px 0 rgba(255,255,255,.85);cursor:pointer;
    }}
    .btn.primary{{background:rgba(17,24,39,.88);color:#fff;border-color:rgba(17,24,39,.35)}}
    .glass{{
      background:linear-gradient(180deg, rgba(255,255,255,.48), rgba(255,255,255,.30));
      -webkit-backdrop-filter: blur(24px) saturate(1.28);
      backdrop-filter: blur(24px) saturate(1.28);
      border:1px solid rgba(255,255,255,.58);
      box-shadow:var(--shadow), var(--inner);
    }}
    .summaryCards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:14px;margin:18px 0}}
    .card{{border-radius:22px;padding:18px;min-height:116px;position:relative;overflow:hidden}}
    .card::after{{content:"";position:absolute;right:-40px;top:-50px;width:110px;height:110px;border-radius:999px;background:rgba(255,255,255,.30);filter:blur(12px)}}
    .card.tone0{{background:linear-gradient(160deg, rgba(219,244,255,.52), rgba(255,255,255,.28));border-color:rgba(14,165,233,.26)}}
    .card.tone1{{background:linear-gradient(160deg, rgba(224,242,254,.48), rgba(238,242,255,.30));border-color:rgba(6,182,212,.24)}}
    .card.tone2{{background:linear-gradient(160deg, rgba(238,242,255,.54), rgba(255,255,255,.28));border-color:rgba(99,102,241,.23)}}
    .card.tone3{{background:linear-gradient(160deg, rgba(245,243,255,.50), rgba(255,255,255,.28));border-color:rgba(139,92,246,.22)}}
    .card.tone4{{background:linear-gradient(160deg, rgba(236,253,245,.50), rgba(255,255,255,.28));border-color:rgba(16,185,129,.22)}}
    .card.tone5{{background:linear-gradient(160deg, rgba(255,241,242,.45), rgba(255,255,255,.28));border-color:rgba(225,29,72,.18)}}
    .card.tone6{{background:linear-gradient(160deg, rgba(241,245,249,.48), rgba(219,234,254,.28));border-color:rgba(51,65,85,.18)}}
    .card.tone0::after{{background:rgba(14,165,233,.18)}}
    .card.tone1::after{{background:rgba(6,182,212,.18)}}
    .card.tone2::after{{background:rgba(99,102,241,.16)}}
    .card.tone3::after{{background:rgba(139,92,246,.15)}}
    .card.tone4::after{{background:rgba(16,185,129,.15)}}
    .card.tone5::after{{background:rgba(225,29,72,.12)}}
    .card.tone6::after{{background:rgba(51,65,85,.10)}}
    .cardLabel{{font-size:12px;color:var(--muted);font-weight:620;text-transform:uppercase;letter-spacing:.11em}}
    .cardValue{{margin-top:12px;font:660 30px/1 var(--sans);letter-spacing:-.04em}}
    .cardHint{{margin-top:10px;color:var(--soft);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .main{{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:18px;align-items:start}}
    .panel{{border-radius:28px;padding:18px;overflow:hidden}}
    .tabs{{display:flex;gap:8px;overflow:auto;padding:2px 2px 14px}}
    .tab{{border:1px solid rgba(17,24,39,.09);background:rgba(255,255,255,.32);border-radius:999px;padding:10px 13px;color:var(--muted);font-weight:620;white-space:nowrap;cursor:pointer}}
    .tab.active{{background:rgba(17,24,39,.90);color:#fff;border-color:rgba(17,24,39,.16);box-shadow:0 10px 24px rgba(17,24,39,.16)}}
    .toolbar{{display:flex;gap:10px;align-items:center;margin-bottom:14px}}
    .search{{width:100%;border:1px solid rgba(17,24,39,.11);border-radius:16px;background:rgba(255,255,255,.46);padding:13px 14px;font-size:14px;outline:none;color:var(--ink)}}
    .search:focus{{border-color:rgba(49,95,147,.34);box-shadow:0 0 0 4px rgba(49,95,147,.08)}}
    .tableWrap{{overflow:auto;border:1px solid rgba(17,24,39,.08);border-radius:20px;background:rgba(255,255,255,.30)}}
    table{{width:100%;border-collapse:collapse;min-width:760px}}
    th{{position:sticky;top:0;background:rgba(248,252,255,.64);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.11em;text-align:left;padding:12px;border-bottom:1px solid var(--line)}}
    td{{padding:12px;border-bottom:1px solid rgba(17,24,39,.065);font-size:13px;color:#273244;max-width:260px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    tr:hover td{{background:rgba(232,246,255,.48)}}
    tr.selected td{{background:rgba(203,232,255,.54)}}
    .drawer{{border-radius:28px;padding:20px;position:sticky;top:20px}}
    .drawer h2{{font-size:18px;margin:0 0 8px;letter-spacing:-.02em}}
    .drawerSub{{color:var(--muted);font-size:13px;margin-bottom:16px}}
    .kv{{display:grid;gap:8px}}
    .kvRow{{padding:11px;border-radius:14px;background:rgba(255,255,255,.34);border:1px solid rgba(17,24,39,.065)}}
    .kvKey{{font-size:11px;color:var(--muted);font-weight:620;letter-spacing:.08em;text-transform:uppercase}}
    .kvVal{{margin-top:5px;color:#1f2937;font-family:var(--mono);font-size:12px;word-break:break-word;white-space:pre-wrap}}
    .gate{{margin-top:18px;border-radius:22px;padding:18px;border:1px solid rgba(180,35,24,.16);background:rgba(255,255,255,.38)}}
    .badge{{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:6px 10px;font-weight:660;font-size:12px;border:1px solid transparent}}
    .badge.danger{{color:var(--red);background:rgba(255,241,242,.78);border-color:rgba(253,164,175,.62)}}
    .badge.ok{{color:var(--green);background:rgba(236,253,245,.76);border-color:rgba(110,231,183,.58)}}
    .badge.warn{{color:var(--violet);background:rgba(237,233,254,.72);border-color:rgba(196,181,253,.62)}}
    td[data-confidence="HIGH"]{{color:#087a55;font-weight:620}}
    td[data-confidence="MEDIUM"]{{color:#2563eb;font-weight:620}}
    td[data-confidence="LOW"]{{color:#7c3aed;font-weight:620}}
    td[data-confidence="BLOCKED"]{{color:#b42318;font-weight:680}}
    tr.confidence-blocked td{{background:rgba(255,241,242,.42)}}
    tr.confidence-high td{{background:rgba(236,253,245,.28)}}
    .empty{{padding:40px;text-align:center;color:var(--muted)}}
    .footer{{margin-top:18px;color:var(--soft);font-size:12px;text-align:center}}
    @media (max-width:1100px){{.summaryCards{{grid-template-columns:repeat(2,1fr)}}.main{{grid-template-columns:1fr}}.drawer{{position:static}}.hero-grid{{grid-template-columns:1fr}}.hero-actions{{justify-content:flex-start}}}}
    @media (prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important;scroll-behavior:auto!important}}}}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero auroraBackdrop">
      <div class="hero-grid">
        <section>
          <p class="eyebrow">Database evidence · lineage · readiness</p>
          <h1>DB Evidence Atlas</h1>
          <p class="subtitle">A refined operational database report for row-level evidence, device claims, sales lineage, schema drift, evidence confidence and production readiness. Calm glass, clear answers.</p>
        </section>
        <section class="hero-actions">
          <button class="btn" id="copySummary">Copy summary</button>
          <button class="btn" id="exportJson">Export JSON</button>
          <button class="btn primary" id="focusGate">Production Gate</button>
        </section>
      </div>
    </header>

    <section class="summaryCards" id="summaryCards"></section>

    <section class="main">
      <section class="panel glass">
        <nav class="tabs" id="tabs" aria-label="Evidence sections"></nav>
        <div class="toolbar">
          <input class="search" id="search" type="search" placeholder="Search current evidence table...">
          <button class="btn" id="clearSearch">Clear</button>
          <button class="btn" id="exportCsv">Export CSV</button>
        </div>
        <div class="tableWrap"><table><thead id="thead"></thead><tbody id="tbody"></tbody></table></div>
      </section>

      <aside class="drawer glass" id="drawer">
        <h2>Entity Detail Drawer</h2>
        <div class="drawerSub">Select a row to inspect its evidence fields.</div>
        <div class="kv" id="detailRows"></div>
        <section class="gate" id="gateBox">
          <span class="badge" id="gateBadge">Production Gate</span>
          <p id="gateReason"></p>
        </section>
      </aside>
    </section>
    <p class="footer">Generated as an offline, self-contained DB Evidence Atlas viewer. No raw database files are embedded.</p>
  </main>
  <script id="atlasData" type="application/json">{data_json}</script>
  <script>
    const DATA = JSON.parse(document.getElementById('atlasData').textContent);
    let active = 0;
    let selectedRow = null;
    let query = '';

    const cardsEl = document.getElementById('summaryCards');
    const tabsEl = document.getElementById('tabs');
    const thead = document.getElementById('thead');
    const tbody = document.getElementById('tbody');
    const search = document.getElementById('search');
    const detailRows = document.getElementById('detailRows');
    const gateBadge = document.getElementById('gateBadge');
    const gateReason = document.getElementById('gateReason');

    function esc(v){{return String(v ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));}}
    function norm(v){{return String(v ?? '').toLowerCase();}}

    function renderCards(){{
      const s = DATA.summary || {{}};
      const items = [
        ['Features', s.featureCount ?? 0, 'implemented'],
        ['Placeholders', s.placeholdersRemaining ?? 0, 'remaining'],
        ['Confidence', `${{s.confidenceAverage ?? 0}}/100`, `${{s.confidenceRowsScored ?? 0}} rows scored`],
        ['High', s.confidenceHigh ?? 0, 'strong evidence'],
        ['Blocked', s.confidenceBlocked ?? 0, 'needs proof'],
        ['Devices', s.devices ?? 0, 'claims'],
        ['Sales', s.sales ?? 0, 'transactions'],
        ['Certifiable Sales', s.productionCertifiableSales ?? 0, 'full provenance'],
        ['Gate', s.gateStatus || 'UNKNOWN', 'production'],
      ];
      cardsEl.innerHTML = items.map(([label,value,hint], index) => `<article class="card glass tone${{index % 7}}"><div class="cardLabel">${{esc(label)}}</div><div class="cardValue">${{esc(value)}}</div><div class="cardHint">${{esc(hint)}}</div></article>`).join('');
    }}

    function renderTabs(){{
      const sections = DATA.sections || [];
      tabsEl.innerHTML = sections.map((s,i) => `<button class="tab ${{i===active?'active':''}}" data-index="${{i}}">${{esc(s.icon || '')}} ${{esc(s.label)}} · ${{Number(s.totalRows||0).toLocaleString()}}</button>`).join('');
      tabsEl.querySelectorAll('.tab').forEach(btn => btn.onclick = () => {{active = Number(btn.dataset.index); selectedRow=null; query=''; search.value=''; render();}});
    }}

    function sectionRows(section){{
      const rows = section.rows || [];
      if(!query) return rows;
      const q = norm(query);
      return rows.filter(row => Object.values(row).some(v => norm(v).includes(q)));
    }}

    function renderTable(){{
      const section = (DATA.sections || [])[active] || {{columns:[], rows:[]}};
      const cols = section.columns && section.columns.length ? section.columns : Object.keys((section.rows||[])[0] || {{message:'No data'}});
      const rows = sectionRows(section);
      thead.innerHTML = `<tr>${{cols.map(c => `<th>${{esc(c)}}</th>`).join('')}}</tr>`;
      if(!rows.length){{tbody.innerHTML = `<tr><td colspan="${{Math.max(1, cols.length)}}"><div class="empty">No matching rows in this section.</div></td></tr>`; renderDetail(null); return;}}
      tbody.innerHTML = rows.map((row, index) => {{
        const level = String(row.confidenceLevel || '').toUpperCase();
        const trClass = level === 'BLOCKED' ? 'confidence-blocked' : (level === 'HIGH' ? 'confidence-high' : '');
        return `<tr data-index="${{index}}" class="${{trClass}}">${{cols.map(c => `<td data-confidence="${{c === 'confidenceLevel' ? esc(row[c]) : ''}}" title="${{esc(row[c])}}">${{esc(row[c])}}</td>`).join('')}}</tr>`;
      }}).join('');
      tbody.querySelectorAll('tr').forEach((tr, idx) => tr.onclick = () => {{
        tbody.querySelectorAll('tr').forEach(x => x.classList.remove('selected'));
        tr.classList.add('selected');
        selectedRow = rows[idx];
        renderDetail(selectedRow);
      }});
      renderDetail(selectedRow || rows[0]);
    }}

    function renderDetail(row){{
      if(!row){{detailRows.innerHTML = '<div class="kvRow"><div class="kvKey">State</div><div class="kvVal">No row selected</div></div>'; return;}}
      const entries = Object.entries(row).slice(0, 80);
      detailRows.innerHTML = entries.map(([k,v]) => `<div class="kvRow"><div class="kvKey">${{esc(k)}}</div><div class="kvVal">${{esc(v)}}</div></div>`).join('');
    }}

    function renderGate(){{
      const s = DATA.summary || {{}};
      const tone = s.gateTone || 'warn';
      gateBadge.className = `badge ${{tone}}`;
      gateBadge.textContent = `Production Gate: ${{s.gateStatus || 'UNKNOWN'}}`;
      gateReason.textContent = (s.gateReason || 'No production gate explanation was included.') + ' Evidence confidence average: ' + (s.confidenceAverage ?? 0) + '/100. Method: ' + (s.confidenceMethod || 'not documented');
    }}

    function render(){{renderCards(); renderTabs(); renderTable(); renderGate();}}

    search.addEventListener('input', () => {{query = search.value; selectedRow=null; renderTable();}});
    document.getElementById('clearSearch').onclick = () => {{query=''; search.value=''; renderTable();}};
    document.getElementById('focusGate').onclick = () => document.getElementById('gateBox').scrollIntoView({{behavior:'smooth', block:'center'}});
    document.getElementById('copySummary').onclick = async () => {{
      const s = DATA.summary || {{}};
      const text = `DB Evidence Atlas\nFeatures: ${{s.featureCount}}\nPlaceholders: ${{s.placeholdersRemaining}}\nSales: ${{s.sales}}\nGate: ${{s.gateStatus}}`;
      if(navigator.clipboard) await navigator.clipboard.writeText(text);
    }};
    document.getElementById('exportJson').onclick = () => download('db-evidence-atlas.json', JSON.stringify(DATA,null,2), 'application/json');
    document.getElementById('exportCsv').onclick = () => {{
      const section = (DATA.sections || [])[active] || {{columns:[], rows:[]}};
      const cols = section.columns || [];
      const rows = sectionRows(section);
      const csv = [cols.join(','), ...rows.map(r => cols.map(c => JSON.stringify(String(r[c] ?? ''))).join(','))].join(String.fromCharCode(10));
      download(`${{section.id || 'evidence'}}.csv`, csv, 'text/csv');
    }};
    function download(name, content, type){{
      const blob = new Blob([content], {{type}}); const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download=name; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    }}
    render();
  </script>
</body>
</html>'''


def rewrite_operational_viewer(*args: Any, **kwargs: Any) -> dict[str, Any]:
    root = _coerce_report_root(*args, **kwargs).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    html_path = root / "operational_evidence_atlas.html"
    html_doc = build_refined_operational_html(root)
    # Final anti-mojibake sweep for common broken Spanish accents.
    html_doc = (html_doc
        .replace("certificaciÃ³n", "certificación")
        .replace("operaciÃ³n", "operación")
        .replace("linaje", "linaje")
    )
    _write_text(html_path, html_doc)
    return {
        "ok": True,
        "viewer": "DB Evidence Confidence Score v1",
        "html_path": str(html_path),
        "bytes": html_path.stat().st_size if html_path.exists() else 0,
    }


def refine_operational_viewer(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return rewrite_operational_viewer(*args, **kwargs)


def rewrite_db_evidence_viewer(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return rewrite_operational_viewer(*args, **kwargs)
