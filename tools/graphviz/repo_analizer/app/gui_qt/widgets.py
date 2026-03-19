"""Premium widget component library for Hitech OS GUI.

ARCHITECTURE:
This module is organized into THREE TIERS of widget coupling:

1. SEMANTIC TIER (low risk)
   - No direct token access in __init__
   - Styled entirely via objectName + stylesheet hooks
   - Fully theme-neutral; cascading stylesheet applies colors
   - Examples: BasicButton, Label, Frame, Spacer
   - RULE: Never read self._tokens in a semantic widget

2. THEMED TIER (medium risk)
   - Tokens injected via set_skin() method only
   - Minimal custom paint; mostly stylesheet-driven
   - Color transitions via QVariantAnimation + stylesheet updates
   - Examples: StatusPill, MetricTile, InfoPill, FilterChip
   - RULE: set_skin() is the ONLY place to read tokens after construction

3. PREMIUM TIER (high care)
   - Direct token access in __init__ and paintEvent()
   - Custom QPainter logic for complex visual effects
   - Each paint method must justify its existence with a comment
   - Examples: HeroPanel, LoadingPlaceholderSurface
   - RULE: Every paintEvent must be documented. Consider if stylesheet can do it.

ANTI-PATTERNS (never do these):
  ❌ Interpolate QColor into stylesheet strings
  ❌ Use QPropertyAnimation on non-existent Qt properties
  ❌ Move layout-managed widgets via pos() manipulation
  ❌ Access tokens in paintEvent for semantic/themed tier
  ❌ Create a new paint method when objectName + stylesheet works

BEST PRACTICES (always do these):
  ✅ Use palette.py for all token-to-CSS conversions
  ✅ Call update() after stylesheet changes, not on every frame
  ✅ Use effects.py utilities (apply_shadow, fade_in) when available
  ✅ Make set_skin() idempotent--safe to call multiple times
  ✅ Document why a paint method exists and what it does
"""

from __future__ import annotations

from enum import Enum
from typing import Callable

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, QTimer, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from . import effects
from .palette import (
    blend_colors,
    glow_css,
    severity_color_css,
    severity_glow_css,
    token_to_css,
    token_with_alpha,
)
from .skins import SkinTokens

__all__ = [
    "Severity",
    # Semantic tier (no tokens, stylesheet-only)
    "BasicFrame",
    "BasicButton",
    "BasicLabel",
    # Themed tier (tokens via set_skin() only)
    "PanelCard",
    "ElevatedPanelCard",
    "InsetPanel",
    "MetricTile",
    "MetricRow",
    "MetricStrip",
    "StatCard",
    "SectionHeader",
    "SectionTitleBlock",
    "HeaderActionRow",
    "Divider",
    "InfoPill",
    "StatusPill",
    "FilterChip",
    "TagPill",
    "CountBadge",
    "SeverityBadge",
    "CompactEmptyState",
    "InlineHintState",
    "MetadataRow",
    "KeyValueGrid",
    "PropertyListCard",
    "ResultListItemCard",
    "PreviewSummaryCard",
    "StatusBanner",
    "InlineStatusBadge",
    # Premium tier (direct paint, special effects)
    "HeroPanel",
    "LoadingPlaceholderSurface",
    "EmptyState",
    "SurfaceFrame",
    "ToolbarSurface",
    "AccentButton",
    "SecondaryButton",
    "GhostButton",
    "QuietButton",
    # Effects
    "HoverRaiseFilter",
    "install_hover_raise",
    # Factory helpers
    "build_metric_row",
    "build_section_header",
    "build_status_pill",
    "build_empty_state",
]


class Severity(Enum):
    """Status severity levels for badges and indicators."""
    NEUTRAL = "neutral"
    ACCENT = "accent"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    MUTED = "muted"


def _set_visual_markers(
    widget: QWidget,
    *,
    role: str,
    tier: str,
    premium: bool = False,
    reveal: bool = False,
    skip: bool = False,
    code_surface: bool = False,
) -> None:
    """Attach lightweight visual metadata used by the runtime auto-detection."""
    try:
        widget.setProperty('visualRole', role)
        widget.setProperty('visualTier', tier)
        if premium:
            widget.setProperty('premium', True)
        if reveal:
            widget.setProperty('visualReveal', True)
        if skip:
            widget.setProperty('visualSkip', True)
        if code_surface:
            widget.setProperty('codeSurface', True)
    except Exception:
        pass


# ============================================================================
# SEMANTIC TIER: No token access, stylesheet-driven only
# ============================================================================

