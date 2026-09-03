from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .errors import ContractError

MODES = {"PREVIEW", "APPLY", "VERIFY", "ROLLBACK"}
OP_TYPES = {"cssDeclarations", "jsonValues"}
REQUIRED_AUTH = ("semanticMeaningId", "bindingId", "layerId", "adapterId", "recipeId")


def _require_keys(obj: dict[str, Any], required: set[str], allowed: set[str], where: str) -> None:
    missing = sorted(required - obj.keys())
    extra = sorted(obj.keys() - allowed)
    if missing or extra:
        raise ContractError(f"{where}: missing={missing} extra={extra}")


def load_request(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        request = value
    else:
        request = json.loads(Path(value).read_text(encoding="utf-8"))
    if not isinstance(request, dict):
        raise ContractError("request must be an object")
    allowed = {"schema", "mode", "targetId", "expectedSourceSha256", "surface", "includeSurfaces", "excludeSurfaces", "semanticMeaningId", "bindingId", "layerId", "adapterId", "recipeId", "operations", "authorityCommit", "transactionId"}
    required = {"schema", "mode", "targetId", "expectedSourceSha256", "surface", "includeSurfaces", "excludeSurfaces", *REQUIRED_AUTH, "operations"}
    _require_keys(request, required, allowed, "request")
    if request["schema"] != "prisma.visual.application.request.v1":
        raise ContractError("unsupported request schema")
    if request["mode"] not in MODES:
        raise ContractError("unsupported mode")
    if not isinstance(request["includeSurfaces"], list) or not isinstance(request["excludeSurfaces"], list):
        raise ContractError("surface scope must use arrays")
    if set(request["includeSurfaces"]) & set(request["excludeSurfaces"]):
        raise ContractError("surface cannot be both included and excluded")
    if request["surface"] not in request["includeSurfaces"]:
        raise ContractError("target surface must be explicitly included")
    if not isinstance(request["operations"], list) or not request["operations"]:
        raise ContractError("operations must be a non-empty array")
    for index, operation in enumerate(request["operations"]):
        if not isinstance(operation, dict):
            raise ContractError(f"operation[{index}] must be an object")
        _require_keys(operation, {"type", "path", "values"}, {"type", "path", "values", "expectedCurrent"}, f"operation[{index}]")
        if operation["type"] not in OP_TYPES:
            raise ContractError(f"operation[{index}] unsupported type")
        if not isinstance(operation["path"], str) or not operation["path"]:
            raise ContractError(f"operation[{index}] path required")
        if not isinstance(operation["values"], dict) or not operation["values"]:
            raise ContractError(f"operation[{index}] values required")
    return request
