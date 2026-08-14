from __future__ import annotations

import os
from pathlib import Path


def _env_path(name: str, default: str = "") -> Path:
    value = str(os.environ.get(name, default)).strip()
    return Path(value or ".")


DEFAULT_REPO_ROOT = _env_path("CODE_ATLAS_PROJECT_ROOT", ".")
DEFAULT_CODE_ATLAS_ROOT = _env_path("CODE_ATLAS_ROOT", ".")
DEFAULT_MOTORS_ROOT = _env_path("CODE_ATLAS_MOTORS_ROOT", "")
DEFAULT_NDC_ROOT = _env_path("CODE_ATLAS_NDC_ROOT", "")
DEFAULT_RUNTIME_ROOT = _env_path("CODE_ATLAS_RUNTIME_ROOT", "")
DEFAULT_OUTPUT_ROOT = _env_path("CODE_ATLAS_OUTPUT_ROOT", "./code-atlas-out")
DEFAULT_ARCHIVE_ROOT = _env_path("CODE_ATLAS_ARCHIVE_ROOT", "")


def canonical_paths() -> dict[str, str]:
    return {
        "repo_root": str(DEFAULT_REPO_ROOT),
        "code_atlas_root": str(DEFAULT_CODE_ATLAS_ROOT),
        "motors_root": "" if str(DEFAULT_MOTORS_ROOT) == "." and not os.environ.get("CODE_ATLAS_MOTORS_ROOT") else str(DEFAULT_MOTORS_ROOT),
        "ndc_root": "" if str(DEFAULT_NDC_ROOT) == "." and not os.environ.get("CODE_ATLAS_NDC_ROOT") else str(DEFAULT_NDC_ROOT),
        "runtime_root": "" if str(DEFAULT_RUNTIME_ROOT) == "." and not os.environ.get("CODE_ATLAS_RUNTIME_ROOT") else str(DEFAULT_RUNTIME_ROOT),
        "output_root": str(DEFAULT_OUTPUT_ROOT),
        "archive_root": "" if str(DEFAULT_ARCHIVE_ROOT) == "." and not os.environ.get("CODE_ATLAS_ARCHIVE_ROOT") else str(DEFAULT_ARCHIVE_ROOT),
    }
