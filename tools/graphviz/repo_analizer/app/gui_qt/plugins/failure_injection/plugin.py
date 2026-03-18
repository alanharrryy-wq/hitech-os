from __future__ import annotations

import os

from app.gui_qt.plugins.plugin_base import Plugin, PluginContext

MODE_ENV = "HITECH_QT_FAILURE_INJECTION_MODE"


def _failure_mode() -> str:
    return str(os.environ.get(MODE_ENV, "off")).strip().lower()


if _failure_mode() == "load":
    raise RuntimeError("Injected plugin load failure (failure_injection)")


class FailureInjectionPlugin(Plugin):
    """
    Deterministic failure-injection plugin for validating error paths.

    Modes (via HITECH_QT_FAILURE_INJECTION_MODE):
    - off: no-op
    - load: module import failure (raised at import time)
    - init: initialization failure
    - integration: registers a dock contribution with a failing widget factory
    """

    name = "failure_injection"
    version = "1.0.0"
    description = "Deterministic failure injection plugin for diagnostics."
    author = "Repo Analyzer Team"

    _DOCK_ID = "failure_injection.failing_dock"

    def initialize(self, context: PluginContext) -> None:
        mode = _failure_mode()
        if mode in {"", "off", "none"}:
            return

        if mode == "init":
            raise RuntimeError("Injected plugin init failure (failure_injection)")

        if mode == "integration":
            context.register_dock(
                contribution_id=self._DOCK_ID,
                title="Failure Injection Dock",
                widget_factory=self._failing_widget_factory,
                area="right",
                visible=True,
            )
            logger = getattr(context, "logger", None)
            if logger is not None and hasattr(logger, "warning"):
                try:
                    logger.warning(
                        "failure_injection registered failing dock for integration diagnostics"
                    )
                except Exception:
                    pass
            return

        logger = getattr(context, "logger", None)
        if logger is not None and hasattr(logger, "warning"):
            try:
                logger.warning(
                    f"failure_injection received unsupported mode='{mode}', defaulting to no-op"
                )
            except Exception:
                pass

    def _failing_widget_factory(self, parent=None):
        raise RuntimeError(
            "Injected integration failure (dock widget factory) from failure_injection plugin"
        )


PluginImplementation = FailureInjectionPlugin
