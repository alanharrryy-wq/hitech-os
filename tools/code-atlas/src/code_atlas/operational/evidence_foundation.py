from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Optional

EVIDENCE_SCHEMA_VERSION = "code_atlas_evidence_record.v1"
FRESHNESS_POLICY_SCHEMA_VERSION = "code_atlas_freshness_policy.v1"
TRUST_LEVELS = (
    "PLACEHOLDER",
    "HEURISTIC",
    "SOURCE",
    "CONTRACT",
    "RUNTIME",
    "AUTHORITATIVE",
)

VOLATILE_KEYS = {
    "createdAt",
    "created_at",
    "generatedAt",
    "generated_at",
    "output_dir",
    "outputDir",
    "project_root",
    "projectRoot",
    "repo",
}


def canonicalize(value: Any, *, drop_keys: Iterable[str] = ()) -> Any:
    drop = set(drop_keys)
    if isinstance(value, Mapping):
        return {
            str(key): canonicalize(value[key], drop_keys=drop)
            for key in sorted(value, key=lambda item: str(item))
            if str(key) not in drop
        }
    if isinstance(value, (list, tuple)):
        return [canonicalize(item, drop_keys=drop) for item in value]
    if isinstance(value, set):
        normalized = [canonicalize(item, drop_keys=drop) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, default=str))
    if isinstance(value, datetime):
        return normalize_timestamp(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def canonical_json(value: Any, *, drop_keys: Iterable[str] = ()) -> str:
    return json.dumps(
        canonicalize(value, drop_keys=drop_keys),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_digest(value: Any, *, drop_keys: Iterable[str] = ()) -> str:
    return hashlib.sha256(canonical_json(value, drop_keys=drop_keys).encode("utf-8")).hexdigest()


def parse_timestamp(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        parsed = value
    elif value is None or str(value).strip() == "":
        return None
    else:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def normalize_timestamp(value: Any) -> str:
    parsed = parse_timestamp(value)
    if parsed is None:
        raise ValueError(f"timestamp must be ISO-8601 with timezone: {value!r}")
    return parsed.isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class ScopeIdentity:
    tenant_id: Optional[str] = None
    business_id: Optional[str] = None
    client_id: Optional[str] = None
    store_id: Optional[str] = None
    terminal_id: Optional[str] = None
    device_id: Optional[str] = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "ScopeIdentity":
        value = value or {}

        def pick(*keys: str) -> Optional[str]:
            for key in keys:
                raw = value.get(key)
                if raw not in (None, ""):
                    return str(raw)
            return None

        return cls(
            tenant_id=pick("tenantId", "tenant_id"),
            business_id=pick("businessId", "business_id"),
            client_id=pick("clientId", "client_id"),
            store_id=pick("storeId", "store_id"),
            terminal_id=pick("terminalId", "terminal_id"),
            device_id=pick("deviceId", "device_id", "originDeviceId", "origin_device_id"),
        )

    def as_dict(self) -> dict[str, str]:
        return {key: value for key, value in asdict(self).items() if value not in (None, "")}

    def relation(self, other: "ScopeIdentity") -> str:
        left = self.as_dict()
        right = other.as_dict()
        shared = set(left) & set(right)
        if any(left[key] != right[key] for key in shared):
            return "CONFLICT"
        if not left and not right:
            return "UNSCOPED"
        if not shared:
            return "PARTIAL_OR_UNRELATED"
        return "MATCH"


@dataclass(frozen=True)
class EvidenceRecord:
    capability_id: str
    source_kind: str
    source_ref: str
    observed_at: str
    trust_level: str
    payload_digest: str
    scope: ScopeIdentity = field(default_factory=ScopeIdentity)
    claims: tuple[str, ...] = ()
    does_not_prove: tuple[str, ...] = ()
    record_id: str = ""
    schema_version: str = EVIDENCE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.capability_id.strip():
            raise ValueError("capability_id is required")
        if not self.source_kind.strip() or not self.source_ref.strip():
            raise ValueError("source_kind and source_ref are required")
        if self.trust_level not in TRUST_LEVELS:
            raise ValueError(f"invalid trust_level: {self.trust_level}")
        normalized = normalize_timestamp(self.observed_at)
        object.__setattr__(self, "observed_at", normalized)
        if len(self.payload_digest) != 64:
            raise ValueError("payload_digest must be a sha256 hex digest")
        if not self.does_not_prove:
            raise ValueError("does_not_prove must be explicit")
        if not self.record_id:
            identity = {
                "schemaVersion": self.schema_version,
                "capabilityId": self.capability_id,
                "sourceKind": self.source_kind,
                "sourceRef": self.source_ref,
                "observedAt": self.observed_at,
                "payloadDigest": self.payload_digest,
                "scope": self.scope.as_dict(),
            }
            object.__setattr__(self, "record_id", canonical_digest(identity))

    def as_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": self.schema_version,
            "recordId": self.record_id,
            "capabilityId": self.capability_id,
            "sourceKind": self.source_kind,
            "sourceRef": self.source_ref,
            "observedAt": self.observed_at,
            "trustLevel": self.trust_level,
            "payloadDigest": self.payload_digest,
            "scope": self.scope.as_dict(),
            "claims": list(self.claims),
            "doesNotProve": list(self.does_not_prove),
            "certifiable": False,
            "productionCertified": False,
        }


def make_evidence_record(
    *,
    capability_id: str,
    source_kind: str,
    source_ref: str,
    observed_at: Any,
    trust_level: str,
    payload: Any,
    scope: Mapping[str, Any] | ScopeIdentity | None = None,
    claims: Iterable[str] = (),
    does_not_prove: Iterable[str],
) -> EvidenceRecord:
    scope_identity = scope if isinstance(scope, ScopeIdentity) else ScopeIdentity.from_mapping(scope)
    return EvidenceRecord(
        capability_id=capability_id,
        source_kind=source_kind,
        source_ref=source_ref,
        observed_at=normalize_timestamp(observed_at),
        trust_level=trust_level,
        payload_digest=canonical_digest(payload, drop_keys=VOLATILE_KEYS),
        scope=scope_identity,
        claims=tuple(str(item) for item in claims),
        does_not_prove=tuple(str(item) for item in does_not_prove),
    )


@dataclass(frozen=True)
class FreshnessPolicy:
    policy_id: str
    ttl_seconds: int
    max_future_skew_seconds: int = 300

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("policy_id is required")
        if isinstance(self.ttl_seconds, bool) or not isinstance(self.ttl_seconds, int) or self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be a positive integer")
        if (
            isinstance(self.max_future_skew_seconds, bool)
            or not isinstance(self.max_future_skew_seconds, int)
            or self.max_future_skew_seconds < 0
        ):
            raise ValueError("max_future_skew_seconds must be a non-negative integer")

    def as_dict(self) -> dict[str, Any]:
        core = {
            "schemaVersion": FRESHNESS_POLICY_SCHEMA_VERSION,
            "policyId": self.policy_id,
            "ttlSeconds": self.ttl_seconds,
            "maxFutureSkewSeconds": self.max_future_skew_seconds,
        }
        return {**core, "policyDigest": canonical_digest(core)}


def _alias_value(value: Mapping[str, Any], camel: str, snake: str) -> tuple[Any, str | None]:
    camel_present = camel in value
    snake_present = snake in value
    if camel_present and snake_present and value[camel] != value[snake]:
        return None, f"CONFLICTING_ALIASES:{camel}:{snake}"
    if camel_present:
        return value[camel], None
    if snake_present:
        return value[snake], None
    return None, None


def parse_freshness_policy(value: Any) -> tuple[FreshnessPolicy | None, dict[str, Any]]:
    if isinstance(value, FreshnessPolicy):
        return value, {
            "status": "PASS_FRESHNESS_POLICY_VALID",
            **value.as_dict(),
            "productionCertified": False,
        }
    if not isinstance(value, Mapping):
        return None, {
            "status": "BLOCKED_INVALID_FRESHNESS_POLICY",
            "reason": "POLICY_MUST_BE_OBJECT",
            "productionCertified": False,
        }
    allowed = {
        "schemaVersion",
        "policyId",
        "policy_id",
        "ttlSeconds",
        "ttl_seconds",
        "maxFutureSkewSeconds",
        "max_future_skew_seconds",
    }
    unknown = sorted(str(key) for key in value if str(key) not in allowed)
    if unknown:
        return None, {
            "status": "BLOCKED_INVALID_FRESHNESS_POLICY",
            "reason": "UNKNOWN_FIELDS",
            "unknownFields": unknown,
            "productionCertified": False,
        }
    schema = value.get("schemaVersion")
    if schema not in (None, "", FRESHNESS_POLICY_SCHEMA_VERSION):
        return None, {
            "status": "BLOCKED_INVALID_FRESHNESS_POLICY",
            "reason": "UNSUPPORTED_SCHEMA",
            "schemaVersion": schema,
            "productionCertified": False,
        }
    policy_id, alias_error = _alias_value(value, "policyId", "policy_id")
    if alias_error:
        return None, {"status": "BLOCKED_INVALID_FRESHNESS_POLICY", "reason": alias_error, "productionCertified": False}
    ttl, alias_error = _alias_value(value, "ttlSeconds", "ttl_seconds")
    if alias_error:
        return None, {"status": "BLOCKED_INVALID_FRESHNESS_POLICY", "reason": alias_error, "productionCertified": False}
    skew, alias_error = _alias_value(value, "maxFutureSkewSeconds", "max_future_skew_seconds")
    if alias_error:
        return None, {"status": "BLOCKED_INVALID_FRESHNESS_POLICY", "reason": alias_error, "productionCertified": False}
    if skew is None:
        skew = 300
    try:
        if policy_id in (None, ""):
            raise ValueError("policyId is required")
        policy = FreshnessPolicy(str(policy_id), ttl, skew)
    except ValueError as exc:
        return None, {
            "status": "BLOCKED_INVALID_FRESHNESS_POLICY",
            "reason": str(exc),
            "productionCertified": False,
        }
    return policy, {
        "status": "PASS_FRESHNESS_POLICY_VALID",
        **policy.as_dict(),
        "productionCertified": False,
    }


def parse_freshness_policies(value: Any) -> tuple[dict[str, FreshnessPolicy], list[dict[str, Any]]]:
    if not isinstance(value, Mapping):
        return {}, [{
            "status": "BLOCKED_FRESHNESS_POLICY_REGISTRY_MISSING",
            "sourceKind": None,
            "productionCertified": False,
        }]
    policies: dict[str, FreshnessPolicy] = {}
    rows: list[dict[str, Any]] = []
    for raw_key in sorted(value, key=lambda item: str(item)):
        source_kind = str(raw_key).strip()
        if not source_kind:
            rows.append({
                "status": "BLOCKED_INVALID_FRESHNESS_POLICY_KEY",
                "sourceKind": source_kind,
                "productionCertified": False,
            })
            continue
        policy, result = parse_freshness_policy(value[raw_key])
        rows.append({"sourceKind": source_kind, **result})
        if policy is not None:
            policies[source_kind] = policy
    if not rows:
        rows.append({
            "status": "BLOCKED_FRESHNESS_POLICY_REGISTRY_EMPTY",
            "sourceKind": None,
            "productionCertified": False,
        })
    return policies, rows


def assess_freshness(
    observed_at: Any,
    policy: FreshnessPolicy | None,
    *,
    now: Any,
) -> dict[str, Any]:
    if policy is None:
        return {
            "status": "BLOCKED_FRESHNESS_POLICY_UNDEFINED",
            "fresh": False,
            "policyId": None,
            "doesNotProve": ["Freshness without an explicit TTL/clock policy."],
        }
    observed = parse_timestamp(observed_at)
    current = parse_timestamp(now)
    if observed is None:
        return {
            "status": "BLOCKED_INVALID_OR_MISSING_TIMESTAMP",
            "fresh": False,
            "policyId": policy.policy_id,
        }
    if current is None:
        raise ValueError("now must be timezone-aware")
    if observed > current + timedelta(seconds=policy.max_future_skew_seconds):
        return {
            "status": "BLOCKED_FUTURE_TIMESTAMP",
            "fresh": False,
            "policyId": policy.policy_id,
            "observedAt": normalize_timestamp(observed),
            "now": normalize_timestamp(current),
        }
    age_seconds = max(0, int((current - observed).total_seconds()))
    fresh = age_seconds <= policy.ttl_seconds
    return {
        "status": "FRESH" if fresh else "STALE",
        "fresh": fresh,
        "policyId": policy.policy_id,
        "ageSeconds": age_seconds,
        "ttlSeconds": policy.ttl_seconds,
        "observedAt": normalize_timestamp(observed),
        "now": normalize_timestamp(current),
    }


def _event_scope(event: Mapping[str, Any]) -> dict[str, str]:
    nested = event.get("scope")
    source = nested if isinstance(nested, Mapping) else event
    return ScopeIdentity.from_mapping(source).as_dict()


def assess_audit_completeness(
    required_actions: Iterable[str] | None,
    events: Iterable[Mapping[str, Any]],
    *,
    required_scope: Mapping[str, Any] | ScopeIdentity | None = None,
) -> dict[str, Any]:
    required = sorted({str(item).strip() for item in (required_actions or []) if str(item).strip()})
    if not required:
        return {
            "status": "BLOCKED_AUDIT_ACTION_CATALOG_MISSING",
            "complete": False,
            "requiredActions": [],
            "missingActions": [],
            "doesNotProve": ["Audit completeness without an authoritative action catalog."],
            "productionCertified": False,
        }
    scope_identity = required_scope if isinstance(required_scope, ScopeIdentity) else ScopeIdentity.from_mapping(required_scope)
    scope = scope_identity.as_dict()
    if not scope:
        return {
            "status": "BLOCKED_AUDIT_SCOPE_CONTRACT_MISSING",
            "complete": False,
            "requiredActions": required,
            "requiredScope": {},
            "missingActions": required,
            "doesNotProve": ["Audit completeness without an explicit governed scope identity."],
            "productionCertified": False,
        }

    matched: dict[str, list[str]] = {action: [] for action in required}
    wrong_scope: list[dict[str, Any]] = []
    invalid_provenance: list[dict[str, Any]] = []
    observed_counts: dict[str, int] = {action: 0 for action in required}

    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            continue
        action = str(event.get("action") or event.get("eventType") or event.get("type") or "").strip()
        if action not in matched:
            continue
        event_scope = _event_scope(event)
        missing_scope_keys = [key for key in scope if key not in event_scope]
        conflicts = [key for key in scope if key in event_scope and event_scope[key] != scope[key]]
        event_ref = str(event.get("eventId") or event.get("recordId") or event.get("id") or "").strip()
        if missing_scope_keys or conflicts:
            wrong_scope.append({
                "action": action,
                "eventRef": event_ref or f"event-index:{index}",
                "missingScopeKeys": missing_scope_keys,
                "conflictingScopeKeys": conflicts,
            })
            continue
        if not event_ref:
            invalid_provenance.append({"action": action, "eventIndex": index, "reason": "MISSING_EVENT_IDENTITY"})
            continue
        matched[action].append(event_ref)
        observed_counts[action] += 1

    missing = [action for action in required if not matched[action]]
    duplicates = {action: len(refs) for action, refs in matched.items() if len(refs) > 1}
    if wrong_scope:
        status = "BLOCKED_WRONG_SCOPE_AUDIT_EVENTS"
    elif invalid_provenance:
        status = "BLOCKED_AUDIT_EVENT_PROVENANCE_INVALID"
    elif missing:
        status = "BLOCKED_MISSING_AUDIT_EVENTS"
    elif duplicates:
        status = "BLOCKED_DUPLICATE_AUDIT_EVENTS"
    else:
        status = "PASS_AUDIT_COVERAGE"
    return {
        "status": status,
        "complete": status == "PASS_AUDIT_COVERAGE",
        "requiredActions": required,
        "requiredScope": scope,
        "observedCounts": observed_counts,
        "missingActions": missing,
        "duplicateActionCounts": duplicates,
        "wrongScopeEvents": wrong_scope,
        "invalidProvenanceEvents": invalid_provenance,
        "productionCertified": False,
        "doesNotProve": [
            "Tenant isolation outside the exact audited scope.",
            "Runtime completeness beyond the supplied authoritative action catalog and events.",
        ],
    }
