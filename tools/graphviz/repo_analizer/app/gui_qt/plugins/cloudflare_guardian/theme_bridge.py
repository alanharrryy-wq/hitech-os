from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from typing import Any

from PySide6.QtGui import QColor

_DEFAULT_TOKENS: dict[str, str] = {
    "name": "cloudflare_guardian_default",
    "display_name": "CloudflareGuardian Default",
    "bg": "#0f1318",
    "bg_alt": "#141a22",
    "bg_elevated": "#1a212c",
    "panel": "#1d2531",
    "panel_alt": "#232d3a",
    "panel_hover": "#2b3747",
    "panel_active": "#314258",
    "text": "#edf2f8",
    "text_muted": "#9aa8bc",
    "text_soft": "#7c8a9e",
    "accent": "#d9a168",
    "accent_hover": "#e4b582",
    "accent_pressed": "#c8925a",
    "accent_soft": "#36281a",
    "accent_glow": "#d9a1682c",
    "success": "#5fc794",
    "warning": "#d8b36d",
    "danger": "#d58086",
    "border": "#2d3848",
    "border_soft": "#263140",
    "border_strong": "#3f5067",
    "bevel_light": "#ffffff12",
    "bevel_shadow": "#00000073",
    "shadow": "#0000009f",
    "selection": "#2f4058",
    "focus_ring": "#d9a1686b",
    "toolbar_bg": "#111821",
    "dock_title_bg": "#151f2b",
    "menu_bg": "#151e28",
    "scrollbar": "#4f5d70",
    "scrollbar_hover": "#d9a168",
    "splitter": "#2f3c4e",
    "code_bg": "#0b1118",
    "code_text": "#e8eef6",
    "code_line": "#15202d",
}

_SUPPORTED_KEYS: tuple[str, ...] = tuple(_DEFAULT_TOKENS.keys())
_ROLE_FALLBACKS: dict[str, str] = {
    "panel": "panel",
    "hero": "hero",
    "toolbar": "toolbar",
    "code": "code",
}
_STATUS_FALLBACKS: dict[str, str] = {
    "muted": "text_muted",
    "accent": "accent",
    "success": "success",
    "warning": "warning",
    "danger": "danger",
}


def _coerce_text(value: object) -> str:
    if value is None:
        return ""
    try:
        return str(value).strip()
    except Exception:
        return ""



def _coerce_qcolor(value: object) -> QColor:
    if isinstance(value, QColor):
        return QColor(value)
    text = _coerce_text(value)
    color = QColor(text)
    if color.isValid():
        return color
    return QColor()



def _css_hex(color: QColor) -> str:
    if not color.isValid():
        return ""
    return color.name(QColor.HexArgb) if color.alpha() < 255 else color.name(QColor.HexRgb)



def _color_to_css(value: object) -> str:
    color = _coerce_qcolor(value)
    return _css_hex(color)



def _iter_attr_source(tokens: object):
    for key in _SUPPORTED_KEYS:
        if hasattr(tokens, key):
            try:
                yield key, getattr(tokens, key)
            except Exception:
                continue



def _mapping_from_tokens(tokens: object | None) -> dict[str, object]:
    if tokens is None:
        return {}
    if isinstance(tokens, DeckThemeBridge):
        return tokens.tokens()
    if isinstance(tokens, Mapping):
        return dict(tokens)
    if is_dataclass(tokens):
        result: dict[str, object] = {}
        for field in fields(tokens):
            if field.name in _SUPPORTED_KEYS:
                try:
                    result[field.name] = getattr(tokens, field.name)
                except Exception:
                    continue
        return result
    return dict(_iter_attr_source(tokens))



def _normalize_tokens(tokens: object | None, overrides: Mapping[str, object] | None = None) -> dict[str, str]:
    normalized = dict(_DEFAULT_TOKENS)
    for source in (_mapping_from_tokens(tokens), dict(overrides or {})):
        for key, value in source.items():
            if key not in normalized:
                continue
            if key in {"name", "display_name"}:
                text = _coerce_text(value)
                if text:
                    normalized[key] = text
                continue
            css = _color_to_css(value)
            if css:
                normalized[key] = css
    return normalized



