from __future__ import annotations

RUNTIME_PHASES = (
    "resolve-target",
    "collect",
    "enrich",
    "analyze",
    "recommend",
    "fix",
    "verify",
    "export",
)

EXECUTION_MODES = (
    "patch-run",
    "diagnose",
    "collect-only",
    "verify-only",
    "support-bundle",
    "fix-plan",
    "apply-fixes",
    "rollback-preview",
    "rollback-apply",
    "plugin-list",
    "plugin-health",
    "plugin-enable",
    "plugin-disable",
    "show-run",
    "list-checkpoints",
)

PLUGIN_KINDS = (
    "guard",
    "target-detector",
    "context-enricher",
    "collector",
    "analyzer",
    "recommender",
    "fixer",
    "verifier",
    "exporter",
)

SEVERITIES = (
    "info",
    "warn",
    "error",
    "critical",
)

PRIORITIES = (
    "low",
    "normal",
    "high",
    "urgent",
)

RISK_LEVELS = (
    "low",
    "medium",
    "high",
    "critical",
)

RISK_TIERS = (
    "safe",
    "guarded",
    "high-risk",
    "blocked",
)

ARTIFACT_CATEGORIES = (
    "diagnostics",
    "system",
    "processes",
    "network",
    "logs",
    "git",
    "python",
    "node",
    "build",
    "tests",
    "findings",
    "recommendations",
    "verification",
    "fixes",
    "bundle",
    "policy",
    "audit",
    "rollback",
    "baseline",
)

APP_KINDS = (
    "auto",
    "unknown",
    "mixed",
    "python",
    "node",
    "web",
    "desktop",
)


REGEX_FLAG_NAMES = (
    "ASCII",
    "DOTALL",
    "IGNORECASE",
    "MULTILINE",
    "VERBOSE",
)


TEXT_FIELD_NAMES = (
    "file",
    "old_text",
    "new_text",
    "pattern",
    "anchor",
    "near_anchor",
    "start_anchor",
    "end_anchor",
    "text",
    "insert_text",
    "line_ending",
    "insert_position",
    "already_applied_text",
    "already_applied_regex",
)


INT_FIELD_NAMES = (
    "start_line",
    "end_line",
    "line_number",
    "expected_count",
)
