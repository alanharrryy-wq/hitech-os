from __future__ import annotations

class BridgeError(RuntimeError):
    code = "BRIDGE_ERROR"

class ContractError(BridgeError):
    code = "BRIDGE_CONTRACT_ERROR"

class ValidationError(BridgeError):
    code = "BRIDGE_VALIDATION_ERROR"

class ResolutionError(BridgeError):
    code = "BRIDGE_RESOLUTION_ERROR"

class DriftError(BridgeError):
    code = "BRIDGE_DRIFT_ERROR"

class ApplicationDisabledError(BridgeError):
    code = "BRIDGE_APPLICATION_DISABLED_SOURCE_ONLY_V1"
