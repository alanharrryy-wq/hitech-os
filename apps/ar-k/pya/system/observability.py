from __future__ import annotations

OBSERVABILITY_RULES = {
    "event_naming": "<engine>.<action>",
    "required_execution_events": [
        "scanner.started",
        "scanner.completed",
        "registry_builder.completed",
        "switch_engine.completed",
        "contract_validator.completed",
        "ai_annotator.completed",
    ],
    "log_policy": {
        "single_log_file": True,
        "default_log_dir": r"F:\descargasf",
        "pattern": "proyecto_int_YYMMDD_HHMM.log",
    },
    "artifact_families": [
        "inventory",
        "graph",
        "metrics",
        "execution_summary",
        "decision_trace",
    ],
}
