from __future__ import annotations
import copy, json, math, re
from pathlib import Path
from typing import Any
from .errors import ContractError
from .security import validate_hex, validate_tx_id, TASK_ID_RE

SURFACES = {"tablet","pc","mobile","web","chart-lab","control-center","shared-ui","governance","quality","prisma-html"}
OP_TYPES = {"cssDeclarations", "jsonValues"}
REQUIRED_AUTH = ("semanticMeaningId", "bindingId", "layerId", "adapterId", "recipeId")
PROP_RE = re.compile(r"^(?:--)?[A-Za-z_][A-Za-z0-9_-]*$")
POINTER_TOKEN_RE = re.compile(r"^(?:0|[1-9][0-9]*)$")

def _require_keys(obj: dict[str, Any], required: set[str], allowed: set[str], where: str) -> None:
    missing = sorted(required - obj.keys())
    extra = sorted(obj.keys() - allowed)
    if missing or extra:
        raise ContractError(f"{where}: missing={missing} extra={extra}")

def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ContractError(f"{field} must be a non-empty string")
    return value

def _scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))

def _finite_scalar(value: Any, field: str) -> None:
    if not _scalar(value):
        raise ContractError(f"{field} must be scalar")
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractError(f"{field} must be finite")

def _canonical_pointer(pointer: Any, field: str) -> str:
    if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/" or "\x00" in pointer:
        raise ContractError(f"{field} must be a non-root JSON Pointer")
    for token in pointer[1:].split("/"):
        i = 0
        while i < len(token):
            if token[i] == "~":
                if i + 1 >= len(token) or token[i+1] not in "01":
                    raise ContractError(f"{field} has invalid JSON Pointer escape")
                i += 2
            else:
                i += 1
    return pointer

def _validate_authorization(auth: Any) -> dict[str, Any]:
    if not isinstance(auth, dict):
        raise ContractError("APPLY requires authorization object")
    required = {
        "task","authorityTaskId","authorityMeshArtifact","authorityMeshArtifactSha256",
        "authorityMeshRequestDigest","uiBridgePlanPath","uiBridgePlanSha256",
        "uiBridgeSemanticDiffPath","uiBridgeSemanticDiffSha256"
    }
    _require_keys(auth, required, required, "authorization")
    _text(auth["task"], "authorization.task")
    if len(auth["task"]) < 10 or len(auth["task"]) > 6000:
        raise ContractError("authorization.task length invalid")
    if not isinstance(auth["authorityTaskId"], str) or not TASK_ID_RE.fullmatch(auth["authorityTaskId"]):
        raise ContractError("authorization.authorityTaskId invalid")
    for key in ("authorityMeshArtifact","uiBridgePlanPath","uiBridgeSemanticDiffPath"):
        _text(auth[key], f"authorization.{key}")
    for key in ("authorityMeshArtifactSha256","authorityMeshRequestDigest","uiBridgePlanSha256","uiBridgeSemanticDiffSha256"):
        validate_hex(auth[key],64,f"authorization.{key}")
    return auth

def load_request(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    try:
        if isinstance(value, dict):
            request = copy.deepcopy(value)
        else:
            request = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"request load failed: {exc}") from exc
    if not isinstance(request, dict):
        raise ContractError("request must be an object")

    if request.get("schema") != "prisma.visual.application.request.v1":
        raise ContractError("unsupported request schema")
    mode = request.get("mode")
    if mode not in {"PREVIEW","APPLY","VERIFY","ROLLBACK"}:
        raise ContractError("unsupported mode")

    if mode == "ROLLBACK":
        allowed = {"schema","mode","transactionId","targetId"}
        required = allowed
        _require_keys(request, required, allowed, "request")
        _text(request["targetId"], "targetId")
        validate_tx_id(request["transactionId"])
        return request

    allowed = {
        "schema","mode","targetId","expectedSourceSha256","surface","includeSurfaces","excludeSurfaces",
        "semanticMeaningId","bindingId","layerId","adapterId","recipeId","operations",
        "authorityCommit","transactionId","authorization"
    }
    required = {
        "schema","mode","targetId","expectedSourceSha256","surface","includeSurfaces","excludeSurfaces",
        *REQUIRED_AUTH,"operations"
    }
    if mode == "APPLY":
        required |= {"authorityCommit","authorization"}
    _require_keys(request, required, allowed, "request")
    _text(request["targetId"], "targetId")
    validate_hex(request["expectedSourceSha256"],64,"expectedSourceSha256")
    _text(request["surface"], "surface")
    if request["surface"] not in SURFACES:
        raise ContractError("unknown surface")
    for field in REQUIRED_AUTH:
        _text(request[field], field)

    for name in ("includeSurfaces","excludeSurfaces"):
        rows=request[name]
        if not isinstance(rows,list) or (name=="includeSurfaces" and not rows):
            raise ContractError("surface scope must use arrays")
        if any(not isinstance(x,str) or x not in SURFACES for x in rows):
            raise ContractError(f"{name} contains unknown surface")
        if len(rows)!=len(set(rows)):
            raise ContractError(f"{name} must be unique")
    if set(request["includeSurfaces"]) & set(request["excludeSurfaces"]):
        raise ContractError("surface cannot be both included and excluded")
    if request["surface"] not in request["includeSurfaces"]:
        raise ContractError("target surface must be explicitly included")

    if "authorityCommit" in request:
        validate_hex(request["authorityCommit"],40,"authorityCommit")
    if "transactionId" in request:
        validate_tx_id(request["transactionId"])
    if mode == "APPLY":
        _validate_authorization(request["authorization"])

    operations=request["operations"]
    if not isinstance(operations,list) or not operations:
        raise ContractError("operations must be a non-empty array")
    for index, operation in enumerate(operations):
        if not isinstance(operation,dict):
            raise ContractError(f"operation[{index}] must be an object")
        _require_keys(operation,{"type","path","values"},{"type","path","values","expectedCurrent"},f"operation[{index}]")
        if operation["type"] not in OP_TYPES:
            raise ContractError(f"operation[{index}] unsupported type")
        _text(operation["path"], f"operation[{index}].path")
        if not isinstance(operation["values"],dict) or not operation["values"]:
            raise ContractError(f"operation[{index}] values required")
        if operation["type"]=="cssDeclarations":
            if "expectedCurrent" in operation:
                raise ContractError("expectedCurrent is only supported for jsonValues")
            for prop,val in operation["values"].items():
                if not isinstance(prop,str) or not PROP_RE.fullmatch(prop):
                    raise ContractError(f"operation[{index}] invalid CSS property")
                if not isinstance(val,str) or "\x00" in val:
                    raise ContractError(f"operation[{index}] CSS values must be strings")
        else:
            _canonical_pointer(operation["path"], f"operation[{index}].path")
            for pointer,val in operation["values"].items():
                _canonical_pointer(pointer, f"operation[{index}].values pointer")
                _finite_scalar(val, f"operation[{index}].values[{pointer}]")
            if "expectedCurrent" in operation:
                if not isinstance(operation["expectedCurrent"],dict):
                    raise ContractError("expectedCurrent must be an object")
                for pointer,val in operation["expectedCurrent"].items():
                    _canonical_pointer(pointer, f"operation[{index}].expectedCurrent pointer")
                    _finite_scalar(val, f"operation[{index}].expectedCurrent[{pointer}]")
    return request
