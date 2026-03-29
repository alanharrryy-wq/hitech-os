from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .bridge_config import (
    BridgeConfig,
    is_under_any_root,
    is_windows_abs,
    normalize_windows_path,
)
from .bridge_contract import (
    BLOCKED_RE,
    ERROR_RE,
    REUSE_RE,
    SUCCESS_RE,
    WARNING_RE,
    ZIP_FALLBACK_RE,
    map_exit_code_to_contract_detail,
    normalize_contract_detail_to_ui_status,
)


@dataclass
class ParseState:
    phases: List[Tuple[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    contract_violations: List[str] = field(default_factory=list)
    all_lines: List[str] = field(default_factory=list)
    raw_zip_path: str = ""
    accepted_zip_path: str = ""
    reused_detected: bool = False
    status_hint: str = ""
    last_status_message: str = ""
    total_lines: int = 0

    def note_warning(self, message: str) -> None:
        if message and message not in self.warnings:
            self.warnings.append(message)

    def note_error(self, message: str) -> None:
        if message and message not in self.errors:
            self.errors.append(message)

    def note_contract_violation(self, message: str) -> None:
        if message and message not in self.contract_violations:
            self.contract_violations.append(message)

    def note_status_hint(self, candidate: str) -> None:
        normalized = (candidate or "").strip().lower()
        if normalized in ("success", "reused", "blocked", "failed"):
            self.status_hint = normalized


class OutputParser:
    def __init__(self, config: BridgeConfig) -> None:
        self._config = config
        self.state = ParseState()

    def ingest_line(self, line: str, source: str) -> None:
        text = (line or "").rstrip("\r\n")
        if not text:
            return

        self.state.total_lines += 1
        self.state.all_lines.append(text)
        if self._try_structured(text):
            return

        self._try_zip_fallback(text)
        self._try_warning_fallback(text, source)
        self._try_error_fallback(text, source)
        self._try_reuse_fallback(text)
        self._try_status_fallback(text)

    def finalize(self, exit_code: int, timed_out: bool = False) -> Dict[str, Any]:
        engine_payload = self._extract_final_json_payload()
        if engine_payload:
            self._register_engine_paths(engine_payload)
            self._register_engine_issues(engine_payload)
            engine_status = str(engine_payload.get("status") or "").strip().lower()
            if engine_status:
                self.state.note_status_hint(self._map_engine_status_hint(engine_status))
            message = str(engine_payload.get("message") or "").strip()
            if message:
                self.state.last_status_message = message

        if int(exit_code) == 0 and not self.state.phases:
            self.state.note_warning(
                "No structured OB_STATUS lines were received from runner output."
            )

        contract_mismatch = False
        has_any_zip = bool(self.state.accepted_zip_path or self.state.raw_zip_path)

        contract_detail = map_exit_code_to_contract_detail(
            exit_code=exit_code,
            warnings_present=bool(self.state.warnings),
            timed_out=timed_out,
            contract_violations_present=bool(self.state.contract_violations),
            status_hint=self.state.status_hint,
        )
        if contract_detail in {"Succeeded", "SucceededWithWarnings"} and not has_any_zip:
            contract_mismatch = True
            self.state.note_contract_violation(
                "Runner reported success but no ZIP output path was emitted."
            )
            contract_detail = "Failed"

        if self.state.contract_violations and contract_detail in {"Succeeded", "SucceededWithWarnings"}:
            contract_mismatch = True
            contract_detail = "Failed"

        normalized_status = normalize_contract_detail_to_ui_status(
            contract_detail=contract_detail,
            reused_detected=bool(self.state.reused_detected),
            status_hint=self.state.status_hint,
        )
        if engine_payload:
            normalized_status = self._map_engine_status(
                engine_status=str(engine_payload.get("status") or "").strip().lower(),
                fallback_status=normalized_status,
            )

        final_message = self.state.last_status_message or contract_detail
        if timed_out:
            final_message = (
                "Execution timed out before the bridge received a final completion signal."
            )
        elif self.state.contract_violations:
            final_message = self.state.contract_violations[-1]
        elif contract_detail == "SucceededWithWarnings" and self.state.warnings:
            final_message = self.state.warnings[-1]
        elif normalized_status in ("failed", "blocked") and self.state.errors:
            final_message = self.state.errors[-1]

        canonical_zip_path = str(engine_payload.get("canonical_zip_path") or "") if engine_payload else ""
        handoff_copy_path = str(engine_payload.get("handoff_copy_path") or "") if engine_payload else ""
        preferred_zip_path = canonical_zip_path or handoff_copy_path or self.state.accepted_zip_path or self.state.raw_zip_path
        zip_path_publicable = self._is_publicable_zip_path(preferred_zip_path)

        return {
            "normalized_status": normalized_status,
            "contract_detail": contract_detail,
            "zip_path": preferred_zip_path,
            "zip_path_publicable": bool(zip_path_publicable),
            "canonical_zip_path": canonical_zip_path,
            "canonical_zip_publicable": bool(self._is_publicable_zip_path(canonical_zip_path)),
            "handoff_copy_path": handoff_copy_path,
            "handoff_copy_publicable": bool(self._is_publicable_zip_path(handoff_copy_path)),
            "warnings": list(self.state.warnings),
            "errors": list(self.state.errors),
            "contract_violations": list(self.state.contract_violations),
            "reused_detected": bool(self.state.reused_detected),
            "last_status_message": final_message,
            "structured_status_count": len(self.state.phases),
            "total_lines": self.state.total_lines,
            "contract_mismatch": bool(contract_mismatch),
            "status": str(engine_payload.get("status") or "") if engine_payload else "",
            "message": str(engine_payload.get("message") or "") if engine_payload else "",
            "session_mode": str(engine_payload.get("session_mode") or "") if engine_payload else "",
            "policy": str(engine_payload.get("policy") or "") if engine_payload else "",
            "dry_run": bool(engine_payload.get("dry_run")) if engine_payload else False,
            "project_id": str(engine_payload.get("project_id") or "") if engine_payload else "",
            "project_name": str(engine_payload.get("project_name") or "") if engine_payload else "",
            "initiative_type": str(engine_payload.get("initiative_type") or "") if engine_payload else "",
            "run_id": str(engine_payload.get("run_id") or "") if engine_payload else "",
            "round_id": str(engine_payload.get("round_id") or "") if engine_payload else "",
            "session_id": str(engine_payload.get("session_id") or "") if engine_payload else "",
            "project_manifest_path": str(engine_payload.get("project_manifest_path") or "") if engine_payload else "",
            "run_manifest_path": str(engine_payload.get("run_manifest_path") or "") if engine_payload else "",
            "round_manifest_path": str(engine_payload.get("round_manifest_path") or "") if engine_payload else "",
            "lock_path": str(engine_payload.get("lock_path") or "") if engine_payload else "",
            "ledger_path": str(engine_payload.get("ledger_path") or "") if engine_payload else "",
            "notes": list(engine_payload.get("notes") or []) if engine_payload else [],
            "issues": list(engine_payload.get("issues") or []) if engine_payload else [],
            "engine_payload": dict(engine_payload) if engine_payload else {},
        }

    def _try_structured(self, text: str) -> bool:
        if text.startswith("OB_STATUS|"):
            parts = text.split("|", 2)
            if len(parts) != 3 or not parts[1].strip() or not parts[2].strip():
                self.state.note_contract_violation(f"Malformed OB_STATUS line: {text}")
                return True
            phase = parts[1].strip()
            message = parts[2].strip()
            self.state.phases.append((phase, message))
            self.state.last_status_message = f"{phase}: {message}"
            self._try_reuse_fallback(message)
            self._try_status_fallback(phase)
            self._try_status_fallback(message)
            return True

        if text.startswith("OB_ZIP|"):
            parts = text.split("|", 1)
            if len(parts) != 2 or not parts[1].strip():
                self.state.note_contract_violation(f"Malformed OB_ZIP line: {text}")
                return True
            self._register_zip_candidate(parts[1].strip(), exact_contract=True)
            return True

        if text.startswith("OB_WARNING|"):
            parts = text.split("|", 1)
            if len(parts) != 2 or not parts[1].strip():
                self.state.note_contract_violation(f"Malformed OB_WARNING line: {text}")
                return True
            self.state.note_warning(parts[1].strip())
            return True

        if text.startswith("OB_ERROR|"):
            parts = text.split("|", 1)
            if len(parts) != 2 or not parts[1].strip():
                self.state.note_contract_violation(f"Malformed OB_ERROR line: {text}")
                return True
            self.state.note_error(parts[1].strip())
            return True

        return False

    def _register_zip_candidate(self, candidate: str, exact_contract: bool) -> None:
        candidate = candidate.strip().strip('"')
        if not candidate:
            return

        if not is_windows_abs(candidate):
            if exact_contract:
                self.state.note_contract_violation(
                    f"OB_ZIP is not an absolute Windows path: {candidate}"
                )
            return

        if not candidate.lower().endswith(".zip"):
            if exact_contract:
                self.state.note_contract_violation(f"OB_ZIP is not a .zip path: {candidate}")
            return

        if not self.state.raw_zip_path:
            self.state.raw_zip_path = candidate

        if self._is_publicable_zip_path(candidate):
            if not self.state.accepted_zip_path:
                self.state.accepted_zip_path = candidate
            elif normalize_windows_path(self.state.accepted_zip_path) != normalize_windows_path(candidate):
                self.state.note_contract_violation(
                    f"Conflicting ZIP paths received: {self.state.accepted_zip_path} vs {candidate}"
                )
        elif exact_contract:
            self.state.note_warning(
                f"ZIP path outside allowed roots or not found yet: {candidate}"
            )

    def _is_publicable_zip_path(self, path_value: str) -> bool:
        if not path_value or not is_windows_abs(path_value):
            return False
        if not path_value.lower().endswith(".zip"):
            return False
        if not is_under_any_root(path_value, self._config.allowed_output_roots):
            return False
        return os.path.exists(path_value)

    def _try_zip_fallback(self, text: str) -> None:
        match = ZIP_FALLBACK_RE.search(text)
        if match:
            self._register_zip_candidate(match.group(1), exact_contract=False)

    def _try_warning_fallback(self, text: str, source: str) -> None:
        if WARNING_RE.search(text):
            self.state.note_warning(f"{source}: {text}")

    def _try_error_fallback(self, text: str, source: str) -> None:
        if ERROR_RE.search(text) or BLOCKED_RE.search(text):
            self.state.note_error(f"{source}: {text}")

    def _try_reuse_fallback(self, text: str) -> None:
        if REUSE_RE.search(text):
            self.state.reused_detected = True
            self.state.note_status_hint("reused")

    def _try_status_fallback(self, text: str) -> None:
        if REUSE_RE.search(text):
            self.state.note_status_hint("reused")
            return
        if BLOCKED_RE.search(text):
            self.state.note_status_hint("blocked")
            return
        if ERROR_RE.search(text):
            self.state.note_status_hint("failed")
            return
        if SUCCESS_RE.search(text):
            self.state.note_status_hint("success")

    def _register_engine_paths(self, payload: Dict[str, Any]) -> None:
        for key in ("canonical_zip_path", "handoff_copy_path", "canonical_zip"):
            value = str(payload.get(key) or "").strip()
            if value:
                self._register_zip_candidate(value, exact_contract=False)

    def _register_engine_issues(self, payload: Dict[str, Any]) -> None:
        issues = payload.get("issues")
        if not isinstance(issues, list):
            return
        for item in issues:
            if not isinstance(item, dict):
                continue
            message = str(item.get("message") or "").strip()
            severity = str(item.get("severity") or "").strip().lower()
            if not message:
                continue
            if severity == "warning":
                self.state.note_warning(message)
            else:
                self.state.note_error(message)

    def _extract_final_json_payload(self) -> Optional[Dict[str, Any]]:
        if not self.state.all_lines:
            return None
        text_blob = "\n".join(self.state.all_lines)
        decoder = json.JSONDecoder()
        best_payload: Optional[Dict[str, Any]] = None
        best_score = -1

        for index, char in enumerate(text_blob):
            if char != "{":
                continue
            try:
                parsed, _end = decoder.raw_decode(text_blob[index:])
            except Exception:
                continue
            if not isinstance(parsed, dict):
                continue
            score = 0
            for key in (
                "status",
                "message",
                "session_mode",
                "project_id",
                "run_id",
                "round_id",
                "session_id",
                "canonical_zip_path",
            ):
                if key in parsed:
                    score += 1
            if score >= best_score:
                best_payload = parsed
                best_score = score
        return best_payload if best_score >= 3 else None

    @staticmethod
    def _map_engine_status_hint(engine_status: str) -> str:
        if engine_status in {"ready_for_dispatch", "ready", "reused", "succeeded", "success"}:
            if engine_status == "reused":
                return "reused"
            return "success"
        if engine_status in {"blocked", "blocked_by_lock"}:
            return "blocked"
        if engine_status:
            return "failed"
        return ""

    @staticmethod
    def _map_engine_status(*, engine_status: str, fallback_status: str) -> str:
        normalized = str(engine_status or "").strip().lower()
        if normalized in {"ready_for_dispatch", "ready", "success", "succeeded"}:
            return "success"
        if normalized == "reused":
            return "reused"
        if normalized in {"blocked", "blocked_by_lock"}:
            return "blocked"
        if normalized in {"failed", "runtime_core_failed", "invalid_policy_transition", "export_contract_failed"}:
            return "failed"
        return fallback_status


__all__ = [
    "OutputParser",
    "ParseState",
]
