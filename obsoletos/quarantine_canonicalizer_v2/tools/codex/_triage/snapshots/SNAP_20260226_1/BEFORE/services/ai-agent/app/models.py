from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Literal, Optional, Union

JsonPrimitive = Union[str, int, float, bool, None]
JsonValue = Union[JsonPrimitive, List["JsonValue"], Dict[str, "JsonValue"]]

JobKind = Literal["echo", "summarize_text", "extract_keywords"]
JobStatus = Literal["queued", "running", "completed", "failed"]
LogLevel = Literal["info", "warn", "error"]
HealthStatus = Literal["ok", "degraded", "error"]


class ModelValidationError(ValueError):
    pass


def _as_dict(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ModelValidationError(f"{path} must be an object")
    return value


def _as_string(value: Any, path: str, *, min_length: int = 1) -> str:
    if not isinstance(value, str):
        raise ModelValidationError(f"{path} must be a string")
    normalized = value.strip()
    if len(normalized) < min_length:
        raise ModelValidationError(f"{path} must be at least {min_length} characters")
    return normalized


def _as_int(value: Any, path: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int):
        raise ModelValidationError(f"{path} must be an integer")
    if value < minimum:
        raise ModelValidationError(f"{path} must be >= {minimum}")
    return value


def _as_iso_utc(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ModelValidationError(f"{path} must be a string date")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_json_value(value: Any, depth: int = 0) -> bool:
    if depth > 30:
        return False

    if value is None:
        return True

    if isinstance(value, (str, int, float, bool)):
        return True

    if isinstance(value, list):
        return all(_is_json_value(item, depth + 1) for item in value)

    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_json_value(item, depth + 1) for key, item in value.items())

    return False


def _as_json_dict(value: Any, path: str) -> Dict[str, JsonValue]:
    raw = _as_dict(value, path)
    normalized: Dict[str, JsonValue] = {}
    for key in sorted(raw.keys()):
        item = raw[key]
        if not _is_json_value(item):
            raise ModelValidationError(f"{path}.{key} must be JSON-compatible")
        normalized[key] = item
    return normalized


def _as_string_list(value: Any, path: str) -> List[str]:
    if not isinstance(value, list):
        raise ModelValidationError(f"{path} must be an array")
    normalized: List[str] = []
    for index, item in enumerate(value):
        normalized.append(_as_string(item, f"{path}[{index}]"))
    return sorted(normalized)


@dataclass(frozen=True)
class FeatureFlagsModel:
    enableAiExecution: bool = False
    enableCapabilitiesProxy: bool = False
    enableExperimentalUi: bool = False
    enableHealthDashboard: bool = False

    @classmethod
    def model_validate(cls, value: Any) -> "FeatureFlagsModel":
        if value is None:
            return cls()
        data = _as_dict(value, "flags")
        return cls(
            enableAiExecution=bool(data.get("enableAiExecution", False)),
            enableCapabilitiesProxy=bool(data.get("enableCapabilitiesProxy", False)),
            enableExperimentalUi=bool(data.get("enableExperimentalUi", False)),
            enableHealthDashboard=bool(data.get("enableHealthDashboard", False)),
        )

    def model_dump(self) -> Dict[str, Any]:
        return {
            "enableAiExecution": self.enableAiExecution,
            "enableCapabilitiesProxy": self.enableCapabilitiesProxy,
            "enableExperimentalUi": self.enableExperimentalUi,
            "enableHealthDashboard": self.enableHealthDashboard,
        }


@dataclass(frozen=True)
class StructuredLogModel:
    seq: int
    level: LogLevel
    event: str
    message: str
    atUtc: str
    details: Dict[str, JsonValue] = field(default_factory=dict)

    @classmethod
    def model_validate(cls, value: Any) -> "StructuredLogModel":
        data = _as_dict(value, "log")
        seq = _as_int(data.get("seq"), "log.seq", minimum=0)
        level = _as_string(data.get("level"), "log.level")
        if level not in {"info", "warn", "error"}:
            raise ModelValidationError("log.level must be info|warn|error")
        event = _as_string(data.get("event"), "log.event")
        message = _as_string(data.get("message"), "log.message")
        at_utc = _as_iso_utc(data.get("atUtc"), "log.atUtc")
        details = _as_json_dict(data.get("details", {}), "log.details")
        return cls(seq=seq, level=level, event=event, message=message, atUtc=at_utc, details=details)

    def model_dump(self) -> Dict[str, Any]:
        return {
            "seq": self.seq,
            "level": self.level,
            "event": self.event,
            "message": self.message,
            "atUtc": self.atUtc,
            "details": self.details,
        }


@dataclass(frozen=True)
class JobRequestModel:
    jobId: str
    kind: JobKind
    input: Dict[str, JsonValue]
    requestedAtUtc: str
    flags: FeatureFlagsModel = field(default_factory=FeatureFlagsModel)

    @classmethod
    def model_validate(cls, value: Any) -> "JobRequestModel":
        data = _as_dict(value, "request")
        job_id = _as_string(data.get("jobId"), "request.jobId")
        kind = _as_string(data.get("kind"), "request.kind")
        if kind not in {"echo", "summarize_text", "extract_keywords"}:
            raise ModelValidationError("request.kind must be echo|summarize_text|extract_keywords")
        input_payload = _as_json_dict(data.get("input"), "request.input")
        requested_at_utc = _as_iso_utc(data.get("requestedAtUtc"), "request.requestedAtUtc")
        flags = FeatureFlagsModel.model_validate(data.get("flags"))
        return cls(jobId=job_id, kind=kind, input=input_payload, requestedAtUtc=requested_at_utc, flags=flags)

    def model_dump(self) -> Dict[str, Any]:
        return {
            "jobId": self.jobId,
            "kind": self.kind,
            "input": self.input,
            "requestedAtUtc": self.requestedAtUtc,
            "flags": self.flags.model_dump(),
        }


@dataclass(frozen=True)
class JobResultModel:
    jobId: str
    kind: JobKind
    status: JobStatus
    output: Dict[str, JsonValue]
    logs: List[StructuredLogModel]
    finishedAtUtc: Optional[str]

    @classmethod
    def model_validate(cls, value: Any) -> "JobResultModel":
        data = _as_dict(value, "result")
        job_id = _as_string(data.get("jobId"), "result.jobId")
        kind = _as_string(data.get("kind"), "result.kind")
        if kind not in {"echo", "summarize_text", "extract_keywords"}:
            raise ModelValidationError("result.kind must be echo|summarize_text|extract_keywords")
        status = _as_string(data.get("status"), "result.status")
        if status not in {"queued", "running", "completed", "failed"}:
            raise ModelValidationError("result.status must be queued|running|completed|failed")
        output = _as_json_dict(data.get("output"), "result.output")

        raw_logs = data.get("logs")
        if not isinstance(raw_logs, list):
            raise ModelValidationError("result.logs must be an array")
        logs = [StructuredLogModel.model_validate(item) for item in raw_logs]
        logs = sorted(logs, key=lambda item: item.seq)

        raw_finished = data.get("finishedAtUtc")
        finished_at_utc: Optional[str]
        if raw_finished is None:
            finished_at_utc = None
        else:
            finished_at_utc = _as_iso_utc(raw_finished, "result.finishedAtUtc")

        return cls(
            jobId=job_id,
            kind=kind,
            status=status,
            output=output,
            logs=logs,
            finishedAtUtc=finished_at_utc,
        )

    def model_dump(self) -> Dict[str, Any]:
        return {
            "jobId": self.jobId,
            "kind": self.kind,
            "status": self.status,
            "output": self.output,
            "logs": [item.model_dump() for item in self.logs],
            "finishedAtUtc": self.finishedAtUtc,
        }


@dataclass(frozen=True)
class AgentCapabilitiesModel:
    serviceName: Literal["ai-agent"]
    version: str
    protocolVersion: str
    deterministic: Literal[True]
    supportedJobKinds: List[JobKind]
    maxInputChars: int
    defaults: FeatureFlagsModel
    notes: List[str]

    @classmethod
    def model_validate(cls, value: Any) -> "AgentCapabilitiesModel":
        data = _as_dict(value, "capabilities")
        service_name = _as_string(data.get("serviceName"), "capabilities.serviceName")
        if service_name != "ai-agent":
            raise ModelValidationError("capabilities.serviceName must be ai-agent")
        version = _as_string(data.get("version"), "capabilities.version")
        protocol_version = _as_string(data.get("protocolVersion"), "capabilities.protocolVersion")
        deterministic = data.get("deterministic")
        if deterministic is not True:
            raise ModelValidationError("capabilities.deterministic must be true")
        supported_kinds = _as_string_list(data.get("supportedJobKinds"), "capabilities.supportedJobKinds")
        for item in supported_kinds:
            if item not in {"echo", "summarize_text", "extract_keywords"}:
                raise ModelValidationError("capabilities.supportedJobKinds contains invalid kind")
        max_input_chars = _as_int(data.get("maxInputChars"), "capabilities.maxInputChars", minimum=1)
        defaults = FeatureFlagsModel.model_validate(data.get("defaults"))
        notes = _as_string_list(data.get("notes"), "capabilities.notes")
        return cls(
            serviceName="ai-agent",
            version=version,
            protocolVersion=protocol_version,
            deterministic=True,
            supportedJobKinds=supported_kinds,  # type: ignore[arg-type]
            maxInputChars=max_input_chars,
            defaults=defaults,
            notes=notes,
        )

    def model_dump(self) -> Dict[str, Any]:
        return {
            "serviceName": self.serviceName,
            "version": self.version,
            "protocolVersion": self.protocolVersion,
            "deterministic": self.deterministic,
            "supportedJobKinds": self.supportedJobKinds,
            "maxInputChars": self.maxInputChars,
            "defaults": self.defaults.model_dump(),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class HealthCheckModel:
    name: str
    status: HealthStatus
    message: str

    @classmethod
    def model_validate(cls, value: Any) -> "HealthCheckModel":
        data = _as_dict(value, "health.check")
        name = _as_string(data.get("name"), "health.check.name")
        status = _as_string(data.get("status"), "health.check.status")
        if status not in {"ok", "degraded", "error"}:
            raise ModelValidationError("health.check.status must be ok|degraded|error")
        message = _as_string(data.get("message"), "health.check.message")
        return cls(name=name, status=status, message=message)

    def model_dump(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }


@dataclass(frozen=True)
class HealthReportModel:
    service: str
    version: str
    contractVersion: str
    status: HealthStatus
    timestampUtc: str
    checks: List[HealthCheckModel]

    @classmethod
    def model_validate(cls, value: Any) -> "HealthReportModel":
        data = _as_dict(value, "health")
        service = _as_string(data.get("service"), "health.service")
        version = _as_string(data.get("version"), "health.version")
        contract_version = _as_string(data.get("contractVersion"), "health.contractVersion")
        status = _as_string(data.get("status"), "health.status")
        if status not in {"ok", "degraded", "error"}:
            raise ModelValidationError("health.status must be ok|degraded|error")
        timestamp_utc = _as_iso_utc(data.get("timestampUtc"), "health.timestampUtc")
        raw_checks = data.get("checks")
        if not isinstance(raw_checks, list):
            raise ModelValidationError("health.checks must be an array")
        checks = [HealthCheckModel.model_validate(item) for item in raw_checks]
        checks = sorted(checks, key=lambda item: item.name)
        return cls(
            service=service,
            version=version,
            contractVersion=contract_version,
            status=status,
            timestampUtc=timestamp_utc,
            checks=checks,
        )

    def model_dump(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "version": self.version,
            "contractVersion": self.contractVersion,
            "status": self.status,
            "timestampUtc": self.timestampUtc,
            "checks": [item.model_dump() for item in self.checks],
        }


def as_json(model: Union[
    FeatureFlagsModel,
    StructuredLogModel,
    JobRequestModel,
    JobResultModel,
    AgentCapabilitiesModel,
    HealthCheckModel,
    HealthReportModel,
]) -> Dict[str, Any]:
    return model.model_dump()


def validate_model_sequence(values: Iterable[Any]) -> List[StructuredLogModel]:
    sequence = [StructuredLogModel.model_validate(item) for item in values]
    return sorted(sequence, key=lambda item: item.seq)