class BasicFrame(QFrame):
    """
    Basic frame for layout containers.
    
    Tier: SEMANTIC
    Styling: objectName + stylesheet only
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('basicFrame')
        self.setFrameShape(QFrame.NoFrame)
        _set_visual_markers(self, role='semantic-surface', tier='semantic', skip=True)


class BasicButton(QPushButton):
    """
    Basic button without token coupling.
    
    Tier: SEMANTIC
    Styling: objectName + stylesheet only
    """
    
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName('basicButton')
        _set_visual_markers(self, role='semantic-control', tier='semantic', skip=True)


class BasicLabel(QLabel):
    """
    Basic label without token coupling.
    
    Tier: SEMANTIC
    Styling: objectName + stylesheet only
    """
    
    def __init__(self, text: str = '', parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName('basicLabel')
        _set_visual_markers(self, role='semantic-label', tier='semantic', skip=True)


# ============================================================================
# THEMED TIER: Tokens via set_skin() only, minimal painting
# ============================================================================

class PanelCard(QFrame):
    """
    Basic panel card with clean rounded corners and border.
    
    Tier: THEMED
    Token access: set_skin() only
    Paint: Removed; stylesheet now handles visual (faster, skin-neutral)
    """
    
    def __init__(
        self,
        tokens: SkinTokens,
        parent: QWidget | None = None,
        *,
        accent: bool = False,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._accent = bool(accent)
        self.setObjectName('panelCard')
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        _set_visual_markers(self, role='panel-surface', tier='themed', premium=True)
        self._apply_skin()

    def _apply_skin(self) -> None:
        """Apply current tokens to stylesheet."""
        bg_top = token_to_css(self._tokens.panel)
        bg_bottom = token_to_css(self._tokens.panel_alt)
        border = token_to_css(self._tokens.border_strong if self._accent else self._tokens.border)
        self.setStyleSheet(f"""
            QFrame#panelCard {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {bg_top},
                    stop:1 {bg_bottom}
                );
                border: 1px solid {border};
                border-top: 1px solid {token_to_css(self._tokens.bevel_light)};
                border-bottom: 1px solid {token_to_css(self._tokens.bevel_shadow)};
                border-radius: 14px;
            }}
            QFrame#panelCard:hover {{
                border: 1px solid {token_to_css(self._tokens.border_strong)};
            }}
        """)

    def set_skin(self, tokens: SkinTokens) -> None:
        """Update theme. Safe to call anytime."""
        self._tokens = tokens
        self._apply_skin()


class ElevatedPanelCard(PanelCard):
    """
    Panel card with elevated shadow for overlays.
    
    Tier: THEMED
    Token access: set_skin() only
    Paint: Shadow via effects.py utility
    """
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(tokens, parent)
        effects.apply_shadow(self, tokens.shadow, blur=16.0, y_offset=8.0)


class InsetPanel(QFrame):
    """
    Inset panel for contained content with soft border.
    
    Tier: THEMED
    Token access: set_skin() only
    Paint: No custom paint
    """
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setObjectName('insetPanel')
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(10, 10, 10, 10)
        self._apply_skin()

    def _apply_skin(self) -> None:
        bg = token_to_css(self._tokens.bg_alt)
        border = token_to_css(self._tokens.border_soft)
        self.setStyleSheet(f"""
            QFrame#insetPanel {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
        """)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._apply_skin()


class MetricTile(PanelCard):
    """
    Metric display tile with title, large value, and optional caption.
    
    Tier: THEMED
    Token access: via parent PanelCard.set_skin()
    """
    
    def __init__(self, tokens: SkinTokens, title: str, parent: QWidget | None = None) -> None:
        super().__init__(tokens, parent)
        self._tokens = tokens
        self.setObjectName('metricTile')
        _set_visual_markers(self, role='metric-surface', tier='themed', premium=True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        
        self._title = QLabel(title, self)
        self._title.setObjectName('metricTitleLabel')
        self._title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self._value = QLabel('0', self)
        self._value.setObjectName('accentValueLabel')
        self._value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self._caption = QLabel('', self)
        self._caption.setObjectName('metricCaptionLabel')
        self._caption.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addWidget(self._title)
        layout.addWidget(self._value)
        layout.addWidget(self._caption)
        layout.addStretch(1)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        super().set_skin(tokens)

    def set_data(self, value: str, caption: str = '') -> None:
        self._value.setText(value)
        self._caption.setText(caption)


class MetricRow(QFrame):
    """Horizontal row of metric tiles."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        metrics: list[tuple[str, str, str]] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        self._tiles: list[MetricTile] = []
        
        if metrics:
            for title, value, caption in metrics:
                tile = MetricTile(tokens, title, self)
                tile.set_data(value, caption)
                layout.addWidget(tile)
                self._tiles.append(tile)
        
        layout.addStretch(1)

    def add_metric(self, title: str, value: str, caption: str = '') -> MetricTile:
        """Add a metric tile to the row."""
        tile = MetricTile(self._tokens, title, self)
        tile.set_data(value, caption)
        self.layout().insertWidget(len(self._tiles), tile)
        self._tiles.append(tile)
        return tile

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        for tile in self._tiles:
            tile.set_skin(tokens)


