from __future__ import annotations

from pathlib import Path
from typing import Iterable

try:
    from PySide6.QtWidgets import QFileDialog, QWidget
except ImportError as exc:  # pragma: no cover - explicit boundary failure
    QFileDialog = None  # type: ignore[assignment]
    QWidget = object  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def choose_file(
    parent: QWidget | None = None,
    *,
    caption: str = "Choose File",
    directory: str | Path = "",
    file_filter: str = "All Files (*)",
) -> str | None:
    _ensure_available()
    path, _ = QFileDialog.getOpenFileName(parent, caption, _directory_string(directory), file_filter)
    return path or None


def choose_files(
    parent: QWidget | None = None,
    *,
    caption: str = "Choose Files",
    directory: str | Path = "",
    file_filter: str = "All Files (*)",
) -> list[str]:
    _ensure_available()
    paths, _ = QFileDialog.getOpenFileNames(parent, caption, _directory_string(directory), file_filter)
    return list(paths)


def choose_directory(
    parent: QWidget | None = None,
    *,
    caption: str = "Choose Folder",
    directory: str | Path = "",
) -> str | None:
    _ensure_available()
    path = QFileDialog.getExistingDirectory(parent, caption, _directory_string(directory))
    return path or None


def save_file(
    parent: QWidget | None = None,
    *,
    caption: str = "Save File",
    directory: str | Path = "",
    file_filter: str = "All Files (*)",
    default_suffix: str = "",
) -> str | None:
    _ensure_available()
    dialog = QFileDialog(parent, caption, _directory_string(directory), file_filter)
    dialog.setAcceptMode(QFileDialog.AcceptSave)
    if default_suffix:
        dialog.setDefaultSuffix(default_suffix)
    if not dialog.exec():
        return None
    selected = dialog.selectedFiles()
    if not selected:
        return None
    return selected[0]


def normalize_dialog_selection(paths: Iterable[str | Path]) -> list[str]:
    return [str(Path(path).expanduser()) for path in paths]


def _directory_string(directory: str | Path) -> str:
    return str(Path(directory).expanduser()) if directory else ""


def _ensure_available() -> None:
    if QFileDialog is None:
        raise RuntimeError("PySide6 is required for infrastructure.system.file_dialogs") from _IMPORT_ERROR
