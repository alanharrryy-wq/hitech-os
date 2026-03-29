from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication

from ..skins import apply_skin

try:
    from shiboken6 import isValid as qt_object_is_valid
except ImportError:  # pragma: no cover - PySide6 ships shiboken6
    def qt_object_is_valid(obj):
        return obj is not None

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class SkinRuntimeCoordinator:
    """Apply selected skin and delegate visual integration to visual_runtime."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def apply_selected_skin(self, skin_name: str) -> None:
        app = QApplication.instance()
        if app is None:
            return

        diagnostics = getattr(self.main, 'runtime_diagnostics', None)
        if diagnostics is not None and hasattr(diagnostics, 'trace'):
            diagnostics.trace('skin-runtime', 'apply skin requested', skin=skin_name)

        self.main._skin_tokens = apply_skin(app, self.main, skin_name)

        preferences_runtime = getattr(self.main, "preferences_runtime", None)
        if preferences_runtime is not None and hasattr(preferences_runtime, "update"):
            try:
                preferences_runtime.update(skin_name=skin_name)
            except Exception:
                self._log_runtime_warning("preferences runtime skin update failed")
        else:
            settings = getattr(self.main, "settings", None)
            if settings is not None:
                try:
                    settings.setValue("skin_name", skin_name)
                except Exception:
                    self._log_runtime_warning("skin settings update failed")

        self._run_visual_runtime(force=True, reason='skin-change')

        svg_window = getattr(self.main, "_svg_window", None)
        if self._is_live_qt_object(svg_window) and hasattr(svg_window, "set_skin"):
            try:
                svg_window.set_skin(self.main._skin_tokens)
            except Exception:
                self._log_runtime_warning("svg skin apply skipped")

        try:
            status_bar = self.main.statusBar()
        except Exception:
            status_bar = None
        if self._is_live_qt_object(status_bar):
            try:
                status_bar.showMessage(
                    f"Skin applied: {self.main._skin_tokens.display_name}",
                    2400,
                )
            except Exception:
                self._log_runtime_warning("status skin message skipped")

    def _apply_skin_to_widgets(self) -> None:
        self._run_visual_runtime(force=False, reason='skin-refresh')

    def _run_visual_runtime(self, *, force: bool, reason: str) -> None:
        runtime = getattr(self.main, 'visual_runtime', None)
        if runtime is None:
            self._log_runtime_warning('visual runtime not available')
            return

        try:
            runtime.process_shell_surfaces(
                self.main._skin_tokens,
                reason=reason,
                force=force,
            )
            diagnostics = getattr(self.main, 'runtime_diagnostics', None)
            if diagnostics is not None and hasattr(diagnostics, 'trace'):
                diagnostics.trace(
                    'skin-runtime',
                    'visual runtime applied',
                    reason=reason,
                    force=force,
                    skin=self.main._skin_tokens.name,
                )
        except Exception:
            self._log_runtime_warning('visual runtime apply skipped')

    def _is_live_qt_object(self, obj: object) -> bool:
        if obj is None:
            return False
        if not hasattr(obj, "metaObject"):
            return False
        try:
            return bool(qt_object_is_valid(obj))
        except Exception:
            return False

    def _log_runtime_warning(self, message: str) -> None:
        text = f"[skin-runtime] {message}"
        logger = getattr(self.main, "log", None)
        if callable(logger):
            try:
                logger(text)
                return
            except Exception:
                pass
        print(text)