def _clamp_alpha(alpha: float | int | None) -> int | None:
    if alpha is None:
        return None
    if isinstance(alpha, float):
        return max(0, min(255, int(round(alpha * 255))))
    try:
        return max(0, min(255, int(alpha)))
    except Exception:
        return None



def _rgba_css(color_text: str, alpha: float | int | None = None) -> str:
    color = QColor(color_text)
    if not color.isValid():
        color = QColor(_DEFAULT_TOKENS["panel"])
    alpha_value = _clamp_alpha(alpha)
    if alpha_value is not None:
        color.setAlpha(alpha_value)
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"



def _mix_colors(base: object, overlay: object, ratio: float) -> str:
    ratio = max(0.0, min(1.0, float(ratio)))
    left = _coerce_qcolor(base)
    right = _coerce_qcolor(overlay)
    if not left.isValid():
        left = QColor(_DEFAULT_TOKENS["panel"])
    if not right.isValid():
        right = QColor(_DEFAULT_TOKENS["accent"])
    inverse = 1.0 - ratio
    mixed = QColor(
        int(round(left.red() * inverse + right.red() * ratio)),
        int(round(left.green() * inverse + right.green() * ratio)),
        int(round(left.blue() * inverse + right.blue() * ratio)),
        int(round(left.alpha() * inverse + right.alpha() * ratio)),
    )
    return _css_hex(mixed)


