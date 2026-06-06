#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from capatch_contracts.constants import BACKUP_DIR_NAME
from capatch_engine import PatchContext, apply, parse_operations
from capatch_ops.base import CapatchError


def _emit_line(level: str, message: str, *, stream: Any = None) -> None:
    try:
        print(f'[{level}] {message}', file=stream if stream is not None else sys.stdout)
    except Exception:
        # Compatibility output must never mask the underlying patch outcome.
        return


def emit_ok(message: str) -> None:
    _emit_line('OK', message)


def emit_warn(message: str) -> None:
    _emit_line('WARN', message)


def sanitize_checkpoint_label(raw_value: str | None) -> str:
    label = (raw_value or "").strip()
    if not label:
        label = datetime.now().strftime("session_%Y%m%d_%H%M%S")
    safe = "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in label).strip("._")
    return safe or datetime.now().strftime("session_%Y%m%d_%H%M%S")


def print_self_test() -> int:
    example = [
        {
            "type": "ReplaceLineRange",
            "label": "Ejemplo de reemplazo",
            "file": "code-atlas.py",
            "start_line": 1,
            "end_line": 1,
            "new_text": "# cambio ejemplo",
        }
    ]
    print(json.dumps(example, indent=2, ensure_ascii=False))
    return 0


def _assert_or_fail(condition: bool, message: str) -> None:
    if not condition:
        raise CapatchError(message)


def run_smoke_tests() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="capatch_smoke_") as tmp:
            root_dir = Path(tmp)
            ctx = PatchContext(
                root_dir=root_dir,
                backup_dir=root_dir / BACKUP_DIR_NAME,
                checkpoint_dir=root_dir / BACKUP_DIR_NAME / "smoke",
                dry_run=False,
                auto_support=True,
            )

            target = root_dir / "demo.txt"
            target.write_text("uno\nANCHOR\ndos\n", encoding="utf-8", newline="")
            ops = parse_operations(
                [
                    {
                        "type": "EnsureInsertAfterExact",
                        "label": "insert local",
                        "file": "demo.txt",
                        "anchor": "ANCHOR",
                        "insert_text": "\nTRES",
                    },
                    {
                        "type": "EnsureReplaceExactOnce",
                        "label": "replace once",
                        "file": "demo.txt",
                        "old_text": "dos",
                        "new_text": "dos_mod",
                    },
                ]
            )
            apply(ctx, ops)
            _assert_or_fail(
                target.read_text(encoding="utf-8") == "uno\nANCHOR\nTRES\ndos_mod\n",
                "Smoke test fallo en flujo base",
            )

            regex_target = root_dir / "regex_demo.txt"
            regex_target.write_text("valor=old\n", encoding="utf-8", newline="")
            regex_ops = parse_operations(
                [
                    {
                        "type": "EnsureReplaceRegexOnce",
                        "label": "regex once",
                        "file": "regex_demo.txt",
                        "pattern": r"valor=old",
                        "new_text": "valor=new",
                        "already_applied_text": "valor=new",
                    }
                ]
            )
            apply(ctx, regex_ops)
            apply(ctx, regex_ops)
            _assert_or_fail(regex_target.read_text(encoding="utf-8") == "valor=new\n", "Smoke test fallo en regex")

            support_target = root_dir / "support_demo.txt"
            support_target.write_text("header   \nbody\n", encoding="utf-8", newline="")
            support_ops = parse_operations(
                [
                    {
                        "type": "InsertAfterExact",
                        "label": "support insert after",
                        "file": "support_demo.txt",
                        "anchor": "header",
                        "insert_text": "\nX",
                    }
                ]
            )
            apply(ctx, support_ops)
            _assert_or_fail(
                support_target.read_text(encoding="utf-8") == "header   \nX\nbody\n",
                "Smoke test fallo en auto-support",
            )
    except Exception as exc:
        emit_warn(f"Smoke tests failed: {exc}")
        return 1

    emit_ok("Smoke tests OK")
    return 0
