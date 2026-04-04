from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from forgeos.shared.pyside6_glass.tools.ui_baseline.validate_ui_baseline import render_report, validate_repository
from forgeos.shared.pyside6_glass.ui_baseline.builder.catalog import list_ingredients
from forgeos.shared.pyside6_glass.ui_baseline.builder.generator import generate_screen
from forgeos.shared.pyside6_glass.ui_baseline.builder.preview import preview_recipe
from forgeos.shared.pyside6_glass.ui_baseline.builder.recipe import ScreenRecipe, derive_class_name


class UIBaselineBuilderWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("UI Baseline Builder")
        self.resize(1080, 760)
        self._class_name_auto = True

        self._build_ui()
        self._load_ingredients()
        self._sync_class_name()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        grid = QGridLayout()
        grid.addWidget(self._build_form_group(), 0, 0)
        grid.addWidget(self._build_zone_group(), 0, 1)
        grid.addWidget(self._build_ingredient_group(), 1, 0, 1, 2)
        root.addLayout(grid)

        buttons = QHBoxLayout()
        self.preview_button = QPushButton("Preview", self)
        self.generate_button = QPushButton("Generate", self)
        self.generate_validate_button = QPushButton("Generate + Validate", self)

        buttons.addWidget(self.preview_button)
        buttons.addWidget(self.generate_button)
        buttons.addWidget(self.generate_validate_button)
        buttons.addStretch(1)
        root.addLayout(buttons)

        self.output_box = QTextEdit(self)
        self.output_box.setReadOnly(True)
        root.addWidget(self.output_box, 1)

        self.preview_button.clicked.connect(self.on_preview)
        self.generate_button.clicked.connect(self.on_generate)
        self.generate_validate_button.clicked.connect(self.on_generate_validate)

    def _build_form_group(self) -> QGroupBox:
        box = QGroupBox("Configuración", self)
        form = QFormLayout(box)

        self.screen_name_edit = QLineEdit("customers_dashboard", box)
        self.class_name_edit = QLineEdit("", box)

        output_row = QHBoxLayout()
        self.output_dir_edit = QLineEdit(str(Path.cwd()), box)
        browse = QPushButton("…", box)
        browse.clicked.connect(self.on_browse_output_dir)
        output_row.addWidget(self.output_dir_edit, 1)
        output_row.addWidget(browse)

        self.preset_combo = self._combo(["glass-default", "glass-quiet", "glass-contrast", "glass-ops"])
        self.visual_level_combo = self._combo(["performance", "standard", "premium", "showcase"])
        self.role_combo = self._combo(["workspace", "dashboard", "detail", "form", "dialog", "supporting"])
        self.variant_combo = self._combo(["default", "data-heavy", "analysis", "focused", "compact"])
        self.emphasis_combo = self._combo(["low", "medium", "high"])
        self.fx_combo = self._combo(["off", "subtle", "standard", "rich"])
        self.data_state_combo = self._combo(["ready", "loading", "empty", "error", "stale"])

        self.screen_name_edit.textChanged.connect(self._sync_class_name)
        self.class_name_edit.textEdited.connect(self._on_class_name_edited)

        form.addRow("Screen name", self.screen_name_edit)
        form.addRow("Class name", self.class_name_edit)
        form.addRow("Output path", output_row)
        form.addRow("Preset", self.preset_combo)
        form.addRow("Visual level", self.visual_level_combo)
        form.addRow("Role", self.role_combo)
        form.addRow("Variant", self.variant_combo)
        form.addRow("Emphasis", self.emphasis_combo)
        form.addRow("Fx level", self.fx_combo)
        form.addRow("Data state", self.data_state_combo)
        return box

    def _build_zone_group(self) -> QGroupBox:
        box = QGroupBox("Zonas", self)
        layout = QVBoxLayout(box)
        self.hero_check = QCheckBox("Hero", box)
        self.main_check = QCheckBox("Main", box)
        self.side_check = QCheckBox("Side", box)
        self.footer_check = QCheckBox("Footer", box)
        self.status_check = QCheckBox("Status", box)

        for control in (self.hero_check, self.main_check, self.side_check, self.footer_check, self.status_check):
            control.setChecked(True)
            layout.addWidget(control)

        layout.addStretch(1)
        return box

    def _build_ingredient_group(self) -> QGroupBox:
        box = QGroupBox("Ingredientes", self)
        layout = QVBoxLayout(box)
        layout.addWidget(QLabel("Marca los ingredientes que quieres incluir en el scaffold.", box))
        self.ingredients_list = QListWidget(box)
        layout.addWidget(self.ingredients_list)
        return box

    def _combo(self, values: list[str]) -> QComboBox:
        combo = QComboBox(self)
        combo.addItems(values)
        return combo

    def _load_ingredients(self) -> None:
        for ingredient in list_ingredients():
            item = QListWidgetItem(
                f"{ingredient.label} | zona sugerida: {ingredient.suggested_zone} | {ingredient.stability}"
            )
            item.setData(Qt.ItemDataRole.UserRole, ingredient.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.ingredients_list.addItem(item)

    def _on_class_name_edited(self, value: str) -> None:
        self._class_name_auto = not bool(value.strip())

    def _sync_class_name(self) -> None:
        if self._class_name_auto or not self.class_name_edit.text().strip():
            self.class_name_edit.setText(derive_class_name(self.screen_name_edit.text().strip()))

    def _selected_ingredients(self) -> list[str]:
        selected = []
        for index in range(self.ingredients_list.count()):
            item = self.ingredients_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        return selected

    def _current_recipe(self) -> ScreenRecipe:
        return ScreenRecipe(
            screen_name=self.screen_name_edit.text().strip(),
            class_name=self.class_name_edit.text().strip(),
            output_dir=self.output_dir_edit.text().strip(),
            preset=self.preset_combo.currentText(),
            visual_level=self.visual_level_combo.currentText(),
            visual_role=self.role_combo.currentText(),
            visual_variant=self.variant_combo.currentText(),
            visual_emphasis=self.emphasis_combo.currentText(),
            visual_fx_level=self.fx_combo.currentText(),
            data_state=self.data_state_combo.currentText(),
            include_hero=self.hero_check.isChecked(),
            include_main=self.main_check.isChecked(),
            include_side=self.side_check.isChecked(),
            include_footer=self.footer_check.isChecked(),
            include_status=self.status_check.isChecked(),
            ingredients=self._selected_ingredients(),
        )

    def on_browse_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Selecciona directorio")
        if directory:
            self.output_dir_edit.setText(directory)

    def on_preview(self) -> None:
        recipe = self._current_recipe()
        summary = preview_recipe(recipe)
        self.output_box.setPlainText(summary.to_markdown())

    def on_generate(self) -> None:
        recipe = self._current_recipe()
        try:
            path = generate_screen(recipe, overwrite=True)
        except Exception as exc:
            QMessageBox.critical(self, "Generate", str(exc))
            return
        self.output_box.setPlainText(f"Archivo generado:\n{path}")

    def on_generate_validate(self) -> None:
        recipe = self._current_recipe()
        try:
            path = generate_screen(recipe, overwrite=True)
        except Exception as exc:
            QMessageBox.critical(self, "Generate + Validate", str(exc))
            return

        issues = validate_repository(path.parent)
        report = render_report(issues, path.parent)
        self.output_box.setPlainText(f"Archivo generado:\n{path}\n\n{report}")



def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = UIBaselineBuilderWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
