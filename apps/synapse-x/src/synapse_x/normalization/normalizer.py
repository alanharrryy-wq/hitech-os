from pathlib import Path
from typing import Any

from synapse_x.models import CanonicalRecord
from synapse_x.normalization import normalize_raw


def normalize_payload(raw: dict[str, Any], source_path: str | Path) -> CanonicalRecord:
    return normalize_raw(raw, Path(source_path))
