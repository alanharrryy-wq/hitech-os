from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject

from ..event_bus import Events


class CommandRoutingRuntime(QObject):
    """Shell-owned runtime for app-wide command dispatch and telemetry hooks."""

    def __init__(self, command_dispatcher, event_bus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.command_dispatcher = command_dispatcher
        self.event_bus = event_bus
        self._detach_before = self.command_dispatcher.on_before_execute(
            self._on_before_execute
        )
        self._detach_after = self.command_dispatcher.on_after_execute(
            self._on_after_execute
        )

    def dispatch(self, name: str, **payload: Any) -> Any:
        self.event_bus.publish(
            Events.COMMAND_DISPATCH_REQUESTED,
            {"name": name, "payload": dict(payload)},
        )
        try:
            result = self.command_dispatcher.execute(name, **payload)
        except Exception as exc:
            self.event_bus.publish(
                Events.COMMAND_FAILED,
                {"name": name, "payload": dict(payload), "error": str(exc)},
            )
            raise
        return result

    def dispose(self) -> None:
        if callable(self._detach_before):
            try:
                self._detach_before()
            except Exception:
                pass
        if callable(self._detach_after):
            try:
                self._detach_after()
            except Exception:
                pass

    def _on_before_execute(self, command_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        self.event_bus.publish(
            Events.COMMAND_WILL_EXECUTE,
            {
                "name": command_name,
                "args": list(args),
                "kwargs": dict(kwargs),
            },
        )

    def _on_after_execute(self, command_name: str, result: Any) -> None:
        self.event_bus.publish(
            Events.COMMAND_EXECUTED,
            {"name": command_name, "result": result},
        )


__all__ = ["CommandRoutingRuntime"]
