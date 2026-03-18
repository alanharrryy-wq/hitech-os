from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QByteArray, QRectF, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QPainter
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
        self._content_rect = QRectF()
        self._padding_ratio = 0.06
        self._padding_min = 36.0
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setObjectName('svgGraphicsView')

    def set_canvas_colors(self, background: str, border: str) -> None:
        self.setBackgroundBrush(QColor(background))
        self.viewport().setStyleSheet(
            f'background: {background}; border-radius: 10px; border: 1px solid {border};'
        )
        self.viewport().update()

    def set_content_rect(self, rect: QRectF) -> None:
        self._content_rect = QRectF(rect)

    def scene_rect_for_content(self, rect: QRectF | None = None) -> QRectF:
        target = QRectF(rect) if rect is not None else self._effective_content_rect()
        return self._expanded_rect(target)

    def fit_scene(self) -> None:
        target = self._effective_content_rect()
        if target.isNull() or not target.isValid():
            return
        self.resetTransform()
        self._zoom = 1.0
        self.centerOn(target.center())
        self.fitInView(self._expanded_rect(target), Qt.KeepAspectRatio)

    def set_actual_size(self) -> None:
        self.resetTransform()
        self._zoom = 1.0
        target = self._effective_content_rect()
        if target.isValid() and not target.isNull():
            self.centerOn(target.center())

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

    def _effective_content_rect(self) -> QRectF:
        if self._content_rect.isValid() and not self._content_rect.isNull():
            return QRectF(self._content_rect)
        scene = self.scene()
        if scene is None:
            return QRectF()
        scene_rect = scene.sceneRect()
        if scene_rect.isValid() and not scene_rect.isNull():
            return QRectF(scene_rect)
        return scene.itemsBoundingRect()

    def _expanded_rect(self, rect: QRectF) -> QRectF:
        if rect.isNull() or not rect.isValid():
            return QRectF()
        basis = max(rect.width(), rect.height(), 240.0)
        padding = max(self._padding_min, basis * self._padding_ratio)
        return rect.adjusted(-padding, -padding, padding, padding)

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
        self._pending_initial_fit = False
        self._renderer = QSvgRenderer(self)
        self._scene = QGraphicsScene(self)
        self._svg_item: QGraphicsSvgItem | None = None

        self.setWindowTitle('SVG Workspace')
        self.resize(1260, 900)

        self._build_ui()
        self._build_toolbar()
        self._rebuild_svg_item()
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

        pill_box = QVBoxLayout()
        pill_box.setContentsMargins(0, 0, 0, 0)
        pill_box.setSpacing(6)
        self.pill_label = QLabel('Pan • Zoom • Fit', header)
        self.pill_label.setObjectName('panelPill')
        self.status_label = QLabel('Canvas IDE dark', header)
        self.status_label.setObjectName('svgStatusLabel')
        pill_box.addWidget(self.pill_label, 0, Qt.AlignRight)
        pill_box.addWidget(self.status_label, 0, Qt.AlignRight)
        header_layout.addLayout(pill_box)
        card_layout.addWidget(header)

        self.view = SvgGraphicsView(card)
        self.view.setScene(self._scene)
        card_layout.addWidget(self.view, 1)

        self.hint_label = QLabel(
            'Ctrl + rueda para zoom. Arrastra para paneo. Ajustar regresa al encuadre ideal.',
            card,
        )
        self.hint_label.setObjectName('svgHintLabel')
        card_layout.addWidget(self.hint_label)

        outer.addWidget(card, 1)
        self.setCentralWidget(central)
        self._card = card

    def _build_toolbar(self) -> None:
        toolbar = QToolBar('SvgToolbar', self)
        toolbar.setObjectName('SvgToolbar')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        self._toolbar = toolbar

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

    def _rebuild_svg_item(self) -> None:
        self._scene.clear()
        self._svg_item = QGraphicsSvgItem()
        self._svg_item.setSharedRenderer(self._renderer)
        self._svg_item.setPos(0, 0)
        self._scene.addItem(self._svg_item)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._card.set_skin(tokens)
        self.view.set_canvas_colors(tokens.code_bg, tokens.border)
        self._scene.setBackgroundBrush(QColor(tokens.code_bg))
        self.centralWidget().setStyleSheet(f'background: {tokens.bg};')
        self._toolbar.setStyleSheet(
            f'''
            QToolBar#SvgToolbar {{
                background: {tokens.bg_alt};
                border-bottom: 1px solid {tokens.accent};
                spacing: 8px;
                padding: 8px 10px;
            }}
            QToolBar#SvgToolbar QToolButton {{
                background: {tokens.panel_alt};
                color: {tokens.text};
                border: 1px solid {tokens.border};
                border-radius: 10px;
                padding: 7px 11px;
                font-weight: 600;
            }}
            QToolBar#SvgToolbar QToolButton:hover {{
                border: 1px solid {tokens.accent};
                background: {tokens.panel_hover};
            }}
            '''
        )
        self.status_label.setText(f'Canvas {tokens.display_name} • fondo real {tokens.code_bg}')
        self.view.viewport().update()
        self._scene.update()

    def load_svg(self, path: str, title: str | None = None) -> None:
        file_path = Path(path)
        if not file_path.exists():
            QMessageBox.critical(self, 'SVG Workspace', f'El archivo no existe:\n{path}')
            return
        if file_path.suffix.lower() != '.svg':
            QMessageBox.information(self, 'SVG Workspace', 'El archivo seleccionado no es .svg.')
            return

        try:
            svg_bytes = file_path.read_bytes()
        except Exception as exc:
            QMessageBox.critical(self, 'SVG Workspace', f'No se pudo leer el SVG:\n{path}\n\n{exc}')
            return

        if svg_bytes.startswith(b'\xef\xbb\xbf'):
            svg_bytes = svg_bytes[3:]

        ok = self._renderer.load(QByteArray(svg_bytes))
        if not ok or not self._renderer.isValid():
            QMessageBox.critical(self, 'SVG Workspace', f'No se pudo cargar el SVG:\n{path}')
            return

        self._current_path = str(file_path)
        self._rebuild_svg_item()

        view_box = self._renderer.viewBoxF()
        if view_box.isValid() and not view_box.isNull():
            content_rect = QRectF(view_box)
        else:
            default_size = self._renderer.defaultSize()
            if default_size.isValid():
                content_rect = QRectF(0, 0, float(default_size.width()), float(default_size.height()))
            else:
                content_rect = QRectF(self._scene.itemsBoundingRect())

        self.view.set_content_rect(content_rect)
        self._scene.setSceneRect(self.view.scene_rect_for_content(content_rect))
        self._scene.update()
        self.view.viewport().update()

        shown_title = title or file_path.name
        self.title_label.setText(shown_title)
        default_size = self._renderer.defaultSize()
        dimensions = f'{default_size.width()}×{default_size.height()}' if default_size.isValid() else 'dimensión desconocida'
        self.meta_label.setText(f'{file_path.name} • {dimensions}')
        self.setWindowTitle(f'SVG Workspace • {shown_title}')

        self._pending_initial_fit = True
        if self.isVisible():
            QTimer.singleShot(0, self._fit_if_pending)

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        if self._pending_initial_fit:
            QTimer.singleShot(0, self._fit_if_pending)

    def _fit_if_pending(self) -> None:
        if not self._pending_initial_fit:
            return
        self._pending_initial_fit = False
        self.fit_to_view()

    def fit_to_view(self) -> None:
        self.view.fit_scene()

    def actual_size(self) -> None:
        self.view.set_actual_size()
