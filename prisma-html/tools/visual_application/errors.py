from __future__ import annotations

class GVAEError(RuntimeError):
    code = "GVAE_ERROR"
    def __init__(self, message: str = "", *, details: dict | None = None):
        super().__init__(message or self.code)
        self.details = details or {}

class ContractError(GVAEError): code = "CONTRACT_ERROR"
class TargetNotFound(GVAEError): code = "TARGET_NOT_FOUND"
class AmbiguousTarget(GVAEError): code = "AMBIGUOUS_TARGET"
class StaleSourceHash(GVAEError): code = "STALE_SOURCE_HASH"
class MissingBinding(GVAEError): code = "MISSING_BINDING"
class MissingLayer(GVAEError): code = "MISSING_LAYER"
class MissingAdapter(GVAEError): code = "MISSING_ADAPTER"
class MissingRecipe(GVAEError): code = "MISSING_RECIPE"
class MissingSemantic(GVAEError): code = "MISSING_SEMANTIC"
class UnsupportedFileType(GVAEError): code = "UNSUPPORTED_FILE_TYPE"
class UnsupportedProjectionMode(GVAEError): code = "UNSUPPORTED_PROJECTION_MODE"
class DirectGeneratedProductWrite(GVAEError): code = "DIRECT_GENERATED_PRODUCT_WRITE"
class SurfaceExpansion(GVAEError): code = "SURFACE_EXPANSION"
class ScopeExclusionViolation(GVAEError): code = "SCOPE_EXCLUSION_VIOLATION"
class TamperedBackup(GVAEError): code = "TAMPERED_BACKUP"
class TamperedTransaction(GVAEError): code = "TAMPERED_TRANSACTION"
class PriorityOverrideForbidden(GVAEError): code = "IMPORTANT_FORBIDDEN"
class ProjectionFailure(GVAEError): code = "PROJECTION_FAILURE"
class StaticEvidenceNotRuntime(GVAEError): code = "STATIC_EVIDENCE_NOT_RUNTIME"
class BlockedUnsupportedCss(GVAEError): code = "BLOCKED_UNSUPPORTED_CSS"
class RollbackWouldOverwriteNewerWork(GVAEError): code = "ROLLBACK_WOULD_OVERWRITE_NEWER_WORK"
class RollbackFailure(GVAEError): code = "ROLLBACK_FAILURE"
class PathSecurityError(GVAEError): code = "PATH_SECURITY_ERROR"
class AuthorizationError(GVAEError): code = "AUTHORIZATION_ERROR"
class PlanBindingError(GVAEError): code = "PLAN_BINDING_ERROR"
