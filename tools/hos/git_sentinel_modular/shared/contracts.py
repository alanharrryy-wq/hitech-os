from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


CONTRACT_VERSION = "1.0.0"
VALID_SEVERITIES = {"info", "low", "medium", "high", "critical"}
VALID_ARTIFACT_CATEGORIES = {
    "build_output",
    "generated_code",
    "cache",
    "temporary",
    "runtime_state",
    "report",
    "unknown",
}
VALID_ACTION_KINDS = {
    "delete",
    "quarantine",
    "restore_tracked",
    "rewrite_ignore_block",
    "notify",
    "noop",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _require_probability(value: float, field_name: str) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric")
    value = float(value)
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0")
    return value


def _coerce_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("metadata/context must be mapping-like")
    return dict(value)


def _deep_convert(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _deep_convert(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _deep_convert(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_deep_convert(v) for v in value]
    return value


@dataclass(slots=True)
class ContractBase:
    contract_version: str = CONTRACT_VERSION
    created_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> "ContractBase":
        _require_non_empty(self.contract_version, "contract_version")
        _require_non_empty(self.created_at, "created_at")
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return _deep_convert(self)

    def to_json_ready(self) -> dict[str, Any]:
        return self.to_dict()


@dataclass(slots=True)
class ScanStats(ContractBase):
    scanned_files: int = 0
    scanned_directories: int = 0
    artifact_findings: int = 0
    security_findings: int = 0
    warnings: int = 0

    def validate(self) -> "ScanStats":
        super(ScanStats, self).validate()
        for field_name in (
            "scanned_files",
            "scanned_directories",
            "artifact_findings",
            "security_findings",
            "warnings",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative int")
        return self


@dataclass(slots=True)
class ArtifactFinding(ContractBase):
    path: str = ""
    category: str = "unknown"
    reason: str = ""
    confidence: float = 0.0
    tracked: bool = False
    ignored: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "ArtifactFinding":
        super(ArtifactFinding, self).validate()
        self.path = _require_non_empty(self.path, "path")
        self.reason = _require_non_empty(self.reason, "reason")
        if self.category not in VALID_ARTIFACT_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(VALID_ARTIFACT_CATEGORIES)}"
            )
        self.confidence = _require_probability(self.confidence, "confidence")
        if not isinstance(self.tracked, bool):
            raise TypeError("tracked must be bool")
        if not isinstance(self.ignored, bool):
            raise TypeError("ignored must be bool")
        self.metadata = _coerce_mapping(self.metadata)
        return self


@dataclass(slots=True)
class SecurityFinding(ContractBase):
    rule_id: str = ""
    path: str = ""
    severity: str = "medium"
    message: str = ""
    secret_like: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "SecurityFinding":
        super(SecurityFinding, self).validate()
        self.rule_id = _require_non_empty(self.rule_id, "rule_id")
        self.path = _require_non_empty(self.path, "path")
        self.message = _require_non_empty(self.message, "message")
        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"severity must be one of {sorted(VALID_SEVERITIES)}")
        if not isinstance(self.secret_like, bool):
            raise TypeError("secret_like must be bool")
        self.metadata = _coerce_mapping(self.metadata)
        return self


@dataclass(slots=True)
class ScanResult(ContractBase):
    repo_root: str = ""
    scan_id: str = ""
    artifact_findings: list[ArtifactFinding] = field(default_factory=list)
    security_findings: list[SecurityFinding] = field(default_factory=list)
    stats: ScanStats = field(default_factory=ScanStats)
    warnings: list[str] = field(default_factory=list)

    def validate(self) -> "ScanResult":
        super(ScanResult, self).validate()
        self.repo_root = _require_non_empty(self.repo_root, "repo_root")
        self.scan_id = _require_non_empty(self.scan_id, "scan_id")
        if not isinstance(self.artifact_findings, list):
            raise TypeError("artifact_findings must be list")
        if not isinstance(self.security_findings, list):
            raise TypeError("security_findings must be list")
        self.artifact_findings = [
            item.validate() if isinstance(item, ArtifactFinding) else ArtifactFinding(**item).validate()
            for item in self.artifact_findings
        ]
        self.security_findings = [
            item.validate() if isinstance(item, SecurityFinding) else SecurityFinding(**item).validate()
            for item in self.security_findings
        ]
        if not isinstance(self.stats, ScanStats):
            self.stats = ScanStats(**self.stats).validate()
        else:
            self.stats.validate()
        if not isinstance(self.warnings, list) or not all(isinstance(w, str) for w in self.warnings):
            raise TypeError("warnings must be list[str]")
        return self


@dataclass(slots=True)
class PredictionResult(ContractBase):
    candidate_path: str = ""
    risk_score: float = 0.0
    confidence: float = 0.0
    rationale: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "PredictionResult":
        super(PredictionResult, self).validate()
        self.candidate_path = _require_non_empty(self.candidate_path, "candidate_path")
        self.risk_score = _require_probability(self.risk_score, "risk_score")
        self.confidence = _require_probability(self.confidence, "confidence")
        if not isinstance(self.rationale, list) or not all(isinstance(r, str) and r.strip() for r in self.rationale):
            raise TypeError("rationale must be list of non-empty strings")
        self.metadata = _coerce_mapping(self.metadata)
        return self


@dataclass(slots=True)
class ActionBase(ContractBase):
    kind: str = "noop"
    target_path: str = ""
    reason: str = ""
    safe: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "ActionBase":
        super(ActionBase, self).validate()
        if self.kind not in VALID_ACTION_KINDS:
            raise ValueError(f"kind must be one of {sorted(VALID_ACTION_KINDS)}")
        self.target_path = _require_non_empty(self.target_path, "target_path")
        self.reason = _require_non_empty(self.reason, "reason")
        if not isinstance(self.safe, bool):
            raise TypeError("safe must be bool")
        self.metadata = _coerce_mapping(self.metadata)
        return self


@dataclass(slots=True)
class RepairAction(ActionBase):
    pass


@dataclass(slots=True)
class CleanupAction(ActionBase):
    quarantine_first: bool = True

    def validate(self) -> "CleanupAction":
        super(CleanupAction, self).validate()
        if not isinstance(self.quarantine_first, bool):
            raise TypeError("quarantine_first must be bool")
        return self


@dataclass(slots=True)
class RepairPlan(ContractBase):
    dry_run: bool = True
    safe_actions: list[RepairAction] = field(default_factory=list)
    risky_actions: list[RepairAction] = field(default_factory=list)

    def validate(self) -> "RepairPlan":
        super(RepairPlan, self).validate()
        if not isinstance(self.dry_run, bool):
            raise TypeError("dry_run must be bool")
        self.safe_actions = [
            item.validate() if isinstance(item, RepairAction) else RepairAction(**item).validate()
            for item in self.safe_actions
        ]
        self.risky_actions = [
            item.validate() if isinstance(item, RepairAction) else RepairAction(**item).validate()
            for item in self.risky_actions
        ]
        return self

    @property
    def has_risky_actions(self) -> bool:
        return bool(self.risky_actions)


@dataclass(slots=True)
class CleanupPlan(ContractBase):
    dry_run: bool = True
    actions: list[CleanupAction] = field(default_factory=list)
    blocked_actions: list[CleanupAction] = field(default_factory=list)

    def validate(self) -> "CleanupPlan":
        super(CleanupPlan, self).validate()
        if not isinstance(self.dry_run, bool):
            raise TypeError("dry_run must be bool")
        self.actions = [
            item.validate() if isinstance(item, CleanupAction) else CleanupAction(**item).validate()
            for item in self.actions
        ]
        self.blocked_actions = [
            item.validate() if isinstance(item, CleanupAction) else CleanupAction(**item).validate()
            for item in self.blocked_actions
        ]
        return self


@dataclass(slots=True)
class SentinelReport(ContractBase):
    report_id: str = ""
    repo_root: str = ""
    scan_result: ScanResult = field(default_factory=ScanResult)
    predictions: list[PredictionResult] = field(default_factory=list)
    repair_plan: RepairPlan = field(default_factory=RepairPlan)
    cleanup_plan: CleanupPlan = field(default_factory=CleanupPlan)
    summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def validate(self) -> "SentinelReport":
        super(SentinelReport, self).validate()
        self.report_id = _require_non_empty(self.report_id, "report_id")
        self.repo_root = _require_non_empty(self.repo_root, "repo_root")
        if not isinstance(self.scan_result, ScanResult):
            self.scan_result = ScanResult(**self.scan_result).validate()
        else:
            self.scan_result.validate()
        self.predictions = [
            item.validate() if isinstance(item, PredictionResult) else PredictionResult(**item).validate()
            for item in self.predictions
        ]
        if not isinstance(self.repair_plan, RepairPlan):
            self.repair_plan = RepairPlan(**self.repair_plan).validate()
        else:
            self.repair_plan.validate()
        if not isinstance(self.cleanup_plan, CleanupPlan):
            self.cleanup_plan = CleanupPlan(**self.cleanup_plan).validate()
        else:
            self.cleanup_plan.validate()
        self.summary = _coerce_mapping(self.summary)
        if not isinstance(self.warnings, list) or not all(isinstance(w, str) for w in self.warnings):
            raise TypeError("warnings must be list[str]")
        return self


def validate_contract_version(version: str) -> None:
    version = _require_non_empty(version, "version")
    if version != CONTRACT_VERSION:
        raise ValueError(f"Unsupported contract version: {version}; expected {CONTRACT_VERSION}")


def require_all_valid(items: Iterable[ContractBase]) -> list[ContractBase]:
    validated = []
    for item in items:
        if not isinstance(item, ContractBase):
            raise TypeError("require_all_valid expects ContractBase instances")
        validated.append(item.validate())
    return validated
