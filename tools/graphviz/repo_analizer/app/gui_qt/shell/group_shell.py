from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDockWidget

from ..event_bus import Events

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


ConsolePolicy = Literal["hidden", "allowed", "preferred"]


@dataclass(frozen=True, slots=True)
class ShellGroupSpec:
    group_id: str
    label: str
    purpose: str
    primary_tool_ids: tuple[str, ...]
    allowed_core_docks: tuple[str, ...]
    console_policy: ConsolePolicy


class ShellGroupRuntime(QObject):
    """
    Shell-level group orchestration layer.

    Groups are not tools; they define shell intent, visibility defaults and
    routing behavior over the existing workstation/tool runtime.
    """

    ACTIVE_GROUP_KEY = "shell_active_group_v1"
    DEFAULT_GROUP_ID = "explore"

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        super().__init__(main_window)
        self.main = main_window
        self._active_group_id = self._load_active_group_id()
        self._applying = False
        self._group_specs = self._build_group_specs()

    @property
    def active_group_id(self) -> str:
        return self._active_group_id

    def list_groups(self) -> tuple[ShellGroupSpec, ...]:
        return tuple(self._group_specs.values())

    def get_group(self, group_id: str) -> ShellGroupSpec | None:
        return self._group_specs.get(self._normalize_group_id(group_id))

    def restore_startup_group(self) -> str:
        target = self._active_group_id
        if target not in self._group_specs:
            target = ""
        if not target:
            target = self._derive_group_from_active_tool()
        if not target:
            target = self.DEFAULT_GROUP_ID
        self.apply_group(target, reason="startup", force=True)
        return target

    def apply_group(self, group_id: str, *, reason: str = "manual", force: bool = False) -> bool:
        normalized = self._normalize_group_id(group_id)
        spec = self._group_specs.get(normalized)
        if spec is None:
            return False
        if self._applying:
            return False

        same_group = self._active_group_id == spec.group_id
        if same_group and not force:
            return True

        self._applying = True
        selected_primary_tool = ""
        try:
            self._apply_core_visibility(spec)
            selected_primary_tool = self._apply_group_primary(spec, reason=reason)
            self._set_active_group(spec.group_id)
            self._publish_group_changed(
                spec=spec,
                reason=reason,
                selected_primary_tool=selected_primary_tool,
            )
        finally:
            self._applying = False

        return True

    def activate_for_tool(self, tool_id: str, *, reason: str = "tool-route") -> str:
        normalized_tool_id = self._normalize_tool_id(tool_id)
        group_id = self.resolve_group_for_tool(normalized_tool_id)
        self.apply_group(group_id, reason=f"{reason}:{normalized_tool_id}", force=True)
        return group_id

    def reopen_last_tool(self, *, reason: str = "reopen") -> bool:
        tool_workspace = getattr(self.main, "tool_workspace", None)
        if tool_workspace is None:
            return False

        reopened = bool(tool_workspace.reopen_last_active_tool())
        active_tool_id = str(getattr(tool_workspace, "active_tool_id", "") or "").strip()
        if reopened and active_tool_id:
            self.activate_for_tool(active_tool_id, reason=f"{reason}:active")
        return reopened

    def resolve_group_for_tool(self, tool_id: str) -> str:
        normalized = self._normalize_tool_id(tool_id)
        if not normalized:
            return self.DEFAULT_GROUP_ID

        for spec in self._group_specs.values():
            if normalized in spec.primary_tool_ids:
                return spec.group_id

        if "cloudflare_guardian" in normalized or "cloudflare" in normalized or "graph" in normalized:
            return "graph"
        if "orchestrator" in normalized or "bridge" in normalized or "run" in normalized:
            return "run"
        return self.DEFAULT_GROUP_ID

    def _set_active_group(self, group_id: str) -> None:
        self._active_group_id = group_id
        self.main.settings.setValue(self.ACTIVE_GROUP_KEY, group_id)
        self._sync_context(group_id=group_id)

    def _load_active_group_id(self) -> str:
        raw = self.main.settings.value(self.ACTIVE_GROUP_KEY, "")
        normalized = self._normalize_group_id(raw)
        return normalized if normalized in self._build_group_specs() else ""

    def _derive_group_from_active_tool(self) -> str:
        tool_workspace = getattr(self.main, "tool_workspace", None)
        if tool_workspace is None:
            return ""
        active_tool_id = str(getattr(tool_workspace, "active_tool_id", "") or "").strip()
        if not active_tool_id:
            return ""
        return self.resolve_group_for_tool(active_tool_id)

    def _build_group_specs(self) -> dict[str, ShellGroupSpec]:
        specs = (
            ShellGroupSpec(
                group_id="explore",
                label="Explore",
                purpose="Repository navigation and structural overview.",
                primary_tool_ids=(),
                allowed_core_docks=(
                    "workspace_summary_dock",
                    "explorer_dock",
                ),
                console_policy="hidden",
            ),
            ShellGroupSpec(
                group_id="search",
                label="Search",
                purpose="Query and review search results with focused preview.",
                primary_tool_ids=(),
                allowed_core_docks=(
                    "results_dock",
                    "preview_workspace_dock",
                ),
                console_policy="allowed",
            ),
            ShellGroupSpec(
                group_id="inspect",
                label="Inspect",
                purpose="Detailed file/context inspection surfaces.",
                primary_tool_ids=(),
                allowed_core_docks=(
                    "preview_workspace_dock",
                    "central_inspector_dock",
                    "inspector_dock",
                ),
                console_policy="hidden",
            ),
            ShellGroupSpec(
                group_id="graph",
                label="Graph",
                purpose="Graph-oriented analysis workspace.",
                primary_tool_ids=("cloudflare_guardian",),
                allowed_core_docks=(),
                console_policy="hidden",
            ),
            ShellGroupSpec(
                group_id="run",
                label="Run",
                purpose="Execution workflows, logs and run output.",
                primary_tool_ids=("orchestrator_bridge",),
                allowed_core_docks=("results_dock",),
                console_policy="preferred",
            ),
            ShellGroupSpec(
                group_id="settings",
                label="Settings",
                purpose="Preferences and runtime policy controls.",
                primary_tool_ids=(),
                allowed_core_docks=("tools_launcher_dock",),
                console_policy="hidden",
            ),
        )
        return {spec.group_id: spec for spec in specs}

    def _all_core_dock_names(self) -> tuple[str, ...]:
        return (
            "workspace_summary_dock",
            "preview_workspace_dock",
            "central_inspector_dock",
            "tools_launcher_dock",
            "explorer_dock",
            "results_dock",
            "inspector_dock",
            "bookmarks_dock",
        )

    def _iter_core_docks(self) -> tuple[tuple[str, object], ...]:
        records: list[tuple[str, object]] = []
        for name in self._all_core_dock_names():
            dock = getattr(self.main, name, None)
            if isinstance(dock, QDockWidget) or (
                dock is not None and hasattr(dock, "show") and hasattr(dock, "hide")
            ):
                records.append((name, dock))
        return tuple(records)

    def _apply_core_visibility(self, spec: ShellGroupSpec) -> None:
        allowed = set(spec.allowed_core_docks)
        first_shown: object | None = None
        for dock_name, dock in self._iter_core_docks():
            should_show = dock_name in allowed
            if should_show:
                dock.show()
                if first_shown is None:
                    first_shown = dock
            else:
                dock.hide()

        # Console policy guardrail: hidden groups always collapse bottom console.
        if spec.console_policy == "hidden":
            results = getattr(self.main, "results_dock", None)
            if isinstance(results, QDockWidget) or (
                results is not None and hasattr(results, "hide")
            ):
                results.hide()

        if first_shown is not None:
            try:
                raise_method = getattr(first_shown, "raise_", None)
                if callable(raise_method):
                    raise_method()
            except Exception:
                pass

    def _apply_group_primary(self, spec: ShellGroupSpec, *, reason: str) -> str:
        workspace = getattr(self.main, "tool_workspace", None)
        if workspace is None:
            return ""

        if spec.primary_tool_ids:
            for tool_id in spec.primary_tool_ids:
                if workspace.activate_tool(tool_id, reason=f"group:{spec.group_id}:{reason}"):
                    return tool_id
            return ""

        # Shell-only groups suspend plugin surfaces so they do not compete.
        for entry in workspace.list_tools():
            if entry.visible:
                workspace.hide_tool(entry.tool_id, reason=f"group:{spec.group_id}:{reason}")
        return ""

    def _publish_group_changed(
        self,
        *,
        spec: ShellGroupSpec,
        reason: str,
        selected_primary_tool: str,
    ) -> None:
        payload: dict[str, Any] = {
            "group_id": spec.group_id,
            "label": spec.label,
            "reason": reason,
            "primary_tool_id": selected_primary_tool,
            "allowed_core_docks": list(spec.allowed_core_docks),
            "console_policy": spec.console_policy,
        }
        self.main.event_bus.publish(Events.SHELL_GROUP_CHANGED, payload)
        self.main.statusBar().showMessage(f"Group: {spec.label}", 1800)

    def _sync_context(self, *, group_id: str) -> None:
        context_runtime = self.main.service_container.get("workstation_context")
        if context_runtime is None:
            return
        try:
            context_runtime.update(active_group=group_id)
        except Exception:
            return

    @staticmethod
    def _normalize_group_id(value: object) -> str:
        text = str(value or "").strip().lower()
        return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")

    @staticmethod
    def _normalize_tool_id(value: object) -> str:
        text = str(value or "").strip().lower()
        return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


__all__ = ["ShellGroupRuntime", "ShellGroupSpec"]