class MetricStrip(PanelCard):
    """Compact horizontal metric strip."""
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(tokens, parent)
        self.setContentsMargins(12, 8, 12, 8)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        self._items: dict[str, tuple[QLabel, QLabel]] = {}

    def add_metric(self, key: str, label: str, value: str) -> None:
        """Add a metric item to the strip."""
        layout = self.layout()
        
        label_widget = QLabel(label, self)
        label_widget.setObjectName('metricStripLabel')
        label_widget.setStyleSheet(f"color: {token_to_css(self._tokens.text_soft)}; font-size: 8pt;")
        
        value_widget = QLabel(value, self)
        value_widget.setObjectName('metricStripValue')
        value_widget.setStyleSheet(f"color: {token_to_css(self._tokens.text)}; font-weight: 600;")
        
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        
        self._items[key] = (label_widget, value_widget)

    def update_value(self, key: str, value: str) -> None:
        """Update a metric value."""
        if key in self._items:
            self._items[key][1].setText(value)


class StatCard(PanelCard):
    """Stat card with prominent large value."""
    
    def __init__(self, tokens: SkinTokens, stat_label: str, parent: QWidget | None = None) -> None:
        super().__init__(tokens, parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        label_widget = QLabel(stat_label, self)
        label_widget.setObjectName('statCardLabel')
        label_widget.setStyleSheet(f"color: {token_to_css(tokens.text_soft)}; font-size: 9pt;")
        
        self._value = QLabel('0', self)
        self._value.setObjectName('statCardValue')
        font = self._value.font()
        font.setPointSize(24)
        font.setWeight(QFont.Bold)
        self._value.setFont(font)
        self._value.setStyleSheet(f"color: {token_to_css(tokens.accent)};")
        
        self._subtitle = QLabel('', self)
        self._subtitle.setObjectName('statCardSubtitle')
        self._subtitle.setStyleSheet(f"color: {token_to_css(tokens.text_muted)}; font-size: 8pt;")
        
        layout.addWidget(label_widget)
        layout.addWidget(self._value)
        layout.addWidget(self._subtitle)
        layout.addStretch(1)

    def set_value(self, value: str, subtitle: str = '') -> None:
        self._value.setText(value)
        self._subtitle.setText(subtitle)


class SectionHeader(QFrame):
    """Header for a content section."""
    
    def __init__(self, tokens: SkinTokens, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 12, 0, 8)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._title = QLabel(title, self)
        self._title.setObjectName('sectionHeaderTitle')
        font = self._title.font()
        font.setPointSize(11)
        font.setWeight(QFont.SemiBold)
        self._title.setFont(font)
        self._title.setStyleSheet(f"color: {token_to_css(tokens.text)};")
        
        layout.addWidget(self._title)
        layout.addStretch(1)

    def set_title(self, title: str) -> None:
        self._title.setText(title)


class SectionTitleBlock(QFrame):
    """Larger section title block with optional subheading."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        title: str,
        subtitle: str = '',
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 16, 0, 12)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self._title = QLabel(title, self)
        self._title.setObjectName('sectionBlockTitle')
        font = self._title.font()
        font.setPointSize(13)
        font.setWeight(QFont.Bold)
        self._title.setFont(font)
        self._title.setStyleSheet(f"color: {token_to_css(tokens.text)};")
        
        layout.addWidget(self._title)
        
        if subtitle:
            self._subtitle = QLabel(subtitle, self)
            self._subtitle.setObjectName('sectionBlockSubtitle')
            self._subtitle.setStyleSheet(f"color: {token_to_css(tokens.text_soft)}; font-size: 9pt;")
            layout.addWidget(self._subtitle)


class HeaderActionRow(QFrame):
    """Header with title and action buttons."""
    
    def __init__(self, tokens: SkinTokens, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self._title = QLabel(title, self)
        font = self._title.font()
        font.setPointSize(10)
        font.setWeight(QFont.SemiBold)
        self._title.setFont(font)
        self._title.setStyleSheet(f"color: {token_to_css(tokens.text)};")
        
        layout.addWidget(self._title)
        layout.addStretch(1)
        
        self._action_layout: QHBoxLayout | None = None

    def add_action(self, button: QPushButton) -> None:
        """Add an action button to the right side."""
        main_layout = self.layout()
        if self._action_layout is None:
            self._action_layout = QHBoxLayout()
            self._action_layout.setContentsMargins(0, 0, 0, 0)
            self._action_layout.setSpacing(6)
            main_layout.addLayout(self._action_layout)
        
        self._action_layout.addWidget(button)


class Divider(QFrame):
    """Visual divider between sections."""
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setContentsMargins(0, 6, 0, 6)
        self.setStyleSheet(f"color: {token_to_css(tokens.border_soft)};")


class InfoPill(QFrame):
    """Small informational pill badge."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        text: str,
        severity: Severity = Severity.NEUTRAL,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._severity = severity
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(6, 3, 6, 3)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)
        
        self._label = QLabel(text, self)
        color = severity_color_css(tokens, severity.value)
        self._label.setStyleSheet(f"color: {color}; font-size: 8pt; font-weight: 500;")
        
        layout.addWidget(self._label)
        self._apply_skin()

    def _apply_skin(self) -> None:
        color = severity_color_css(self._tokens, self._severity.value)
        glow = severity_glow_css(self._tokens, self._severity.value)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {glow};
                border: 1px solid {color};
                border-radius: 12px;
            }}
        """)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._apply_skin()


class StatusPill(QFrame):
    """Status indicator pill with severity color."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        label: str,
        severity: Severity = Severity.NEUTRAL,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._severity = severity
        self.setFrameShape(QFrame.NoFrame)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)
        
        color = severity_color_css(tokens, severity.value)
        
        # Dot indicator
        self._dot = QFrame(self)
        self._dot.setFrameShape(QFrame.NoFrame)
        self._dot.setFixedSize(8, 8)
        self._dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        
        # Label
        self._label = QLabel(label, self)
        self._label.setStyleSheet(f"color: {token_to_css(tokens.text)}; font-size: 9pt; font-weight: 500;")
        
        layout.addWidget(self._dot)
        layout.addWidget(self._label)
        layout.addStretch(1)
        
        self._apply_skin()

    def _apply_skin(self) -> None:
        color = severity_color_css(self._tokens, self._severity.value)
        glow = severity_glow_css(self._tokens, self._severity.value)
        self._dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {glow};
                border: 1px solid {color};
                border-radius: 8px;
            }}
        """)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._apply_skin()


class FilterChip(QPushButton):
    """Toggleable filter chip."""
    
    def __init__(self, text: str, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._tokens = tokens
        self._checked = False
        self.clicked.connect(self._on_clicked)
        self._refresh_style()

    def _on_clicked(self) -> None:
        self._checked = not self._checked
        self._refresh_style()

    def is_checked(self) -> bool:
        return self._checked

    def set_checked(self, checked: bool) -> None:
        self._checked = checked
        self._refresh_style()

    def _refresh_style(self) -> None:
        if self._checked:
            bg = token_with_alpha(self._tokens.accent, 20)
            color = token_to_css(self._tokens.accent)
            border = token_to_css(self._tokens.accent)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {color};
                    border: 1px solid {border};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 8pt;
                    font-weight: 500;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {token_to_css(self._tokens.text_muted)};
                    border: 1px solid {token_to_css(self._tokens.border)};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 8pt;
                }}
                QPushButton:hover {{
                    color: {token_to_css(self._tokens.text)};
                    border: 1px solid {token_to_css(self._tokens.border_strong)};
                }}
            """)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._refresh_style()


