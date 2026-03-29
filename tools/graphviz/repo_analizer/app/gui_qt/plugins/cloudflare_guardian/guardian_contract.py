from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

GUARDIAN_REQUIRED_KEYS = (
    "hostname",
    "tunnel_id",
    "origin_expected",
    "origin_observed",
    "config_path",
    "last_good_state",
    "current_error",
    "last_check_time",
)


@dataclass(slots=True)
class CloudflareGuardianContext:
    hostname: str = ""
    tunnel_id: str = ""
    origin_expected: str = ""
    origin_observed: str = ""
    config_path: str = ""
    last_good_state: str = ""
    current_error: str = ""
    last_check_time: str = ""

    def to_payload(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GuardianSectionCard:
    title: str
    headline: str
    detail: str


def normalize_guardian_context(payload: Any) -> CloudflareGuardianContext:
    if isinstance(payload, CloudflareGuardianContext):
        return payload

    mapping: Mapping[str, Any]
    if isinstance(payload, Mapping):
        mapping = payload
    else:
        mapping = {}
        for key in GUARDIAN_REQUIRED_KEYS:
            if hasattr(payload, key):
                mapping[key] = getattr(payload, key)

    normalized = {
        key: str(mapping.get(key) or "").strip()
        for key in GUARDIAN_REQUIRED_KEYS
    }
    return CloudflareGuardianContext(**normalized)


def build_guardian_cards(payload: Any) -> dict[str, GuardianSectionCard]:
    ctx = normalize_guardian_context(payload)
    drift = "match" if ctx.origin_expected and ctx.origin_expected == ctx.origin_observed else "drift"
    health_headline = "Healthy" if not ctx.current_error else "Attention required"
    health_detail = f"Tunnel {ctx.tunnel_id or 'unknown'} | last check {ctx.last_check_time or 'n/a'}"
    path_headline = ctx.hostname or "Hostname unavailable"
    path_detail = f"Edge -> tunnel -> {ctx.origin_observed or 'origin unknown'}"
    evidence_headline = ctx.current_error or ctx.last_good_state or "No explicit evidence yet"
    evidence_detail = f"Config {ctx.config_path or 'not provided'}"
    drift_headline = f"Origin {drift}"
    drift_detail = f"expected {ctx.origin_expected or 'n/a'} | observed {ctx.origin_observed or 'n/a'}"
    return {
        "Health": GuardianSectionCard("Health", health_headline, health_detail),
        "Path": GuardianSectionCard("Path", path_headline, path_detail),
        "Evidence": GuardianSectionCard("Evidence", evidence_headline, evidence_detail),
        "Config Drift": GuardianSectionCard("Config Drift", drift_headline, drift_detail),
    }


def build_orchestrator_intent(payload: Any, *, action: str) -> str:
    ctx = normalize_guardian_context(payload)
    verb = {
        "check": "Run Cloudflare Guardian check",
        "rerun": "Rerun Cloudflare Guardian check",
        "remediation": "Apply Cloudflare Guardian remediation",
    }.get(action, "Run Cloudflare Guardian action")
    return (
        f"{verb} for hostname '{ctx.hostname or 'unknown'}', tunnel '{ctx.tunnel_id or 'unknown'}', "
        f"expected origin '{ctx.origin_expected or 'n/a'}', observed origin '{ctx.origin_observed or 'n/a'}', "
        f"config '{ctx.config_path or 'n/a'}', last good '{ctx.last_good_state or 'n/a'}', "
        f"current error '{ctx.current_error or 'n/a'}', last check '{ctx.last_check_time or 'n/a'}'."
    )


__all__ = [
    "CloudflareGuardianContext",
    "GuardianSectionCard",
    "GUARDIAN_REQUIRED_KEYS",
    "build_guardian_cards",
    "build_orchestrator_intent",
    "normalize_guardian_context",
]
