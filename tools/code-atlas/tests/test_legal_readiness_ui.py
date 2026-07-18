from __future__ import annotations

import ast
import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    main_path = root / "code-atlas.py"
    dialog_path = root / "src" / "code_atlas" / "ui" / "legal_readiness.py"
    init_path = root / "src" / "code_atlas" / "ui" / "__init__.py"
    contracts_path = root / "src" / "code_atlas" / "legal_readiness" / "contracts.py"
    cli_path = root / "src" / "code_atlas" / "legal_readiness" / "cli.py"
    pipeline_path = root / "src" / "code_atlas" / "legal_readiness" / "pipeline.py"
    wrapper_path = root / "scripts" / "RUN_LEGAL_READINESS_BACKEND.ps1"

    required = [
        main_path, dialog_path, init_path, contracts_path, cli_path, pipeline_path, wrapper_path
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("MISSING_UI_FILES:" + json.dumps(missing))

    for path in [main_path, dialog_path, init_path, contracts_path, cli_path, pipeline_path]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    main_text = main_path.read_text(encoding="utf-8")
    dialog_text = dialog_path.read_text(encoding="utf-8")
    contracts_text = contracts_path.read_text(encoding="utf-8")
    cli_text = cli_path.read_text(encoding="utf-8")
    pipeline_text = pipeline_path.read_text(encoding="utf-8")
    wrapper_text = wrapper_path.read_text(encoding="utf-8")

    checks = {
        "main_button": "CODE_ATLAS_LEGAL_READINESS_BUTTON_V01" in main_text,
        "main_footer": "CODE_ATLAS_LEGAL_READINESS_FOOTER_V01" in main_text,
        "main_method": "CODE_ATLAS_LEGAL_READINESS_METHOD_V01" in main_text,
        "dialog_class": "class LegalReadinessDialog" in dialog_text,
        "qprocess": "QProcess" in dialog_text,
        "external_concurrency_label": "Concurrencia externa: 1" in dialog_text,
        "cooperative_cancel": "Cancelación cooperativa solicitada" in dialog_text,
        "cancel_contract": "cancel_file" in contracts_text,
        "cancel_cli": "--cancel-file" in cli_text,
        "cancel_pipeline": "_cancel_requested" in pipeline_text,
        "cancel_wrapper": "CancelFile" in wrapper_text,
        "no_ui_kill": "taskkill" not in dialog_text.lower() and "stop-process" not in dialog_text.lower(),
        "no_ui_terminate": ".terminate(" not in dialog_text and ".kill(" not in dialog_text,
    }
    failed = [name for name, value in checks.items() if not value]
    if failed:
        raise RuntimeError("LEGAL_UI_CHECKS_FAILED:" + ",".join(failed))

    print("PASS_CODE_ATLAS_LEGAL_UI_SELFTEST")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