class TagPill(QFrame):
    """Styled tag pill with optional close callback."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        text: str,
        on_close: Callable | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        label = QLabel(text, self)
        label.setStyleSheet(f"color: {token_to_css(tokens.text)}; font-size: 8pt;")
        layout.addWidget(label)
        
        if on_close:
            close_btn = QPushButton('×', self)
            close_btn.setFixedSize(16, 16)
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {token_to_css(tokens.text_soft)};
                    border: none;
                    padding: 0px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: {token_to_css(tokens.text)};
                }}
            """)
            close_btn.clicked.connect(on_close)
            layout.addWidget(close_btn)
        
        bg = token_with_alpha(tokens.accent, 15)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {token_to_css(tokens.border)};
                border-radius: 6px;
            }}
        """)


class CountBadge(QFrame):
    """Numeric count badge."""
    
    def __init__(self, tokens: SkinTokens, count: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedSize(24, 24)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._label = QLabel(str(count), self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet(f"color: white; font-size: 7pt; font-weight: bold;")
        layout.addWidget(self._label)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {token_to_css(tokens.accent)};
                border-radius: 12px;
            }}
        """)

    def set_count(self, count: int) -> None:
        self._label.setText(str(count))


class SeverityBadge(QFrame):
    """Severity badge with color coding."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        severity: Severity,
        label: str = '',
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._severity = severity
        self.setFrameShape(QFrame.NoFrame)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        text_label = label or severity.value.capitalize()
        label_widget = QLabel(text_label, self)
        color = severity_color_css(tokens, severity.value)
        label_widget.setStyleSheet(f"color: {color}; font-size: 8pt; font-weight: 600;")
        layout.addWidget(label_widget)
        
        glow = severity_glow_css(tokens, severity.value)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {glow};
                border: 1px solid {color};
                border-radius: 4px;
            }}
        """)


class CompactEmptyState(InsetPanel):
    """Compact empty state for inline use."""
    
    def __init__(self, tokens: SkinTokens, message: str, parent: QWidget | None = None) -> None:
        super().__init__(tokens, parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"color: {token_to_css(tokens.text_soft)}; font-size: 9pt;")
        label.setWordWrap(True)
        layout.addWidget(label)


