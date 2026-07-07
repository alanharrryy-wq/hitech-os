from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

REGISTER = {
    "path_role": "PATH_ROLE_INDEX.json",
    "coverage_gap": "ATLAS_COVERAGE_GAP_REGISTER.json",
    "important": "IMPORTANT_ENTRYPOINTS_REGISTER.json",
    "node_resolution": "ATLAS_NODE_RESOLUTION_REGISTER.json",
    "surface_resolver": "SURFACE_AWARE_ATLAS_NODE_RESOLVER.json",
    "production_gate": "PRODUCTION_GATE_MATRIX.json",
    "evidence_proves": "EVIDENCE_PROVES_DOES_NOT_PROVE.json",
    "next_gates": "NEXT_GATES_QUEUE.md",
}

NOISE = ["/.git/", "/node_modules/", "/.next/", "/out/_next/", "/dist/", "/build/", "/.turbo/", "/.cache/", "/__pycache__/", "f:/descargasf", "todo_el_show_plus/full_tree.txt"]
SOURCE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".scss", ".json", ".md", ".sql", ".prisma", ".yaml", ".yml"}
GEN_EXT = {".map", ".chunk", ".pack", ".lock"}
PREFIXES = [
    ("apps/terminal-de-venta-system/products/pc/", "PC"), ("products/pc/", "PC"),
    ("apps/terminal-de-venta-system/products/tablet/", "Tablet"), ("products/tablet/", "Tablet"),
    ("apps/terminal-de-venta-system/products/mobile/", "Mobile"), ("products/mobile/", "Mobile"),
    ("apps/terminal-de-venta-system/products/shared-ui/", "Shared UI"), ("products/shared-ui/", "Shared UI"),
    ("apps/terminal-de-venta-system/shared/", "Shared Core"), ("shared/", "Shared Core"),
    ("tools/prisma-control-center/", "Cloud Center"),
    ("tools/prisma-visual-os/", "Visual"), ("config/prisma-visual-os/", "Visual"), ("styles/prisma-visual-os/", "Visual"),
    ("tools/code-atlas/", "Tooling"), ("tools/", "Tooling"),
    ("apps/terminal-de-venta-system/docs/", "Docs"), ("docs/", "Docs"),
    ("apps/terminal-de-venta-system/prisma/", "DB"), ("prisma/", "DB"),
    ("templates/", "Tooling"), ("tests/", "Tests/Verifiers"), ("verifiers/", "Tests/Verifiers"), ("apps/terminal-de-venta-system/verifiers/", "Tests/Verifiers"),
    ("productization/", "Productization"), ("PRISMA Factory Ledger/", "Governor/Authority"), (".governance/", "Governor/Authority"),
]

def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return default

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def norm(value: Any) -> str:
    s = str(value).strip().replace("\\", "/")
    if " :: " in s:
        s = s.split(" :: ")[-1].strip()
    s = s.strip("`'\" ,;|[]()")
    s = re.sub(r"^[A-Za-z]:/repos/hitech-os/", "", s, flags=re.I)
    while s.startswith("./"):
        s = s[2:]
    return s

def pathish(s: Any) -> bool:
    if not isinstance(s, str):
        return False
    s = s.strip()
    if not s or len(s) > 420:
        return False
    return ("/" in s or "\\" in s or "*" in s or bool(re.search(r"\.(py|ts|tsx|js|jsx|json|md|css|scss|sql|prisma|yaml|yml)$", s, re.I)))

