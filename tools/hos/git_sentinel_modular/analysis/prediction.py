from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..shared.contracts import PredictionResult, ScanResult, ArtifactFinding, SecurityFinding


SEVERITY_WEIGHTS = {
    "info": 0.05,
    "low": 0.15,
    "medium": 0.35,
    "high": 0.60,
    "critical": 0.85,
}


@dataclass(slots=True)
class PredictionConfig:
    churn_weight: float = 0.08
    artifact_weight: float = 0.18
    security_weight: float = 0.22
    base_score: float = 0.05
    max_results: int = 10

    def validate(self) -> "PredictionConfig":
        for field_name in ("churn_weight", "artifact_weight", "security_weight", "base_score"):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative number")
        if not isinstance(self.max_results, int) or self.max_results <= 0:
            raise ValueError("max_results must be a positive int")
        return self


class RuleBasedPredictionEngine:
    def __init__(self, config: PredictionConfig | None = None):
        self.config = (config or PredictionConfig()).validate()

    def predict(self, scan_result: ScanResult, learning_snapshot: Mapping[str, Any]) -> list[PredictionResult]:
        scan_result = scan_result.validate()
        snapshot = dict(learning_snapshot or {})
        churn_map = dict(snapshot.get("file_churn", {}))
        predictions_by_path: dict[str, dict[str, Any]] = {}

        for artifact in scan_result.artifact_findings:
            artifact = artifact if isinstance(artifact, ArtifactFinding) else ArtifactFinding(**artifact).validate()
            bucket = predictions_by_path.setdefault(
                artifact.path,
                {"score": self.config.base_score, "reasons": [], "path": artifact.path},
            )
            bucket["score"] += self.config.artifact_weight * max(artifact.confidence, 0.20)
            bucket["reasons"].append(f"artifact:{artifact.category}:{artifact.reason}")

        for finding in scan_result.security_findings:
            finding = finding if isinstance(finding, SecurityFinding) else SecurityFinding(**finding).validate()
            bucket = predictions_by_path.setdefault(
                finding.path,
                {"score": self.config.base_score, "reasons": [], "path": finding.path},
            )
            bucket["score"] += self.config.security_weight * SEVERITY_WEIGHTS.get(finding.severity, 0.10)
            bucket["reasons"].append(f"security:{finding.rule_id}:{finding.severity}")

        for path, count in churn_map.items():
            if not isinstance(path, str) or not isinstance(count, int) or count <= 0:
                continue
            bucket = predictions_by_path.setdefault(
                path,
                {"score": self.config.base_score, "reasons": [], "path": path},
            )
            bucket["score"] += min(count * self.config.churn_weight, 0.35)
            bucket["reasons"].append(f"historical_churn:{count}")

        ranked = sorted(
            predictions_by_path.values(),
            key=lambda item: (-item["score"], item["path"]),
        )[: self.config.max_results]

        predictions: list[PredictionResult] = []
        for item in ranked:
            raw_score = min(float(item["score"]), 0.99)
            confidence = min(0.55 + (len(item["reasons"]) * 0.08), 0.95)
            predictions.append(
                PredictionResult(
                    candidate_path=item["path"],
                    risk_score=raw_score,
                    confidence=confidence,
                    rationale=list(item["reasons"]),
                    metadata={"engine": "RuleBasedPredictionEngine"},
                ).validate()
            )

        return predictions
