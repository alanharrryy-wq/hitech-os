from __future__ import annotations

"""Pure application core for the PRISMA Support Resolver workspace.

This module defines normalization boundaries, the operational view model,
state transitions and command guards.  It deliberately contains no database,
filesystem, HTTP or process operations.  A successful command guard is a plan
decision only; another authorized layer must perform and verify any mutation.
"""

from copy import deepcopy
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence
from uuid import uuid4

try:  # Supports both package-style tests and the 3160 flat module loader.
    from .triapp_consistency_resolver import (
        FreshnessPolicy,
        TriAppConsistencyResolver,
        build_envelope,
    )
except ImportError:  # pragma: no cover - exercised by the live flat loader.
    from triapp_consistency_resolver import (  # type: ignore
        FreshnessPolicy,
        TriAppConsistencyResolver,
        build_envelope,
    )


JsonMapping = Mapping[str, Any]
Clock = Callable[[], datetime]
CorrelationFactory = Callable[[], str]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _correlation_id() -> str:
    return str(uuid4())


def _iso(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return str(value)


def _revision_key(value: Any) -> tuple[int, float | str]:
    if isinstance(value, bool):
        return (0, str(value))
    if isinstance(value, (int, float)):
        return (2, float(value))
    raw = str(value or "")
    try:
        return (2, float(raw))
    except ValueError:
        return (1, raw)


def _is_older(revision: Any, latest_revision: Any) -> bool:
    if revision in (None, "") or latest_revision in (None, ""):
        return False
    return _revision_key(revision) < _revision_key(latest_revision)


def _json_copy(value: Any) -> Any:
    return deepcopy(value)


@dataclass(frozen=True)
class AdapterContext:
    """Per-request controls used to cancel or reject late adapter responses."""

    cancelled: bool = False
    latestRevision: Any = None
    correlationId: str | None = None


class AdapterFailure(RuntimeError):
    code = "ADAPTER_FAILURE"

    def __init__(self, message: str, *, details: JsonMapping | None = None) -> None:
        super().__init__(message)
        self.details = _json_copy(dict(details or {}))


class AdapterCancelled(AdapterFailure):
    code = "ADAPTER_CANCELLED"


class StaleAdapterResponse(AdapterFailure):
    code = "STALE_ADAPTER_RESPONSE"


class InvalidAdapterPayload(AdapterFailure):
    code = "INVALID_ADAPTER_PAYLOAD"


class BaseSupportAdapter:
    """Shared provenance, freshness, error and stale-response behavior."""

    adapter_name = "BaseSupportAdapter"
    domain = "support"

    def __init__(
        self,
        *,
        freshness_policy: FreshnessPolicy | None = None,
        now_factory: Clock | None = None,
        correlation_factory: CorrelationFactory | None = None,
    ) -> None:
        self._freshness_policy = freshness_policy or FreshnessPolicy()
        self._now = now_factory or _utc_now
        self._new_correlation = correlation_factory or _correlation_id

    def normalize_data(self, payload: JsonMapping) -> dict[str, Any]:
        raw = payload.get("data")
        if isinstance(raw, Mapping):
            return _json_copy(dict(raw))
        return _json_copy(dict(payload))

    def normalize(
        self,
        payload: JsonMapping,
        *,
        source: str | None = None,
        revision: Any = None,
        updated_at: datetime | str | None = None,
        observed_at: datetime | str | None = None,
        freshness: str | None = None,
        correlation_id: str | None = None,
        provenance: Iterable[JsonMapping | str] = (),
        context: AdapterContext | None = None,
    ) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise InvalidAdapterPayload("Adapter payload must be a mapping")
        request = context or AdapterContext()
        if request.cancelled:
            raise AdapterCancelled("Adapter request was cancelled")
        resolved_revision = revision if revision is not None else payload.get("revision")
        if _is_older(resolved_revision, request.latestRevision):
            raise StaleAdapterResponse(
                "Adapter response revision is older than the latest accepted revision",
                details={"revision": resolved_revision, "latestRevision": request.latestRevision},
            )
        resolved_source = source or payload.get("source")
        if resolved_source in (None, ""):
            raise InvalidAdapterPayload("Adapter source is required")
        observed = observed_at or payload.get("observedAt") or self._now()
        updated = updated_at if updated_at is not None else payload.get("updatedAt")
        resolved_freshness = self._freshness_policy.classify(
            updated,
            observed,
            freshness or payload.get("freshness"),
        )
        correlation = correlation_id or request.correlationId or payload.get("correlationId") or self._new_correlation()
        normalized = build_envelope(
            self.normalize_data(payload),
            source=str(resolved_source),
            revision=resolved_revision,
            updated_at=updated,
            observed_at=observed,
            freshness=resolved_freshness,
            correlation_id=str(correlation),
        )
        normalized["adapter"] = self.adapter_name
        normalized["domain"] = self.domain
        normalized["provenance"] = [
            _json_copy(dict(item)) if isinstance(item, Mapping) else str(item)
            for item in provenance
        ]
        normalized["errors"] = []
        return normalized

    def map_error(
        self,
        error: BaseException,
        *,
        source: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        code = error.code if isinstance(error, AdapterFailure) else "ADAPTER_UNEXPECTED_ERROR"
        details = error.details if isinstance(error, AdapterFailure) else {}
        return {
            "adapter": self.adapter_name,
            "domain": self.domain,
            "source": str(source),
            "correlationId": str(correlation_id or self._new_correlation()),
            "error": {
                "code": code,
                "message": str(error),
                "details": _json_copy(details),
            },
        }


class SupportCaseAdapter(BaseSupportAdapter):
    adapter_name = "SupportCaseAdapter"
    domain = "support_case"


class SupportSearchAdapter(BaseSupportAdapter):
    adapter_name = "SupportSearchAdapter"
    domain = "support_search"


class ScopeResolutionAdapter(BaseSupportAdapter):
    adapter_name = "ScopeResolutionAdapter"
    domain = "scope_resolution"


class LicenseContextAdapter(BaseSupportAdapter):
    adapter_name = "LicenseContextAdapter"
    domain = "license_context"


class DeviceContextAdapter(BaseSupportAdapter):
    adapter_name = "DeviceContextAdapter"
    domain = "device_context"


class CustomerSetupAdapter(BaseSupportAdapter):
    adapter_name = "CustomerSetupAdapter"
    domain = "customer_setup"


class SurfaceStatusAdapter(BaseSupportAdapter):
    adapter_name = "SurfaceStatusAdapter"
    domain = "surface_status"


class IncidentTimelineAdapter(BaseSupportAdapter):
    adapter_name = "IncidentTimelineAdapter"
    domain = "incident_timeline"


class EvidenceAdapter(BaseSupportAdapter):
    adapter_name = "EvidenceAdapter"
    domain = "evidence"


class SupportActionAdapter(BaseSupportAdapter):
    adapter_name = "SupportActionAdapter"
    domain = "support_action"


class AuthorizationAdapter(BaseSupportAdapter):
    adapter_name = "AuthorizationAdapter"
    domain = "authorization"

    @staticmethod
    def allows(permissions: Iterable[str], required: Iterable[str]) -> bool:
        return set(required).issubset(set(permissions))


class FeatureGateAdapter(BaseSupportAdapter):
    adapter_name = "FeatureGateAdapter"
    domain = "feature_gate"

    @staticmethod
    def enabled(gates: JsonMapping, gate: str) -> bool:
        return gates.get(gate) is True


class TriAppConsistencyAdapter(BaseSupportAdapter):
    adapter_name = "TriAppConsistencyAdapter"
    domain = "triapp_consistency"

    def __init__(
        self,
        *,
        resolver: TriAppConsistencyResolver | None = None,
        freshness_policy: FreshnessPolicy | None = None,
        now_factory: Clock | None = None,
        correlation_factory: CorrelationFactory | None = None,
    ) -> None:
        super().__init__(
            freshness_policy=freshness_policy,
            now_factory=now_factory,
            correlation_factory=correlation_factory,
        )
        self.resolver = resolver or TriAppConsistencyResolver(
            freshness_policy=self._freshness_policy,
            now_factory=self._now,
            correlation_factory=self._new_correlation,
        )

    def build_report(
        self,
        projections: Iterable[JsonMapping],
        *,
        licenses: Iterable[JsonMapping] = (),
        source: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        return self.resolver.buildConsistencyReport(
            projections,
            licenses=licenses,
            source=source,
            correlation_id=correlation_id,
        )


class DeviceFleetAdapter(BaseSupportAdapter):
    adapter_name = "DeviceFleetAdapter"
    domain = "device_fleet"


class LicenseOperationsAdapter(BaseSupportAdapter):
    adapter_name = "LicenseOperationsAdapter"
    domain = "license_operations"


ADAPTER_TYPES = {
    adapter.adapter_name: adapter
    for adapter in (
        SupportCaseAdapter,
        SupportSearchAdapter,
        ScopeResolutionAdapter,
        LicenseContextAdapter,
        DeviceContextAdapter,
        CustomerSetupAdapter,
        SurfaceStatusAdapter,
        IncidentTimelineAdapter,
        EvidenceAdapter,
        SupportActionAdapter,
        AuthorizationAdapter,
        FeatureGateAdapter,
        TriAppConsistencyAdapter,
        DeviceFleetAdapter,
        LicenseOperationsAdapter,
    )
}


@dataclass(frozen=True)
class SupportWorkspaceViewModel:
    """Complete read model for one Support Resolver workspace."""

    currentCase: JsonMapping | None = None
    queue: tuple[JsonMapping, ...] = ()
    scope: JsonMapping = field(default_factory=dict)
    client: JsonMapping | None = None
    business: JsonMapping | None = None
    store: JsonMapping | None = None
    terminal: JsonMapping | None = None
    device: JsonMapping | None = None
    deviceFleet: tuple[JsonMapping, ...] = ()
    license: JsonMapping | None = None
    licenseGroup: JsonMapping | None = None
    surfaceStatuses: tuple[JsonMapping, ...] = ()
    triAppConsistency: JsonMapping = field(default_factory=dict)
    diagnosis: JsonMapping = field(default_factory=dict)
    recommendedActions: tuple[JsonMapping, ...] = ()
    simulation: JsonMapping = field(default_factory=dict)
    approval: JsonMapping = field(default_factory=dict)
    execution: JsonMapping = field(default_factory=dict)
    verification: JsonMapping = field(default_factory=dict)
    evidence: tuple[JsonMapping, ...] = ()
    timeline: tuple[JsonMapping, ...] = ()
    authority: JsonMapping = field(default_factory=dict)
    security: JsonMapping = field(default_factory=dict)
    featureGates: JsonMapping = field(default_factory=dict)
    permissions: tuple[str, ...] = ()
    blockers: tuple[JsonMapping | str, ...] = ()
    freshness: JsonMapping = field(default_factory=dict)
    relatedCases: tuple[JsonMapping, ...] = ()
    knowledge: tuple[JsonMapping, ...] = ()

    @classmethod
    def from_mapping(cls, value: JsonMapping) -> "SupportWorkspaceViewModel":
        sequence_fields = {
            "queue",
            "deviceFleet",
            "surfaceStatuses",
            "recommendedActions",
            "evidence",
            "timeline",
            "permissions",
            "blockers",
            "relatedCases",
            "knowledge",
        }
        known = {item.name for item in fields(cls)}
        payload: dict[str, Any] = {}
        for key in known:
            if key not in value:
                continue
            item = _json_copy(value[key])
            payload[key] = tuple(item or ()) if key in sequence_fields else item
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return {item.name: _json_copy(getattr(self, item.name)) for item in fields(self)}


class SupportWorkspaceState(str, Enum):
    IDLE = "IDLE"
    QUEUE_LOADING = "QUEUE_LOADING"
    CASE_LOADING = "CASE_LOADING"
    CASE_OPEN = "CASE_OPEN"
    SCOPE_RESOLVING = "SCOPE_RESOLVING"
    SCOPE_VALID = "SCOPE_VALID"
    SCOPE_CONFLICT = "SCOPE_CONFLICT"
    DIAGNOSING = "DIAGNOSING"
    DIAGNOSED = "DIAGNOSED"
    SIMULATING = "SIMULATING"
    SIMULATED = "SIMULATED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    APPLYING = "APPLYING"
    APPLIED = "APPLIED"
    PROPAGATING = "PROPAGATING"
    VERIFYING = "VERIFYING"
    VERIFIED = "VERIFIED"
    RESOLVED = "RESOLVED"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED_SAFE = "FAILED_SAFE"
    OFFLINE_READ_ONLY = "OFFLINE_READ_ONLY"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class StateContext:
    scopeValid: bool = False
    scopeConflict: bool = False
    diagnosisComplete: bool = False
    simulationComplete: bool = False
    approvalGranted: bool = False
    backupAvailable: bool = False
    rollbackAvailable: bool = False
    mutationPerformed: bool = False
    propagationComplete: bool = False
    verificationPassed: bool = False
    online: bool = True
    expectedRevision: Any = None
    currentRevision: Any = None
    blockers: tuple[str, ...] = ()


@dataclass(frozen=True)
class StateTransition:
    previous: SupportWorkspaceState
    current: SupportWorkspaceState
    changed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "previous": self.previous.value,
            "current": self.current.value,
            "changed": self.changed,
        }


class InvalidStateTransition(ValueError):
    pass


class StateInvariantViolation(ValueError):
    pass


_FAILED_OR_BLOCKED = {
    SupportWorkspaceState.FAILED_SAFE,
    SupportWorkspaceState.BLOCKED,
    SupportWorkspaceState.OFFLINE_READ_ONLY,
}

STATE_TRANSITIONS: dict[SupportWorkspaceState, frozenset[SupportWorkspaceState]] = {
    SupportWorkspaceState.IDLE: frozenset({
        SupportWorkspaceState.QUEUE_LOADING,
        SupportWorkspaceState.CASE_LOADING,
        SupportWorkspaceState.OFFLINE_READ_ONLY,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.QUEUE_LOADING: frozenset({
        SupportWorkspaceState.IDLE,
        SupportWorkspaceState.CASE_LOADING,
        *_FAILED_OR_BLOCKED,
    }),
    SupportWorkspaceState.CASE_LOADING: frozenset({SupportWorkspaceState.CASE_OPEN, *_FAILED_OR_BLOCKED}),
    SupportWorkspaceState.CASE_OPEN: frozenset({
        SupportWorkspaceState.SCOPE_RESOLVING,
        SupportWorkspaceState.DIAGNOSING,
        SupportWorkspaceState.ROLLING_BACK,
        *_FAILED_OR_BLOCKED,
    }),
    SupportWorkspaceState.SCOPE_RESOLVING: frozenset({
        SupportWorkspaceState.SCOPE_VALID,
        SupportWorkspaceState.SCOPE_CONFLICT,
        *_FAILED_OR_BLOCKED,
    }),
    SupportWorkspaceState.SCOPE_VALID: frozenset({
        SupportWorkspaceState.DIAGNOSING,
        SupportWorkspaceState.SIMULATING,
        SupportWorkspaceState.SCOPE_RESOLVING,
        *_FAILED_OR_BLOCKED,
    }),
    SupportWorkspaceState.SCOPE_CONFLICT: frozenset({
        SupportWorkspaceState.SCOPE_RESOLVING,
        SupportWorkspaceState.CASE_OPEN,
        SupportWorkspaceState.OFFLINE_READ_ONLY,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.DIAGNOSING: frozenset({SupportWorkspaceState.DIAGNOSED, *_FAILED_OR_BLOCKED}),
    SupportWorkspaceState.DIAGNOSED: frozenset({
        SupportWorkspaceState.SIMULATING,
        SupportWorkspaceState.SCOPE_RESOLVING,
        *_FAILED_OR_BLOCKED,
    }),
    SupportWorkspaceState.SIMULATING: frozenset({SupportWorkspaceState.SIMULATED, *_FAILED_OR_BLOCKED}),
    SupportWorkspaceState.SIMULATED: frozenset({
        SupportWorkspaceState.AWAITING_APPROVAL,
        SupportWorkspaceState.SIMULATING,
        SupportWorkspaceState.SCOPE_RESOLVING,
        *_FAILED_OR_BLOCKED,
    }),
    SupportWorkspaceState.AWAITING_APPROVAL: frozenset({
        SupportWorkspaceState.APPROVED,
        SupportWorkspaceState.SIMULATED,
        SupportWorkspaceState.BLOCKED,
        SupportWorkspaceState.OFFLINE_READ_ONLY,
    }),
    SupportWorkspaceState.APPROVED: frozenset({
        SupportWorkspaceState.APPLYING,
        SupportWorkspaceState.SIMULATING,
        SupportWorkspaceState.BLOCKED,
        SupportWorkspaceState.OFFLINE_READ_ONLY,
    }),
    SupportWorkspaceState.APPLYING: frozenset({
        SupportWorkspaceState.APPLIED,
        SupportWorkspaceState.ROLLING_BACK,
        SupportWorkspaceState.FAILED_SAFE,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.APPLIED: frozenset({
        SupportWorkspaceState.PROPAGATING,
        SupportWorkspaceState.VERIFYING,
        SupportWorkspaceState.ROLLING_BACK,
        SupportWorkspaceState.FAILED_SAFE,
    }),
    SupportWorkspaceState.PROPAGATING: frozenset({
        SupportWorkspaceState.VERIFYING,
        SupportWorkspaceState.ROLLING_BACK,
        SupportWorkspaceState.FAILED_SAFE,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.VERIFYING: frozenset({
        SupportWorkspaceState.VERIFIED,
        SupportWorkspaceState.ROLLING_BACK,
        SupportWorkspaceState.FAILED_SAFE,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.VERIFIED: frozenset({SupportWorkspaceState.RESOLVED, SupportWorkspaceState.ROLLING_BACK}),
    SupportWorkspaceState.RESOLVED: frozenset({SupportWorkspaceState.CASE_OPEN, SupportWorkspaceState.ROLLING_BACK}),
    SupportWorkspaceState.ROLLING_BACK: frozenset({
        SupportWorkspaceState.ROLLED_BACK,
        SupportWorkspaceState.FAILED_SAFE,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.ROLLED_BACK: frozenset({
        SupportWorkspaceState.CASE_OPEN,
        SupportWorkspaceState.VERIFYING,
        SupportWorkspaceState.RESOLVED,
    }),
    SupportWorkspaceState.FAILED_SAFE: frozenset({
        SupportWorkspaceState.CASE_OPEN,
        SupportWorkspaceState.ROLLING_BACK,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.OFFLINE_READ_ONLY: frozenset({
        SupportWorkspaceState.IDLE,
        SupportWorkspaceState.CASE_OPEN,
        SupportWorkspaceState.BLOCKED,
    }),
    SupportWorkspaceState.BLOCKED: frozenset({
        SupportWorkspaceState.IDLE,
        SupportWorkspaceState.CASE_OPEN,
        SupportWorkspaceState.SCOPE_RESOLVING,
        SupportWorkspaceState.OFFLINE_READ_ONLY,
    }),
}


class SupportStateMachine:
    """Validate every workspace transition and its safety invariants."""

    @staticmethod
    def _state(value: SupportWorkspaceState | str) -> SupportWorkspaceState:
        return value if isinstance(value, SupportWorkspaceState) else SupportWorkspaceState(str(value))

    @classmethod
    def allowed_targets(cls, current: SupportWorkspaceState | str) -> tuple[SupportWorkspaceState, ...]:
        state = cls._state(current)
        return tuple(sorted(STATE_TRANSITIONS[state], key=lambda item: item.value))

    @classmethod
    def validate_invariants(cls, target: SupportWorkspaceState | str, context: StateContext) -> None:
        state = cls._state(target)
        violations: list[str] = []
        if state == SupportWorkspaceState.SCOPE_VALID and (not context.scopeValid or context.scopeConflict):
            violations.append("SCOPE_VALID_REQUIRES_VALID_NON_CONFLICTING_SCOPE")
        if state == SupportWorkspaceState.SCOPE_CONFLICT and not context.scopeConflict:
            violations.append("SCOPE_CONFLICT_REQUIRES_CONFLICT")
        if state in {
            SupportWorkspaceState.DIAGNOSING,
            SupportWorkspaceState.DIAGNOSED,
            SupportWorkspaceState.SIMULATING,
            SupportWorkspaceState.SIMULATED,
            SupportWorkspaceState.AWAITING_APPROVAL,
            SupportWorkspaceState.APPROVED,
            SupportWorkspaceState.APPLYING,
        } and (not context.scopeValid or context.scopeConflict):
            violations.append("OPERATION_REQUIRES_VALID_SCOPE")
        if state == SupportWorkspaceState.DIAGNOSED and not context.diagnosisComplete:
            violations.append("DIAGNOSED_REQUIRES_COMPLETED_DIAGNOSIS")
        if state in {
            SupportWorkspaceState.SIMULATED,
            SupportWorkspaceState.AWAITING_APPROVAL,
            SupportWorkspaceState.APPROVED,
            SupportWorkspaceState.APPLYING,
        } and not context.simulationComplete:
            violations.append("STATE_REQUIRES_COMPLETED_SIMULATION")
        if state in {SupportWorkspaceState.APPROVED, SupportWorkspaceState.APPLYING} and not context.approvalGranted:
            violations.append("STATE_REQUIRES_APPROVAL")
        if state == SupportWorkspaceState.APPLYING:
            if not context.online:
                violations.append("APPLYING_FORBIDDEN_OFFLINE")
            if not context.backupAvailable:
                violations.append("APPLYING_REQUIRES_BACKUP")
            if not context.rollbackAvailable:
                violations.append("APPLYING_REQUIRES_ROLLBACK")
            if context.expectedRevision in (None, ""):
                violations.append("APPLYING_REQUIRES_EXPECTED_REVISION")
            elif context.currentRevision in (None, "") or context.expectedRevision != context.currentRevision:
                violations.append("APPLYING_REVISION_CONFLICT")
        if state == SupportWorkspaceState.APPLIED and not context.mutationPerformed:
            violations.append("APPLIED_REQUIRES_RECORDED_MUTATION")
        if state == SupportWorkspaceState.VERIFIED and not context.verificationPassed:
            violations.append("VERIFIED_REQUIRES_SUCCESSFUL_VERIFICATION")
        if state == SupportWorkspaceState.RESOLVED and not context.verificationPassed:
            violations.append("RESOLVED_REQUIRES_SUCCESSFUL_VERIFICATION")
        if state == SupportWorkspaceState.ROLLING_BACK and not context.rollbackAvailable:
            violations.append("ROLLING_BACK_REQUIRES_ROLLBACK")
        if state == SupportWorkspaceState.OFFLINE_READ_ONLY and context.online:
            violations.append("OFFLINE_READ_ONLY_REQUIRES_OFFLINE_CONTEXT")
        if context.blockers and state not in {
            SupportWorkspaceState.BLOCKED,
            SupportWorkspaceState.FAILED_SAFE,
            SupportWorkspaceState.OFFLINE_READ_ONLY,
            SupportWorkspaceState.ROLLING_BACK,
        }:
            violations.append("UNRESOLVED_BLOCKERS_REQUIRE_SAFE_STATE")
        if violations:
            raise StateInvariantViolation(";".join(violations))

    @classmethod
    def transition(
        cls,
        current: SupportWorkspaceState | str,
        target: SupportWorkspaceState | str,
        context: StateContext,
    ) -> StateTransition:
        previous = cls._state(current)
        desired = cls._state(target)
        if previous == desired:
            cls.validate_invariants(desired, context)
            return StateTransition(previous, desired, False)
        if desired not in STATE_TRANSITIONS[previous]:
            raise InvalidStateTransition(f"{previous.value}->{desired.value}")
        cls.validate_invariants(desired, context)
        return StateTransition(previous, desired, True)

    @classmethod
    def can_transition(
        cls,
        current: SupportWorkspaceState | str,
        target: SupportWorkspaceState | str,
        context: StateContext,
    ) -> bool:
        try:
            cls.transition(current, target, context)
            return True
        except (InvalidStateTransition, StateInvariantViolation, ValueError):
            return False


class CommandMode(str, Enum):
    READ = "READ"
    SIMULATE = "SIMULATE"
    MUTATE = "MUTATE"
    VERIFY = "VERIFY"
    EXPORT = "EXPORT"


@dataclass(frozen=True)
class CommandDescriptor:
    name: str
    mode: CommandMode
    mutates: bool
    requiredPermissions: tuple[str, ...] = ()
    featureGate: str | None = None
    requiresScope: bool = True
    requiredScopeFields: tuple[str, ...] = ("tenantId", "businessId")
    requiresFreshness: bool = True
    requiresExpectedRevision: bool = False
    requiresSimulation: bool = False
    requiresApproval: bool = False
    requiresBackup: bool = False
    requiresRollback: bool = False
    allowedStates: tuple[SupportWorkspaceState, ...] = ()
    risk: str = "LOW"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mode": self.mode.value,
            "mutates": self.mutates,
            "requiredPermissions": list(self.requiredPermissions),
            "featureGate": self.featureGate,
            "requiresScope": self.requiresScope,
            "requiredScopeFields": list(self.requiredScopeFields),
            "requiresFreshness": self.requiresFreshness,
            "requiresExpectedRevision": self.requiresExpectedRevision,
            "requiresSimulation": self.requiresSimulation,
            "requiresApproval": self.requiresApproval,
            "requiresBackup": self.requiresBackup,
            "requiresRollback": self.requiresRollback,
            "allowedStates": [state.value for state in self.allowedStates],
            "risk": self.risk,
        }


READ_CASE_STATES = (
    SupportWorkspaceState.CASE_OPEN,
    SupportWorkspaceState.SCOPE_VALID,
    SupportWorkspaceState.DIAGNOSED,
    SupportWorkspaceState.SIMULATED,
    SupportWorkspaceState.APPROVED,
    SupportWorkspaceState.APPLIED,
    SupportWorkspaceState.PROPAGATING,
    SupportWorkspaceState.VERIFYING,
    SupportWorkspaceState.VERIFIED,
    SupportWorkspaceState.RESOLVED,
    SupportWorkspaceState.FAILED_SAFE,
    SupportWorkspaceState.OFFLINE_READ_ONLY,
    SupportWorkspaceState.BLOCKED,
)
MUTATION_READY_STATES = (SupportWorkspaceState.APPROVED,)
LICENSE_MUTATION_STATES = (
    SupportWorkspaceState.SIMULATED,
    SupportWorkspaceState.APPROVED,
)


def _descriptor(
    name: str,
    *,
    mode: CommandMode,
    mutates: bool,
    permission: str | None = None,
    gate: str | None = None,
    scope: bool = True,
    freshness: bool = True,
    expected_revision: bool = False,
    simulation: bool = False,
    approval: bool = False,
    backup: bool = False,
    rollback: bool = False,
    states: Sequence[SupportWorkspaceState] = READ_CASE_STATES,
    risk: str = "LOW",
) -> CommandDescriptor:
    return CommandDescriptor(
        name=name,
        mode=mode,
        mutates=mutates,
        requiredPermissions=(permission,) if permission else (),
        featureGate=gate,
        requiresScope=scope,
        requiresFreshness=freshness,
        requiresExpectedRevision=expected_revision,
        requiresSimulation=simulation,
        requiresApproval=approval,
        requiresBackup=backup,
        requiresRollback=rollback,
        allowedStates=tuple(states),
        risk=risk,
    )


COMMAND_DESCRIPTORS: dict[str, CommandDescriptor] = {
    "createCase": _descriptor(
        "createCase", mode=CommandMode.MUTATE, mutates=True,
        permission="support.case.create", gate="support.case_management",
        scope=False, freshness=False,
        states=(SupportWorkspaceState.IDLE, SupportWorkspaceState.CASE_OPEN),
    ),
    "assignCase": _descriptor(
        "assignCase", mode=CommandMode.MUTATE, mutates=True,
        permission="support.case.assign", gate="support.case_management",
        expected_revision=True,
        states=(SupportWorkspaceState.CASE_OPEN, SupportWorkspaceState.BLOCKED),
    ),
    "refreshEvidence": _descriptor(
        "refreshEvidence", mode=CommandMode.READ, mutates=False,
        permission="support.evidence.read", freshness=False,
    ),
    "resolveScope": _descriptor(
        "resolveScope", mode=CommandMode.READ, mutates=False,
        permission="support.scope.read", scope=False, freshness=False,
        states=(SupportWorkspaceState.CASE_OPEN, SupportWorkspaceState.SCOPE_CONFLICT, SupportWorkspaceState.BLOCKED),
    ),
    "runDiagnosis": _descriptor(
        "runDiagnosis", mode=CommandMode.READ, mutates=False,
        permission="support.diagnosis.run",
        states=(SupportWorkspaceState.SCOPE_VALID, SupportWorkspaceState.DIAGNOSED),
    ),
    "runSimulation": _descriptor(
        "runSimulation", mode=CommandMode.SIMULATE, mutates=False,
        permission="support.simulation.run",
        states=(SupportWorkspaceState.DIAGNOSED, SupportWorkspaceState.SIMULATED, SupportWorkspaceState.APPROVED),
    ),
    "requestApproval": _descriptor(
        "requestApproval", mode=CommandMode.MUTATE, mutates=True,
        permission="support.approval.request", gate="support.approvals",
        expected_revision=True, simulation=True,
        states=(SupportWorkspaceState.SIMULATED,),
    ),
    "applyResolution": _descriptor(
        "applyResolution", mode=CommandMode.MUTATE, mutates=True,
        permission="support.resolution.apply", gate="support.resolution.apply",
        expected_revision=True, simulation=True, approval=True, backup=True, rollback=True,
        states=MUTATION_READY_STATES, risk="HIGH",
    ),
    "verifyResolution": _descriptor(
        "verifyResolution", mode=CommandMode.VERIFY, mutates=False,
        permission="support.resolution.verify",
        expected_revision=True,
        states=(SupportWorkspaceState.APPLIED, SupportWorkspaceState.PROPAGATING, SupportWorkspaceState.VERIFYING, SupportWorkspaceState.ROLLED_BACK),
    ),
    "rollbackResolution": _descriptor(
        "rollbackResolution", mode=CommandMode.MUTATE, mutates=True,
        permission="support.resolution.rollback", gate="support.resolution.rollback",
        expected_revision=True, backup=True, rollback=True,
        states=(SupportWorkspaceState.APPLYING, SupportWorkspaceState.APPLIED, SupportWorkspaceState.PROPAGATING, SupportWorkspaceState.VERIFYING, SupportWorkspaceState.VERIFIED, SupportWorkspaceState.RESOLVED, SupportWorkspaceState.FAILED_SAFE),
        risk="HIGH",
    ),
    "closeCase": _descriptor(
        "closeCase", mode=CommandMode.MUTATE, mutates=True,
        permission="support.case.close", gate="support.case_management",
        expected_revision=True,
        states=(SupportWorkspaceState.VERIFIED, SupportWorkspaceState.RESOLVED),
    ),
    "reopenCase": _descriptor(
        "reopenCase", mode=CommandMode.MUTATE, mutates=True,
        permission="support.case.reopen", gate="support.case_management",
        expected_revision=True,
        states=(SupportWorkspaceState.RESOLVED,),
    ),
    "exportEvidence": _descriptor(
        "exportEvidence", mode=CommandMode.EXPORT, mutates=False,
        permission="support.evidence.export", gate="support.evidence.export",
        freshness=False,
    ),
    "copySupportSummary": _descriptor(
        "copySupportSummary", mode=CommandMode.EXPORT, mutates=False,
        permission="support.summary.read", freshness=False,
    ),
    "escalateCase": _descriptor(
        "escalateCase", mode=CommandMode.MUTATE, mutates=True,
        permission="support.case.escalate", gate="support.case_management",
        expected_revision=True,
        states=READ_CASE_STATES,
    ),
}


LICENSE_COMMANDS = (
    "issueLicense",
    "importLicenses",
    "activateLicense",
    "assignLicense",
    "reassignLicense",
    "renewLicense",
    "changePlan",
    "changeModules",
    "changeSlots",
    "suspendLicense",
    "reactivateLicense",
    "cancelLicense",
    "revokeLicense",
    "replaceLicense",
    "moveDevice",
    "releaseDeviceSlot",
    "reconcileLicenseGroup",
)

for _name in LICENSE_COMMANDS:
    _risk = "CRITICAL" if _name in {"cancelLicense", "revokeLicense"} else "HIGH"
    _permission = "license.security.revoke" if _name == "revokeLicense" else "license.operations.write"
    _gate = "license.security" if _name == "revokeLicense" else "license.operations"
    COMMAND_DESCRIPTORS[_name] = _descriptor(
        _name,
        mode=CommandMode.MUTATE,
        mutates=True,
        permission=_permission,
        gate=_gate,
        expected_revision=True,
        simulation=True,
        approval=True,
        backup=True,
        rollback=True,
        states=LICENSE_MUTATION_STATES,
        risk=_risk,
    )

COMMAND_DESCRIPTORS["verifyPropagation"] = _descriptor(
    "verifyPropagation",
    mode=CommandMode.VERIFY,
    mutates=False,
    permission="license.propagation.verify",
    expected_revision=True,
    states=(
        SupportWorkspaceState.APPLIED,
        SupportWorkspaceState.PROPAGATING,
        SupportWorkspaceState.VERIFYING,
        SupportWorkspaceState.VERIFIED,
    ),
)


@dataclass(frozen=True)
class CommandContext:
    scope: JsonMapping = field(default_factory=dict)
    permissions: frozenset[str] = frozenset()
    featureGates: JsonMapping = field(default_factory=dict)
    freshness: str = "UNKNOWN"
    expectedRevision: Any = None
    currentRevision: Any = None
    correlationId: str | None = None
    simulationId: str | None = None
    approvalId: str | None = None
    backupId: str | None = None
    rollbackId: str | None = None
    state: SupportWorkspaceState = SupportWorkspaceState.IDLE
    online: bool = True
    blockers: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandDecision:
    command: str
    allowed: bool
    correlationId: str
    reasons: tuple[str, ...]
    requirements: JsonMapping
    executesExternalMutation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "allowed": self.allowed,
            "correlationId": self.correlationId,
            "reasons": list(self.reasons),
            "requirements": _json_copy(dict(self.requirements)),
            "executesExternalMutation": self.executesExternalMutation,
        }


class UnknownCommand(KeyError):
    pass


class CommandGuard:
    """Return a traceable allow/block decision without executing the command."""

    FRESH_VALUES = frozenset({"FRESH", "CURRENT", "SYNCED"})

    def __init__(self, *, correlation_factory: CorrelationFactory | None = None) -> None:
        self._new_correlation = correlation_factory or _correlation_id

    @staticmethod
    def descriptor(name: str) -> CommandDescriptor:
        try:
            return COMMAND_DESCRIPTORS[name]
        except KeyError as exc:
            raise UnknownCommand(name) from exc

    def evaluate(
        self,
        command: str | CommandDescriptor,
        context: CommandContext,
    ) -> CommandDecision:
        descriptor = command if isinstance(command, CommandDescriptor) else self.descriptor(command)
        correlation = str(context.correlationId or self._new_correlation())
        reasons: list[str] = []
        try:
            state = context.state if isinstance(context.state, SupportWorkspaceState) else SupportWorkspaceState(str(context.state))
        except ValueError:
            state = SupportWorkspaceState.BLOCKED
            reasons.append("INVALID_WORKSPACE_STATE")
        if descriptor.allowedStates and state not in descriptor.allowedStates:
            reasons.append("COMMAND_NOT_ALLOWED_IN_STATE")
        if context.blockers:
            reasons.append("UNRESOLVED_BLOCKERS")
        if descriptor.mutates and not context.online:
            reasons.append("OFFLINE_READ_ONLY")
        if descriptor.requiresScope:
            missing_scope = [
                key for key in descriptor.requiredScopeFields
                if context.scope.get(key) in (None, "")
            ]
            if missing_scope:
                reasons.append("SCOPE_INCOMPLETE:" + ",".join(missing_scope))
            if context.scope.get("conflict") is True or str(context.scope.get("status") or "").upper() == "SCOPE_CONFLICT":
                reasons.append("SCOPE_CONFLICT")
        missing_permissions = sorted(set(descriptor.requiredPermissions) - set(context.permissions))
        if missing_permissions:
            reasons.append("PERMISSION_REQUIRED:" + ",".join(missing_permissions))
        if descriptor.featureGate and context.featureGates.get(descriptor.featureGate) is not True:
            reasons.append("FEATURE_GATE_DISABLED:" + descriptor.featureGate)
        if descriptor.requiresFreshness and str(context.freshness).upper() not in self.FRESH_VALUES:
            reasons.append("FRESH_EVIDENCE_REQUIRED")
        if descriptor.requiresExpectedRevision:
            if context.expectedRevision in (None, ""):
                reasons.append("EXPECTED_REVISION_REQUIRED")
            elif context.currentRevision in (None, ""):
                reasons.append("CURRENT_REVISION_REQUIRED")
            elif context.expectedRevision != context.currentRevision:
                reasons.append("REVISION_CONFLICT")
        if descriptor.requiresSimulation and not context.simulationId:
            reasons.append("SIMULATION_REQUIRED")
        if descriptor.requiresApproval and not context.approvalId:
            reasons.append("APPROVAL_REQUIRED")
        if descriptor.requiresBackup and not context.backupId:
            reasons.append("BACKUP_REQUIRED")
        if descriptor.requiresRollback and not context.rollbackId:
            reasons.append("ROLLBACK_REQUIRED")
        requirements = {
            "scope": descriptor.requiresScope,
            "requiredScopeFields": list(descriptor.requiredScopeFields),
            "permissions": list(descriptor.requiredPermissions),
            "featureGate": descriptor.featureGate,
            "freshness": descriptor.requiresFreshness,
            "expectedRevision": descriptor.requiresExpectedRevision,
            "simulation": descriptor.requiresSimulation,
            "approval": descriptor.requiresApproval,
            "backup": descriptor.requiresBackup,
            "rollback": descriptor.requiresRollback,
            "online": descriptor.mutates,
        }
        return CommandDecision(
            command=descriptor.name,
            allowed=not reasons,
            correlationId=correlation,
            reasons=tuple(reasons),
            requirements=requirements,
            executesExternalMutation=False,
        )

    def plan(
        self,
        command: str | CommandDescriptor,
        context: CommandContext,
    ) -> dict[str, Any]:
        descriptor = command if isinstance(command, CommandDescriptor) else self.descriptor(command)
        decision = self.evaluate(descriptor, context)
        return {
            "descriptor": descriptor.to_dict(),
            "decision": decision.to_dict(),
            "externalExecutionRequired": descriptor.mutates,
            "mutationPerformed": False,
        }


def guard_command(
    command: str,
    context: CommandContext,
    *,
    correlation_factory: CorrelationFactory | None = None,
) -> CommandDecision:
    return CommandGuard(correlation_factory=correlation_factory).evaluate(command, context)


__all__ = [
    "ADAPTER_TYPES",
    "COMMAND_DESCRIPTORS",
    "AdapterCancelled",
    "AdapterContext",
    "AdapterFailure",
    "AuthorizationAdapter",
    "BaseSupportAdapter",
    "CommandContext",
    "CommandDecision",
    "CommandDescriptor",
    "CommandGuard",
    "CommandMode",
    "CustomerSetupAdapter",
    "DeviceContextAdapter",
    "DeviceFleetAdapter",
    "EvidenceAdapter",
    "FeatureGateAdapter",
    "IncidentTimelineAdapter",
    "InvalidAdapterPayload",
    "InvalidStateTransition",
    "LicenseContextAdapter",
    "LicenseOperationsAdapter",
    "ScopeResolutionAdapter",
    "StaleAdapterResponse",
    "StateContext",
    "StateInvariantViolation",
    "StateTransition",
    "SupportActionAdapter",
    "SupportCaseAdapter",
    "SupportSearchAdapter",
    "SupportStateMachine",
    "SupportWorkspaceState",
    "SupportWorkspaceViewModel",
    "SurfaceStatusAdapter",
    "TriAppConsistencyAdapter",
    "guard_command",
]
