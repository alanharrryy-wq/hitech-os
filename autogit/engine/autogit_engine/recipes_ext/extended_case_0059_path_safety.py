from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from autogit_engine.recipes.base import Recipe, RecipeResult

@dataclass(frozen=True)
class DiagnosticCommand:
    command: str
    reason: str
    required: bool = True

@dataclass(frozen=True)
class FailureSignature:
    family: str
    pattern: str
    token: str
    severity: str
    mutation_allowed: bool
    commands: tuple[DiagnosticCommand, ...]
    remediation_steps: tuple[str, ...]

SIGNATURE = FailureSignature(
    family='path_safety',
    pattern='F:\\\\repos',
    token='0ee049b34a197eae253dc39b334fc76ab05cc31413c3effd5a3145a3fe67c56e',
    severity='medium',
    mutation_allowed=True,
    commands=(
        DiagnosticCommand('git log --oneline --decorate -n 20', 'collect evidence for path_safety'),
        DiagnosticCommand('git rev-parse HEAD', 'collect evidence for path_safety'),
        DiagnosticCommand('git ls-files', 'collect evidence for path_safety'),
        DiagnosticCommand('gh auth status', 'collect evidence for path_safety'),
        DiagnosticCommand('gh pr checks --watch --fail-fast', 'collect evidence for path_safety'),
    ),
    remediation_steps=(
        'freeze head using git rev-parse before handling path_safety',
        'capture failing command logs for signature F:\\\\repos',
        'create backups before changing any tracked file',
        'never delete source files; move disposables to F:\\\\Trash-old',
        'apply one targeted mutation and re-run only the failed gate',
        'stage exact paths and compare staged list with plan',
        'stop at first unexpected dirty tree or validation failure',
    ),
)

class ExtendedCase0059PathSafetyRecipe(Recipe):
    name = "extended-0059-path_safety"
    patterns = ('F:\\\\repos', 'path_safety', '0ee049b34a19')

    def confidence(self, text: str) -> int:
        lowered = (text or "").lower()
        score = 0
        for pattern in self.patterns:
            if str(pattern).lower() in lowered:
                score += 15
        if SIGNATURE.family.lower() in lowered:
            score += 5
        if "traceback" in lowered or "error:" in lowered:
            score += 2
        return min(score, 100)

    def diagnostic_plan(self) -> list[dict]:
        return [
            {"command": cmd.command, "reason": cmd.reason, "required": cmd.required}
            for cmd in SIGNATURE.commands
        ]

    def remediation_plan(self) -> list[str]:
        return list(SIGNATURE.remediation_steps)

    def should_mutate(self, text: str) -> bool:
        return SIGNATURE.mutation_allowed and self.confidence(text) >= 15

    def apply(self, ctx, text: str | None = None) -> RecipeResult:
        body = text or ""
        return RecipeResult(
            self.name,
            False,
            {
                "advisory": True,
                "confidence": self.confidence(body),
                "signature": SIGNATURE.__dict__,
                "diagnostics": self.diagnostic_plan(),
                "remediation": self.remediation_plan(),
                "mutating_recipe_required": self.should_mutate(body),
                "safety": {
                    "fail_fast": True,
                    "never_delete": True,
                    "exact_stage_required": True,
                    "rollback_required": True,
                },
            },
        )
