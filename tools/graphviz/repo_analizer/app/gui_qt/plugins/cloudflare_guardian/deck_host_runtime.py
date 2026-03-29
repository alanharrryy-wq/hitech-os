from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .spec_factory import build_action_specs, build_command_specs


@dataclass(slots=True)
class DeckHostRuntimeState:
    dispatcher: Any = None
    state_adapter: Any = None
    snapshot_payload_fn: Callable[[Any], Any] | None = None


class DeckHostRuntimeCoordinator:
    """Non-visual host runtime for CloudflareGuardian context/command/snapshot wiring."""

    def __init__(self) -> None:
        self.state = DeckHostRuntimeState()

    @property
    def dispatcher(self) -> Any:
        return self.state.dispatcher

    @property
    def state_adapter(self) -> Any:
        return self.state.state_adapter

    def bind_plugin_context(self, context: Any) -> None:
        self.state.dispatcher = getattr(context, "dispatcher", None) if context is not None else None

    def set_state_adapter(self, adapter: Any) -> None:
        self.state.state_adapter = adapter

    def set_snapshot_payload_fn(self, payload_fn: Callable[[Any], Any] | None) -> None:
        self.state.snapshot_payload_fn = payload_fn

    def build_current_snapshot(
        self,
        *,
        normalize_snapshot: Callable[[Any, Callable[[Any], Any] | None], dict[str, Any]],
    ) -> dict[str, Any]:
        adapter = self.state.state_adapter
        if adapter is None:
            return normalize_snapshot(None, self.state.snapshot_payload_fn)

        raw_snapshot = None
        refresh_snapshot = getattr(adapter, "refresh_snapshot", None)
        if callable(refresh_snapshot):
            try:
                raw_snapshot = refresh_snapshot()
            except Exception:
                raw_snapshot = None

        if raw_snapshot is None:
            getter = getattr(adapter, "get_last_snapshot", None)
            if callable(getter):
                try:
                    raw_snapshot = getter()
                except Exception:
                    raw_snapshot = None

        if raw_snapshot is None:
            builder = getattr(adapter, "build_snapshot", None)
            if callable(builder):
                try:
                    raw_snapshot = builder()
                except Exception:
                    raw_snapshot = None

        if raw_snapshot is None:
            payload_method = getattr(adapter, "snapshot_payload", None)
            if callable(payload_method):
                try:
                    raw_snapshot = payload_method()
                except Exception:
                    raw_snapshot = None

        return normalize_snapshot(raw_snapshot, self.state.snapshot_payload_fn)

    def dispatcher_has(self, command_name: str) -> bool:
        dispatcher = self.state.dispatcher
        if dispatcher is None:
            return False
        has_method = getattr(dispatcher, "has", None)
        if callable(has_method):
            try:
                return bool(has_method(command_name))
            except Exception:
                return False
        commands = getattr(dispatcher, "_commands", None)
        if isinstance(commands, dict):
            return command_name in commands
        return False

    def build_command_specs(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        return build_command_specs(snapshot, dispatcher_has=self.dispatcher_has)

    def build_action_specs(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        return build_action_specs(snapshot, dispatcher_has=self.dispatcher_has)


__all__ = ["DeckHostRuntimeCoordinator", "DeckHostRuntimeState"]

