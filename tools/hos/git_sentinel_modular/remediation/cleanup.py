from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..shared.contracts import CleanupAction, CleanupPlan, ScanResult
from ..shared.errors import PathSafetyError


@dataclass(slots=True)
class CleanupPolicy:
    allowed_prefixes: tuple[str, ...] = ("dist/", "build/", "tools/_local/", "tools/_reports/")
    quarantine_root: str = "tools/_local/quarantine"
    block_tracked_files: bool = True

    def validate_target(self, relative_path: str) -> None:
        rel = relative_path.replace("\\", "/")
        if not any(rel.startswith(prefix) for prefix in self.allowed_prefixes):
            raise PathSafetyError(
                "Cleanup target is outside allowed prefixes.",
                candidate=rel,
                allowed_prefixes=list(self.allowed_prefixes),
            )


class CleanupPlanner:
    def __init__(self, policy: CleanupPolicy | None = None):
        self.policy = policy or CleanupPolicy()

    def plan_cleanup(self, scan_result: ScanResult) -> CleanupPlan:
        scan_result = scan_result.validate()
        actions: list[CleanupAction] = []
        blocked_actions: list[CleanupAction] = []

        for finding in scan_result.artifact_findings:
            path = finding.path
            action = CleanupAction(
                kind="quarantine",
                target_path=path,
                reason=f"cleanup artifact category={finding.category}",
                safe=True,
                quarantine_first=True,
                metadata={"category": finding.category},
            ).validate()
            if finding.tracked and self.policy.block_tracked_files:
                blocked_actions.append(
                    CleanupAction(
                        kind="noop",
                        target_path=path,
                        reason="tracked artifact blocked by cleanup policy",
                        safe=True,
                        quarantine_first=True,
                        metadata={"tracked": True, "category": finding.category},
                    ).validate()
                )
                continue
            try:
                self.policy.validate_target(path)
            except PathSafetyError:
                blocked_actions.append(
                    CleanupAction(
                        kind="noop",
                        target_path=path,
                        reason="artifact path outside allowed cleanup prefixes",
                        safe=True,
                        quarantine_first=True,
                        metadata={"category": finding.category},
                    ).validate()
                )
                continue
            actions.append(action)

        return CleanupPlan(
            dry_run=True,
            actions=actions,
            blocked_actions=blocked_actions,
        ).validate()

    def quarantine_destination(self, relative_path: str) -> str:
        rel = relative_path.replace("\\", "/").strip("/")
        return f"{self.policy.quarantine_root.rstrip('/')}/{rel}"
