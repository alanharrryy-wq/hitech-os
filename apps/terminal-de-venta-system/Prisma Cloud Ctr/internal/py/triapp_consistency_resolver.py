from __future__ import annotations

"""Pure consistency analysis for PRISMA PC, Tablet, Mobile and 3160.

The resolver intentionally performs no I/O and no mutations.  Callers provide
observations as mappings and receive JSON-serialisable reports.  Clock and
correlation factories are injectable so every operation can be deterministic
in tests.
"""

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping, Sequence
from uuid import uuid4


JsonMapping = Mapping[str, Any]
Clock = Callable[[], datetime]
CorrelationFactory = Callable[[], str]

DEFAULT_SOURCE = "prisma-triapp-consistency-resolver"
DEFAULT_REQUIRED_SURFACES = ("pc", "tablet", "mobile", "3160")

IDENTITY_FIELDS = (
    "tenantId",
    "businessId",
    "licenseGroupId",
)
LICENSE_GROUP_FIELDS = (
    "tenantId",
    "businessId",
    "licenseGroupId",
    "planId",
    "entitlementSetId",
)
DEVICE_PROJECTION_FIELDS = (
    "tenantId",
    "businessId",
    "storeId",
    "licenseGroupId",
    "licenseId",
    "parentLicenseId",
    "deviceSlotId",
    "terminalId",
    "surfaceId",
    "appInstanceId",
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_correlation_id() -> str:
    return str(uuid4())


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return _as_utc(value).isoformat().replace("+00:00", "Z")
    return str(value)


def _parse_instant(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return _as_utc(value)
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return _as_utc(datetime.fromisoformat(raw))
    except ValueError:
        return None


def _record(value: JsonMapping) -> dict[str, Any]:
    """Return a detached record while accepting either data or an envelope."""

    outer = dict(value)
    inner = outer.get("data")
    result = deepcopy(dict(inner)) if isinstance(inner, Mapping) else deepcopy(outer)
    for key in (
        "source",
        "revision",
        "updatedAt",
        "observedAt",
        "freshness",
        "correlationId",
    ):
        if key not in result and key in outer:
            result[key] = deepcopy(outer[key])
    return result


def _records(values: Iterable[JsonMapping]) -> tuple[dict[str, Any], ...]:
    return tuple(_record(value) for value in values if isinstance(value, Mapping))


def _stable(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _values(rows: Sequence[JsonMapping], field: str) -> tuple[Any, ...]:
    unique: dict[str, Any] = {}
    for row in rows:
        value = row.get(field)
        if value is None or value == "":
            continue
        unique.setdefault(_stable(value), deepcopy(value))
    return tuple(unique[key] for key in sorted(unique))


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


def _latest_revision(rows: Sequence[JsonMapping]) -> Any:
    revisions = [row.get("revision") for row in rows if row.get("revision") not in (None, "")]
    return deepcopy(max(revisions, key=_revision_key)) if revisions else None


def _latest_updated_at(rows: Sequence[JsonMapping]) -> str | None:
    candidates: list[tuple[datetime, str]] = []
    for row in rows:
        raw = row.get("updatedAt")
        instant = _parse_instant(raw)
        if instant is not None:
            candidates.append((instant, str(raw)))
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def _active_assignment(row: JsonMapping) -> bool:
    status = str(row.get("slotStatus") or row.get("status") or "active").strip().lower()
    return status not in {
        "available",
        "cancelled",
        "canceled",
        "disabled",
        "inactive",
        "released",
        "revoked",
        "unassigned",
    }


@dataclass(frozen=True)
class FreshnessPolicy:
    """Classify observations without consulting external state."""

    max_age_seconds: float = 300.0

    def classify(
        self,
        updated_at: datetime | str | None,
        observed_at: datetime | str | None,
        explicit: Any = None,
    ) -> str:
        if explicit is not None and str(explicit).strip():
            normalized = str(explicit).strip().upper()
            aliases = {
                "CURRENT": "FRESH",
                "SYNCED": "FRESH",
                "FRESH": "FRESH",
                "STALE": "STALE",
                "EXPIRED": "STALE",
                "UNKNOWN": "UNKNOWN",
                "UNVERIFIED": "UNVERIFIED",
            }
            return aliases.get(normalized, normalized)
        updated = _parse_instant(updated_at)
        observed = _parse_instant(observed_at)
        if updated is None or observed is None:
            return "UNKNOWN"
        age = max(0.0, (observed - updated).total_seconds())
        return "FRESH" if age <= self.max_age_seconds else "STALE"


def build_envelope(
    data: Any,
    *,
    source: str,
    revision: Any,
    updated_at: datetime | str | None,
    observed_at: datetime | str,
    freshness: str,
    correlation_id: str,
) -> dict[str, Any]:
    """Create the canonical read envelope required by Support Resolver."""

    return {
        "data": deepcopy(data),
        "source": str(source),
        "revision": deepcopy(revision),
        "updatedAt": _iso(updated_at),
        "observedAt": _iso(observed_at),
        "freshness": str(freshness).upper(),
        "correlationId": str(correlation_id),
    }


class TriAppConsistencyResolver:
    """Deterministic consistency engine shared by Support Resolver and 3160."""

    def __init__(
        self,
        *,
        freshness_policy: FreshnessPolicy | None = None,
        now_factory: Clock | None = None,
        correlation_factory: CorrelationFactory | None = None,
    ) -> None:
        self._freshness_policy = freshness_policy or FreshnessPolicy()
        self._now = now_factory or _utc_now
        self._new_correlation = correlation_factory or _new_correlation_id

    def _correlation(self, value: str | None) -> str:
        return str(value or self._new_correlation())

    def _envelope(
        self,
        data: Any,
        rows: Sequence[JsonMapping],
        *,
        source: str,
        revision: Any = None,
        updated_at: datetime | str | None = None,
        observed_at: datetime | str | None = None,
        freshness: str | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        observed = observed_at or self._now()
        updated = updated_at if updated_at is not None else _latest_updated_at(rows)
        resolved_freshness = self._freshness_policy.classify(updated, observed, freshness)
        return build_envelope(
            data,
            source=source,
            revision=revision if revision is not None else _latest_revision(rows),
            updated_at=updated,
            observed_at=observed,
            freshness=resolved_freshness,
            correlation_id=self._correlation(correlation_id),
        )

    @staticmethod
    def groupDevicesByBusiness(devices: Iterable[JsonMapping]) -> dict[str, list[dict[str, Any]]]:
        return TriAppConsistencyResolver._group_devices(devices, "businessId")

    @staticmethod
    def groupDevicesByStore(devices: Iterable[JsonMapping]) -> dict[str, list[dict[str, Any]]]:
        return TriAppConsistencyResolver._group_devices(devices, "storeId")

    @staticmethod
    def groupDevicesByLicenseGroup(devices: Iterable[JsonMapping]) -> dict[str, list[dict[str, Any]]]:
        return TriAppConsistencyResolver._group_devices(devices, "licenseGroupId")

    @staticmethod
    def _group_devices(devices: Iterable[JsonMapping], field: str) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in _records(devices):
            key = _stable(row.get(field))
            if key:
                grouped[key].append(row)
        return {
            key: sorted(
                values,
                key=lambda item: (
                    _stable(item.get("deviceId")),
                    _stable(item.get("surfaceId") or item.get("surface")),
                    _stable(item.get("appInstanceId")),
                ),
            )
            for key, values in sorted(grouped.items())
        }

    def resolveIdentity(
        self,
        projections: Iterable[JsonMapping],
        *,
        source: str = DEFAULT_SOURCE,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        rows = _records(projections)
        fields: dict[str, dict[str, Any]] = {}
        conflicts: list[dict[str, Any]] = []
        missing: list[str] = []
        for field in IDENTITY_FIELDS:
            values = _values(rows, field)
            status = "MATCH" if len(values) == 1 else "CONFLICT" if len(values) > 1 else "UNVERIFIED"
            fields[field] = {"status": status, "values": list(values)}
            if status == "CONFLICT":
                conflicts.append({"field": field, "values": list(values)})
            elif status == "UNVERIFIED":
                missing.append(field)
        status = "CONFLICT" if conflicts else "UNVERIFIED" if missing else "MATCH"
        data = {
            "status": status,
            "identity": {
                field: fields[field]["values"][0] if fields[field]["status"] == "MATCH" else None
                for field in IDENTITY_FIELDS
            },
            "fields": fields,
            "conflicts": conflicts,
            "missingFields": missing,
            "observationCount": len(rows),
        }
        return self._envelope(data, rows, source=source, correlation_id=correlation_id)

    def resolveLicenseGroup(
        self,
        licenses: Iterable[JsonMapping],
        *,
        source: str = DEFAULT_SOURCE,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        rows = _records(licenses)
        fields: dict[str, dict[str, Any]] = {}
        for field in LICENSE_GROUP_FIELDS:
            values = _values(rows, field)
            fields[field] = {
                "status": "MATCH" if len(values) == 1 else "CONFLICT" if len(values) > 1 else "UNVERIFIED",
                "values": list(values),
            }
        conflicts = [field for field, result in fields.items() if result["status"] == "CONFLICT"]
        missing = [field for field, result in fields.items() if result["status"] == "UNVERIFIED"]
        child_results = [
            self.validateChildLicenseRelationship(row, licenses=rows)
            for row in rows
            if row.get("parentLicenseId")
        ]
        invalid_children = [result for result in child_results if not result["valid"]]
        status = "CONFLICT" if conflicts or invalid_children else "UNVERIFIED" if missing else "MATCH_BY_LICENSE_GROUP"
        data = {
            "status": status,
            "licenseGroup": {
                field: fields[field]["values"][0] if fields[field]["status"] == "MATCH" else None
                for field in LICENSE_GROUP_FIELDS
            },
            "fields": fields,
            "conflictFields": conflicts,
            "missingFields": missing,
            "childLicenseValidation": child_results,
        }
        return self._envelope(data, rows, source=source, correlation_id=correlation_id)

    def resolveDeviceFleet(
        self,
        devices: Iterable[JsonMapping],
        *,
        licenses: Iterable[JsonMapping] = (),
        source: str = DEFAULT_SOURCE,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        rows = _records(devices)
        license_rows = _records(licenses)
        duplicates = self.detectDuplicateDeviceIdentity(rows)
        slot_conflicts = self.detectSharedSlotConflict(rows)
        business_conflicts = self.detectCrossBusinessAssignment(rows, license_rows)
        stale = self.detectStaleProjection(rows)
        data = {
            "status": "CONFLICT" if duplicates or slot_conflicts or business_conflicts else "STALE" if stale else "MATCH",
            "devices": sorted(
                rows,
                key=lambda item: (
                    _stable(item.get("businessId")),
                    _stable(item.get("storeId")),
                    _stable(item.get("deviceId")),
                    _stable(item.get("appInstanceId")),
                ),
            ),
            "groups": {
                "byBusiness": self.groupDevicesByBusiness(rows),
                "byStore": self.groupDevicesByStore(rows),
                "byLicenseGroup": self.groupDevicesByLicenseGroup(rows),
            },
            "conflicts": {
                "duplicateIdentity": duplicates,
                "sharedSlot": slot_conflicts,
                "crossBusiness": business_conflicts,
            },
            "staleProjections": stale,
            "counts": {
                "devices": len(rows),
                "businesses": len(self.groupDevicesByBusiness(rows)),
                "stores": len(self.groupDevicesByStore(rows)),
                "licenseGroups": len(self.groupDevicesByLicenseGroup(rows)),
            },
        }
        return self._envelope(data, rows, source=source, correlation_id=correlation_id)

    def validateDeviceSlotAssignment(
        self,
        device: JsonMapping,
        *,
        fleet: Iterable[JsonMapping] = (),
    ) -> dict[str, Any]:
        row = _record(device)
        slot_id = row.get("deviceSlotId")
        device_id = row.get("deviceId")
        conflicts = []
        if slot_id:
            for candidate in _records(fleet):
                if (
                    candidate.get("deviceSlotId") == slot_id
                    and candidate.get("deviceId") != device_id
                    and _active_assignment(candidate)
                ):
                    conflicts.append(candidate)
        reasons: list[str] = []
        if not device_id:
            reasons.append("DEVICE_ID_MISSING")
        if not slot_id:
            reasons.append("DEVICE_SLOT_ID_MISSING")
        if conflicts:
            reasons.append("DEVICE_SLOT_SHARED")
        return {
            "valid": not reasons,
            "status": "VALID" if not reasons else "CONFLICT",
            "deviceId": deepcopy(device_id),
            "deviceSlotId": deepcopy(slot_id),
            "reasons": reasons,
            "conflictingAssignments": conflicts,
        }

    def validateChildLicenseRelationship(
        self,
        child: JsonMapping,
        parent: JsonMapping | None = None,
        *,
        licenses: Iterable[JsonMapping] = (),
    ) -> dict[str, Any]:
        child_row = _record(child)
        parent_id = child_row.get("parentLicenseId")
        parent_row = _record(parent) if isinstance(parent, Mapping) else None
        if parent_row is None and parent_id:
            parent_row = next(
                (row for row in _records(licenses) if row.get("licenseId") == parent_id),
                None,
            )
        reasons: list[str] = []
        if not child_row.get("licenseId"):
            reasons.append("CHILD_LICENSE_ID_MISSING")
        if not parent_id:
            reasons.append("PARENT_LICENSE_ID_MISSING")
        if parent_id and parent_row is None:
            reasons.append("PARENT_LICENSE_NOT_FOUND")
        if parent_row is not None:
            for field in ("tenantId", "businessId", "licenseGroupId"):
                child_value = child_row.get(field)
                parent_value = parent_row.get(field)
                if child_value not in (None, "") and parent_value not in (None, "") and child_value != parent_value:
                    reasons.append(f"{field.upper()}_MISMATCH")
            if child_row.get("licenseId") == parent_row.get("licenseId"):
                reasons.append("CHILD_EQUALS_PARENT")
        return {
            "valid": not reasons,
            "status": "MATCH_WITH_VALID_CHILD_LICENSE" if not reasons else "CONFLICT",
            "childLicenseId": deepcopy(child_row.get("licenseId")),
            "parentLicenseId": deepcopy(parent_id),
            "reasons": reasons,
        }

    def detectDuplicateDeviceIdentity(self, devices: Iterable[JsonMapping]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in _records(devices):
            device_id = _stable(row.get("deviceId"))
            if device_id:
                grouped[device_id].append(row)
        duplicates: list[dict[str, Any]] = []
        for device_id, rows in sorted(grouped.items()):
            if len(rows) < 2:
                continue
            fingerprints = {
                tuple(_stable(row.get(field)) for field in DEVICE_PROJECTION_FIELDS if field != "deviceId")
                for row in rows
            }
            duplicates.append(
                {
                    "deviceId": device_id,
                    "status": "CONFLICT" if len(fingerprints) > 1 else "DUPLICATE",
                    "observationCount": len(rows),
                    "projections": rows,
                }
            )
        return duplicates

    def detectSharedSlotConflict(self, devices: Iterable[JsonMapping]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in _records(devices):
            slot_id = _stable(row.get("deviceSlotId"))
            if slot_id and _active_assignment(row):
                grouped[slot_id].append(row)
        conflicts: list[dict[str, Any]] = []
        for slot_id, rows in sorted(grouped.items()):
            device_ids = sorted({_stable(row.get("deviceId")) for row in rows if row.get("deviceId")})
            if len(device_ids) > 1:
                conflicts.append(
                    {
                        "deviceSlotId": slot_id,
                        "status": "CONFLICT",
                        "deviceIds": device_ids,
                        "assignments": rows,
                    }
                )
        return conflicts

    def detectCrossBusinessAssignment(
        self,
        devices: Iterable[JsonMapping],
        licenses: Iterable[JsonMapping] = (),
    ) -> list[dict[str, Any]]:
        license_by_id = {
            _stable(row.get("licenseId")): row
            for row in _records(licenses)
            if row.get("licenseId")
        }
        conflicts: list[dict[str, Any]] = []
        for row in _records(devices):
            actual = row.get("businessId")
            expected = row.get("expectedBusinessId")
            license_row = license_by_id.get(_stable(row.get("licenseId")))
            if expected in (None, "") and license_row is not None:
                expected = license_row.get("businessId")
            if actual not in (None, "") and expected not in (None, "") and actual != expected:
                conflicts.append(
                    {
                        "deviceId": deepcopy(row.get("deviceId")),
                        "licenseId": deepcopy(row.get("licenseId")),
                        "actualBusinessId": deepcopy(actual),
                        "expectedBusinessId": deepcopy(expected),
                        "status": "CONFLICT",
                    }
                )
        return conflicts

    def detectStaleProjection(
        self,
        projections: Iterable[JsonMapping],
        *,
        observed_at: datetime | str | None = None,
        max_age_seconds: float | None = None,
    ) -> list[dict[str, Any]]:
        observed = _parse_instant(observed_at) or _as_utc(self._now())
        policy = self._freshness_policy if max_age_seconds is None else FreshnessPolicy(max_age_seconds)
        stale: list[dict[str, Any]] = []
        for row in _records(projections):
            updated = _parse_instant(row.get("updatedAt"))
            status = policy.classify(updated, observed, row.get("freshness"))
            if status != "STALE":
                continue
            age_seconds = max(0.0, (observed - updated).total_seconds()) if updated else None
            stale.append(
                {
                    "surfaceId": deepcopy(row.get("surfaceId") or row.get("surface")),
                    "deviceId": deepcopy(row.get("deviceId")),
                    "revision": deepcopy(row.get("revision")),
                    "updatedAt": _iso(updated),
                    "observedAt": _iso(observed),
                    "ageSeconds": age_seconds,
                    "status": "STALE",
                }
            )
        return stale

    def compareBusinessAggregates(self, projections: Iterable[JsonMapping]) -> dict[str, Any]:
        rows = _records(projections)
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            business_id = _stable(row.get("businessId"))
            if business_id:
                grouped[business_id].append(row)
        aggregates: dict[str, Any] = {}
        conflicts: list[dict[str, Any]] = []
        for business_id, business_rows in sorted(grouped.items()):
            by_surface: dict[str, dict[str, Any]] = {}
            for surface, surface_rows in self._group_devices(business_rows, "surfaceId").items():
                by_surface[surface] = {
                    "deviceCount": len({_stable(row.get("deviceId")) for row in surface_rows if row.get("deviceId")}),
                    "slotCount": len({_stable(row.get("deviceSlotId")) for row in surface_rows if row.get("deviceSlotId")}),
                    "licenseIds": sorted({_stable(row.get("licenseId")) for row in surface_rows if row.get("licenseId")}),
                    "revisions": list(_values(surface_rows, "revision")),
                }
            revision_sets = {tuple(value["revisions"]) for value in by_surface.values() if value["revisions"]}
            if len(revision_sets) > 1:
                conflicts.append({"businessId": business_id, "field": "revision", "surfaces": by_surface})
            aggregates[business_id] = {"surfaces": by_surface, "projectionCount": len(business_rows)}
        return {
            "status": "CONFLICT" if conflicts else "MATCH",
            "aggregates": aggregates,
            "conflicts": conflicts,
        }

    def comparePerDeviceProjection(self, projections: Iterable[JsonMapping]) -> dict[str, Any]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in _records(projections):
            device_id = _stable(row.get("deviceId"))
            if device_id:
                grouped[device_id].append(row)
        results: dict[str, Any] = {}
        conflicts: list[dict[str, Any]] = []
        for device_id, rows in sorted(grouped.items()):
            fields: dict[str, list[Any]] = {}
            for field in DEVICE_PROJECTION_FIELDS:
                values = list(_values(rows, field))
                if len(values) > 1:
                    fields[field] = values
            revisions = list(_values(rows, "revision"))
            if len(revisions) > 1:
                fields["revision"] = revisions
            status = "CONFLICT" if fields else "MATCH"
            result = {"status": status, "conflictingFields": fields, "projections": rows}
            results[device_id] = result
            if fields:
                conflicts.append({"deviceId": device_id, **result})
        return {"status": "CONFLICT" if conflicts else "MATCH", "devices": results, "conflicts": conflicts}

    def buildConsistencyReport(
        self,
        projections: Iterable[JsonMapping],
        *,
        licenses: Iterable[JsonMapping] = (),
        source: str = DEFAULT_SOURCE,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        rows = _records(projections)
        license_rows = _records(licenses)
        correlation = self._correlation(correlation_id)
        identity = self.resolveIdentity(rows, source=source, correlation_id=correlation)
        license_group = self.resolveLicenseGroup(license_rows or rows, source=source, correlation_id=correlation)
        fleet = self.resolveDeviceFleet(rows, licenses=license_rows, source=source, correlation_id=correlation)
        business = self.compareBusinessAggregates(rows)
        per_device = self.comparePerDeviceProjection(rows)
        stale = self.detectStaleProjection(rows)
        conflict = any(
            value == "CONFLICT"
            for value in (
                identity["data"]["status"],
                license_group["data"]["status"],
                fleet["data"]["status"],
                business["status"],
                per_device["status"],
            )
        )
        status = "PRISMA_TRIAPP_CONFLICT" if conflict else "STALE" if stale else "PRISMA_TRIAPP_CONSISTENT"
        data = {
            "status": status,
            "identity": identity["data"],
            "licenseGroup": license_group["data"],
            "deviceFleet": fleet["data"],
            "businessAggregates": business,
            "deviceProjections": per_device,
            "staleProjections": stale,
            "safeRefresh": self.recommendSafeRefresh(rows, licenses=license_rows),
        }
        return self._envelope(data, rows, source=source, correlation_id=correlation)

    def recommendSafeRefresh(
        self,
        projections: Iterable[JsonMapping],
        *,
        licenses: Iterable[JsonMapping] = (),
    ) -> dict[str, Any]:
        rows = _records(projections)
        hard_conflicts = (
            self.detectSharedSlotConflict(rows)
            + self.detectCrossBusinessAssignment(rows, licenses)
        )
        if hard_conflicts:
            return {
                "safe": False,
                "status": "BLOCKED",
                "reason": "IDENTITY_OR_ASSIGNMENT_CONFLICT",
                "targets": [],
                "conflicts": hard_conflicts,
            }
        stale_keys = {
            (_stable(row.get("surfaceId")), _stable(row.get("deviceId")))
            for row in self.detectStaleProjection(rows)
        }
        targets = []
        for row in rows:
            key = (_stable(row.get("surfaceId") or row.get("surface")), _stable(row.get("deviceId")))
            freshness = str(row.get("freshness") or "").upper()
            if key not in stale_keys and freshness not in {"UNKNOWN", "UNVERIFIED"}:
                continue
            targets.append(
                {
                    "action": "refresh_projection",
                    "surfaceId": deepcopy(row.get("surfaceId") or row.get("surface")),
                    "deviceId": deepcopy(row.get("deviceId")),
                    "expectedRevision": deepcopy(row.get("revision")),
                    "mutatesCanonicalState": False,
                }
            )
        return {
            "safe": True,
            "status": "REFRESH_RECOMMENDED" if targets else "NO_REFRESH_REQUIRED",
            "targets": targets,
            "conflicts": [],
        }

    def verifyPropagation(
        self,
        projections: Iterable[JsonMapping],
        *,
        expected_revision: Any,
        required_surfaces: Sequence[str] = DEFAULT_REQUIRED_SURFACES,
        source: str = DEFAULT_SOURCE,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        rows = _records(projections)
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            surface = _stable(row.get("surfaceId") or row.get("surface")).lower()
            if surface:
                grouped[surface].append(row)
        surface_results: dict[str, Any] = {}
        for required in required_surfaces:
            surface = str(required).lower()
            candidates = grouped.get(surface, [])
            if not candidates:
                surface_results[surface] = {"status": "MISSING", "observations": []}
                continue
            revisions = list(_values(candidates, "revision"))
            stale = self.detectStaleProjection(candidates)
            if stale:
                status = "STALE"
            elif expected_revision is not None and any(revision != expected_revision for revision in revisions):
                status = "REVISION_CONFLICT"
            elif expected_revision is not None and not revisions:
                status = "UNVERIFIED"
            else:
                status = "VERIFIED"
            surface_results[surface] = {
                "status": status,
                "revisions": revisions,
                "observations": candidates,
            }
        verified = all(result["status"] == "VERIFIED" for result in surface_results.values())
        data = {
            "status": "VERIFIED" if verified else "PARTIAL_PROPAGATION",
            "verified": verified,
            "expectedRevision": deepcopy(expected_revision),
            "requiredSurfaces": [str(surface).lower() for surface in required_surfaces],
            "surfaces": surface_results,
        }
        return self._envelope(
            data,
            rows,
            source=source,
            revision=expected_revision,
            correlation_id=correlation_id,
        )

    # Python-style aliases keep integrations readable without changing the
    # stable contract names used by Support Resolver and its matrices.
    resolve_identity = resolveIdentity
    resolve_license_group = resolveLicenseGroup
    resolve_device_fleet = resolveDeviceFleet
    group_devices_by_business = groupDevicesByBusiness
    group_devices_by_store = groupDevicesByStore
    group_devices_by_license_group = groupDevicesByLicenseGroup
    validate_device_slot_assignment = validateDeviceSlotAssignment
    validate_child_license_relationship = validateChildLicenseRelationship
    compare_business_aggregates = compareBusinessAggregates
    compare_per_device_projection = comparePerDeviceProjection
    detect_duplicate_device_identity = detectDuplicateDeviceIdentity
    detect_shared_slot_conflict = detectSharedSlotConflict
    detect_cross_business_assignment = detectCrossBusinessAssignment
    detect_stale_projection = detectStaleProjection
    build_consistency_report = buildConsistencyReport
    recommend_safe_refresh = recommendSafeRefresh
    verify_propagation = verifyPropagation


__all__ = [
    "DEFAULT_REQUIRED_SURFACES",
    "FreshnessPolicy",
    "TriAppConsistencyResolver",
    "build_envelope",
]