class InlineHintState(QFrame):
    """Inline hint or helper text panel."""
    
    def __init__(self, tokens: SkinTokens, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        
        label = QLabel(text, self)
        label.setWordWrap(True)
        bg = token_with_alpha(tokens.accent, 10)
        label.setStyleSheet(f"""
            QLabel {{
                color: {token_to_css(tokens.text_soft)};
                font-size: 8pt;
                background-color: {bg};
                padding: 4px;
                border-radius: 4px;
                border-left: 2px solid {token_to_css(tokens.accent)};
            }}
        """)
        layout.addWidget(label)


class MetadataRow(QFrame):
    """Single row of metadata key-value pair."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        key: str,
        value: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)
        
        key_label = QLabel(key + ':', self)
        key_label.setStyleSheet(f"color: {token_to_css(tokens.text_soft)}; font-size: 8pt; font-weight: 500;")
        key_label.setMinimumWidth(80)
        
        value_label = QLabel(value, self)
        value_label.setStyleSheet(f"color: {token_to_css(tokens.text)}; font-size: 8pt;")
        value_label.setWordWrap(True)
        
        layout.addWidget(key_label)
        layout.addWidget(value_label)
        layout.addStretch(1)


class KeyValueGrid(QFrame):
    """Grid of key-value pairs."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        columns: int = 2,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._columns = columns
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self._row = 0

    def add_pair(self, key: str, value: str) -> None:
        """Add a key-value pair to the grid."""
        col = self._row % self._columns
        grid_row = self._row // self._columns
        
        key_label = QLabel(key + ':', self)
        key_label.setStyleSheet(
            f"color: {token_to_css(self._tokens.text_soft)}; font-size: 8pt; font-weight: 600;"
        )
        
        value_label = QLabel(value, self)
        value_label.setStyleSheet(f"color: {token_to_css(self._tokens.text)}; font-size: 8pt;")
        value_label.setWordWrap(True)
        
        grid_layout = self.layout()
        grid_layout.addWidget(key_label, grid_row, col * 2)
        grid_layout.addWidget(value_label, grid_row, col * 2 + 1)
        
        self._row += 1


class PropertyListCard(PanelCard):
    """Card for displaying a list of properties."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        title: str = '',
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(tokens, parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(0)
        
        if title:
            header = QLabel(title, self)
            header.setStyleSheet(f"color: {token_to_css(tokens.text)}; font-size: 9pt; font-weight: 600;")
            layout.addWidget(header)
            layout.addSpacing(8)
        
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(6)
        layout.addLayout(self._content_layout)
        layout.addStretch(1)

    def add_property(self, key: str, value: str) -> None:
        """Add a property line."""
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)
        
        key_label = QLabel(key + ':', self)
        key_label.setMinimumWidth(100)
        key_label.setStyleSheet(f"color: {token_to_css(self._tokens.text_soft)}; font-size: 8pt;")
        
        value_label = QLabel(value, self)
        value_label.setStyleSheet(f"color: {token_to_css(self._tokens.text)}; font-size: 8pt;")
        value_label.setWordWrap(True)
        
        row_layout.addWidget(key_label)
        row_layout.addWidget(value_label, 1)
        
        self._content_layout.addLayout(row_layout)


class ResultListItemCard(PanelCard):
    """Card for a search result or list item."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        title: str,
        subtitle: str = '',
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(tokens, parent)
        self.setContentsMargins(12, 12, 12, 12)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self._title = QLabel(title, self)
        self._title.setObjectName('resultItemTitle')
        font = self._title.font()
        font.setPointSize(10)
        font.setWeight(QFont.SemiBold)
        self._title.setFont(font)
        self._title.setStyleSheet(f"color: {token_to_css(tokens.text)};")
        layout.addWidget(self._title)
        
        if subtitle:
            self._subtitle = QLabel(subtitle, self)
            self._subtitle.setObjectName('resultItemSubtitle')
            self._subtitle.setStyleSheet(f"color: {token_to_css(tokens.text_soft)}; font-size: 8pt;")
            layout.addWidget(self._subtitle)
        
        self._detail_layout = QHBoxLayout()
        self._detail_layout.setContentsMargins(0, 4, 0, 0)
        self._detail_layout.setSpacing(8)
        layout.addLayout(self._detail_layout)

    def add_detail(self, widget: QWidget) -> None:
        """Add a detail widget (pill, badge, etc)."""
        self._detail_layout.addWidget(widget)

    def add_detail_text(self, text: str, muted: bool = False) -> None:
        """Add detail text."""
        label = QLabel(text, self)
        color = self._tokens.text_soft if muted else self._tokens.text_muted
        label.setStyleSheet(f"color: {token_to_css(color)}; font-size: 8pt;")
        self.add_detail(label)


class PreviewSummaryCard(PanelCard):
    """Summary preview card for quick glance info."""
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(tokens, parent)
        self.setContentsMargins(12, 12, 12, 12)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        self._header_layout = QHBoxLayout()
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._header_layout)
        
        self._body_layout = QVBoxLayout()
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(4)
        layout.addLayout(self._body_layout)

    def set_header(self, title: str, icon_text: str = '') -> None:
        """Set the header title and optional icon/label."""
        for i in reversed(range(self._header_layout.count())):
            widget = self._header_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        title_label = QLabel(title, self)
        title_label.setStyleSheet(
            f"color: {token_to_css(self._tokens.text)}; font-weight: 600; font-size: 9pt;"
        )
        self._header_layout.addWidget(title_label)
        
        if icon_text:
            icon_label = QLabel(icon_text, self)
            icon_label.setStyleSheet(f"color: {token_to_css(self._tokens.accent)}; font-size: 8pt;")
            self._header_layout.addStretch(1)
            self._header_layout.addWidget(icon_label)

    def add_body_item(self, label: str, value: str) -> None:
        """Add item to body."""
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(8)
        
        label_widget = QLabel(label + ':', self)
        label_widget.setStyleSheet(f"color: {token_to_css(self._tokens.text_soft)}; font-size: 8pt;")
        label_widget.setMinimumWidth(60)
        
        value_widget = QLabel(value, self)
        value_widget.setStyleSheet(f"color: {token_to_css(self._tokens.text)}; font-size: 8pt;")
        
        item_layout.addWidget(label_widget)
        item_layout.addWidget(value_widget, 1)
        
        self._body_layout.addLayout(item_layout)


