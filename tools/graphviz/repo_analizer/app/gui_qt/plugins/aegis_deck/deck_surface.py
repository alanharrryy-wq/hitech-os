from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from .motion import DeckStateAnimator
from .theme_bridge import DeckThemeBridge

_ALLOWED_TONES = {"muted", "accent", "success", "warning", "danger"}
_ALLOWED_SURFACE_ROLES = {"panel", "hero", "toolbar", "code"}
_ALLOWED_BODY_STATES = {"ready", "empty", "loading", "error", "sparse"}
_STATE_COPY: dict[str, dict[str, str]] = {
    "empty": {
        "headline": "No deck content connected",
        "detail": "This surface is ready but no lane-owned widget has been attached yet.",
        "tone": "muted",
        "badge": "EMPTY VALID",
    },
    "loading": {
        "headline": "Preparing visual snapshot",
        "detail": "Use this when a sibling lane is normalizing or assembling data. Layout stays stable while the body resolves.",
        "tone": "accent",
        "badge": "LOADING",
    },
    "error": {
        "headline": "Surface degraded safely",
        "detail": "Render a precise local error summary here without widening shared contracts or mutating the host.",
        "tone": "danger",
        "badge": "DEGRADED",
    },
    "sparse": {
        "headline": "Sparse input, deliberate output",
        "detail": "Useful chrome and hierarchy remain intact even when sibling payloads only contain a subset of expected detail.",
        "tone": "warning",
        "badge": "SPARSE DATA",
    },
}


