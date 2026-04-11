from __future__ import annotations

from .handlers import execute_handler, handle_echo, handle_extract_keywords, handle_summarize_text
from .service import (
    APP_VERSION,
    CONTRACT_VERSION,
    build_error_payload,
    build_health_report,
    get_capabilities,
    parse_request,
    run_job,
)

__all__ = [
    "APP_VERSION",
    "CONTRACT_VERSION",
    "build_error_payload",
    "build_health_report",
    "execute_handler",
    "get_capabilities",
    "handle_echo",
    "handle_extract_keywords",
    "handle_summarize_text",
    "parse_request",
    "run_job",
]