class StatusBanner(QFrame):
    """Status banner for messages and notifications."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        text: str,
        severity: Severity = Severity.NEUTRAL,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._severity = severity
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        label = QLabel(text, self)
        color = severity_color_css(tokens, severity.value)
        label.setStyleSheet(f"color: {color}; font-size: 9pt; font-weight: 500;")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        glow = severity_glow_css(tokens, severity.value)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {glow};
                border-left: 3px solid {color};
            }}
        """)


class InlineStatusBadge(QFrame):
    """Small inline status indicator dot."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        severity: Severity = Severity.NEUTRAL,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._severity = severity
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedSize(10, 10)
        
        color = severity_color_css(tokens, severity.value)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)


# ============================================================================
# PREMIUM TIER: Custom paint for special visual effects
# ============================================================================

class HeroPanel(QFrame):
    """
    Large hero panel for prominent featured content.
    
    Tier: PREMIUM
    Token access: Direct in paintEvent()
    Paint: YES - Diagonal gradient for visual impact
    Justification: Requires precise gradient control unavailable in stylesheets
    """
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setObjectName('heroPanel')
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(16, 20, 16, 20)
        self.setMinimumHeight(200)
        _set_visual_markers(self, role='hero-surface', tier='premium', premium=True)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        """Paint: Diagonal gradient from top-left to bottom-right."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = 20.0

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)

        # Diagonal gradient
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor(self._tokens.bg_elevated))
        gradient.setColorAt(1.0, QColor(self._tokens.panel_alt))
        painter.fillPath(path, gradient)

        # Border
        painter.setPen(QPen(QColor(self._tokens.border_strong), 1.5))
        painter.drawPath(path)

        super().paintEvent(event)


