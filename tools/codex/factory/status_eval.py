from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

PASS = "PASS"
BLOCKED = "BLOCKED"
FAIL = "FAIL"
WARN = "WARN"
PENDING = "PENDING"

_TERMINAL = {PASS, BLOCKED, FAIL}
_KNOWN = {PASS, BLOCKED, FAIL, WARN, PENDING}
_EXIT_CODES = {
    PASS: 0,
    BLOCKED: 2,
    FAIL: 1,
    WARN: 0,
    PENDING: 3,
}


def normalize_status(value: str | None, *, fallback: str = PENDING) -> str:
    if value is None:
        return fallback
    candidate = str(value).strip().upper()
    if not candidate:
        return fallback
    if candidate in _KNOWN:
        return candidate
    return fallback


def status_from_rc(rc: int, *, nonzero_status: str = BLOCKED) -> str:
    return PASS if int(rc) == 0 else normalize_status(nonzero_status, fallback=BLOCKED)


def status_exit_code(status: str) -> int:
    return _EXIT_CODES.get(normalize_status(status, fallback=FAIL), 1)


def is_terminal(status: str) -> bool:
    return normalize_status(status) in _TERMINAL


def is_pass(status: str) -> bool:
    return normalize_status(status) == PASS


def _coerce_rc(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1


def make_check(
    name: str,
    *,
    status: str | None = None,
    rc: int | None = None,
    required: bool = True,
    detail: str = "",
    actor: str = "",
) -> dict[str, Any]:
    computed_rc = _coerce_rc(rc)
    computed_status = normalize_status(status) if status is not None else status_from_rc(computed_rc)
    return {
        "name": str(name),
        "status": computed_status,
        "rc": computed_rc,
        "required": bool(required),
        "detail": str(detail),
        "actor": str(actor),
    }


def normalize_check(check: Mapping[str, Any], *, default_required: bool = True) -> dict[str, Any]:
    name = str(check.get("name", "unnamed_check"))
    status = normalize_status(check.get("status"))
    rc = _coerce_rc(check.get("rc", 0))

    # The rc status is authoritative when the caller provides both.
    if rc != 0 and status == PASS:
        status = BLOCKED

    return {
        "name": name,
        "status": status,
        "rc": rc,
        "required": bool(check.get("required", default_required)),
        "detail": str(check.get("detail", "")),
        "actor": str(check.get("actor", "")),
    }


def sort_checks(checks: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized = [normalize_check(check) for check in checks]
    normalized.sort(key=lambda item: (item["name"], item["actor"], item["status"], item["rc"]))
    return normalized


@dataclass(frozen=True)
class StatusEvaluation:
    status: str
    required_checks: tuple[dict[str, Any], ...]
    optional_checks: tuple[dict[str, Any], ...]
    required_failures: tuple[dict[str, Any], ...]
    schema_errors: tuple[str, ...]
    blockers: tuple[str, ...]
    internal_errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.status == PASS

    @property
    def exit_code(self) -> int:
        return status_exit_code(self.status)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "required_checks": [dict(item) for item in self.required_checks],
            "optional_checks": [dict(item) for item in self.optional_checks],
            "required_failures": [dict(item) for item in self.required_failures],
            "schema_errors": list(self.schema_errors),
            "blockers": list(self.blockers),
            "internal_errors": list(self.internal_errors),
            "exit_code": self.exit_code,
            "ok": self.ok,
        }


def evaluate_status(
    *,
    required_checks: Iterable[Mapping[str, Any]],
    optional_checks: Iterable[Mapping[str, Any]] | None = None,
    schema_errors: Iterable[str] | None = None,
    blockers: Iterable[str] | None = None,
    internal_errors: Iterable[str] | None = None,
) -> StatusEvaluation:
    normalized_required = sort_checks(required_checks)
    normalized_optional = sort_checks(optional_checks or [])

    required_failures = [
        check
        for check in normalized_required
        if check["status"] != PASS or int(check["rc"]) != 0
    ]

    collected_schema_errors = sorted(str(item) for item in (schema_errors or []) if str(item).strip())
    collected_blockers = sorted(str(item) for item in (blockers or []) if str(item).strip())
    collected_internal = sorted(str(item) for item in (internal_errors or []) if str(item).strip())

    if collected_internal:
        final_status = FAIL
    elif required_failures or collected_schema_errors or collected_blockers:
        final_status = BLOCKED
    else:
        final_status = PASS

    return StatusEvaluation(
        status=final_status,
        required_checks=tuple(normalized_required),
        optional_checks=tuple(normalized_optional),
        required_failures=tuple(required_failures),
        schema_errors=tuple(collected_schema_errors),
        blockers=tuple(collected_blockers),
        internal_errors=tuple(collected_internal),
    )


def combine_statuses(statuses: Iterable[str], *, fail_on_warn: bool = False) -> str:
    normalized = [normalize_status(item) for item in statuses]
    if any(item == FAIL for item in normalized):
        return FAIL
    if any(item == BLOCKED for item in normalized):
        return BLOCKED
    if fail_on_warn and any(item == WARN for item in normalized):
        return BLOCKED
    if all(item == PASS for item in normalized):
        return PASS
    return PENDING
