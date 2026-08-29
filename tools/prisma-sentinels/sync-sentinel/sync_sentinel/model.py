from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass
class Check:
    id: str
    verdict: Verdict
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)
    does_not_prove: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["verdict"] = self.verdict.value
        return out


@dataclass
class RunReport:
    mode: str
    verdict: Verdict = Verdict.UNKNOWN
    checks: list[Check] = field(default_factory=list)
    facts: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def add(self, check: Check) -> None:
        self.checks.append(check)
        if check.verdict == Verdict.FAIL:
            self.failures.append(f"{check.id}: {check.detail}")
        elif check.verdict in {Verdict.BLOCKED, Verdict.UNKNOWN}:
            self.warnings.append(f"{check.id}: {check.detail}")

    def finalize(self) -> Verdict:
        verdicts = {c.verdict for c in self.checks}
        if Verdict.FAIL in verdicts:
            self.verdict = Verdict.FAIL
        elif Verdict.BLOCKED in verdicts:
            self.verdict = Verdict.BLOCKED
        elif Verdict.UNKNOWN in verdicts:
            self.verdict = Verdict.UNKNOWN
        elif self.checks and verdicts == {Verdict.PASS}:
            self.verdict = Verdict.PASS
        else:
            self.verdict = Verdict.UNKNOWN
        return self.verdict

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "verdict": self.verdict.value,
            "checks": [c.to_dict() for c in self.checks],
            "facts": self.facts,
            "warnings": self.warnings,
            "failures": self.failures,
        }
