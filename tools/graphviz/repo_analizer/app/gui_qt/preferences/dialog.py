from __future__ import annotations

from dataclasses import asdict
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..skins import list_skins
from .runtime import PreferencesRuntime


class PreferencesDialog(QDialog):
    """Centralized preferences placeholder for future UX/product work."""

    def __init__(self, runtime: PreferencesRuntime, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.runtime = runtime
        self._reset_requested = False
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(520, 420)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        intro = QLabel(
            "Product-level settings center. This surface is intentionally mechanics-first.",
            self,
        )
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        root.addWidget(intro)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        root.addLayout(form)

        self.skin_combo = QComboBox(self)
        for skin in list_skins():
            self.skin_combo.addItem(skin.display_name, skin.name)
        form.addRow("Theme / Skin", self.skin_combo)

        self.font_family_combo = QComboBox(self)
        self.font_family_combo.addItems(["System", "Segoe UI", "Consolas"])
        form.addRow("Font family", self.font_family_combo)

        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setRange(10, 28)
        form.addRow("Font size", self.font_size_spin)

        self.density_combo = QComboBox(self)
        self.density_combo.addItems(["compact", "comfortable", "spacious"])
        form.addRow("Density", self.density_combo)

        self.contrast_combo = QComboBox(self)
        self.contrast_combo.addItems(["normal", "high"])
        form.addRow("Contrast", self.contrast_combo)

        self.motion_combo = QComboBox(self)
        self.motion_combo.addItems(["full", "reduced", "off"])
        form.addRow("Motion", self.motion_combo)

        self.performance_combo = QComboBox(self)
        self.performance_combo.addItems(["balanced", "performance"])
        form.addRow("Performance", self.performance_combo)

        self.layout_behavior_combo = QComboBox(self)
        self.layout_behavior_combo.addItem("single_active_tool")
        self.layout_behavior_combo.addItem("legacy_docking")
        form.addRow("Layout behavior", self.layout_behavior_combo)

        self.include_dev_tools_check = QCheckBox("Include development tools at startup", self)
        form.addRow("Developer tools", self.include_dev_tools_check)

        self.enable_legacy_plugins_check = QCheckBox("Enable legacy *_plugin.py loading", self)
        form.addRow("Legacy plugins", self.enable_legacy_plugins_check)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self,
        )
        reset_button = buttons.addButton("Reset Defaults", QDialogButtonBox.ResetRole)
        reset_button.clicked.connect(self._reset_to_defaults)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._load_current_preferences()

    def gather_updates(self) -> dict[str, Any]:
        if self._reset_requested:
            prefs = self.runtime.reset_defaults()
            self._reset_requested = False
            return asdict(prefs)
        return {
            "skin_name": str(self.skin_combo.currentData() or self.skin_combo.currentText()).strip(),
            "font_family": self.font_family_combo.currentText().strip(),
            "font_size": int(self.font_size_spin.value()),
            "density": self.density_combo.currentText().strip(),
            "contrast": self.contrast_combo.currentText().strip(),
            "motion": self.motion_combo.currentText().strip(),
            "performance": self.performance_combo.currentText().strip(),
            "layout_behavior": self.layout_behavior_combo.currentText().strip(),
            "include_dev_tools": bool(self.include_dev_tools_check.isChecked()),
            "enable_legacy_plugins": bool(self.enable_legacy_plugins_check.isChecked()),
        }

    def _load_current_preferences(self) -> None:
        prefs = asdict(self.runtime.current)

        skin_index = self.skin_combo.findData(prefs["skin_name"])
        if skin_index >= 0:
            self.skin_combo.setCurrentIndex(skin_index)

        self._set_combo_text(self.font_family_combo, prefs["font_family"])
        self.font_size_spin.setValue(int(prefs["font_size"]))
        self._set_combo_text(self.density_combo, prefs["density"])
        self._set_combo_text(self.contrast_combo, prefs["contrast"])
        self._set_combo_text(self.motion_combo, prefs["motion"])
        self._set_combo_text(self.performance_combo, prefs["performance"])
        self._set_combo_text(self.layout_behavior_combo, prefs["layout_behavior"])
        self.include_dev_tools_check.setChecked(bool(prefs["include_dev_tools"]))
        self.enable_legacy_plugins_check.setChecked(bool(prefs["enable_legacy_plugins"]))

    def _reset_to_defaults(self) -> None:
        self._reset_requested = True
        default_skin_name = getattr(self.runtime, "_default_skin_name", self.runtime.current.skin_name)
        defaults = asdict(self.runtime.current.defaults(skin_name=default_skin_name).normalized())
        skin_index = self.skin_combo.findData(defaults["skin_name"])
        if skin_index >= 0:
            self.skin_combo.setCurrentIndex(skin_index)
        self._set_combo_text(self.font_family_combo, defaults["font_family"])
        self.font_size_spin.setValue(int(defaults["font_size"]))
        self._set_combo_text(self.density_combo, defaults["density"])
        self._set_combo_text(self.contrast_combo, defaults["contrast"])
        self._set_combo_text(self.motion_combo, defaults["motion"])
        self._set_combo_text(self.performance_combo, defaults["performance"])
        self._set_combo_text(self.layout_behavior_combo, defaults["layout_behavior"])
        self.include_dev_tools_check.setChecked(bool(defaults["include_dev_tools"]))
        self.enable_legacy_plugins_check.setChecked(bool(defaults["enable_legacy_plugins"]))

    @staticmethod
    def _set_combo_text(combo: QComboBox, value: str) -> None:
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
