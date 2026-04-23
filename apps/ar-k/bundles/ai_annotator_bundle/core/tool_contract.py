
"""Python-first contract definitions for AI Annotator artifacts and semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from core.bundle_constants import ADVISORY_OUTPUT_REL, REQUIRED_ANNOTATION_ARTIFACTS


@dataclass(frozen=True)
class AnnotationArtifactContract:
    name: str
    relative_path: str
    invariants: tuple[str, ...]
    semantics: str


ANNOTATION_ARTIFACT_CONTRACTS = {
    "annotations.json": AnnotationArtifactContract(
        name="annotations.json",
        relative_path=f"{ADVISORY_OUTPUT_REL}/annotations.json",
        invariants=(
            "contains advisory records only",
            "records must cite upstream evidence sources",
            "records must not change canonical identity or gate state",
        ),
        semantics="Primary advisory payload written after validation.",
    ),
    "annotation_index.json": AnnotationArtifactContract(
        name="annotation_index.json",
        relative_path=f"{ADVISORY_OUTPUT_REL}/annotation_index.json",
        invariants=(
            "one entry per annotation target",
            "index points to advisory artifacts only",
            "index names registry_index.json as canonical upstream source",
        ),
        semantics="Lookup surface for advisory output without changing registry canon.",
    ),
    "annotation_summary.json": AnnotationArtifactContract(
        name="annotation_summary.json",
        relative_path=f"{ADVISORY_OUTPUT_REL}/annotation_summary.json",
        invariants=(
            "contains counts, ambiguity tallies, and ignored-path totals",
            "does not encode authoritative pass/fail decisions",
            "must remain derivable from annotations.json",
        ),
        semantics="Aggregate advisory summary for humans and tooling.",
    ),
}


@dataclass(frozen=True)
class AdvisoryBoundary:
    may_read: tuple[str, ...]
    may_write: tuple[str, ...]
    may_not_write: tuple[str, ...]
    may_not_override: tuple[str, ...]
    may_not_promote: bool = True


AI_ANNOTATOR_BOUNDARY = AdvisoryBoundary(
    may_read=(
        "module_registry.json",
        "boundary_registry.json",
        "registry_index.json",
        "switch_decision_registry.json",
        "switch_decision_trace.json",
        "validation_report.json",
        "gate_decisions.json",
    ),
    may_write=tuple(REQUIRED_ANNOTATION_ARTIFACTS),
    may_not_write=(
        "module_registry.json",
        "boundary_registry.json",
        "registry_index.json",
        "switch_decision_registry.json",
        "switch_decision_trace.json",
        "validation_report.json",
        "gate_decisions.json",
    ),
    may_not_override=(
        "canonical registry content",
        "switch resolution state",
        "validator gate outcome",
        "promotion decisions",
    ),
)


def approved_output_paths(root: Path) -> list[Path]:
    output_root = root / ADVISORY_OUTPUT_REL
    return [output_root / item for item in REQUIRED_ANNOTATION_ARTIFACTS]


def iter_contract_rows() -> Iterable[tuple[str, str, tuple[str, ...], str]]:
    for contract in ANNOTATION_ARTIFACT_CONTRACTS.values():
        yield (contract.name, contract.relative_path, contract.invariants, contract.semantics)
