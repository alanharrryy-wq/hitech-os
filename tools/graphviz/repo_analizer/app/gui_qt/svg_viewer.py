from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPainter
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QGraphicsSvgItem

from .skins import SkinTokens
from .widgets import PanelCard


class SvgGraphicsView(QGraphicsView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._zoom = 1.0
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def fit_scene(self) -> None:
        scene = self.scene()
        if scene is None or scene.itemsBoundingRect().isNull():
            return
        self.resetTransform()
        self._zoom = 1.0
        self.fitInView(scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def set_actual_size(self) -> None:
        self.resetTransform()
        self._zoom = 1.0

    def zoom_in(self) -> None:
        self._apply_zoom(1.15)

    def zoom_out(self) -> None:
        self._apply_zoom(1 / 1.15)

    def _apply_zoom(self, factor: float) -> None:
        next_zoom = self._zoom * factor
        if next_zoom < 0.08 or next_zoom > 40:
            return
        self._zoom = next_zoom
        self.scale(factor, factor)

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)


class SvgPreviewWindow(QMainWindow):
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._current_path: str | None = None
        self._renderer = QSvgRenderer(self)
        self._scene = QGraphicsScene(self)
        self._svg_item = QGraphicsSvgItem()
        self._svg_item.setSharedRenderer(self._renderer)
        self._scene.addItem(self._svg_item)

        self.setWindowTitle('SVG Workspace')
        self.resize(1260, 900)

        self._build_ui()
        self._build_toolbar()
        self.set_skin(tokens)

    def _build_ui(self) -> None:
        central = QWidget(self)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        card = PanelCard(self._tokens, accent=True, parent=central)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        header = QWidget(card)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(2)
        self.title_label = QLabel('SVG Workspace', header)
        self.title_label.setObjectName('heroTitleLabel')
        self.meta_label = QLabel('Sin archivo cargado', header)
        self.meta_label.setObjectName('svgMetaLabel')
        self.meta_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.meta_label)
        header_layout.addLayout(title_box, 1)

        self.pill_label = QLabel('Pan • Zoom • Fit', header)
        self.pill_label.setObjectName('panelPill')
        header_layout.addWidget(self.pill_label)
        card_layout.addWidget(header)

        self.view = SvgGraphicsView(card)
        self.view.setScene(self._scene)
        card_layout.addWidget(self.view, 1)

        self.hint_label = QLabel('Ctrl + rueda para zoom. Arrastra para paneo. Ajustar regresa al encuadre ideal.', card)
        self.hint_label.setObjectName('svgHintLabel')
        card_layout.addWidget(self.hint_label)

        outer.addWidget(card, 1)
        self.setCentralWidget(central)
        self._card = card

    def _build_toolbar(self) -> None:
        toolbar = QToolBar('SvgToolbar', self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        fit_action = QAction('Ajustar', self)
        fit_action.triggered.connect(self.fit_to_view)
        toolbar.addAction(fit_action)

        actual_action = QAction('100%', self)
        actual_action.triggered.connect(self.actual_size)
        toolbar.addAction(actual_action)

        zoom_in_action = QAction('Zoom +', self)
        zoom_in_action.triggered.connect(self.view.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction('Zoom -', self)
        zoom_out_action.triggered.connect(self.view.zoom_out)
        toolbar.addAction(zoom_out_action)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._card.set_skin(tokens)
        self.view.setStyleSheet(
            f"""
            QGraphicsView {{
                background: {tokens.code_bg};
                border: 1px solid {tokens.border};
                border-radius: 12px;
            }}
            """
        )

    def load_svg(self, path: str, title: str | None = None) -> None:
        file_path = Path(path)
        if not file_path.exists():
            QMessageBox.critical(self, 'SVG Workspace', f'El archivo no existe:\n{path}')
            return
        if file_path.suffix.lower() != '.svg':
            QMessageBox.information(self, 'SVG Workspace', 'El archivo seleccionado no es .svg.')
            return

        ok = self._renderer.load(str(file_path))
        if not ok or not self._renderer.isValid():
            QMessageBox.critical(self, 'SVG Workspace', f'No se pudo cargar el SVG:\n{path}')
            return

        self._current_path = str(file_path)
        bounds = self._scene.itemsBoundingRect()
        if bounds.isNull():
            default_size = self._renderer.defaultSize()
            if default_size.isValid():
                self._scene.setSceneRect(0, 0, default_size.width(), default_size.height())
        else:
            self._scene.setSceneRect(bounds)

        shown_title = title or file_path.name
        self.title_label.setText(shown_title)
        default_size = self._renderer.defaultSize()
        dimensions = f'{default_size.width()}×{default_size.height()}' if default_size.isValid() else 'dimensión desconocida'
        self.meta_label.setText(f'{file_path.name} • {dimensions}')
        self.setWindowTitle(f'SVG Workspace • {shown_title}')
        self.fit_to_view()

    def fit_to_view(self) -> None:
        self.view.fit_scene()

    def actual_size(self) -> None:
        self.view.set_actual_size()
