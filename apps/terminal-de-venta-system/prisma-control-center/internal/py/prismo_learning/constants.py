# PRISMO Learning Core V1.1 F2
# Generated package: prismo learn2 3005 1100 fix1
# Operation model: evidence-intake-real, local store writes only, read-only against repo/DB/secrets.
# This file intentionally uses only Python standard library modules.


"""Constants and canonical labels for PRISMO Learning Core.

The constants module intentionally contains no file-system access. It is safe to import
from UI routes, verifiers, tests and report builders.
"""
from __future__ import annotations

SCHEMA_VERSION = "1.1.0"
ENGINE_NAME = "PRISMO Learning Core V1.1 F2 Evidence Intake"
STORE_FOLDER_NAME = "PRISMO_LEARNING_STORE"
DEFAULT_OUTPUT_ROOT = r"F:\descargasf"

READ_ONLY = True
MUTATION_ALLOWED = False

PROTOCOL_EXECUTIVE_BRIEF = "executive_brief"
PROTOCOL_DIAGNOSTIC = "diagnostic"
PROTOCOL_EVIDENCE_TRAIL = "evidence_trail"
PROTOCOL_NEURAL_GRAPH = "neural_graph"
PROTOCOL_DECISION_CHECKLIST = "decision_checklist"
PROTOCOL_RISK_MATRIX = "risk_matrix"
PROTOCOL_VISUAL_QA_SUMMARY = "visual_qa_summary"
PROTOCOL_CONTRACT_ALIGNMENT = "contract_alignment"
PROTOCOL_MULTISURFACE_IMPACT = "multisurface_impact"
PROTOCOL_PUBLIC_SAFE_SUMMARY = "public_safe_summary"

ALL_PROTOCOLS = [
    PROTOCOL_EXECUTIVE_BRIEF,
    PROTOCOL_DIAGNOSTIC,
    PROTOCOL_EVIDENCE_TRAIL,
    PROTOCOL_NEURAL_GRAPH,
    PROTOCOL_DECISION_CHECKLIST,
    PROTOCOL_RISK_MATRIX,
    PROTOCOL_VISUAL_QA_SUMMARY,
    PROTOCOL_CONTRACT_ALIGNMENT,
    PROTOCOL_MULTISURFACE_IMPACT,
    PROTOCOL_PUBLIC_SAFE_SUMMARY,
]

EVIDENCE_PLAYWRIGHT = "playwright_evidence"
EVIDENCE_GOVERNANCE_CANON = "governance_canon"
EVIDENCE_QUERY_TYPE_GUARD = "query_type_guard"
EVIDENCE_PRISMO_VERIFY_REPORT = "prismo_verify_report"
EVIDENCE_SKILLOPS_CLEAN = "skillops_clean"
EVIDENCE_RELEASE_TRAIN = "release_train"
EVIDENCE_DEPENDENCY_ATLAS = "dependency_atlas"
EVIDENCE_DB_GLASS_ERD = "db_glass_erd"
EVIDENCE_CODEX_REPORT = "codex_report"
EVIDENCE_RUNTIME_SCREENSHOT = "runtime_screenshot"
EVIDENCE_REPO_INVENTORY = "repo_inventory"
EVIDENCE_DOWNLOADS_INVENTORY = "downloads_inventory"
EVIDENCE_UNKNOWN_PRISMO_RELATED = "unknown_prismo_related"

ALL_EVIDENCE_TYPES = [
    EVIDENCE_PLAYWRIGHT,
    EVIDENCE_GOVERNANCE_CANON,
    EVIDENCE_QUERY_TYPE_GUARD,
    EVIDENCE_PRISMO_VERIFY_REPORT,
    EVIDENCE_SKILLOPS_CLEAN,
    EVIDENCE_RELEASE_TRAIN,
    EVIDENCE_DEPENDENCY_ATLAS,
    EVIDENCE_DB_GLASS_ERD,
    EVIDENCE_CODEX_REPORT,
    EVIDENCE_RUNTIME_SCREENSHOT,
    EVIDENCE_REPO_INVENTORY,
    EVIDENCE_DOWNLOADS_INVENTORY,
    EVIDENCE_UNKNOWN_PRISMO_RELATED,
]

