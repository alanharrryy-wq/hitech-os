# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""F3 Pattern Miner + Authority Brain orchestration."""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import json
from .clock import now_iso
from .evidence_registry import load_registry
from .memory_store import write_store, read_store
from .paths import ensure_store
from .report_json import write_json_report
from .report_markdown import write_markdown_report

TYPE_WEIGHT = {"governance_canon": .94, "prismo_verify_report": .90, "playwright_evidence": .86, "codex_report": .78, "db_glass_erd": .74, "dependency_atlas": .72, "release_train": .70, "runtime_screenshot": .66, "skillops_clean": .64, "downloads_inventory": .44, "unknown_prismo_related": .35}
STATUS_WEIGHT = {"PASS": .92, "FAIL": .86, "WARN": .70, "PARTIAL": .58, "UNKNOWN": .38}
PROTOCOL_BY_TYPE = {"playwright_evidence": ["visual_qa_summary", "diagnostic", "evidence_trail"], "prismo_verify_report": ["evidence_trail", "decision_checklist"], "governance_canon": ["governance_check", "authority_review"], "db_glass_erd": ["system_map", "risk_matrix"], "dependency_atlas": ["system_map", "multisurface_impact"], "codex_report": ["implementation_review", "decision_checklist"], "runtime_screenshot": ["visual_qa_summary", "evidence_trail"], "release_train": ["release_review", "risk_matrix"]}

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def warning_penalty(record: dict[str, Any]) -> float:
    warnings = record.get("warnings") or []
    if isinstance(warnings, str): warnings = [warnings]
    return min(.18, .035 * len(warnings))

def evidence_authority_score(record: dict[str, Any]) -> float:
    etype = str(record.get("type") or "unknown_prismo_related")
    status = str(record.get("status") or "UNKNOWN").upper()
    base = TYPE_WEIGHT.get(etype, .40)
    status_score = STATUS_WEIGHT.get(status, .38)
    conf = float(record.get("confidence") or .5)
    auth = float(record.get("authority_weight") or base)
    penalty = warning_penalty(record)
    if record.get("metadata_only"): penalty += .10
    if record.get("secret_like") or record.get("has_secret_like_pattern"): penalty += .08
    score = (base*.36)+(status_score*.20)+(conf*.20)+(auth*.24)-penalty
    return round(clamp(score), 4)

def rank_evidence(records: list[dict[str, Any]], limit: int = 80) -> list[dict[str, Any]]:
    ranked = []
    for r in records:
        ranked.append({"id": r.get("id"), "type": r.get("type"), "status": r.get("status"), "surface": r.get("surface") or [], "safe_source_label": r.get("safe_source_label") or Path(str(r.get("source_path") or "")).name, "authority_score": evidence_authority_score(r), "confidence": r.get("confidence"), "metadata_only": bool(r.get("metadata_only")), "recommended_protocols": r.get("protocols") or PROTOCOL_BY_TYPE.get(str(r.get("type")), ["evidence_trail"])})
    return sorted(ranked, key=lambda x: (float(x.get("authority_score") or 0), str(x.get("status") == "PASS")), reverse=True)[:limit]

