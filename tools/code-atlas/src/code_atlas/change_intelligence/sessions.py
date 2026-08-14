from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import SESSION_SCHEMA, ContractError, normalize_scope, require_nonempty_string, sha256_json


def normalize_agent_session(session: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(session, Mapping):
        raise ContractError("agent session must be an object")
    normalized = deepcopy(dict(session))
    normalized["schemaVersion"] = SESSION_SCHEMA
    normalized["sessionId"] = require_nonempty_string(session.get("sessionId"), "sessionId")
    normalized["packId"] = require_nonempty_string(session.get("packId"), "packId")
    normalized["agentIdentity"] = require_nonempty_string(session.get("agentIdentity"), "agentIdentity")
    normalized["requestedTask"] = require_nonempty_string(session.get("requestedTask"), "requestedTask")
    normalized["inspectedPaths"] = normalize_scope(session.get("inspectedPaths", []))
    normalized["changedPaths"] = normalize_scope(session.get("changedPaths", []))
    normalized["checksRequested"] = sorted(set(session.get("checksRequested", [])))
    normalized["checksExecuted"] = sorted(set(session.get("checksExecuted", [])))
    normalized["humanInterventions"] = int(session.get("humanInterventions", 0))
    if normalized["humanInterventions"] < 0:
        raise ContractError("humanInterventions must be non-negative")
    normalized["hiddenReasoningInferred"] = False
    normalized["certifiable"] = False
    normalized["productionCertified"] = False
    normalized["sessionDigest"] = sha256_json({k: v for k, v in normalized.items() if k != "sessionDigest"})
    return normalized