class LoadingPlaceholderSurface(PanelCard):
    """
    Loading placeholder surface with animated shimmer gradient.
    
    Tier: PREMIUM
    Token access: Direct in paintEvent()
    Paint: YES - Animated gradient sweep
    Justification: Requires precise frame-by-frame gradient animation
    
    Note: Uses QVariantAnimation + manual update() loop (correct pattern)
    NOT QPropertyAnimation on non-existent Qt property (broken)
    """
    
    def __init__(self, tokens: SkinTokens, height: int = 80, parent: QWidget | None = None) -> None:
        super().__init__(tokens, parent)
        self.setMinimumHeight(height)
        self._phase = 0.0
        _set_visual_markers(self, role='premium-surface', tier='premium', premium=True)
        
        # Correct: QVariantAnimation with manual update() on value change
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(1500)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setLoopCount(-1)
        self._anim.valueChanged.connect(self._on_phase_changed)
        self._anim.start()

    def _on_phase_changed(self, value: float) -> None:
        """Update phase and trigger paint."""
        self._phase = float(value)
        self.update()  # Trigger paintEvent

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        """Paint: Animated shimmer gradient sweep across surface."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = 16.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        
        # Shimmer gradient moves left-to-right
        gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        gradient.setColorAt(0.0, QColor(self._tokens.panel))
        gradient.setColorAt(self._phase, QColor(self._tokens.panel_hover))
        gradient.setColorAt(min(self._phase + 0.3, 1.0), QColor(self._tokens.panel))
        gradient.setColorAt(1.0, QColor(self._tokens.panel))
        
        painter.fillPath(path, gradient)
        painter.setPen(QPen(QColor(self._tokens.border), 1))
        painter.drawPath(path)


class EmptyState(PanelCard):
    """Full empty state card for prominent "nothing here" messaging."""
    
    def __init__(
        self,
        tokens: SkinTokens,
        title: str,
        message: str = '',
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(tokens, parent)
        self.setMinimumHeight(200)
        _set_visual_markers(self, role='summary-surface', tier='premium', premium=True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)
        layout.addStretch(1)
        
        title_label = QLabel(title, self)
        title_label.setObjectName('emptyStateTitle')
        font = title_label.font()
        font.setPointSize(12)
        font.setWeight(QFont.SemiBold)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {token_to_css(tokens.text)};")
        layout.addWidget(title_label)
        
        if message:
            msg_label = QLabel(message, self)
            msg_label.setObjectName('emptyStateMessage')
            msg_label.setAlignment(Qt.AlignCenter)
            msg_label.setWordWrap(True)
            msg_label.setStyleSheet(f"color: {token_to_css(tokens.text_soft)}; font-size: 9pt;")
            layout.addWidget(msg_label)
        
        layout.addStretch(1)


class SurfaceFrame(QFrame):
    """
    Minimal surface frame for grouped controls.
    
    Tier: PREMIUM (specialized styling)
    Token access: Direct in __init__
    Paint: Minimal - just fills color and border
    """
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setObjectName('surfaceFrame')
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(6, 6, 6, 6)
        _set_visual_markers(self, role='panel-surface', tier='premium', premium=True)
        self._apply_style()

    def _apply_style(self) -> None:
        bg = token_to_css(self._tokens.panel)
        border = token_to_css(self._tokens.border)
        self.setStyleSheet(f"""
            QFrame#surfaceFrame {{
                background-color: {bg};
                border: 0.5px solid {border};
                border-radius: 8px;
            }}
        """)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._apply_style()


class ToolbarSurface(QFrame):
    """Specialized surface for toolbar-like components."""
    
    def __init__(self, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self.setObjectName('toolbarSurface')
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(4, 4, 4, 4)
        _set_visual_markers(self, role='toolbar-surface', tier='themed', premium=False)
        self._apply_style()

    def _apply_style(self) -> None:
        bg = token_to_css(self._tokens.toolbar_bg)
        border = token_to_css(self._tokens.border_soft)
        self.setStyleSheet(f"""
            QFrame#toolbarSurface {{
                background-color: {bg};
                border-bottom: 1px solid {border};
            }}
        """)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._apply_style()


class AccentButton(QPushButton):
    """
    Emphasized accent button for primary actions.
    
    Tier: PREMIUM (animated color blend)
    Token access: Direct for color interpolation
    Paint: No; uses stylesheet + QVariantAnimation
    """
    
    def __init__(
        self,
        text: str,
        tokens: SkinTokens,
        parent: QWidget | None = None,
        *,
        strong: bool = False,
    ) -> None:
        super().__init__(text, parent)
        self._tokens = tokens
        self._strong = strong
        self._mix = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(130)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_value_changed)
        self._refresh_style()

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._refresh_style()

    def _on_value_changed(self, value) -> None:
        self._mix = float(value)
        self._refresh_style()

    def _refresh_style(self) -> None:
        if self._strong:
            start = self._tokens.accent_soft
            end = self._tokens.accent
            border = blend_colors(self._tokens.border_strong, self._tokens.accent, self._mix)
            text = self._tokens.text
        else:
            start = self._tokens.panel_alt
            end = self._tokens.panel_hover
            border = blend_colors(self._tokens.border, self._tokens.accent, self._mix * 0.45)
            text = self._tokens.text

        mixed = blend_colors(start, end, self._mix)
        hover = blend_colors(mixed, self._tokens.accent_hover, 0.18)
        
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {mixed};
                color: {token_to_css(text)};
                border: 1px solid {token_to_css(border)};
                border-top: 1px solid {token_to_css(self._tokens.bevel_light)};
                border-bottom: 1px solid {token_to_css(self._tokens.bevel_shadow)};
                border-radius: 9px;
                padding: 7px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {hover};
                border: 1px solid {token_to_css(blend_colors(border, self._tokens.accent_hover, 0.5))};
            }}
            QPushButton:pressed {{
                background-color: {token_to_css(self._tokens.panel_active)};
                color: {token_to_css(self._tokens.text)};
                border: 1px solid {token_to_css(self._tokens.accent_pressed)};
            }}
            QPushButton:disabled {{
                background-color: {token_to_css(self._tokens.panel)};
                border: 1px solid {token_to_css(self._tokens.border_soft)};
                color: {token_to_css(self._tokens.text_soft)};
            }}
            """
        )

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.72 if self._strong else 0.42)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)


class SecondaryButton(QPushButton):
    """Secondary button for standard actions."""
    
    def __init__(self, text: str, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._tokens = tokens
        self._mix = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._update_mix)
        self._refresh_style()

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._refresh_style()

    def _update_mix(self, value) -> None:
        self._mix = float(value)
        self._refresh_style()

    def _refresh_style(self) -> None:
        mixed = blend_colors(self._tokens.panel_alt, self._tokens.panel_hover, self._mix)
        border = blend_colors(self._tokens.border, self._tokens.border_strong, self._mix)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {mixed};
                color: {token_to_css(self._tokens.text)};
                border: 1px solid {token_to_css(border)};
                border-top: 1px solid {token_to_css(self._tokens.bevel_light)};
                border-bottom: 1px solid {token_to_css(self._tokens.bevel_shadow)};
                border-radius: 9px;
                padding: 7px 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border: 1px solid {token_to_css(self._tokens.border_strong)};
            }}
            QPushButton:pressed {{
                background-color: {token_to_css(self._tokens.panel_active)};
                border: 1px solid {token_to_css(self._tokens.border_strong)};
            }}
            """
        )

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)


class GhostButton(QPushButton):
    """Ghost button with minimal styling."""
    
    def __init__(self, text: str, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._tokens = tokens
        self._mix = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(110)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._update_mix)
        self._refresh_style()

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._refresh_style()

    def _update_mix(self, value) -> None:
        self._mix = float(value)
        self._refresh_style()

    def _refresh_style(self) -> None:
        bg = token_with_alpha(self._tokens.panel_hover, int(46 * self._mix))
        border = blend_colors(self._tokens.border_soft, self._tokens.border_strong, self._mix)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: {token_to_css(self._tokens.text_muted)};
                border: 1px solid {token_to_css(border)};
                border-radius: 8px;
                padding: 6px 11px;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                color: {token_to_css(self._tokens.text)};
            }}
            """
        )

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)


