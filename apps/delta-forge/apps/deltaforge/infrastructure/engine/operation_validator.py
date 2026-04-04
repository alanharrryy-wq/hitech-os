from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from domain.models import OpsDocument, SessionWorkspace


SUPPORTED_OPERATION_TYPES = {
    "ReplaceLineRange",
    "ReplaceExactOnce",
    "InsertAfterExact",
}


@dataclass(slots=True)
class ResolvedOperation:
    index: int
    operation_type: str
    label: str
    file: str
    payload: dict[str, Any]
    target_path: Path


@dataclass(slots=True)
class OperationValidationReport:
    root_dir: Path | None
    operations: list[ResolvedOperation] = field(default_factory=list)
    touched_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class OperationValidator:
    def validate(
        self,
        session: SessionWorkspace,
        *,
        fallback_root_dir: str | Path | None = None,
    ) -> OperationValidationReport:
        warnings: list[str] = []
        errors: list[str] = []

        operations, envelope, parse_warnings, parse_errors = self._parse_operations(session.ops_document)
        warnings.extend(parse_warnings)
        errors.extend(parse_errors)

        root_dir = self._resolve_root_dir(session, envelope, fallback_root_dir)
        if root_dir is None:
            errors.append("No root_dir available in session scope or ops payload.")
            return OperationValidationReport(root_dir=None, warnings=warnings, errors=errors)

        if not root_dir.exists() or not root_dir.is_dir():
            errors.append(f"Root directory does not exist: {root_dir}")
            return OperationValidationReport(root_dir=root_dir, warnings=warnings, errors=errors)

        resolved_operations: list[ResolvedOperation] = []
        touched_files: list[str] = []
        touched_seen: set[str] = set()

        for index, raw in enumerate(operations, start=1):
            op_errors, resolved = self._validate_single_operation(index, raw, root_dir)
            if op_errors:
                errors.extend(op_errors)
                continue
            if resolved is None:
                continue

            resolved_operations.append(resolved)
            target_key = str(resolved.target_path)
            if target_key not in touched_seen:
                touched_seen.add(target_key)
                touched_files.append(target_key)

        return OperationValidationReport(
            root_dir=root_dir,
            operations=resolved_operations,
            touched_files=touched_files,
            warnings=warnings,
            errors=errors,
        )

    def _parse_operations(
        self,
        document: OpsDocument,
    ) -> tuple[list[dict[str, Any]], dict[str, Any], list[str], list[str]]:
        warnings: list[str] = []
        errors: list[str] = []
        envelope: dict[str, Any] = {}

        text = document.content.strip()
        if not text:
            errors.append("Ops document is empty.")
            return [], envelope, warnings, errors

        parsed_payload = document.parsed_payload()
        if not parsed_payload:
            errors.append("Ops document is not valid JSON.")
            return [], envelope, warnings, errors

        operations_raw: Any
        if isinstance(parsed_payload, dict) and "ops" in parsed_payload:
            envelope = parsed_payload
            operations_raw = parsed_payload.get("ops")
        elif isinstance(parsed_payload, dict) and "operations" in parsed_payload:
            envelope = parsed_payload
            operations_raw = parsed_payload.get("operations")
            warnings.append("Using 'operations' key. Prefer canonical 'ops'.")
        elif isinstance(parsed_payload, dict) and document.operation_items():
            envelope = parsed_payload
            operations_raw = document.operation_items()
        else:
            operations_raw = document.operation_items()

        if not isinstance(operations_raw, list):
            errors.append("Ops payload must be a JSON array or envelope with 'ops'.")
            return [], envelope, warnings, errors

        operations: list[dict[str, Any]] = []
        for index, item in enumerate(operations_raw, start=1):
            if not isinstance(item, dict):
                errors.append(f"Operation #{index} must be an object.")
                continue
            operations.append(dict(item))

        if not operations and not errors:
            errors.append("Ops payload does not contain operations.")

        return operations, envelope, warnings, errors

    def _resolve_root_dir(
        self,
        session: SessionWorkspace,
        envelope: dict[str, Any],
        fallback_root_dir: str | Path | None,
    ) -> Path | None:
        raw_candidates = [
            envelope.get("root_dir"),
            getattr(getattr(session, "scope", None), "root_dir", None),
            fallback_root_dir,
        ]
        for candidate in raw_candidates:
            value = str(candidate or "").strip()
            if not value:
                continue
            return Path(value).expanduser().resolve()
        return None

    def _validate_single_operation(
        self,
        index: int,
        operation: dict[str, Any],
        root_dir: Path,
    ) -> tuple[list[str], ResolvedOperation | None]:
        errors: list[str] = []

        op_type = str(operation.get("type", "")).strip()
        label = str(operation.get("label", "")).strip()
        file_path = str(operation.get("file", "")).strip()

        if not op_type:
            errors.append(f"Operation #{index} missing 'type'.")
        elif op_type not in SUPPORTED_OPERATION_TYPES:
            errors.append(f"Operation #{index} uses unsupported type: {op_type}")

        if not label:
            errors.append(f"Operation #{index} missing 'label'.")

        if not file_path:
            errors.append(f"Operation #{index} missing 'file'.")
            return errors, None

        target_path = self._resolve_target_file(root_dir, file_path)
        if target_path is None:
            errors.append(f"Operation #{index} points outside root: {file_path}")
            return errors, None
        if not target_path.exists() or not target_path.is_file():
            errors.append(f"Operation #{index} target file not found: {target_path}")
            return errors, None

        content = target_path.read_text(encoding="utf-8")
        payload = dict(operation)

        if op_type == "ReplaceLineRange":
            self._validate_replace_line_range(index, payload, content, errors)
        elif op_type == "ReplaceExactOnce":
            self._validate_replace_exact_once(index, payload, content, errors)
        elif op_type == "InsertAfterExact":
            self._validate_insert_after_exact(index, payload, content, errors)

        if errors:
            return errors, None

        return errors, ResolvedOperation(
            index=index,
            operation_type=op_type,
            label=label,
            file=file_path,
            payload=payload,
            target_path=target_path,
        )

    def _validate_replace_line_range(
        self,
        index: int,
        payload: dict[str, Any],
        content: str,
        errors: list[str],
    ) -> None:
        start_line = payload.get("start_line")
        end_line = payload.get("end_line")
        new_text = payload.get("new_text")

        if not isinstance(start_line, int) or start_line < 1:
            errors.append(f"Operation #{index} ReplaceLineRange requires start_line >= 1.")
        if not isinstance(end_line, int) or end_line < 1:
            errors.append(f"Operation #{index} ReplaceLineRange requires end_line >= 1.")
        if isinstance(start_line, int) and isinstance(end_line, int) and end_line < start_line:
            errors.append(f"Operation #{index} ReplaceLineRange end_line must be >= start_line.")
        if not isinstance(new_text, str):
            errors.append(f"Operation #{index} ReplaceLineRange requires new_text string.")

        if errors:
            return

        lines = content.splitlines()
        total_lines = len(lines)
        if total_lines == 0:
            errors.append(f"Operation #{index} ReplaceLineRange cannot target empty file.")
            return
        if end_line > total_lines:
            errors.append(
                f"Operation #{index} ReplaceLineRange out of bounds: {start_line}-{end_line} (file has {total_lines} lines)."
            )

    def _validate_replace_exact_once(
        self,
        index: int,
        payload: dict[str, Any],
        content: str,
        errors: list[str],
    ) -> None:
        old_text = payload.get("old_text")
        new_text = payload.get("new_text")

        if not isinstance(old_text, str) or not old_text:
            errors.append(f"Operation #{index} ReplaceExactOnce requires non-empty old_text.")
            return
        if not isinstance(new_text, str):
            errors.append(f"Operation #{index} ReplaceExactOnce requires new_text string.")
            return

        count = content.count(old_text)
        if count == 0:
            errors.append(f"Operation #{index} ReplaceExactOnce old_text was not found.")
        elif count > 1:
            errors.append(f"Operation #{index} ReplaceExactOnce old_text appears more than once.")

    def _validate_insert_after_exact(
        self,
        index: int,
        payload: dict[str, Any],
        content: str,
        errors: list[str],
    ) -> None:
        anchor = payload.get("anchor")
        insert_text = payload.get("insert_text")

        if not isinstance(anchor, str) or not anchor:
            errors.append(f"Operation #{index} InsertAfterExact requires non-empty anchor.")
            return
        if not isinstance(insert_text, str):
            errors.append(f"Operation #{index} InsertAfterExact requires insert_text string.")
            return

        count = content.count(anchor)
        if count == 0:
            errors.append(f"Operation #{index} InsertAfterExact anchor was not found.")
        elif count > 1:
            errors.append(f"Operation #{index} InsertAfterExact anchor appears more than once.")

    def _resolve_target_file(self, root_dir: Path, relative_file: str) -> Path | None:
        target = (root_dir / relative_file).resolve()
        try:
            target.relative_to(root_dir)
        except ValueError:
            return None
        return target
