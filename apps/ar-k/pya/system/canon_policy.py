from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

NONPRODUCT_TOP_LEVEL_CLASSES = {
    "docs": "docs",
    "reports": "reports",
    "report": "reports",
    "_dependency_graphs": "graphs",
    ".ark_install": "artifacts",
    "tests": "tests",
    "test": "tests",
    "tools": "tooling",
    "scripts": "scripts",
    "script": "scripts",
    "fixtures": "fixtures",
    "fixture": "fixtures",
    "examples": "examples",
    "example": "examples",
}

NONPRODUCT_SEGMENT_CLASSES = {
    "_tracking": "history",
    "artifacts": "artifacts",
    "baselines": "artifacts",
    "history": "history",
    "patch_runs": "history",
    "patch_transactions": "history",
    "rollback": "history",
    "rollbacks": "history",
    "snapshots": "artifacts",
    "__tests__": "tests",
    "__mocks__": "tests",
    "fixtures": "fixtures",
    "examples": "examples",
}


@dataclass(frozen=True)
class SourcePathPolicy:
    canonical_source: bool
    non_product_class: str | None = None


def classify_source_path(relative_path: str) -> SourcePathPolicy:
    pure = PurePosixPath(relative_path)
    parts = [part for part in pure.parts if part not in {"", "."}]
    if not parts:
        return SourcePathPolicy(canonical_source=False, non_product_class="invalid")

    lower_parts = [part.lower() for part in parts]
    first = lower_parts[0]
    if first.startswith("."):
        return SourcePathPolicy(canonical_source=False, non_product_class="hidden")
    if first in NONPRODUCT_TOP_LEVEL_CLASSES:
        return SourcePathPolicy(canonical_source=False, non_product_class=NONPRODUCT_TOP_LEVEL_CLASSES[first])
    for part in lower_parts:
        if part in NONPRODUCT_SEGMENT_CLASSES:
            return SourcePathPolicy(canonical_source=False, non_product_class=NONPRODUCT_SEGMENT_CLASSES[part])

    filename = lower_parts[-1]
    if ".test." in filename or ".spec." in filename or filename.endswith(("_test.py", "_spec.py")):
        return SourcePathPolicy(canonical_source=False, non_product_class="tests")
    if filename.endswith((".bak", ".orig", ".rej")):
        return SourcePathPolicy(canonical_source=False, non_product_class="history")
    return SourcePathPolicy(canonical_source=True, non_product_class=None)


def is_canonical_source_path(relative_path: str) -> bool:
    return classify_source_path(relative_path).canonical_source