class AegisDeckSurface(QFrame):
    """Reusable premium surface with metadata, one content widget, and local body states."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "",
        subtitle: str = "",
        status_text: str = "",
        status_tone: str = "muted",
        theme_tokens: object | None = None,
        animation_enabled: bool = True,
        content_widget: QWidget | None = None,
        surface_role: str = "panel",
        body_state: str = "ready",
        state_headline: str = "",
        state_detail: str = "",
    ) -> None:
        super().__init__(parent)
        self._theme_bridge = DeckThemeBridge.coerce(theme_tokens)
        self._animator = DeckStateAnimator(self, animation_enabled=animation_enabled)
        self._content_widget: QWidget | None = None
        self._status_tone = "muted"
        self._surface_role = _coerce_role(surface_role)
        self._body_state = _coerce_body_state(body_state)
        self._state_headline_text = _coerce_text(state_headline)
        self._state_detail_text = _coerce_text(state_detail)
        self._state_badge_text = ""
        self._state_tone_override = ""
        self._hover_strength = 0.0
        self._focus_strength = 0.0
        self._pulse_strength = 0.0
        self._current_effective_state = "ready"
        self._current_state_tone = "muted"

        self.setObjectName("aegisDeckSurface")
        self.setProperty("visualRole", "panel-surface")
        self.setProperty("premium", True)
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._chrome = QFrame(self)
        self._chrome.setObjectName("aegisDeckSurfaceChrome")
        self._chrome.setFrameShape(QFrame.NoFrame)
        chrome_layout = QVBoxLayout(self._chrome)
        chrome_layout.setContentsMargins(1, 1, 1, 1)
        chrome_layout.setSpacing(0)
        root_layout.addWidget(self._chrome)

        self._accent_band = QFrame(self._chrome)
        self._accent_band.setObjectName("aegisDeckSurfaceAccentBand")
        self._accent_band.setFixedHeight(4)
        chrome_layout.addWidget(self._accent_band)

        self._header = QFrame(self._chrome)
        self._header.setObjectName("aegisDeckSurfaceHeader")
        self._header.setFrameShape(QFrame.NoFrame)
        self._header_layout = QVBoxLayout(self._header)
        self._header_layout.setContentsMargins(18, 16, 18, 12)
        self._header_layout.setSpacing(8)
        chrome_layout.addWidget(self._header)

        self._eyebrow_row = QHBoxLayout()
        self._eyebrow_row.setContentsMargins(0, 0, 0, 0)
        self._eyebrow_row.setSpacing(8)
        self._header_layout.addLayout(self._eyebrow_row)

        self._role_chip = QLabel(self._header)
        self._role_chip.setObjectName("aegisDeckSurfaceRoleChip")
        self._role_chip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._role_chip.setTextInteractionFlags(Qt.NoTextInteraction)
        self._eyebrow_row.addWidget(self._role_chip, 0, Qt.AlignLeft)
        self._eyebrow_row.addStretch(1)

        self._title_row = QHBoxLayout()
        self._title_row.setContentsMargins(0, 0, 0, 0)
        self._title_row.setSpacing(10)
        self._header_layout.addLayout(self._title_row)

        self._title_label = QLabel(self._header)
        self._title_label.setObjectName("aegisDeckSurfaceTitle")
        self._title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._title_label.setWordWrap(True)
        self._title_label.setTextInteractionFlags(Qt.NoTextInteraction)
        self._title_row.addWidget(self._title_label, 1)

        self._status_label = QLabel(self._header)
        self._status_label.setObjectName("aegisDeckSurfaceStatus")
        self._status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._status_label.setTextInteractionFlags(Qt.NoTextInteraction)
        self._title_row.addWidget(self._status_label, 0, Qt.AlignTop)

        self._subtitle_label = QLabel(self._header)
        self._subtitle_label.setObjectName("aegisDeckSurfaceSubtitle")
        self._subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setTextInteractionFlags(Qt.NoTextInteraction)
        self._header_layout.addWidget(self._subtitle_label)

        self._body = QFrame(self._chrome)
        self._body.setObjectName("aegisDeckSurfaceBody")
        self._body.setFrameShape(QFrame.NoFrame)
        self._body.setProperty("visualRole", "panel-surface")
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(18, 0, 18, 18)
        body_layout.setSpacing(0)
        chrome_layout.addWidget(self._body, 1)

        self._body_stack_host = QFrame(self._body)
        self._body_stack_host.setObjectName("aegisDeckSurfaceBodyStackHost")
        self._body_stack_host.setFrameShape(QFrame.NoFrame)
        self._body_stack = QStackedLayout(self._body_stack_host)
        self._body_stack.setContentsMargins(0, 0, 0, 0)
        self._body_stack.setStackingMode(QStackedLayout.StackOne)
        body_layout.addWidget(self._body_stack_host, 1)

        self._content_page = QFrame(self._body_stack_host)
        self._content_page.setObjectName("aegisDeckSurfaceContentPage")
        self._content_page.setFrameShape(QFrame.NoFrame)
        self._content_layout = QVBoxLayout(self._content_page)
        self._content_layout.setContentsMargins(12, 12, 12, 12)
        self._content_layout.setSpacing(0)
        self._body_stack.addWidget(self._content_page)

        self._state_page = QFrame(self._body_stack_host)
        self._state_page.setObjectName("aegisDeckSurfaceStatePage")
        self._state_page.setFrameShape(QFrame.NoFrame)
        self._state_layout = QVBoxLayout(self._state_page)
        self._state_layout.setContentsMargins(14, 14, 14, 10)
        self._state_layout.setSpacing(8)
        self._state_layout.addStretch(1)

        self._state_badge = QLabel(self._state_page)
        self._state_badge.setObjectName("aegisDeckSurfaceStateBadge")
        self._state_badge.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._state_badge.setTextInteractionFlags(Qt.NoTextInteraction)
        self._state_layout.addWidget(self._state_badge, 0, Qt.AlignLeft)

        self._state_headline = QLabel(self._state_page)
        self._state_headline.setObjectName("aegisDeckSurfaceStateHeadline")
        self._state_headline.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._state_headline.setWordWrap(True)
        self._state_headline.setTextInteractionFlags(Qt.NoTextInteraction)
        self._state_layout.addWidget(self._state_headline)

        self._state_detail = QLabel(self._state_page)
        self._state_detail.setObjectName("aegisDeckSurfaceStateDetail")
        self._state_detail.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._state_detail.setWordWrap(True)
        self._state_detail.setTextInteractionFlags(Qt.NoTextInteraction)
        self._state_layout.addWidget(self._state_detail)
        self._state_layout.addStretch(2)
        self._body_stack.addWidget(self._state_page)

        self.set_title(title)
        self.set_subtitle(subtitle)
        self.set_status_tone(status_tone)
        self.set_status_text(status_text)
        self.set_surface_role(surface_role)
        if content_widget is not None:
            self.set_content_widget(content_widget)
        self.set_body_state(body_state, headline=state_headline, detail=state_detail)
        self.refresh_style()

    def theme_bridge(self) -> DeckThemeBridge:
        return self._theme_bridge

    def set_theme_tokens(self, tokens: object | None) -> None:
        self._theme_bridge = DeckThemeBridge.coerce(tokens)
        self.refresh_style()

    def set_skin(self, tokens: object | None) -> None:
        self.set_theme_tokens(tokens)

    def set_animation_enabled(self, enabled: bool) -> None:
        self._animator.set_animation_enabled(enabled)

    def animation_enabled(self) -> bool:
        return self._animator.animation_enabled()

    def surface_role(self) -> str:
        return self._surface_role

    def set_surface_role(self, role: str) -> None:
        next_role = _coerce_role(role)
        if next_role == self._surface_role:
            self._role_chip.setText(_role_chip_text(next_role))
            return
        self._surface_role = next_role
        self._role_chip.setText(_role_chip_text(next_role))
        self.refresh_style()

    def title(self) -> str:
        return self._title_label.text()

    def set_title(self, text: object) -> None:
        value = _coerce_text(text)
        self._title_label.setText(value)
        self._title_label.setVisible(bool(value))
        self._sync_header_visibility()

    def subtitle(self) -> str:
        return self._subtitle_label.text()

    def set_subtitle(self, text: object) -> None:
        value = _coerce_text(text)
        self._subtitle_label.setText(value)
        self._subtitle_label.setVisible(bool(value))
        self._sync_header_visibility()

    def status_text(self) -> str:
        return self._status_label.text()

    def set_status_text(self, text: object) -> None:
        previous = self._status_label.text()
        value = _coerce_text(text)
        self._status_label.setText(value)
        self._status_label.setVisible(bool(value))
        self._sync_header_visibility()
        if value != previous and value:
            self._pulse_surface(peak=0.9, duration_ms=420)
        self.refresh_style()

    def status_tone(self) -> str:
        return self._status_tone

    def set_status_tone(self, tone: object) -> None:
        next_tone = _coerce_tone(tone)
        if next_tone == self._status_tone:
            return
        self._status_tone = next_tone
        self.refresh_style()
        self._pulse_surface(peak=0.85, duration_ms=380)

    def body_state(self) -> str:
        return self._body_state

    def set_body_state(
        self,
        state: object,
        *,
        headline: object | None = None,
        detail: object | None = None,
        tone: object | None = None,
        badge: object | None = None,
    ) -> None:
        next_state = _coerce_body_state(state)
        state_changed = next_state != self._body_state
        self._body_state = next_state
        if state_changed:
            self._state_headline_text = ""
            self._state_detail_text = ""
            self._state_badge_text = ""
            self._state_tone_override = ""
        if headline is not None:
            self._state_headline_text = _coerce_text(headline)
        if detail is not None:
            self._state_detail_text = _coerce_text(detail)
        if badge is not None:
            self._state_badge_text = _coerce_text(badge)
        if tone is not None:
            self._state_tone_override = _coerce_tone(tone)
        self._sync_body_mode()
        self.refresh_style()
        if next_state != "ready":
            self._pulse_surface(peak=1.0, duration_ms=440)

    def content_widget(self) -> QWidget | None:
        return self._content_widget

    def set_content_widget(self, widget: QWidget | None) -> QWidget | None:
        previous = self._content_widget
        if previous is widget:
            return previous
        if previous is not None:
            self._content_layout.removeWidget(previous)
            previous.setParent(None)
        self._content_widget = widget
        if widget is not None:
            widget.setParent(self._content_page)
            widget.setProperty("visualRole", widget.property("visualRole") or "panel-surface")
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._content_layout.addWidget(widget)
            self._animator.fade_widget(widget, start=0.18, end=1.0, duration_ms=150)
        self._sync_body_mode()
        self.refresh_style()
        return previous

    def clear_content_widget(self) -> QWidget | None:
        return self.set_content_widget(None)

    def refresh_style(self) -> None:
        palette = self._theme_bridge.role_palette(self._surface_role)
        status_palette = self._theme_bridge.status_palette(self._status_tone)
        state_tone = self._current_state_tone if self._current_effective_state != "ready" else self._status_tone
        state_palette = self._theme_bridge.status_palette(state_tone)

        emphasis = max(self._hover_strength, self._focus_strength * 1.12, self._pulse_strength * 0.9)
        surface_fill = _mix_css(palette["surface"], palette["accent"], 0.04 + (0.08 * emphasis))
        chrome_fill = _mix_css(palette["surface_alt"], palette["accent"], 0.10 + (0.10 * emphasis))
        border_color = _mix_css(palette["border"], palette["accent"], 0.16 + (0.24 * max(self._focus_strength, self._pulse_strength)))
        header_top = _mix_css(chrome_fill, palette["bevel_light"], 0.26)
        header_bottom = _mix_css(surface_fill, palette["accent_soft"], 0.24)
        content_fill = _mix_css(surface_fill, self._theme_bridge.token("bg_elevated", palette["surface"]), 0.18)
        accent_band_left = _mix_css(palette["accent"], state_palette["ink"], 0.22)
        accent_band_right = _mix_css(palette["accent_hover"], palette["text"], 0.16)
        role_chip_bg = _mix_css(palette["accent_soft"], palette["surface_alt"], 0.32)
        role_chip_border = _mix_css(palette["divider"], palette["accent"], 0.28)
        role_chip_text = _mix_css(palette["soft_text"], palette["text"], 0.42)
        status_bg = _mix_css(status_palette["soft"], palette["surface_alt"], 0.16)
        status_border = _mix_css(status_palette["line"], palette["accent"], 0.14)
        state_badge_bg = _mix_css(state_palette["soft"], palette["surface_alt"], 0.08)
        state_panel_bg = _mix_css(content_fill, state_palette["soft"], 0.22 if self._current_effective_state != "ready" else 0.0)
        state_border = _mix_css(palette["divider"], state_palette["ink"], 0.24)
        title_color = _mix_css(palette["text"], palette["accent_hover"], 0.07 + (0.08 * emphasis))
        subtitle_color = _mix_css(palette["muted"], palette["text"], 0.10 + (0.08 * self._hover_strength))
        empty_text = _mix_css(palette["soft_text"], palette["text"], 0.22)
        focus_ring = _mix_css(palette["focus_ring"], palette["accent"], 0.12)
        shadow_glow = self._theme_bridge.css_color("accent", alpha=int(44 + (40 * emphasis)))
        header_hairline = self._theme_bridge.css_color("bevel_light", alpha=int(58 + (26 * emphasis)))

        self.setStyleSheet(
            """
            QFrame#aegisDeckSurface {
                background: transparent;
                border: none;
            }
            QFrame#aegisDeckSurfaceChrome {
                background: %(surface_fill)s;
                border: 1px solid %(border_color)s;
                border-radius: 18px;
            }
            QFrame#aegisDeckSurfaceAccentBand {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 %(accent_band_left)s,
                    stop: 0.52 %(accent_band_right)s,
                    stop: 1 %(shadow_glow)s
                );
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
                border: none;
            }
            QFrame#aegisDeckSurfaceHeader {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0.92, y2: 1,
                    stop: 0 %(header_top)s,
                    stop: 0.55 %(chrome_fill)s,
                    stop: 1 %(header_bottom)s
                );
                border: none;
                border-bottom: 1px solid %(state_border)s;
            }
            QLabel#aegisDeckSurfaceRoleChip {
                color: %(role_chip_text)s;
                background: %(role_chip_bg)s;
                border: 1px solid %(role_chip_border)s;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.8px;
                padding: 4px 9px;
                text-transform: uppercase;
            }
            QLabel#aegisDeckSurfaceTitle {
                color: %(title_color)s;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
            QLabel#aegisDeckSurfaceSubtitle {
                color: %(subtitle_color)s;
                font-size: 12px;
                line-height: 1.35em;
                background: transparent;
                border: none;
                padding-top: 1px;
            }
            QLabel#aegisDeckSurfaceStatus {
                color: %(status_ink)s;
                background: %(status_bg)s;
                border: 1px solid %(status_border)s;
                border-radius: 11px;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.7px;
                padding: 5px 10px;
                min-height: 14px;
            }
            QFrame#aegisDeckSurfaceBody {
                background: transparent;
                border: none;
                border-bottom-left-radius: 18px;
                border-bottom-right-radius: 18px;
            }
            QFrame#aegisDeckSurfaceContentPage,
            QFrame#aegisDeckSurfaceStatePage {
                background: %(content_fill)s;
                border: 1px solid %(header_hairline)s;
                border-radius: 14px;
            }
            QFrame#aegisDeckSurfaceStatePage {
                background: %(state_panel_bg)s;
                border-color: %(state_border)s;
            }
            QLabel#aegisDeckSurfaceStateBadge {
                color: %(state_ink)s;
                background: %(state_badge_bg)s;
                border: 1px solid %(state_border)s;
                border-radius: 11px;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.8px;
                padding: 5px 10px;
                min-height: 14px;
            }
            QLabel#aegisDeckSurfaceStateHeadline {
                color: %(title_color)s;
                background: transparent;
                border: none;
                font-size: 15px;
                font-weight: 700;
                padding-top: 2px;
            }
            QLabel#aegisDeckSurfaceStateDetail {
                color: %(empty_text)s;
                background: transparent;
                border: none;
                font-size: 12px;
                line-height: 1.45em;
                padding-bottom: 2px;
            }
            AegisDeckSurface:focus {
                outline: none;
            }
            AegisDeckSurface[enabled="false"] QFrame#aegisDeckSurfaceChrome {
                border-color: %(disabled_border)s;
                background: %(disabled_surface)s;
            }
            AegisDeckSurface[enabled="false"] QLabel {
                color: %(disabled_text)s;
            }
            """
            % {
                "surface_fill": surface_fill,
                "border_color": border_color,
                "accent_band_left": accent_band_left,
                "accent_band_right": accent_band_right,
                "shadow_glow": shadow_glow,
                "header_top": header_top,
                "chrome_fill": chrome_fill,
                "header_bottom": header_bottom,
                "role_chip_text": role_chip_text,
                "role_chip_bg": role_chip_bg,
                "role_chip_border": role_chip_border,
                "title_color": title_color,
                "subtitle_color": subtitle_color,
                "status_ink": status_palette["ink"],
                "status_bg": status_bg,
                "status_border": status_border,
                "content_fill": content_fill,
                "header_hairline": header_hairline,
                "state_panel_bg": state_panel_bg,
                "state_border": state_border,
                "state_ink": state_palette["ink"],
                "state_badge_bg": state_badge_bg,
                "empty_text": empty_text,
                "disabled_border": self._theme_bridge.css_color("border", alpha=92),
                "disabled_surface": self._theme_bridge.css_color("panel", alpha=168),
                "disabled_text": self._theme_bridge.css_color("text_muted", alpha=150),
                "focus_ring": focus_ring,
            }
        )
        self.setProperty("bodyState", self._current_effective_state)
        self.setProperty("surfaceRole", self._surface_role)
        self.setProperty("statusTone", self._status_tone)
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
        self.update()

    def enterEvent(self, event: Any) -> None:
        super().enterEvent(event)
        self._animate_hover(1.0)

    def leaveEvent(self, event: Any) -> None:
        super().leaveEvent(event)
        self._animate_hover(0.0)

    def focusInEvent(self, event: Any) -> None:
        super().focusInEvent(event)
        self._animate_focus(1.0)

    def focusOutEvent(self, event: Any) -> None:
        super().focusOutEvent(event)
        self._animate_focus(0.0)

    def _animate_hover(self, end_value: float) -> None:
        start_value = self._hover_strength
        if not self._animator.animate_scalar(
            "surface:hover",
            start=start_value,
            end=end_value,
            duration_ms=150,
            easing=QEasingCurve.OutCubic,
            on_value=self._set_hover_strength,
        ):
            self._set_hover_strength(end_value)

    def _animate_focus(self, end_value: float) -> None:
        start_value = self._focus_strength
        if not self._animator.animate_scalar(
            "surface:focus",
            start=start_value,
            end=end_value,
            duration_ms=170,
            easing=QEasingCurve.OutCubic,
            on_value=self._set_focus_strength,
        ):
            self._set_focus_strength(end_value)

    def _pulse_surface(self, *, peak: float = 1.0, duration_ms: int = 420) -> None:
        if not self._animator.pulse_scalar(
            "surface:pulse",
            base=0.0,
            peak=peak,
            duration_ms=duration_ms,
            on_value=self._set_pulse_strength,
        ):
            self._set_pulse_strength(0.0)

    def _set_hover_strength(self, value: float) -> None:
        self._hover_strength = _clamp_scalar(value)
        self.refresh_style()

    def _set_focus_strength(self, value: float) -> None:
        self._focus_strength = _clamp_scalar(value)
        self.refresh_style()

    def _set_pulse_strength(self, value: float) -> None:
        self._pulse_strength = _clamp_scalar(value)
        self.refresh_style()

    def _sync_header_visibility(self) -> None:
        header_visible = any(
            label.isVisible()
            for label in (self._role_chip, self._title_label, self._subtitle_label, self._status_label)
        )
        self._header.setVisible(header_visible)

    def _sync_body_mode(self) -> None:
        effective_state = self._body_state
        if effective_state == "ready" and self._content_widget is None:
            effective_state = "empty"
        self._current_effective_state = effective_state
        if effective_state == "ready":
            next_index = self._body_stack.indexOf(self._content_page)
        else:
            next_index = self._body_stack.indexOf(self._state_page)
            state_copy = dict(_STATE_COPY.get(effective_state, _STATE_COPY["empty"]))
            headline = self._state_headline_text or state_copy["headline"]
            detail = self._state_detail_text or state_copy["detail"]
            badge = self._state_badge_text or state_copy["badge"]
            tone = _coerce_tone(self._state_tone_override or state_copy["tone"])
            self._current_state_tone = tone
            self._state_badge.setText(badge)
            self._state_headline.setText(headline)
            self._state_detail.setText(detail)
        current_index = self._body_stack.currentIndex()
        if current_index != next_index:
            self._body_stack.setCurrentIndex(next_index)
            page = self._body_stack.currentWidget()
            if isinstance(page, QWidget):
                self._animator.fade_widget(page, key=f"body-page:{id(page)}", start=0.28, end=1.0, duration_ms=160)
        if effective_state == "ready":
            self._current_state_tone = self._status_tone



def _coerce_text(value: object) -> str:
    if value is None:
        return ""
    try:
        return str(value).strip()
    except Exception:
        return ""



def _coerce_tone(value: object) -> str:
    tone = _coerce_text(value).lower()
    return tone if tone in _ALLOWED_TONES else "muted"



def _coerce_role(value: object) -> str:
    role = _coerce_text(value).lower()
    return role if role in _ALLOWED_SURFACE_ROLES else "panel"



def _coerce_body_state(value: object) -> str:
    state = _coerce_text(value).lower()
    return state if state in _ALLOWED_BODY_STATES else "ready"



def _clamp_scalar(value: object, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = minimum
    return max(minimum, min(maximum, numeric))



def _mix_css(left: object, right: object, ratio: float) -> str:
    ratio = _clamp_scalar(ratio)
    left_color = QColor(_coerce_text(left))
    right_color = QColor(_coerce_text(right))
    if not left_color.isValid():
        left_color = QColor("#1d2531")
    if not right_color.isValid():
        right_color = QColor("#d9a168")
    inverse = 1.0 - ratio
    mixed = QColor(
        int(round(left_color.red() * inverse + right_color.red() * ratio)),
        int(round(left_color.green() * inverse + right_color.green() * ratio)),
        int(round(left_color.blue() * inverse + right_color.blue() * ratio)),
        int(round(left_color.alpha() * inverse + right_color.alpha() * ratio)),
    )
    return mixed.name(QColor.HexArgb) if mixed.alpha() < 255 else mixed.name(QColor.HexRgb)



def _role_chip_text(role: str) -> str:
    labels = {
        "panel": "FOUNDATION SURFACE",
        "hero": "HERO SURFACE",
        "toolbar": "TOOLBAR SURFACE",
        "code": "CODE SURFACE",
    }
    return labels.get(role, "FOUNDATION SURFACE")


__all__ = ["AegisDeckSurface"]
