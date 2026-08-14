from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from .evidence_foundation import ScopeIdentity, canonical_digest, parse_timestamp

RISK_SCOPE_VERSION = "code_atlas_risk_scope_foundation.v1"

SEVERITY_FACTORS = {
    "LOW": 0.25,
    "MEDIUM": 0.50,
    "HIGH": 0.75,
    "CRITICAL": 1.00,
}

REQUIRED_ISOLATION_TESTS = (
    "cross_tenant_read",
    "cross_tenant_join",
    "cross_business_projection",
    "wrong_scope_runtime_evidence",
)

_ALLOWED_EVIDENCE_LEVELS = {"source_test", "runtime"}


@dataclass(frozen=True)
class RiskPolicy:
    max_age_seconds: int
    decay_half_life_seconds: int
    max_future_skew_seconds: int
    thresholds: tuple[tuple[str, float], ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "RiskPolicy":
        if not isinstance(value, Mapping):
            raise ValueError("risk policy is required")
        required = {
            "maxAgeSeconds",
            "decayHalfLifeSeconds",
            "maxFutureSkewSeconds",
            "thresholds",
        }
        missing = required - set(value)
        if missing:
            raise ValueError(f"risk policy missing {sorted(missing)}")
        max_age = int(value["maxAgeSeconds"])
        half_life = int(value["decayHalfLifeSeconds"])
        skew = int(value["maxFutureSkewSeconds"])
        if max_age <= 0 or half_life <= 0 or skew < 0:
            raise ValueError("risk policy durations must be positive and skew non-negative")
        raw_thresholds = value["thresholds"]
        if not isinstance(raw_thresholds, Mapping) or not raw_thresholds:
            raise ValueError("risk thresholds must be a non-empty mapping")
        thresholds = tuple(
            sorted(
                ((str(name).upper(), float(score)) for name, score in raw_thresholds.items()),
                key=lambda item: item[1],
            )
        )
        scores = [score for _, score in thresholds]
        if scores[0] != 0.0 or any(score < 0.0 or score > 100.0 for score in scores):
            raise ValueError("risk thresholds must start at 0 and remain within 0..100")
        if scores != sorted(set(scores)):
            raise ValueError("risk thresholds must be unique and ascending")
        return cls(max_age, half_life, skew, thresholds)


def _blocked(status: str, blockers: Sequence[str], **extra: Any) -> dict[str, Any]:
    return {
        "schemaVersion": RISK_SCOPE_VERSION,
        "status": status,
        "blockers": sorted(set(str(item) for item in blockers)),
        "certifiable": False,
        "productionCertified": False,
        **extra,
    }


def _signal_row(value: Mapping[str, Any], policy: RiskPolicy, now: datetime) -> tuple[dict[str, Any] | None, str | None]:
    required = {
        "signalId",
        "clientId",
        "severity",
        "confidence",
        "weight",
        "observedAt",
        "sourceRef",
    }
    missing = required - set(value)
    if missing:
        return None, f"signal_missing_fields:{','.join(sorted(missing))}"
    signal_id = str(value["signalId"]).strip()
    client_id = str(value["clientId"]).strip()
    source_ref = str(value["sourceRef"]).strip()
    severity = str(value["severity"]).upper().strip()
    observed = parse_timestamp(value["observedAt"])
    if not signal_id or not client_id or not source_ref:
        return None, "signal_identity_or_source_empty"
    if severity not in SEVERITY_FACTORS:
        return None, f"signal_invalid_severity:{signal_id}"
    if observed is None:
        return None, f"signal_invalid_timestamp:{signal_id}"
    try:
        confidence = float(value["confidence"])
        weight = float(value["weight"])
    except (TypeError, ValueError):
        return None, f"signal_invalid_numeric:{signal_id}"
    if not (0.0 <= confidence <= 1.0) or not (0.0 < weight <= 100.0):
        return None, f"signal_numeric_out_of_range:{signal_id}"

    age_seconds = (now - observed).total_seconds()
    if age_seconds < -policy.max_future_skew_seconds:
        return None, f"signal_future_timestamp:{signal_id}"
    if age_seconds > policy.max_age_seconds:
        return None, f"signal_stale:{signal_id}"
    effective_age = max(0.0, age_seconds)
    decay = math.pow(0.5, effective_age / policy.decay_half_life_seconds)
    severity_factor = SEVERITY_FACTORS[severity]
    raw_contribution = severity_factor * confidence * weight * decay
    scope = ScopeIdentity.from_mapping(
        value.get("scope") if isinstance(value.get("scope"), Mapping) else value
    ).as_dict()
    row = {
        "signalId": signal_id,
        "clientId": client_id,
        "severity": severity,
        "severityFactor": severity_factor,
        "confidence": confidence,
        "weight": weight,
        "observedAt": observed.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "ageSeconds": round(effective_age, 3),
        "decayFactor": round(decay, 8),
        "rawContribution": round(raw_contribution, 8),
        "sourceRef": source_ref,
        "scope": scope,
    }
    row["signalDigest"] = canonical_digest(row)
    return row, None


def evaluate_client_risk(
    signals: Sequence[Mapping[str, Any]] | None,
    policy: Mapping[str, Any] | RiskPolicy | None,
    *,
    now: Any = None,
) -> dict[str, Any]:
    """Calculate a deterministic score only when the full policy/signal contract exists.

    This is deliberately fail-closed. Missing or stale signals produce no score.
    """
    try:
        typed_policy = policy if isinstance(policy, RiskPolicy) else RiskPolicy.from_mapping(policy)
    except (TypeError, ValueError) as exc:
        return _blocked(
            "BLOCKED_MISSING_OR_INVALID_RISK_POLICY",
            [str(exc)],
            score=None,
            riskBand=None,
            signalCount=0,
            explanation=[],
        )

    current = parse_timestamp(now) if now is not None else datetime.now(timezone.utc)
    if current is None:
        return _blocked(
            "BLOCKED_INVALID_RISK_CLOCK",
            ["now_must_be_timezone_aware_iso8601"],
            score=None,
            riskBand=None,
            signalCount=0,
            explanation=[],
        )
    if not isinstance(signals, Sequence) or isinstance(signals, (str, bytes, bytearray)) or not signals:
        return _blocked(
            "BLOCKED_NO_RISK_SIGNALS",
            ["risk_signal_evidence_missing"],
            score=None,
            riskBand=None,
            signalCount=0,
            explanation=[],
        )

    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    seen: set[str] = set()
    client_ids: set[str] = set()
    for raw in signals:
        if not isinstance(raw, Mapping):
            blockers.append("signal_not_mapping")
            continue
        row, error = _signal_row(raw, typed_policy, current)
        if error:
            blockers.append(error)
            continue
        assert row is not None
        signal_id = row["signalId"]
        if signal_id in seen:
            blockers.append(f"duplicate_signal_id:{signal_id}")
            continue
        seen.add(signal_id)
        client_ids.add(row["clientId"])
        rows.append(row)

    if len(client_ids) > 1:
        blockers.append("mixed_client_signals")
    if blockers or not rows:
        return _blocked(
            "BLOCKED_RISK_SIGNAL_CONTRACT",
            blockers or ["no_valid_signals"],
            score=None,
            riskBand=None,
            signalCount=len(rows),
            explanation=sorted(rows, key=lambda row: row["signalId"]),
        )

    total_weight = sum(float(row["weight"]) for row in rows)
    weighted = sum(float(row["rawContribution"]) for row in rows)
    score = round(max(0.0, min(100.0, 100.0 * weighted / total_weight)), 2)
    band = typed_policy.thresholds[0][0]
    for name, threshold in typed_policy.thresholds:
        if score >= threshold:
            band = name

    explanation = []
    for row in sorted(rows, key=lambda item: item["signalId"]):
        item = dict(row)
        item["normalizedContributionPoints"] = round(
            100.0 * float(row["rawContribution"]) / total_weight,
            4,
        )
        explanation.append(item)
    return {
        "schemaVersion": RISK_SCOPE_VERSION,
        "status": "RISK_SCORE_CONTRACT_BACKED",
        "clientId": next(iter(client_ids)),
        "score": score,
        "riskBand": band,
        "signalCount": len(rows),
        "policy": {
            "maxAgeSeconds": typed_policy.max_age_seconds,
            "decayHalfLifeSeconds": typed_policy.decay_half_life_seconds,
            "maxFutureSkewSeconds": typed_policy.max_future_skew_seconds,
            "thresholds": dict(typed_policy.thresholds),
        },
        "explanation": explanation,
        "blockers": [],
        "certifiable": False,
        "productionCertified": False,
        "doesNotProve": [
            "Business outcome prediction or calibration beyond the supplied governed policy.",
            "Production risk state when supplied signals are not runtime-backed.",
        ],
    }


def _scope_pair_is_cross_scope(source: Mapping[str, Any], target: Mapping[str, Any]) -> bool:
    left = ScopeIdentity.from_mapping(source)
    right = ScopeIdentity.from_mapping(target)
    return left.relation(right) == "CONFLICT"


def evaluate_tenant_isolation(
    scope_authority: Any,
    evidence: Sequence[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    """Evaluate required negative isolation cases without converting them into certification."""
    scope_status = ""
    if isinstance(scope_authority, Mapping):
        scope_status = str(scope_authority.get("status") or "")
    elif isinstance(scope_authority, list) and scope_authority and isinstance(scope_authority[0], Mapping):
        scope_status = str(scope_authority[0].get("status") or "")
    scope_observed = scope_status == "PASS_SCOPE_AUTHORITY_FOUND"

    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes, bytearray)):
        evidence = []
    rows: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []
    failures: list[str] = []
    for raw in evidence:
        if not isinstance(raw, Mapping):
            blockers.append("negative_test_not_mapping")
            continue
        test_id = str(raw.get("testId") or "")
        if test_id not in REQUIRED_ISOLATION_TESTS:
            blockers.append(f"unknown_negative_test:{test_id or 'missing'}")
            continue
        if test_id in rows:
            blockers.append(f"duplicate_negative_test:{test_id}")
            continue
        level = str(raw.get("evidenceLevel") or "")
        assertion = str(raw.get("assertion") or "")
        status = str(raw.get("status") or "")
        source_ref = str(raw.get("sourceRef") or "")
        source_scope = raw.get("sourceScope")
        target_scope = raw.get("targetScope")
        if level not in _ALLOWED_EVIDENCE_LEVELS:
            blockers.append(f"invalid_evidence_level:{test_id}")
        if assertion != "ACCESS_DENIED_OR_EMPTY":
            blockers.append(f"invalid_negative_assertion:{test_id}")
        if status not in {"PASS", "FAIL"}:
            blockers.append(f"invalid_negative_status:{test_id}")
        if not source_ref:
            blockers.append(f"missing_negative_source_ref:{test_id}")
        if not isinstance(source_scope, Mapping) or not isinstance(target_scope, Mapping):
            blockers.append(f"missing_scope_pair:{test_id}")
        elif not _scope_pair_is_cross_scope(source_scope, target_scope):
            blockers.append(f"negative_case_not_cross_scope:{test_id}")
        if status == "FAIL":
            failures.append(test_id)
        row = {
            "testId": test_id,
            "status": status,
            "assertion": assertion,
            "evidenceLevel": level,
            "sourceRef": source_ref,
            "sourceScope": ScopeIdentity.from_mapping(source_scope if isinstance(source_scope, Mapping) else {}).as_dict(),
            "targetScope": ScopeIdentity.from_mapping(target_scope if isinstance(target_scope, Mapping) else {}).as_dict(),
        }
        row["evidenceDigest"] = canonical_digest(row)
        rows[test_id] = row

    missing = sorted(set(REQUIRED_ISOLATION_TESTS) - set(rows))
    if missing:
        blockers.extend(f"missing_negative_test:{item}" for item in missing)
    runtime_backed = bool(rows) and not blockers and all(
        row["evidenceLevel"] == "runtime" for row in rows.values()
    )

    ordered = [rows[test_id] for test_id in REQUIRED_ISOLATION_TESTS if test_id in rows]
    if failures:
        return _blocked(
            "FAIL_CROSS_SCOPE_ISOLATION",
            [*blockers, *(f"failed_negative_test:{item}" for item in failures)],
            scopeAuthorityObserved=scope_observed,
            negativeTestsPassed=False,
            runtimeBacked=runtime_backed,
            requiredNegativeTests=list(REQUIRED_ISOLATION_TESTS),
            evidence=ordered,
        )
    if blockers:
        return _blocked(
            "BLOCKED_NEGATIVE_ISOLATION_TESTS_REQUIRED",
            blockers,
            scopeAuthorityObserved=scope_observed,
            negativeTestsPassed=False,
            runtimeBacked=False,
            requiredNegativeTests=list(REQUIRED_ISOLATION_TESTS),
            evidence=ordered,
        )

    if not scope_observed:
        return _blocked(
            "BLOCKED_SCOPE_AUTHORITY_REQUIRED",
            ["scope_authority_not_observed"],
            scopeAuthorityObserved=False,
            negativeTestsPassed=True,
            runtimeBacked=runtime_backed,
            requiredNegativeTests=list(REQUIRED_ISOLATION_TESTS),
            evidence=ordered,
        )

    status = (
        "NEGATIVE_ISOLATION_RUNTIME_EVIDENCE_OBSERVED_NOT_CERTIFIED"
        if runtime_backed
        else "NEGATIVE_ISOLATION_CONTRACT_SOURCE_TESTED"
    )
    return {
        "schemaVersion": RISK_SCOPE_VERSION,
        "status": status,
        "scopeAuthorityObserved": scope_observed,
        "negativeTestsPassed": True,
        "runtimeBacked": runtime_backed,
        "requiredNegativeTests": list(REQUIRED_ISOLATION_TESTS),
        "evidence": ordered,
        "blockers": [],
        "certifiable": False,
        "productionCertified": False,
        "doesNotProve": [
            "Production tenant isolation without current runtime negative evidence across all required cases.",
            "Authorization correctness outside the tested scope pairs.",
        ],
    }


__all__ = [
    "REQUIRED_ISOLATION_TESTS",
    "RISK_SCOPE_VERSION",
    "RiskPolicy",
    "evaluate_client_risk",
    "evaluate_tenant_isolation",
]
