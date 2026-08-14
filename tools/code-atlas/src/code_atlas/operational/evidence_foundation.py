from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Optional

EVIDENCE_SCHEMA_VERSION = "code_atlas_evidence_record.v1"
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
        if self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")
        if self.max_future_skew_seconds < 0:
            raise ValueError("max_future_skew_seconds must be >= 0")


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


def assess_audit_completeness(
    required_actions: Iterable[str] | None,
    events: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    required = sorted({str(item).strip() for item in (required_actions or []) if str(item).strip()})
    if not required:
        return {
            "status": "BLOCKED_AUDIT_ACTION_CATALOG_MISSING",
            "complete": False,
            "requiredActions": [],
            "missingActions": [],
            "doesNotProve": ["Audit completeness without an authoritative action catalog."],
        }
    counts: dict[str, int] = {}
    for event in events:
        action = str(event.get("action") or event.get("eventType") or event.get("type") or "").strip()
        if action:
            counts[action] = counts.get(action, 0) + 1
    missing = [action for action in required if counts.get(action, 0) == 0]
    duplicates = {action: count for action, count in counts.items() if count > 1 and action in required}
    return {
        "status": "PASS_AUDIT_COVERAGE" if not missing else "BLOCKED_MISSING_AUDIT_EVENTS",
        "complete": not missing,
        "requiredActions": required,
        "observedCounts": {action: counts.get(action, 0) for action in required},
        "missingActions": missing,
        "duplicateActionCounts": duplicates,
        "productionCertified": False,
    }