def mine_advanced_patterns(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    by_type_status = Counter((str(r.get("type") or "unknown"), str(r.get("status") or "UNKNOWN").upper()) for r in records)
    by_surface_status = Counter()
    by_protocol_status = Counter()
    for r in records:
        status = str(r.get("status") or "UNKNOWN").upper()
        for s in r.get("surface") or ["unknown"]:
            by_surface_status[(str(s), status)] += 1
        for p in r.get("protocols") or PROTOCOL_BY_TYPE.get(str(r.get("type")), []):
            by_protocol_status[(str(p), status)] += 1
    for (typ, status), count in by_type_status.items():
        if count >= 5 and status in {"FAIL", "PARTIAL", "WARN"}:
            patterns.append({"id": f"pattern_{typ}_{status.lower()}_cluster", "signal": f"{typ}:{status}", "count": count, "priority": "high" if status == "FAIL" else "medium", "recommended_protocols": PROTOCOL_BY_TYPE.get(typ, ["diagnostic", "evidence_trail"]), "explanation": "Repeated evidence cluster detected by type and status."})
    for (surface, status), count in by_surface_status.items():
        if count >= 8 and status in {"FAIL", "PARTIAL", "WARN"}:
            patterns.append({"id": f"pattern_surface_{surface}_{status.lower()}_hotspot".replace("/", "_"), "signal": f"surface:{surface}:{status}", "count": count, "priority": "high" if count >= 20 else "medium", "recommended_protocols": ["risk_matrix", "multisurface_impact", "decision_checklist"], "explanation": "Surface-level hotspot detected from repeated non-green evidence."})
    for (protocol, status), count in by_protocol_status.items():
        if count >= 4 and status == "PASS":
            patterns.append({"id": f"pattern_protocol_{protocol}_pass_bias", "signal": f"protocol:{protocol}:PASS", "count": count, "priority": "low", "recommended_protocols": [protocol], "explanation": "Protocol has repeated successful evidence."})
    priority = {"high": 3, "medium": 2, "low": 1}
    return sorted(patterns, key=lambda p: (priority.get(p.get("priority"), 0), p.get("count", 0)), reverse=True)[:120]

def authority_summary(records: list[dict[str, Any]], ranked: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(str(r.get("status") or "UNKNOWN").upper() for r in records)
    type_counts = Counter(str(r.get("type") or "unknown") for r in records)
    avg_score = round(sum(float(r.get("authority_score") or 0) for r in ranked[:50]) / max(1, min(50, len(ranked))), 4)
    return {"schema_version": "1.2.0", "generated_at": now_iso(), "record_count": len(records), "status_counts": dict(status_counts), "type_counts": dict(type_counts), "top_evidence": ranked[:25], "average_top_authority_score": avg_score, "precedence_applied": ["evidence_type", "status", "confidence", "authority_weight", "metadata_only_penalty", "warning_penalty", "secret_redaction_penalty"], "read_only": True, "mutation_allowed": False, "fix_applied": "report_markdown_raw_mode_and_latest_reports"}

def protocol_stats(records: list[dict[str, Any]], patterns: list[dict[str, Any]]) -> dict[str, Any]:
    stats = defaultdict(lambda: {"count": 0, "pass": 0, "fail": 0, "partial": 0, "warn": 0, "unknown": 0, "pattern_refs": []})
    for r in records:
        status = str(r.get("status") or "UNKNOWN").upper().lower()
        for p in r.get("protocols") or PROTOCOL_BY_TYPE.get(str(r.get("type")), ["evidence_trail"]):
            b = stats[str(p)]; b["count"] += 1; b[status if status in b else "unknown"] += 1
    for pat in patterns:
        for p in pat.get("recommended_protocols") or []:
            stats[str(p)]["pattern_refs"].append(pat.get("id"))
    rows = []
    for name, s in stats.items():
        rows.append({"protocol": name, **s, "success_score": round(s["pass"] / max(1, s["count"]),4), "urgency_score": round((s["fail"]+s["partial"]+s["warn"]) / max(1,s["count"]),4)})
    return {"schema_version": "1.2.0", "generated_at": now_iso(), "protocols": sorted(rows, key=lambda x: (x["urgency_score"], x["count"]), reverse=True), "read_only": True, "mutation_allowed": False, "fix_applied": "report_markdown_raw_mode_and_latest_reports"}

def build_f3_report(base: str | Path | None = None) -> dict[str, Any]:
    registry = load_registry(base); records = list(registry.get("records") or [])
    ranked = rank_evidence(records, 120); patterns = mine_advanced_patterns(records); auth = authority_summary(records, ranked); pstats = protocol_stats(records, patterns)
    root = ensure_store(base)
    write_store("patterns", {"schema_version": "1.2.0", "generated_at": now_iso(), "patterns": patterns, "read_only": True, "mutation_allowed": False, "fix_applied": "report_markdown_raw_mode_and_latest_reports"}, base)
    write_store("authority", auth, base); write_store("protocol_stats", pstats, base)
    procedural = read_store("procedural", {"schema_version": "1.2.0", "recipes": []}, base)
    procedural.update({"schema_version": "1.2.0", "generated_at": now_iso(), "recipes": [
        {"recipe_id": "f3_repeated_failure_investigation", "when": ["FAIL cluster", "surface hotspot"], "protocol_chain": ["diagnostic", "evidence_trail", "risk_matrix", "decision_checklist"], "success_score": .82},
        {"recipe_id": "f3_visual_evidence_review", "when": ["playwright_evidence", "runtime_screenshot"], "protocol_chain": ["visual_qa_summary", "evidence_trail", "decision_checklist"], "success_score": .78},
        {"recipe_id": "f3_governance_alignment", "when": ["governance_canon", "contract drift"], "protocol_chain": ["governance_check", "authority_review", "implementation_review"], "success_score": .88}]})
    write_store("procedural", procedural, base)
    report = {"ok": True, "status": "PASS", "phase": "F3 Pattern Miner + Authority Brain fix1", "generated_at": now_iso(), "evidence_count": len(records), "pattern_count": len(patterns), "top_evidence_count": len(ranked), "authority_summary": auth, "patterns": patterns[:40], "protocol_stats": pstats, "outputs": {"patterns": str(root/"03_PATTERNS"/"patterns.json"), "authority": str(root/"02_MEMORY"/"authority.json"), "protocol_stats": str(root/"04_PROTOCOL_STATS"/"protocol_stats.json"), "report_json": str(root/"05_REPORTS"/"f3_pattern_authority_report.json"), "report_md": str(root/"05_REPORTS"/"f3_pattern_authority_report.md")}, "read_only": True, "mutation_allowed": False, "fix_applied": "report_markdown_raw_mode_and_latest_reports"}
    write_json_report("f3_pattern_authority_report", report, base)
    md = ["# PRISMO Learning F3 · Pattern Miner + Authority Brain", "", f"- Status: **{report['status']}**", f"- Evidence count: **{len(records)}**", f"- Patterns detected: **{len(patterns)}**", f"- Top authority evidence ranked: **{len(ranked)}**", "- Runtime: read-only", "- mutation_allowed: false", "", "## Top patterns"]
    for p in patterns[:20]: md.append(f"- `{p.get('id')}` · {p.get('priority')} · count={p.get('count')} · protocols={', '.join(p.get('recommended_protocols') or [])}")
    md += ["", "## Top authority evidence"]
    for r in ranked[:15]: md.append(f"- `{r.get('id')}` · score={r.get('authority_score')} · {r.get('type')} · {r.get('status')} · {r.get('safe_source_label')}")
    write_markdown_report("f3_pattern_authority_report", "\n".join(md)+"\n", base)
    return report

def f3_status(base: str | Path | None = None) -> dict[str, Any]:
    path = ensure_store(base)/"05_REPORTS"/"f3_pattern_authority_report.json"
    if not path.exists(): return {"ok": True, "status": "missing", "phase": "F3", "message": "F3 report not generated yet.", "read_only": True, "mutation_allowed": False, "fix_applied": "report_markdown_raw_mode_and_latest_reports"}
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: return {"ok": False, "status": "error", "phase": "F3", "error": str(exc), "read_only": True, "mutation_allowed": False, "fix_applied": "report_markdown_raw_mode_and_latest_reports"}
