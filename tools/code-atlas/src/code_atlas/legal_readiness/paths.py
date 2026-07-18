from __future__ import annotations

import os
from pathlib import Path


DEFAULT_REPO_ROOT = Path(os.environ.get("CODE_ATLAS_REPO_ROOT", r"F:\repos\hitech-os"))
DEFAULT_CODE_ATLAS_ROOT = Path(os.environ.get("CODE_ATLAS_APP_ROOT", str(DEFAULT_REPO_ROOT / "tools" / "code-atlas")))
DEFAULT_MOTORS_ROOT = Path(os.environ.get("PRISMA_CTX_MOTORS_ROOT", r"F:\PRISMA_CTX\MOTORES"))
DEFAULT_NDC_ROOT = Path(os.environ.get("PRISMA_NDC_ROOT", r"F:\PRISMA_CTX\NDC"))
DEFAULT_MAMASTROPHIC_ROOT = Path(
    os.environ.get("PRISMA_MAMASTROPHIC_ROOT", str(DEFAULT_REPO_ROOT / "tools" / "Plawright Mamastrophic"))
)
DEFAULT_OUTPUT_ROOT = Path(os.environ.get("CODE_ATLAS_DOWNLOADS_ROOT", r"F:\descargasf"))
DEFAULT_TRASH_ROOT = Path(os.environ.get("PRISMA_TRASH_ROOT", r"F:\Trash-old"))


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
