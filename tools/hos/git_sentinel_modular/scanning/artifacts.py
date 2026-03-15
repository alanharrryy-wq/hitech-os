from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ..shared.contracts import ArtifactFinding


@dataclass(slots=True, frozen=True)
class ArtifactRuleSet:
    generated_suffixes: tuple[str, ...] = (".map", ".log", ".tmp", ".cache", ".sqlite", ".db")
    generated_directories: tuple[str, ...] = ("dist", "build", ".cache", ".next", "_reports", "_local")
    report_names: tuple[str, ...] = ("report.json", "report.md", "audit_report.json", "audit_report.md")
    runtime_state_markers: tuple[str, ...] = ("runtime", "quarantine", "telemetry", "history")

    def describe(self) -> dict[str, list[str]]:
        return {
            "generated_suffixes": list(self.generated_suffixes),
            "generated_directories": list(self.generated_directories),
            "report_names": list(self.report_names),
            "runtime_state_markers": list(self.runtime_state_markers),
        }


class ArtifactClassifier:
    def __init__(self, rules: ArtifactRuleSet | None = None):
        self.rules = rules or ArtifactRuleSet()

    def classify_path(self, relative_path: str, tracked: bool = False, ignored: bool = False) -> ArtifactFinding | None:
        rel = relative_path.replace("\\", "/").strip("/")
        if not rel:
            return None

        path = Path(rel)
        lower_name = path.name.lower()
        lower_parts = [p.lower() for p in path.parts]
        lower_suffix = path.suffix.lower()

        if lower_name in {name.lower() for name in self.rules.report_names}:
            return self._finding(path, "report", "report file name matched", 0.95, tracked, ignored)

        if any(part in {d.lower() for d in self.rules.generated_directories} for part in lower_parts):
            category = "runtime_state" if any(m in "/".join(lower_parts) for m in self.rules.runtime_state_markers) else "generated_code"
            reason = "path matched generated directory rule"
            return self._finding(path, category, reason, 0.80, tracked, ignored)

        if lower_suffix in {s.lower() for s in self.rules.generated_suffixes}:
            category = "cache" if lower_suffix in {".cache", ".db", ".sqlite"} else "temporary"
            return self._finding(path, category, "file suffix matched generated artifact rule", 0.72, tracked, ignored)

        if "coverage" in lower_name or "snapshot" in lower_name:
            return self._finding(path, "report", "name matched coverage/snapshot heuristic", 0.70, tracked, ignored)

        return None

    def classify_many(self, relative_paths: Iterable[str]) -> list[ArtifactFinding]:
        findings: list[ArtifactFinding] = []
        for rel in relative_paths:
            finding = self.classify_path(rel)
            if finding is not None:
                findings.append(finding)
        return findings

    @staticmethod
    def _finding(path: Path, category: str, reason: str, confidence: float, tracked: bool, ignored: bool) -> ArtifactFinding:
        return ArtifactFinding(
            path=path.as_posix(),
            category=category,
            reason=reason,
            confidence=confidence,
            tracked=tracked,
            ignored=ignored,
            metadata={"detector": "ArtifactClassifier"},
        ).validate()
