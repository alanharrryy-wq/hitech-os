from __future__ import annotations

import os
from pathlib import Path


def _env_path(name: str, fallback: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser() if raw else fallback


_DEFAULT_REPO = Path.cwd()
DEFAULT_REPO_ROOT = _env_path("CODE_ATLAS_PROJECT_ROOT", _DEFAULT_REPO)
DEFAULT_CODE_ATLAS_ROOT = _env_path("CODE_ATLAS_APP_ROOT", DEFAULT_REPO_ROOT / "tools" / "code-atlas")
DEFAULT_MOTORS_ROOT = _env_path("CODE_ATLAS_MOTORS_ROOT", DEFAULT_CODE_ATLAS_ROOT / "motors")
DEFAULT_NDC_ROOT = _env_path("CODE_ATLAS_NDC_ROOT", DEFAULT_CODE_ATLAS_ROOT / "ndc")
DEFAULT_MAMASTROPHIC_ROOT = _env_path("CODE_ATLAS_RUNTIME_EVIDENCE_ROOT", DEFAULT_CODE_ATLAS_ROOT / "runtime-evidence")
DEFAULT_OUTPUT_ROOT = _env_path("CODE_ATLAS_OUTPUT_ROOT", DEFAULT_REPO_ROOT / "code-atlas-out")
DEFAULT_TRASH_ROOT = _env_path("CODE_ATLAS_TRASH_ROOT", DEFAULT_OUTPUT_ROOT / ".trash")


def canonical_paths() -> dict[str, str]:
    return {
        "repo_root": str(DEFAULT_REPO_ROOT),
        "code_atlas_root": str(DEFAULT_CODE_ATLAS_ROOT),
        "motors_root": str(DEFAULT_MOTORS_ROOT),
        "ndc_root": str(DEFAULT_NDC_ROOT),
        "mamastrophic_root": str(DEFAULT_MAMASTROPHIC_ROOT),
        "output_root": str(DEFAULT_OUTPUT_ROOT),
        "trash_root": str(DEFAULT_TRASH_ROOT),
    }
