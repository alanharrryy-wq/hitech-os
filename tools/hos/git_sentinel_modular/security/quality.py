from __future__ import annotations

from dataclasses import dataclass, field

from ..shared.contracts import SecurityFinding


@dataclass(slots=True)
class SecurityQualityDataset:
    expected_rule_ids: set[str] = field(default_factory=set)
    expected_paths: set[str] = field(default_factory=set)

    def validate(self) -> "SecurityQualityDataset":
        if not isinstance(self.expected_rule_ids, set):
            self.expected_rule_ids = set(self.expected_rule_ids)
        if not isinstance(self.expected_paths, set):
            self.expected_paths = set(self.expected_paths)
        return self


@dataclass(slots=True)
class SecurityQualityResult:
    precision: float
    recall: float
    matched_findings: int
    unexpected_findings: int
    missed_expectations: int

    def validate(self) -> "SecurityQualityResult":
        for field_name in ("precision", "recall"):
            value = getattr(self, field_name)
            if value < 0.0 or value > 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0")
        for field_name in ("matched_findings", "unexpected_findings", "missed_expectations"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative int")
        return self


class SecurityQualityEvaluator:
    def evaluate(self, findings: list[SecurityFinding], dataset: SecurityQualityDataset) -> SecurityQualityResult:
        dataset = dataset.validate()

        actual_keys = {(finding.rule_id, finding.path) for finding in findings}
        expected_keys = {(rule_id, path) for rule_id in dataset.expected_rule_ids for path in dataset.expected_paths}

        matched = len(actual_keys & expected_keys)
        unexpected = len(actual_keys - expected_keys)
        missed = len(expected_keys - actual_keys)

        precision = 1.0 if not actual_keys else matched / len(actual_keys)
        recall = 1.0 if not expected_keys else matched / len(expected_keys)

        return SecurityQualityResult(
            precision=precision,
            recall=recall,
            matched_findings=matched,
            unexpected_findings=unexpected,
            missed_expectations=missed,
        ).validate()
