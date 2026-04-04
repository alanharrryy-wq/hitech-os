"""
Runtime foundation for approved UI stack wiring.

This module intentionally keeps the logic simple and explicit:
- discover optional libraries
- expose capability flags
- apply lightweight defaults
- avoid making every screen remember the stack
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class RuntimeCapabilities:
    qtawesome: bool
    pyqtgraph: bool
    fluent_widgets: bool
    frameless_window: bool


class VisualRuntime:
    """Central runtime that knows which approved helpers are available."""

    def __init__(self) -> None:
        self.capabilities = RuntimeCapabilities(
            qtawesome=self._module_available("qtawesome"),
            pyqtgraph=self._module_available("pyqtgraph"),
            fluent_widgets=self._module_available("qfluentwidgets"),
            frameless_window=self._module_available("qframelesswindow"),
        )

    @staticmethod
    def _module_available(module_name: str) -> bool:
        try:
            __import__(module_name)
            return True
        except Exception:
            return False

    def apply_app_defaults(self, app: QApplication) -> None:
        """Apply safe baseline defaults at application startup."""
        app.setApplicationDisplayName(app.applicationDisplayName() or "Visual Tool")
        app.setStyle("Fusion")
        app.setFont(QFont("Segoe UI", 10))

    def configure_optional_integrations(self) -> None:
        """Configure optional libraries when present."""
        if self.capabilities.pyqtgraph:
            try:
                import pyqtgraph as pg

                pg.setConfigOptions(antialias=True)
            except Exception:
                pass

    def describe_fx(self, visual_fx_level: str) -> dict[str, int]:
        """Map semantic FX level to simple helper values."""
        table = {
            "off": {"radius": 10, "shadow_blur": 0, "border_alpha": 40},
            "subtle": {"radius": 12, "shadow_blur": 14, "border_alpha": 60},
            "standard": {"radius": 14, "shadow_blur": 22, "border_alpha": 80},
            "rich": {"radius": 16, "shadow_blur": 28, "border_alpha": 110},
            "showcase": {"radius": 20, "shadow_blur": 36, "border_alpha": 130},
        }
        return table.get(visual_fx_level, table["standard"])

    def tone_for_role(self, visual_role: str, visual_variant: str) -> dict[str, str]:
        """Return lightweight style hints derived from intent."""
        if visual_role == "workspace" and visual_variant == "data-heavy":
            return {
                "header_class": "workspaceHeader",
                "surface_class": "dataSurface",
                "density": "compact",
            }
        if visual_variant == "form":
            return {
                "header_class": "formHeader",
                "surface_class": "formSurface",
                "density": "comfortable",
            }
        return {
            "header_class": "defaultHeader",
            "surface_class": "defaultSurface",
            "density": "comfortable",
        }


_RUNTIME: Optional[VisualRuntime] = None


def get_visual_runtime() -> VisualRuntime:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = VisualRuntime()
    return _RUNTIME