STATUS_AVAILABLE = "AVAILABLE"
STATUS_MISSING = "MISSING"
STATUS_PARTIAL = "PARTIAL"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_WARN = "WARN"
STATUS_UNKNOWN = "UNKNOWN"

SEVERITY_INFO = "info"
SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"
SEVERITY_CRITICAL = "critical"

MAX_ZIP_ENTRIES = 5000
MAX_TEXT_BYTES = 768 * 1024
MAX_ZIP_TEXT_ENTRY_BYTES = 512 * 1024
MAX_TOTAL_ZIP_READ_BYTES = 4 * 1024 * 1024
MAX_REGISTRY_RECORDS = 50000
MAX_REPORT_PREVIEW_CHARS = 12000

SAFE_TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".jsonl", ".log", ".csv", ".html", ".htm",
    ".xml", ".yaml", ".yml", ".py", ".ps1", ".mjs", ".js", ".ts", ".tsx", ".css"
}
METADATA_ONLY_EXTENSIONS = {
    ".db", ".sqlite", ".sqlite3", ".parquet", ".bin", ".exe", ".dll", ".pyd",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".7z", ".rar"
}
FORBIDDEN_PATH_PARTS = {
    ".git", "node_modules", ".next", "dist", "out", "build", "__pycache__", ".pytest_cache",
    ".turbo", ".pnpm-store", "coverage", ".cache"
}
FORBIDDEN_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development", "id_rsa", "id_ed25519",
    "credentials.json", "secrets.json", "service-account.json"
}
STORE_SUBDIRS = [
    "00_INDEX",
    "01_EVIDENCE_REGISTRY",
    "02_MEMORY",
    "03_PATTERNS",
    "04_PROTOCOL_STATS",
    "05_REPORTS",
    "06_SNAPSHOTS",
    "90_QUARANTINE_METADATA_ONLY",
]
API_ENDPOINTS = [
    "/api/prismo/learning/status",
    "/api/prismo/learning/evidence-index",
    "/api/prismo/learning/recommend-protocol",
    "/api/prismo/learning/insights",
    "/api/prismo/learning/graph",
    "/api/prismo/learning/patterns",
    "/api/prismo/learning/authority",
    "/api/prismo/learning/f3/status",
    "/api/prismo/learning/safe-summary",
]

def constant_snapshot() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "engine_name": ENGINE_NAME,
        "read_only": READ_ONLY,
        "mutation_allowed": MUTATION_ALLOWED,
        "protocol_count": len(ALL_PROTOCOLS),
        "evidence_type_count": len(ALL_EVIDENCE_TYPES),
        "api_endpoints": list(API_ENDPOINTS),
        "limits": {
            "max_zip_entries": MAX_ZIP_ENTRIES,
            "max_text_bytes": MAX_TEXT_BYTES,
            "max_registry_records": MAX_REGISTRY_RECORDS,
        },
    }


# F2 evidence intake controls. These limits keep PRISMO from scanning the whole universe
# like a chismoso with fiber óptica.
INTAKE_SCHEMA_VERSION = "f2.1"
INTAKE_DEFAULT_MAX_FILES_PER_ROOT = 3500
INTAKE_DEFAULT_MAX_ZIPS = 240
INTAKE_DEFAULT_MAX_TOTAL_SECONDS = 240
INTAKE_PRIORITY_EXTENSIONS = {".zip", ".md", ".json", ".log", ".txt", ".html", ".htm", ".csv", ".xml", ".yml", ".yaml"}
INTAKE_PRIORITY_KEYWORDS = (
    "prismo", "prisma", "learning", "learn", "result", "fail", "diagnostic", "verify", "verification",
    "playwright", "evidence", "canon", "governance", "snapshot", "report", "manifest", "control", "center",
    "chart", "lab", "sync", "tablet", "pc", "mobile", "codex", "dependency", "atlas",
)
