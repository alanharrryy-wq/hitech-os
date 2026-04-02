from enum import Enum


class SessionState(str, Enum):
    EMPTY = "empty"
    SCOPE_LOADED = "scope_loaded"
    OPS_LOADED = "ops_loaded"
    VALIDATED = "validated"
    PLAN_GENERATED = "plan_generated"
    APPLIED = "applied"
    ROLLBACK_AVAILABLE = "rollback_available"
    DIRTY_OR_STALE = "dirty_or_stale"
    REFRESHING = "refreshing"
    ERROR = "error"
