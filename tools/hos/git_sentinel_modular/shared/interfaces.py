from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable, Iterable, Any, Mapping

from .contracts import (
    CleanupPlan,
    PredictionResult,
    RepairPlan,
    ScanResult,
    SecurityFinding,
    SentinelReport,
)


@runtime_checkable
class RepositoryScannerPort(Protocol):
    def scan_repository(self, repo_root: str) -> ScanResult: ...


@runtime_checkable
class SecurityScannerPort(Protocol):
    def scan_security(self, repo_root: str) -> list[SecurityFinding]: ...


@runtime_checkable
class LearningStorePort(Protocol):
    def load_snapshot(self, repo_root: str) -> Mapping[str, Any]: ...
    def save_snapshot(self, repo_root: str, payload: Mapping[str, Any]) -> None: ...


@runtime_checkable
class PredictionEnginePort(Protocol):
    def predict(self, scan_result: ScanResult, learning_snapshot: Mapping[str, Any]) -> list[PredictionResult]: ...


@runtime_checkable
class RepairEnginePort(Protocol):
    def plan_repairs(self, scan_result: ScanResult, predictions: list[PredictionResult]) -> RepairPlan: ...


@runtime_checkable
class CleanupEnginePort(Protocol):
    def plan_cleanup(self, scan_result: ScanResult) -> CleanupPlan: ...


@runtime_checkable
class ReportGeneratorPort(Protocol):
    def build_report(
        self,
        scan_result: ScanResult,
        predictions: list[PredictionResult],
        repair_plan: RepairPlan,
        cleanup_plan: CleanupPlan,
    ) -> SentinelReport: ...


@dataclass(slots=True, frozen=True)
class ProviderSpec:
    name: str
    expected_protocol: type
    description: str
    optional: bool = False


@dataclass(slots=True)
class ProviderBinding:
    spec: ProviderSpec
    provider: object
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "ProviderBinding":
        if not self.spec.name.strip():
            raise ValueError("ProviderSpec.name must be non-empty")
        if self.provider is None:
            raise ValueError(f"Provider for `{self.spec.name}` is None")
        if not isinstance(self.metadata, dict):
            raise TypeError("ProviderBinding.metadata must be dict")
        return self


DEFAULT_PROVIDER_SPECS: tuple[ProviderSpec, ...] = (
    ProviderSpec(
        name="repository_scanner",
        expected_protocol=RepositoryScannerPort,
        description="Scans repository state and emits typed ScanResult.",
    ),
    ProviderSpec(
        name="security_scanner",
        expected_protocol=SecurityScannerPort,
        description="Runs security checks and emits SecurityFinding instances.",
    ),
    ProviderSpec(
        name="learning_store",
        expected_protocol=LearningStorePort,
        description="Loads and saves persistent learning snapshots.",
    ),
    ProviderSpec(
        name="prediction_engine",
        expected_protocol=PredictionEnginePort,
        description="Produces typed predictions from scan result + learning snapshot.",
    ),
    ProviderSpec(
        name="repair_engine",
        expected_protocol=RepairEnginePort,
        description="Builds repair plan from findings and predictions.",
        optional=True,
    ),
    ProviderSpec(
        name="cleanup_engine",
        expected_protocol=CleanupEnginePort,
        description="Builds cleanup plan constrained by safety rules.",
        optional=True,
    ),
    ProviderSpec(
        name="report_generator",
        expected_protocol=ReportGeneratorPort,
        description="Builds typed final SentinelReport.",
    ),
)


def provider_specs_by_name() -> dict[str, ProviderSpec]:
    return {spec.name: spec for spec in DEFAULT_PROVIDER_SPECS}
