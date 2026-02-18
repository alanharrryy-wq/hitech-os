from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from .handlers import execute_handler
from .logging_utils import build_log
from .models import AgentCapabilitiesModel, FeatureFlagsModel, HealthReportModel, JobRequestModel, JobResultModel

APP_VERSION = "0.2.0"
CONTRACT_VERSION = "1.1.0"
MAX_INPUT_CHARS = 12000


def _stable_iso_utc(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def get_capabilities() -> AgentCapabilitiesModel:
    return AgentCapabilitiesModel.model_validate(
        {
            "serviceName": "ai-agent",
            "version": APP_VERSION,
            "protocolVersion": CONTRACT_VERSION,
            "deterministic": True,
            "supportedJobKinds": ["echo", "extract_keywords", "summarize_text"],
            "maxInputChars": MAX_INPUT_CHARS,
            "defaults": FeatureFlagsModel().model_dump(),
            "notes": [
                "Deterministic local handlers only",
                "No external network calls",
                "Stable structured logs sorted by seq",
            ],
        }
    )


def build_health_report() -> HealthReportModel:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    checks: List[Dict[str, str]] = [
        {
            "name": "contracts",
            "status": "ok",
            "message": f"contract version {CONTRACT_VERSION}",
        },
        {
            "name": "handlers",
            "status": "ok",
            "message": "echo/summarize_text/extract_keywords enabled",
        },
    ]
    status = "ok"

    return HealthReportModel.model_validate(
        {
            "service": "ai-agent",
            "version": APP_VERSION,
            "contractVersion": CONTRACT_VERSION,
            "status": status,
            "timestampUtc": now,
            "checks": checks,
        }
    )


def _build_execution_logs(request: JobRequestModel, output: Dict[str, object]) -> List[dict]:
    at_utc = _stable_iso_utc(request.requestedAtUtc)
    return [
        build_log(
            seq=0,
            level="info",
            event="job.received",
            message="job request accepted",
            at_utc=at_utc,
            details={"kind": request.kind, "jobId": request.jobId},
        ).model_dump(),
        build_log(
            seq=1,
            level="info",
            event="job.executed",
            message=f"handler completed for {request.kind}",
            at_utc=at_utc,
            details={"outputKeys": sorted(output.keys())},
        ).model_dump(),
        build_log(
            seq=2,
            level="info",
            event="job.completed",
            message="deterministic execution completed",
            at_utc=at_utc,
            details={"status": "completed"},
        ).model_dump(),
    ]


def run_job(request: JobRequestModel) -> JobResultModel:
    output = execute_handler(request)
    logs = _build_execution_logs(request, output)
    finished_at = _stable_iso_utc(request.requestedAtUtc)

    return JobResultModel.model_validate(
        {
            "jobId": request.jobId,
            "kind": request.kind,
            "status": "completed",
            "output": output,
            "logs": logs,
            "finishedAtUtc": finished_at,
        }
    )


def parse_request(raw_payload: object) -> JobRequestModel:
    request = JobRequestModel.model_validate(raw_payload)
    text_len = len(str(request.input.get("text", "")))
    if text_len > MAX_INPUT_CHARS:
        raise ValueError(f"input text exceeds maxInputChars={MAX_INPUT_CHARS}")
    return request


def build_error_payload(code: str, message: str) -> dict:
    return {
        "error": code,
        "message": message,
        "service": "ai-agent",
        "contractVersion": CONTRACT_VERSION,
    }
