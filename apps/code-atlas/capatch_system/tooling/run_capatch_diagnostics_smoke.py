#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Smoke mínimo para la subparte D.

Valida que:
- el loader cargue el layout plano de plugins activos
- la sesión diagnóstica corra con APIs públicas de capatch_diagnostics
- se persistan `diagnostic_session.*` y `support_bundle.*`
"""

from argparse import Namespace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_diagnostics.loader import initialize_plugin_runtime
from capatch_diagnostics.runtime import build_session, run_session, run_session_reports


def main() -> int:
    base_dir = ROOT
    plugin_state = initialize_plugin_runtime(base_dir)
    args = Namespace(
        target_path=".",
        app_kind=None,
        collect_only=False,
        verify_only=False,
        support_bundle=True,
        fix_plan=False,
        apply_fixes=False,
        dry_diagnose=True,
        include_logs=True,
        include_processes=False,
        include_ports=False,
        include_git=True,
        include_build=False,
        include_tests=False,
        max_log_lines=80,
        max_log_bytes=65536,
        command_timeout_seconds=15,
        bundle_format="md",
    )
    session = build_session(args, base_dir, plugin_state)
    session = run_session(session, plugin_state)
    written = run_session_reports(base_dir, session)
    required = {"session_json", "session_md", "bundle_md"}
    missing = sorted(key for key in required if key not in written)
    if missing:
        raise SystemExit(f"Missing outputs: {missing}")
    print(
        "[OK] capatch_diagnostics smoke | "
        f"plugins={len(session.enabled_plugin_ids)} findings={len(session.findings)} artifacts={len(session.artifacts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