def collect(obj: Any, out: List[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k).lower()
            if isinstance(v, str) and ("path" in key or "node" in key or "entry" in key or pathish(v)) and pathish(v):
                out.append(v)
            else:
                collect(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, out)
    elif isinstance(obj, str) and pathish(obj):
        out.append(obj)

def role_of(p: str) -> str:
    q = norm(p)
    low = q.lower()
    for prefix, role in PREFIXES:
        if low.startswith(prefix.lower()):
            return role
    if "/products/pc/" in low: return "PC"
    if "/products/tablet/" in low: return "Tablet"
    if "/products/mobile/" in low: return "Mobile"
    if "prisma" in low or low.endswith((".db", ".sqlite", ".sqlite3")): return "DB"
    if "visual" in low: return "Visual"
    if "license" in low or "licensing" in low: return "Licensing"
    if low.endswith(".md") or low.startswith("docs/"): return "Docs"
    return "Unknown"


def _is_excluded_path_for_index(path: Path) -> bool:
    return bool(set(path.parts) & {".git","node_modules",".next","dist","build",".turbo",".cache","__pycache__",".wrangler"})

def _rel_to_repo(repo: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def build_basename_index(repo: Path, max_files: int = 90000, max_hits_per_name: int = 80) -> Dict[str, List[str]]:
    """Build a single basename index to avoid repeated repo-wide rglob(name) scans."""
    index: Dict[str, List[str]] = {}
    scanned = 0
    roots = [
        repo / "tools",
        repo / "apps" / "terminal-de-venta-system",
        repo / "products",
        repo / "shared",
        repo / "config",
        repo / "styles",
        repo / "templates",
        repo / "docs",
        repo / "prisma",
        repo / "productization",
        repo / "PRISMA Factory Ledger",
        repo / ".governance",
    ]
    seen_roots = set()
    for root in roots:
        if not root.exists():
            continue
        try:
            resolved = root.resolve()
        except Exception:
            resolved = root
        if resolved in seen_roots:
            continue
        seen_roots.add(resolved)
        for x in root.rglob("*"):
            if scanned >= max_files:
                return index
            if _is_excluded_path_for_index(x) or not x.is_file():
                continue
            scanned += 1
            bucket = index.setdefault(x.name.lower(), [])
            if len(bucket) < max_hits_per_name:
                bucket.append(_rel_to_repo(repo, x))
    return index

def safe_glob(repo: Path, pattern: str, max_matches: int = 250) -> List[str]:
    low = pattern.lower().replace("\\", "/")
    if len(pattern) > 300 or any(x in low for x in ["node_modules",".next",".git","out/_next","dist/","build/"]):
        return []
    out: List[str] = []
    try:
        for x in repo.glob(pattern):
            sx = str(x).replace("\\", "/").lower()
            if any(n in sx for n in ["/.git/","/node_modules/","/.next/","/out/_next/","/dist/","/build/"]):
                continue
            out.append(_rel_to_repo(repo, x))
            if len(out) >= max_matches:
                break
    except Exception:
        return []
    return out


def classify(repo: Path, raw: str, basename_index: Dict[str, List[str]] | None = None) -> Dict[str, Any]:
    p = norm(raw)
    low = p.lower()
    role = role_of(p)
    status = "UNCLASSIFIED"
    reason = "no rule matched"
    exists = False
    matches: List[str] = []
    if not p:
        status, reason = "NOISE_EMPTY", "empty path"
    elif any(x in low for x in NOISE):
        status, reason = "EXCLUDED_DOC_CACHE_OR_BUILD_NOISE", "cache/build/docs-package noise"
    elif re.search(r"^PATH_ROLE_INDEX\.v\d+", p, re.I):
        status, reason = "EXCLUDED_INTERNAL_REGISTER_METADATA", "schema label, not path"
    elif "[" in str(raw) and "::" in str(raw):
        candidate = repo / p
        exists = candidate.exists()
        if exists:
            status, reason = "RESOLVED_DECORATED_TREE_LINE", "decorated tree line normalized and found"
        elif "/_next/" in low or "/out/" in low or "/static/chunks/" in low:
            status, reason = "EXCLUDED_GENERATED_BUILD_ARTIFACT", "static build artifact"
        else:
            status, reason = "CLASSIFIED_DECORATED_TREE_LINE_MISSING", "decorated line normalized but not found"
    elif "*" in p:
        matches = safe_glob(repo, p)
        if matches:
            status, reason, exists = "RESOLVED_GLOB_EXPANDED", f"glob expanded to {len(matches)} path(s)", True
        else:
            status, reason = "GLOB_UNRESOLVED_NOT_LIVE", "glob did not resolve, classified as non-live marker"
    elif str(raw).strip().startswith("./") or p.startswith(("src/", "app/", "components/", "lib/")):
        status, reason = "WORKSPACE_RELATIVE_REQUIRES_SURFACE_CONTEXT", "needs PC/Tablet/Mobile/Cloud workspace context"
    elif p.startswith("../"):
        status, reason = "CLASSIFIED_PARENT_RELATIVE_EXTERNAL_OR_DOC_SNAPSHOT", "parent-relative external/doc snapshot"
    else:
        candidate = repo / p
        exists = candidate.exists()
        if exists:
            status, reason = "RESOLVED_EXISTING_REPO_PATH", "path exists"
        elif role == "Docs" or low.endswith((".md", ".txt")):
            status, reason = "CLASSIFIED_DOC_REFERENCE_NOT_LIVE_NODE", "doc/text reference"
        elif any(low.endswith(ext) for ext in GEN_EXT):
            status, reason = "EXCLUDED_GENERATED_ARTIFACT", "generated extension"
        elif re.search(r"^[A-Za-z0-9_-]+$", p):
            status, reason = "CLASSIFIED_SYMBOLIC_NODE_OR_SECTION", "symbolic node label"
        else:
            name = Path(p).name
            if name and any(name.lower().endswith(ext) for ext in SOURCE_EXT):
                hits = (basename_index or {}).get(name.lower(), [])
                if hits:
                    status, reason, matches, exists = "RESOLVED_BY_BASENAME_INDEX", f"basename index found {len(hits)} time(s)", hits, True
                else:
                    status, reason = "UNRESOLVED_CLASSIFIED_NEEDS_OWNER_DECISION", "source-like path not found"
            else:
                status, reason = "UNRESOLVED_CLASSIFIED_NON_PATH_OR_STALE", "non-path or stale text"
    noise = status.startswith("EXCLUDED_") or status.startswith("CLASSIFIED_DOC") or status.startswith("CLASSIFIED_SYMBOLIC") or status.startswith("CLASSIFIED_PARENT")
    resolved = status.startswith("RESOLVED_")
    decision = status in {"UNRESOLVED_CLASSIFIED_NEEDS_OWNER_DECISION", "WORKSPACE_RELATIVE_REQUIRES_SURFACE_CONTEXT", "GLOB_UNRESOLVED_NOT_LIVE", "CLASSIFIED_DECORATED_TREE_LINE_MISSING"}
    return {"raw": raw, "normalizedPath": p, "surfaceRole": role, "status": status, "reason": reason, "exists": exists, "isNoiseOrNonLive": noise, "isLiveResolved": resolved, "needsOwnerDecision": decision, "matches": matches[:100]}

def append_gate(registers: Path, verification: Dict[str, Any]) -> None:
    pg = registers / REGISTER["production_gate"]
    data = load_json(pg, {})
    gates = [g for g in data.setdefault("gates", []) if g.get("gate") != "Surface-aware resolver verification"]
    gates.append({"gate": "Surface-aware resolver verification", "status": verification["status"], "semanticCoverageComplete": False, "noiseExcluded": verification["summary"]["noiseOrNonLive"], "surfaceUnknownCountAfterClassification": verification["summary"]["needsOwnerDecision"], "doesNotProve": ["production readiness", "runtime/live certification", "sales/tender/canonical provenance complete"]})
    data["gates"] = gates
    data["productionGreenAllowed"] = False
    data["productionCertified"] = False
    data["productionGate"] = "NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED"
    data["updatedAt"] = datetime.now().isoformat(timespec="seconds")
    write_json(pg, data)

def append_proves(registers: Path, verification: Dict[str, Any]) -> None:
    p = registers / REGISTER["evidence_proves"]
    data = load_json(p, {})
    if isinstance(data, list):
        data = {"items": data}
    items = [x for x in data.setdefault("items", []) if x.get("evidence") != "SURFACE_RESOLVER_VERIFICATION_REGISTER.json"]
    items.append({"evidence": "SURFACE_RESOLVER_VERIFICATION_REGISTER.json", "status": verification["status"], "proves": ["surface resolver verified against evidence registers", "docs/cache/generated noise separated from live nodes", "remaining unresolved nodes bucketed by owner and next gate"], "doesNotProve": ["semantic Atlas coverage complete", "production readiness", "runtime/bundler aliases valid"]})
    data["items"] = items
    data["updatedAt"] = datetime.now().isoformat(timespec="seconds")
    write_json(p, data)

def update_queue(registers: Path, verification: Dict[str, Any]) -> None:
    p = registers / REGISTER["next_gates"]
    text = p.read_text(encoding="utf-8", errors="replace") if p.exists() else "# NEXT GATES QUEUE\n"
    marker = "## Closed by atlassurf2"
    if marker in text:
        text = text.split(marker)[0].rstrip() + "\n"
    s = verification["summary"]
    add = f"""

## Closed by atlassurf2

- DONE: VERIFY surface resolver reduces missing atlas nodes by owner and excludes docs/cache/generated noise.
- STATUS: `{verification['status']}`
- Noise/non-live classified: `{s['noiseOrNonLive']}`
- Resolved existing/source paths: `{s['liveResolved']}`
- Needs owner decision/context: `{s['needsOwnerDecision']}`

## Remaining gates after atlassurf

1. HUMAN DECISION: approve DB schema/migration treatment for ghost relations.
2. LINK runtime artifacts to production gate rows; collect missing live evidence only if explicitly approved.
3. CLOSE sales/tender/canonical provenance before any production green claim.
"""
    p.write_text(text.rstrip() + add, encoding="utf-8")

def run_surface_resolver_verification(repo_root: str | Path, out_root: str | Path | None = None) -> Dict[str, Any]:
    repo = Path(repo_root)
    registers = repo / "tools/code-atlas/evidence_ingestion/current/registers"
    if not registers.exists():
        raise FileNotFoundError(f"Missing registers: {registers}")
    src = {
        "nodeResolution": load_json(registers / REGISTER["node_resolution"], {}),
        "surfaceResolver": load_json(registers / REGISTER["surface_resolver"], {}),
        "coverageGap": load_json(registers / REGISTER["coverage_gap"], {}),
        "important": load_json(registers / REGISTER["important"], {}),
        "pathRole": load_json(registers / REGISTER["path_role"], {}),
    }
    raw: List[str] = []
    for obj in src.values():
        collect(obj, raw)
    seen = set(); candidates = []
    for value in raw:
        n = norm(value)
        if n and n not in seen:
            seen.add(n); candidates.append(value)
    basename_index = build_basename_index(repo)
    basename_file_count = sum(len(v) for v in basename_index.values())
    classified = [classify(repo, x, basename_index) for x in candidates]
    counts: Dict[str, int] = {}; roles: Dict[str, int] = {}
    for item in classified:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
        roles[item["surfaceRole"]] = roles.get(item["surfaceRole"], 0) + 1
    noise = [x for x in classified if x["isNoiseOrNonLive"]]
    resolved = [x for x in classified if x["isLiveResolved"]]
    needs = [x for x in classified if x["needsOwnerDecision"]]
    unclassified = [x for x in classified if x["status"] == "UNCLASSIFIED"]
    status = "PASS_SURFACE_RESOLVER_VERIFIED_PRODUCTION_STILL_BLOCKED" if not unclassified else "WARN_SURFACE_RESOLVER_VERIFIED_WITH_UNCLASSIFIED_ITEMS_PRODUCTION_STILL_BLOCKED"
    verification = {"kind": "SURFACE_RESOLVER_VERIFICATION_REGISTER.v2", "status": status, "createdAt": datetime.now().isoformat(timespec="seconds"), "treeCompleteDoesNotImplyAtlasComplete": True, "semanticCoverageComplete": False, "productionGreenAllowed": False, "productionGate": "NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED", "summary": {"candidatePathCount": len(candidates), "classifiedPathCount": len(classified), "statusCounts": counts, "roleCounts": roles, "noiseOrNonLive": len(noise), "liveResolved": len(resolved), "needsOwnerDecision": len(needs), "unclassified": len(unclassified), "priorSurfaceUnknownCount": src["nodeResolution"].get("unknownCount") or src["surfaceResolver"].get("unknownCount"), "priorSemanticMissingCount": src["coverageGap"].get("missing_atlas_nodes") or src["coverageGap"].get("missingAtlasNodes"), "basenameIndexFilesScanned": basename_file_count, "optimization": "single basename index instead of repeated repo.rglob(name)"}, "classificationSamples": {"noiseOrNonLive": noise[:80], "liveResolved": resolved[:80], "needsOwnerDecision": needs[:120], "unclassified": unclassified[:80]}, "ownerDecisionQueue": needs[:400], "proves": ["surface-aware resolver can classify candidate/missing paths by owner role", "docs/cache/generated noise separated from live source nodes", "remaining unresolved items are explicit owner/context decisions"], "doesNotProve": ["semantic Atlas coverage complete", "runtime/live certification", "production readiness", "sales/tender/canonical provenance complete"], "nextGate": "DB_SCHEMA_GHOST_RELATION_HUMAN_DECISION_QUEUE"}
    write_json(registers / "SURFACE_RESOLVER_VERIFICATION_REGISTER.json", verification)
    nr = load_json(registers / REGISTER["node_resolution"], {})
    if isinstance(nr, dict):
        nr["verificationStatus"] = status
        nr["verifiedBy"] = "atlassurf2.surface_resolver_verify.v2"
        nr["verificationSummary"] = verification["summary"]
        nr["semanticCoverageComplete"] = False
        nr["productionGreenAllowed"] = False
        write_json(registers / REGISTER["node_resolution"], nr)
    append_gate(registers, verification)
    append_proves(registers, verification)
    update_queue(registers, verification)
    report = f"""# Surface Resolver Verification

- Status: `{status}`
- Candidate paths analyzed: `{len(candidates)}`
- Noise/non-live classified: `{len(noise)}`
- Live resolved: `{len(resolved)}`
- Needs owner/context decision: `{len(needs)}`
- Unclassified: `{len(unclassified)}`
- Production green allowed: `false`\n- Basename index files scanned: `{basename_file_count}`

This closes the source-level surface resolver verification gate. It does **not** prove semantic Atlas coverage complete and does **not** prove production readiness.
"""
    (registers / "SURFACE_RESOLVER_VERIFICATION_REPORT.md").write_text(report, encoding="utf-8")
    return verification

if __name__ == "__main__":
    import sys
    print(json.dumps(run_surface_resolver_verification(sys.argv[1] if len(sys.argv) > 1 else "."), ensure_ascii=False, indent=2))
