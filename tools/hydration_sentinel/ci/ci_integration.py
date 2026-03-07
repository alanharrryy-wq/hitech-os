from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..reporting.report_builder import ReportBuilder


@dataclass(slots=True)
class CIResult:
    exit_code: int
    risk_level: str
    risk_score: float
    report_paths: dict[str, str]
    message: str


class CIIntegration:
    def __init__(
        self,
        repo_root: str | Path,
        *,
        config_path: str | Path | None = None,
        baseline_path: str | Path | None = None,
        report_root: str | Path | None = None,
        fail_threshold: float = 60.0,
        warn_threshold: float = 25.0,
        diff_only: bool = False,
        diff_base_ref: str | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.config_path = config_path
        self.baseline_path = baseline_path
        self.report_root = report_root
        self.fail_threshold = fail_threshold
        self.warn_threshold = warn_threshold
        self.diff_only = diff_only
        self.diff_base_ref = diff_base_ref

    def run(self) -> CIResult:
        builder = ReportBuilder(
            self.repo_root,
            config_path=self.config_path,
            baseline_path=self.baseline_path,
            report_root=self.report_root,
            diff_only=self.diff_only,
            diff_base_ref=self.diff_base_ref,
        )
        built = builder.build()
        written = builder.write_latest(built)
        risk = built.summary_payload['risk']
        score = float(risk['total_score'])
        if score >= self.fail_threshold:
            exit_code = 2
            message = 'Hydration Sentinel risk threshold exceeded.'
        elif score >= self.warn_threshold:
            exit_code = 1
            message = 'Hydration Sentinel reported warning-level risk.'
        else:
            exit_code = 0
            message = 'Hydration Sentinel passed CI thresholds.'
        return CIResult(
            exit_code=exit_code,
            risk_level=str(risk['risk_level']),
            risk_score=score,
            report_paths={key: str(path) for key, path in written.items()},
            message=message,
        )
