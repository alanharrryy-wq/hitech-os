from __future__ import annotations

TIMEZONE_NAME = "America/Mexico_City"

STATUS_OK = "OK"
STATUS_BLOCKED = "BLOCKED"
STATUS_DEGRADED = "DEGRADED"
STATUS_OFFLINE = "OFFLINE"
STATUS_MISSING_TOOLING = "MISSING_TOOLING"
STATUS_FAIL = "FAIL"

DOCS_DOCTOR_REL = "tools/ops/Docs-Doctor.ps1"
FINAL_REPORT_REL = "docs/govos/_reports/FINAL_REPORT.md"
REPORTS_DIR_REL = "docs/govos/_reports"

META_ROOT_REL = "docs/meta-gov"
RUNS_REL = "docs/meta-gov/_runs"
LATEST_REL = "docs/meta-gov/LATEST"

EXCERPT_LINES = 12
MAX_IMMEDIATE_ACTIONS = 10

DEBT_TOKENS = ("DEBT", "TODO")

STABLE_SORT_RULES = [
    "repos sorted by name ascending",
    "blockers sorted by (repo, type, message)",
    "debt items sorted by debt_id ascending",
    "json keys sorted lexicographically",
    "meta report table rows sorted by repo name ascending",
]

DEFAULT_REGISTRY = {
    "version": 1,
    "timezone": TIMEZONE_NAME,
    "feature_flags": {
        "convergence_actions": "OFF",
        "forced_repo_changes": "OFF",
    },
    "repos": [
        {
            "name": "hitech-os",
            "path": r".",
            "docs_doctor": DOCS_DOCTOR_REL,
        },
        {
            "name": "inversion-next",
            "path": r"F:\repos\inversion-next",
            "docs_doctor": DOCS_DOCTOR_REL,
        },
        {
            "name": "hitech-frontend",
            "path": r"F:\OneDrive\Hitech\3.Proyectos\CHAT GPT AI Estudio\HITECH_AISTUDIO_SYSTEM\0.Origins\app\frontend\hitech-frontend",
            "docs_doctor": DOCS_DOCTOR_REL,
        },
    ],
}