class QuietButton(QPushButton):
    """Quiet button for toolbar use."""
    
    def __init__(self, text: str, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._tokens = tokens
        self._mix = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(100)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._update_mix)
        self._refresh_style()

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._refresh_style()

    def _update_mix(self, value) -> None:
        self._mix = float(value)
        self._refresh_style()

    def _refresh_style(self) -> None:
        mixed_text = blend_colors(self._tokens.text_muted, self._tokens.accent, self._mix)
        bg = token_with_alpha(self._tokens.accent_soft, int(38 * self._mix))
        border = token_with_alpha(self._tokens.accent, int(48 * self._mix))
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: {mixed_text};
                border: 1px solid {border};
                border-radius: 7px;
                padding: 4px 9px;
                font-size: 9pt;
                font-weight: 500;
            }}
            """
        )

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)


# ============================================================================
# EFFECTS & HELPERS
# ============================================================================

class HoverRaiseFilter(QObject):
    """
    Event filter for safe hover-raise effect.
    
    FIXED: No longer modifies pos() directly on layout-managed widgets.
    Instead, uses a subtle shadow/opacity effect for visual feedback.
    This is layout-safe and future-proof.
    """
    
    def __init__(self, widget: QWidget, lift_px: float = 2.0) -> None:
        super().__init__(widget)
        self._widget = widget
        self._lift_px = lift_px
        self._shadow: QGraphicsDropShadowEffect | None
        self._base_blur = 0.0
        self._base_offset_y = 0.0
        self._base_color = QColor(0, 0, 0, 0)

        existing = widget.graphicsEffect()
        if isinstance(existing, QGraphicsDropShadowEffect):
            self._shadow = existing
            self._base_blur = float(existing.blurRadius())
            self._base_offset_y = float(existing.offset().y())
            self._base_color = QColor(existing.color())
        elif existing is None:
            self._shadow = QGraphicsDropShadowEffect(widget)
            self._shadow.setBlurRadius(0)
            self._shadow.setColor(QColor(0, 0, 0, 0))
            self._shadow.setOffset(0.0, 0.0)
            widget.setGraphicsEffect(self._shadow)
        else:
            self._shadow = None
        
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(130)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._apply_lift)
        widget.installEventFilter(self)

    def _apply_lift(self, value) -> None:
        """Apply shadow blur as visual lift."""
        if self._shadow is None:
            return
        strength = float(value) if value is not None else 0.0
        self._shadow.setBlurRadius(max(0.0, self._base_blur + strength * 3.2))
        self._shadow.setOffset(0.0, self._base_offset_y + strength * 0.6)
        lifted = QColor(self._base_color)
        if not lifted.isValid():
            lifted = QColor(0, 0, 0, 0)
        lifted.setAlpha(min(255, int(max(0, lifted.alpha()) + strength * 14)))
        self._shadow.setColor(lifted)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._widget:
            if event.type() == QEvent.Enter:
                self._anim.stop()
                self._anim.setStartValue(0.0)
                self._anim.setEndValue(self._lift_px)
                self._anim.start()
            elif event.type() == QEvent.Leave:
                self._anim.stop()
                if self._shadow is None:
                    return False
                current = max(0.0, (self._shadow.blurRadius() - self._base_blur) / 3.2)
                self._anim.setStartValue(current)
                self._anim.setEndValue(0.0)
                self._anim.start()
        return False


def install_hover_raise(widget: QWidget, lift_px: float = 2.0) -> HoverRaiseFilter:
    """Install a hover-raise effect on a widget (safe for layouts)."""
    filt = HoverRaiseFilter(widget, lift_px)
    widget._hover_raise_filter = filt  # type: ignore[attr-defined]
    return filt


# ============================================================================
# FACTORY HELPERS
# ============================================================================

def build_metric_row(
    tokens: SkinTokens,
    metrics: list[tuple[str, str, str]],
    parent: QWidget | None = None,
) -> MetricRow:
    """Build a metric row with multiple tiles."""
    return MetricRow(tokens, metrics, parent)


def build_section_header(
    tokens: SkinTokens,
    title: str,
    parent: QWidget | None = None,
) -> SectionHeader:
    """Build a section header."""
    return SectionHeader(tokens, title, parent)


def build_status_pill(
    tokens: SkinTokens,
    label: str,
    severity: Severity = Severity.NEUTRAL,
    parent: QWidget | None = None,
) -> StatusPill:
    """Build a status pill."""
    return StatusPill(tokens, label, severity, parent)


def build_empty_state(
    tokens: SkinTokens,
    title: str,
    message: str = '',
    parent: QWidget | None = None,
) -> EmptyState:
    """Build an empty state card."""
    return EmptyState(tokens, title, message, parent)
