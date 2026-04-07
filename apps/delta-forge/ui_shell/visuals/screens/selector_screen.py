from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ..chrome.frameless import FramelessResizeController
from ..chrome.titlebar import WindowChromeBar
from ..common.types import SelectorResult
from ..controls.buttons import create_button
from ..controls.chips import create_chip
from ..controls.inputs import create_combo, create_line_edit
from ..effects.polish import enable_card_hover, repolish
from ..effects.shadow import apply_shadow
from ..layout.scene import build_glass_dialog_scene
from ..style.scale import apply_layout_scale, normalize_scale
from ..style.stylesheet import build_stylesheet
from ..themes.catalog import normalize_theme, resolve_theme
from ..widgets.primitives import make_separator


class SelectorLikeScreen(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        theme_id: str = "silver_frost_cyan",
        scale_id: str = "100",
    ) -> None:
        super().__init__(parent)
        self._theme_id = normalize_theme(theme_id)
        self._scale_id = normalize_scale(scale_id)
        self._result = SelectorResult(False, "", self._theme_id, self._scale_id, "Overview", "Default")

        self.setWindowTitle("Workspace Selector")
        self.setModal(True)
        self.setMinimumSize(920, 660)
        self.resize(980, 700)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self._resize_controller = FramelessResizeController(self, margin=14, edge_hit=12, corner_hit=24)

        self._build_ui()
        self.apply_theme(self._theme_id)
        self.apply_ui_scale(self._scale_id, force=True)
        self.refresh_preview()

    def _build_ui(self) -> None:
        outer, content_layer, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._theme_id,
            variant="selector",
            margins=(0, 0, 0, 0),
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content_layer)
        scene_layout.setContentsMargins(10, 10, 10, 10)
        scene_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("Shell")
        shell.setProperty("variant", "selector")
        apply_shadow(shell, blur=30.0, y_offset=10.0, alpha=58)
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(22, 22, 22, 22)
        shell_layout.setSpacing(18)

        self.window_chrome = WindowChromeBar(
            self,
            title=self.windowTitle(),
            on_close=self.reject,
            allow_minimize=True,
            allow_maximize=True,
            title_icon="workspace",
        )
        shell_layout.addWidget(self.window_chrome)

        header = QFrame()
        header.setProperty("card", "hero")
        apply_shadow(header, blur=22.0, y_offset=8.0, alpha=18)
        enable_card_hover(header)
        shell_layout.addWidget(header)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 20, 22, 20)
        header_layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        header_layout.addLayout(top_row)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(6)
        top_row.addLayout(title_stack, 1)

        eyebrow = QLabel("Workspace")
        eyebrow.setProperty("role", "eyebrow")
        title_stack.addWidget(eyebrow, 0, Qt.AlignLeft)

        title = QLabel("Template Selector")
        title.setProperty("role", "title")
        title_stack.addWidget(title)

        subtitle = QLabel("Choose workspace path, theme, and profile. This screen is reusable and domain-neutral.")
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        title_stack.addWidget(subtitle)

        chip_stack = QVBoxLayout()
        chip_stack.setSpacing(8)
        top_row.addLayout(chip_stack, 0)
        self.mode_chip = create_chip("Selector", tone="accent", icon="panel", parent=header)
        chip_stack.addWidget(self.mode_chip, 0, Qt.AlignRight)
        chip_stack.addWidget(create_chip("Reusable", tone="neutral", icon="spark", parent=header), 0, Qt.AlignRight)
        chip_stack.addStretch(1)

        header_line = make_separator()
        header_line.setProperty("tone", "glow")
        repolish(header_line)
        header_layout.addWidget(header_line)

        content = QHBoxLayout()
        content.setSpacing(18)
        shell_layout.addLayout(content, 1)

        self.form_card = QFrame()
        self.form_card.setProperty("card", "true")
        apply_shadow(self.form_card, blur=18.0, y_offset=6.0, alpha=16)
        enable_card_hover(self.form_card)
        content.addWidget(self.form_card, 6)

        self.preview_card = QFrame()
        self.preview_card.setProperty("card", "muted")
        apply_shadow(self.preview_card, blur=18.0, y_offset=6.0, alpha=14)
        enable_card_hover(self.preview_card)
        content.addWidget(self.preview_card, 5)

        self._build_form_panel()
        self._build_preview_panel()

        footer = QFrame()
        footer.setProperty("card", "footer")
        apply_shadow(footer, blur=14.0, y_offset=5.0, alpha=10)
        enable_card_hover(footer)
        shell_layout.addWidget(footer)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(18, 14, 18, 14)
        footer_layout.setSpacing(12)

        footer_text_stack = QVBoxLayout()
        footer_text_stack.setSpacing(4)
        footer_layout.addLayout(footer_text_stack, 1)

        footer_label = QLabel("Selection")
        footer_label.setProperty("role", "eyebrow")
        footer_text_stack.addWidget(footer_label, 0, Qt.AlignLeft)

        footer_hint = QLabel("Use this selector as a reusable entry screen in any PySide6 project.")
        footer_hint.setProperty("role", "hint")
        footer_hint.setWordWrap(True)
        footer_text_stack.addWidget(footer_hint)

        self.cancel_button = create_button("Cancel", "danger", self.reject, minimum_width=124)
        self.confirm_button = create_button("Apply", "primary", self.confirm, default=True, minimum_width=156)
        footer_layout.addWidget(self.cancel_button, 0)
        footer_layout.addWidget(self.confirm_button, 0)

    def _build_form_panel(self) -> None:
        layout = QVBoxLayout(self.form_card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        section_title = QLabel("Workspace")
        section_title.setProperty("role", "section")
        layout.addWidget(section_title)

        path_label = QLabel("Path")
        path_label.setProperty("role", "field")
        layout.addWidget(path_label)

        self.path_entry = create_line_edit("Paste a folder or file path", parent=self.form_card)
        self.path_entry.textChanged.connect(self.refresh_preview)
        layout.addWidget(self.path_entry)

        picker_row = QHBoxLayout()
        picker_row.setSpacing(10)
        layout.addLayout(picker_row)

        self.folder_button = create_button("Folder", "secondary", self.pick_directory, icon="folder")
        self.file_button = create_button("File", "secondary", self.pick_file, icon="file")
        picker_row.addWidget(self.folder_button)
        picker_row.addWidget(self.file_button)
        picker_row.addStretch(1)

        path_hint = QLabel("Path is editable. You can paste, tweak, and re-run selection quickly.")
        path_hint.setProperty("role", "hint")
        path_hint.setWordWrap(True)
        layout.addWidget(path_hint)

        layout.addWidget(make_separator())

        options_title = QLabel("Options")
        options_title.setProperty("role", "section")
        layout.addWidget(options_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)
        layout.addLayout(grid)

        theme_label = QLabel("Theme (Global)")
        theme_label.setProperty("role", "field")
        grid.addWidget(theme_label, 0, 0)
        self.theme_value = QLabel(resolve_theme(self._theme_id).label, self.form_card)
        self.theme_value.setProperty("role", "mono")
        self.theme_value.setWordWrap(True)
        grid.addWidget(self.theme_value, 0, 1)

        mode_label = QLabel("Mode")
        mode_label.setProperty("role", "field")
        grid.addWidget(mode_label, 1, 0)
        self.mode_combo = create_combo(["Overview", "Details", "Focus"], parent=self.form_card)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        grid.addWidget(self.mode_combo, 1, 1)

        profile_label = QLabel("Profile")
        profile_label.setProperty("role", "field")
        grid.addWidget(profile_label, 2, 0)
        self.profile_combo = create_combo(["Default", "Compact", "Verbose"], parent=self.form_card)
        self.profile_combo.currentIndexChanged.connect(self.refresh_preview)
        grid.addWidget(self.profile_combo, 2, 1)

        grid.setColumnStretch(1, 1)
        layout.addStretch(1)

    def _build_preview_panel(self) -> None:
        layout = QVBoxLayout(self.preview_card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        section_title = QLabel("Preview")
        section_title.setProperty("role", "section")
        layout.addWidget(section_title)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(8)
        layout.addLayout(chip_row)
        self.path_chip = create_chip("No path", tone="neutral", icon="warning", parent=self.preview_card)
        self.mode_state_chip = create_chip("Overview", tone="accent", icon="overview", parent=self.preview_card)
        chip_row.addWidget(self.path_chip, 0)
        chip_row.addWidget(self.mode_state_chip, 0)
        chip_row.addStretch(1)

        summary_title = QLabel("Selection summary")
        summary_title.setProperty("role", "field")
        layout.addWidget(summary_title)

        self.summary_value = QLabel("")
        self.summary_value.setProperty("role", "value")
        self.summary_value.setWordWrap(True)
        layout.addWidget(self.summary_value)

        detail_title = QLabel("Resolved details")
        detail_title.setProperty("role", "field")
        layout.addWidget(detail_title)

        self.detail_value = QLabel("")
        self.detail_value.setProperty("role", "mono")
        self.detail_value.setWordWrap(True)
        layout.addWidget(self.detail_value)
        layout.addStretch(1)

    def _selected_theme_id(self) -> str:
        return self._theme_id

    def apply_theme(self, theme_id: str) -> None:
        theme = resolve_theme(theme_id)
        self._theme_id = theme.theme_id
        self.setStyleSheet(build_stylesheet(theme.theme_id, self._scale_id))
        self._glass_backdrop.apply_theme(theme.theme_id)
        if getattr(self, "theme_value", None) is not None:
            self.theme_value.setText(theme.label)

    def apply_ui_scale(self, scale_id: str, *, force: bool = False) -> None:
        resolved = normalize_scale(scale_id)
        if (not force) and resolved == self._scale_id:
            return
        self._scale_id = resolved
        self._resize_controller.apply_scale(resolved)
        self.window_chrome.apply_scale(resolved)
        apply_layout_scale(self, resolved)
        self.setStyleSheet(build_stylesheet(self._theme_id, resolved))
        self._glass_backdrop.update()

    def _set_chip(self, label: QLabel, text: str, tone: str) -> None:
        current_text = label.text()
        current_tone = str(label.property("tone") or "")
        text_changed = current_text != text
        tone_changed = current_tone != tone

        if text_changed:
            label.setText(text)
        if tone_changed:
            label.setProperty("tone", tone)
        if text_changed or tone_changed:
            repolish(label)

    def on_mode_changed(self) -> None:
        self.mode_chip.setText(self.mode_combo.currentText())
        self.refresh_preview()

    def pick_directory(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select workspace folder", str(Path.cwd()))
        if selected:
            self.path_entry.setText(selected)

    def pick_file(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Select workspace file",
            str(Path.cwd()),
            "All Files (*.*)",
        )
        if selected:
            self.path_entry.setText(selected)

    def refresh_preview(self) -> None:
        path_value = self.path_entry.text().strip()
        mode = self.mode_combo.currentText().strip()
        profile = self.profile_combo.currentText().strip()
        theme = self._selected_theme_id()

        if path_value:
            self._set_chip(self.path_chip, "Path set", "good")
        else:
            self._set_chip(self.path_chip, "No path", "neutral")
        self._set_chip(self.mode_state_chip, mode or "Overview", "accent")

        self.summary_value.setText(
            "\n".join(
                [
                    f"Theme: {theme}",
                    f"Scale: {self._scale_id}%",
                    f"Mode: {mode or 'Overview'}",
                    f"Profile: {profile or 'Default'}",
                ]
            )
        )
        self.detail_value.setText(
            "\n".join(
                [
                    f"Workspace: {path_value or '(none)'}",
                    f"Exists: {'yes' if path_value and Path(path_value).exists() else 'no'}",
                    f"Window style: frameless glass",
                ]
            )
        )
        self.confirm_button.setEnabled(bool(path_value))

    def confirm(self) -> None:
        workspace = self.path_entry.text().strip()
        if not workspace:
            QMessageBox.warning(self, "Selector", "Please select or paste a workspace path.")
            return
        self._result = SelectorResult(
            accepted=True,
            workspace=workspace,
            theme_id=self._selected_theme_id(),
            scale_id=self._scale_id,
            mode=self.mode_combo.currentText().strip() or "Overview",
            profile=self.profile_combo.currentText().strip() or "Default",
        )
        self.accept()

    def reject(self) -> None:  # type: ignore[override]
        self._result = SelectorResult(
            accepted=False,
            workspace=self.path_entry.text().strip(),
            theme_id=self._selected_theme_id(),
            scale_id=self._scale_id,
            mode=self.mode_combo.currentText().strip() or "Overview",
            profile=self.profile_combo.currentText().strip() or "Default",
        )
        super().reject()

    def result_selection(self) -> SelectorResult:
        return self._result
