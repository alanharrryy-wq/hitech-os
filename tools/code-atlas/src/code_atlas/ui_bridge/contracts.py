from __future__ import annotations

import re

from code_atlas.app_map.uimap.contracts import (
    ACTIVE_RUNTIME_ALIASES,
    ADAPTERS,
    ANCHOR_KINDS,
    APPLICATION_READINESS,
    COMPONENT_UI_ID_PATTERN,
    CONDITIONAL_STATES,
    CONFIDENCE_VALUES,
    FULL_CHAIN_FIELDS,
    NDC_ID_PATTERN,
    NDC_STATUSES,
    PROHIBITED_CANONICAL_KEYS,
    RECIPE_COVERAGE,
    REQUIRED_STATES,
    SCHEMA_VERSION as UIMAP_SCHEMA_VERSION,
    STATE_VALUES,
    TARGET_RESOLUTION_STATUSES,
    TARGET_ROLES,
)

BRIDGE_VERSION = "1.0.0"
BRIDGE_SCHEMA = "prisma.ui.bridge.v1"
SOURCE_ONLY = True
APPLICATION_ENABLED = False

# UIMAP owns the component and batch contract.  Bridge intentionally re-exports
# those values instead of maintaining a second, drifting contract copy.
RUNTIME_ALIASES = ACTIVE_RUNTIME_ALIASES
CANONICAL_ADAPTERS = ADAPTERS
INTERACTIVE_STATES = REQUIRED_STATES
RECIPE_COVERAGE_VALUES = RECIPE_COVERAGE
APPLICATION_READINESS_VALUES = APPLICATION_READINESS
TARGET_RESOLUTION_VALUES = TARGET_RESOLUTION_STATUSES
FORBIDDEN_CANONICAL_KEYS = PROHIBITED_CANONICAL_KEYS
SOURCE_RESOLVED_FIELDS = set(FULL_CHAIN_FIELDS)

REQUIRED_BATCH_FIELDS = {
    "schema",
    "schemaVersion",
    "batchId",
    "supersedesBatchId",
    "contractHash",
    "runtimeAlias",
    "sourceSnapshotHash",
    "components",
    "aliases",
    "conflicts",
    "coverage",
    "integrity",
}
NDC_ID_RE = re.compile(NDC_ID_PATTERN)
COMPONENT_UI_ID_RE = re.compile(COMPONENT_UI_ID_PATTERN)
RESERVED_SEGMENTS = {
    "unknown",
    "undefined",
    "null",
    "temp",
    "tmp",
    "new",
    "old",
    "fix1",
    "fix2",
    "final_final",
}


def adapter_for(runtime_alias: str) -> str:
    return CANONICAL_ADAPTERS[runtime_alias]
