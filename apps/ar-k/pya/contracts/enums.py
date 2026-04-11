from __future__ import annotations

from enum import Enum


class State(str, Enum):
    OBSERVED = "observed"
    DECLARED = "declared"
    CANDIDATE = "candidate"
    CANONICAL = "canonical"
    RESOLVED = "resolved"
    VALIDATED = "validated"
    SUGGESTED = "suggested"
    EFFECTIVE = "effective"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    QUARANTINED = "quarantined"
    AMBIGUOUS = "ambiguous"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    STALE = "stale"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Stage(str, Enum):
    SCAN = "scan"
    REGISTRY = "registry"
    SWITCH = "switch"
    VALIDATE = "validate"
    ANNOTATE = "annotate"


class EngineType(str, Enum):
    SCANNER = "scanner"
    REGISTRY_BUILDER = "registry_builder"
    SWITCH_ENGINE = "switch_engine"
    CONTRACT_VALIDATOR = "contract_validator"
    AI_ANNOTATOR = "ai_annotator"


class ArtifactFamily(str, Enum):
    SIGNALS = "signals"
    MODULE_REGISTRY = "module_registry"
    BOUNDARY_REGISTRY = "boundary_registry"
    CONTRACT_REGISTRY = "contract_registry"
    SWITCH_REGISTRY = "switch_registry"
    SWITCH_RESOLUTIONS = "switch_resolutions"
    VALIDATION_REPORT = "validation_report"
    ANNOTATIONS = "annotations"
    SNAPSHOT = "snapshot"
    DELTA = "delta"
    EXECUTION_SUMMARY = "execution_summary"
    QUERY_INDEX = "query_index"
    INVENTORY = "inventory"
    GRAPH = "graph"
    METRICS = "metrics"
    DECISION_TRACE = "decision_trace"
