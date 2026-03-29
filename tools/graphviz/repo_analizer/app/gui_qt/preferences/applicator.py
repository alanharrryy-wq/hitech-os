from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .policy import RuntimePolicy

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


@dataclass(slots=True)
class RuntimePolicyApplyReport:
    applied_targets: list[str] = field(default_factory=list)
    skipped_targets: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


class RuntimePolicyApplicator:
    """Apply computed runtime policy to shell and surface hook points."""

    DOCK_NAMES = (
        "workspace_summary_dock",
        "preview_workspace_dock",
        "central_inspector_dock",
        "tools_launcher_dock",
        "explorer_dock",
        "results_dock",
        "inspector_dock",
        "bookmarks_dock",
    )

    def apply(
        self,
        main_window: RepoAnalyzerMainWindow,
        policy: RuntimePolicy,
    ) -> RuntimePolicyApplyReport:
        report = RuntimePolicyApplyReport()
        self._apply_surface_properties(main_window, policy, target_name="main_window", report=report)

        central = main_window.centralWidget()
        if central is not None:
            self._apply_surface_properties(central, policy, target_name="central_widget", report=report)

        launcher = getattr(main_window, "tool_launcher_panel", None)
        if launcher is not None:
            self._apply_surface_properties(launcher, policy, target_name="tool_launcher_panel", report=report)

        for dock_name in self.DOCK_NAMES:
            dock = getattr(main_window, dock_name, None)
            if dock is None:
                report.skipped_targets.append(dock_name)
                continue
            self._apply_surface_properties(dock, policy, target_name=dock_name, report=report)
            widget = dock.widget() if hasattr(dock, "widget") else None
            if widget is not None:
                self._apply_surface_properties(
                    widget,
                    policy,
                    target_name=f"{dock_name}.widget",
                    report=report,
                )
        return report

    def _apply_surface_properties(
        self,
        widget,
        policy: RuntimePolicy,
        *,
        target_name: str,
        report: RuntimePolicyApplyReport,
    ) -> None:
        setter = getattr(widget, "setProperty", None)
        if not callable(setter):
            report.skipped_targets.append(target_name)
            return
        try:
            setter("runtimeDensityScale", policy.density_scale)
            setter("runtimeMotionPolicy", policy.motion_policy)
            setter("runtimePerformancePolicy", policy.performance_policy)
            setter("runtimeHighContrast", policy.high_contrast)
            setter("runtimeTypographyScale", policy.typography_scale)
            setter("runtimeSpacingScale", policy.spacing_scale)
            setter("runtimeMinReadableFontPt", policy.min_readable_font_pt)
            report.applied_targets.append(target_name)
        except Exception as exc:
            report.failures.append(f"{target_name}: {exc}")


__all__ = ["RuntimePolicyApplicator", "RuntimePolicyApplyReport"]