class DeckThemeBridge:
    """Normalizes sparse skin tokens into CSS-safe, read-only theme access.

    Accepted sources:
    - None
    - mapping-like objects with canonical SkinTokens keys
    - SkinTokens-like objects exposing canonical attributes
    - dataclass instances with canonical SkinTokens field names
    - another DeckThemeBridge
    """

    SUPPORTED_KEYS: tuple[str, ...] = _SUPPORTED_KEYS

    def __init__(self, tokens: object | None = None, /, **overrides: object) -> None:
        self._tokens = _normalize_tokens(tokens, overrides)

    @classmethod
    def coerce(cls, tokens: object | None = None, /, **overrides: object) -> "DeckThemeBridge":
        if isinstance(tokens, cls) and not overrides:
            return tokens
        return cls(tokens, **overrides)

    def with_tokens(self, tokens: object | None = None, /, **overrides: object) -> "DeckThemeBridge":
        source = self.tokens()
        if tokens is not None:
            source.update(_mapping_from_tokens(tokens))
        if overrides:
            source.update(dict(overrides))
        return DeckThemeBridge(source)

    def tokens(self) -> dict[str, str]:
        return dict(self._tokens)

    def token(self, name: str, fallback: object | None = None) -> str:
        key = _coerce_text(name)
        value = self._tokens.get(key)
        if value:
            return value
        if fallback is None:
            return ""
        css = _color_to_css(fallback)
        return css or _coerce_text(fallback)

    def css_color(
        self,
        name: str,
        fallback: object | None = None,
        *,
        alpha: float | int | None = None,
    ) -> str:
        base = self.token(name, fallback if fallback is not None else _DEFAULT_TOKENS.get(name, ""))
        return _rgba_css(base, alpha)

    def color(self, name: str, fallback: object | None = None) -> QColor:
        base = self.token(name, fallback if fallback is not None else _DEFAULT_TOKENS.get(name, ""))
        color = QColor(base)
        if color.isValid():
            return color
        return QColor(_DEFAULT_TOKENS["panel"])

    def accent_mix(self, name: str, ratio: float = 0.5, fallback: object | None = None) -> str:
        base = self.token(name, fallback if fallback is not None else _DEFAULT_TOKENS.get(name, _DEFAULT_TOKENS["panel"]))
        return _mix_colors(base, self.token("accent", _DEFAULT_TOKENS["accent"]), ratio)

    def status_palette(self, tone: str = "muted") -> dict[str, str]:
        tone_key = _coerce_text(tone).lower()
        status_name = _STATUS_FALLBACKS.get(tone_key, _STATUS_FALLBACKS["muted"])
        ink = self.token(status_name, _DEFAULT_TOKENS[status_name])
        return {
            "tone": tone_key if tone_key in _STATUS_FALLBACKS else "muted",
            "ink": ink,
            "soft": _mix_colors(self.token("panel", _DEFAULT_TOKENS["panel"]), ink, 0.18),
            "glow": _rgba_css(ink, 74),
            "line": _mix_colors(self.token("border", _DEFAULT_TOKENS["border"]), ink, 0.52),
        }

    def role_palette(self, role: str = "panel") -> dict[str, str]:
        role_key = _coerce_text(role).lower()
        if role_key not in _ROLE_FALLBACKS:
            role_key = "panel"

        if role_key == "toolbar":
            surface = self.token("toolbar_bg", _DEFAULT_TOKENS["toolbar_bg"])
            surface_alt = self.token("panel", _DEFAULT_TOKENS["panel"])
            border = self.token("border", _DEFAULT_TOKENS["border"])
        elif role_key == "code":
            surface = self.token("code_bg", _DEFAULT_TOKENS["code_bg"])
            surface_alt = self.token("code_line", _DEFAULT_TOKENS["code_line"])
            border = self.token("border", _DEFAULT_TOKENS["border"])
        elif role_key == "hero":
            surface = self.token("bg_elevated", _DEFAULT_TOKENS["bg_elevated"])
            surface_alt = self.token("panel", _DEFAULT_TOKENS["panel"])
            border = self.token("border_strong", _DEFAULT_TOKENS["border_strong"])
        else:
            surface = self.token("panel", _DEFAULT_TOKENS["panel"])
            surface_alt = self.token("panel_alt", _DEFAULT_TOKENS["panel_alt"])
            border = self.token("border", _DEFAULT_TOKENS["border"])

        accent = self.token("accent", _DEFAULT_TOKENS["accent"])
        accent_soft = self.token("accent_soft", _DEFAULT_TOKENS["accent_soft"])
        text = self.token("text", _DEFAULT_TOKENS["text"])
        muted = self.token("text_muted", _DEFAULT_TOKENS["text_muted"])
        surface_hover = _mix_colors(surface_alt, accent, 0.14)
        surface_active = _mix_colors(surface_alt, accent, 0.22)
        divider = _mix_colors(border, accent, 0.18)
        hairline = _rgba_css(border, 196)
        glow = self.css_color("accent", alpha=82)
        focus_ring = self.token("focus_ring", _DEFAULT_TOKENS["focus_ring"])

        return {
            "role": role_key,
            "surface": surface,
            "surface_alt": surface_alt,
            "surface_hover": surface_hover,
            "surface_active": surface_active,
            "border": border,
            "divider": divider,
            "hairline": hairline,
            "text": text,
            "muted": muted,
            "soft_text": self.token("text_soft", _DEFAULT_TOKENS["text_soft"]),
            "accent": accent,
            "accent_hover": self.token("accent_hover", _DEFAULT_TOKENS["accent_hover"]),
            "accent_pressed": self.token("accent_pressed", _DEFAULT_TOKENS["accent_pressed"]),
            "accent_soft": accent_soft,
            "accent_glow": glow,
            "focus_ring": focus_ring,
            "shadow": self.token("shadow", _DEFAULT_TOKENS["shadow"]),
            "selection": self.token("selection", _DEFAULT_TOKENS["selection"]),
            "bevel_light": self.token("bevel_light", _DEFAULT_TOKENS["bevel_light"]),
            "bevel_shadow": self.token("bevel_shadow", _DEFAULT_TOKENS["bevel_shadow"]),
            "header_sheen": _rgba_css(self.accent_mix("bg_elevated", 0.52), 46),
            "panel_glow": _rgba_css(self.accent_mix("panel_alt", 0.34), 54),
        }


__all__ = ["DeckThemeBridge"]


