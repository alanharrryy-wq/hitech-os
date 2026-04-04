from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping, Optional

from PySide6.QtCore import QEvent, QObject, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QAbstractButton, QLabel, QWidget

from .contracts import DEFAULT_THEME_ID
from .theme import get_palette


DEFAULT_ICON_SIZE_TOKENS: dict[str, int] = {
    "micro": 12,
    "small": 14,
    "body": 16,
    "large": 20,
    "xlarge": 24,
}


@dataclass(frozen=True, slots=True)
class GlassIconPack:
    name: str
    root: Path
    default_size_token: str = "body"
    aliases: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GlassResolvedIcon:
    pack: str
    icon_name: str
    path: Path | None


class GlassIconRegistry:
    """Registry with icon-pack registration, metadata, aliases and size tokens."""

    def __init__(self) -> None:
        self._packs: Dict[str, GlassIconPack] = {}
        self._icon_cache: Dict[str, QIcon] = {}
        self._default_pack: str = "default"
        self._size_tokens: Dict[str, int] = dict(DEFAULT_ICON_SIZE_TOKENS)

    @property
    def default_pack(self) -> str:
        return self._default_pack

    @property
    def size_tokens(self) -> dict[str, int]:
        return dict(self._size_tokens)

    def register_pack(
        self,
        name: str,
        root: str | Path,
        *,
        default_size_token: str = "body",
        aliases: Mapping[str, str] | None = None,
        metadata: Mapping[str, str] | None = None,
        override: bool = True,
    ) -> None:
        normalized = str(name or "").strip().lower()
        if not normalized:
            raise ValueError("icon pack name is required")
        if not override and normalized in self._packs:
            raise ValueError(f"icon pack '{normalized}' already exists")
        pack = GlassIconPack(
            name=normalized,
            root=Path(root).resolve(),
            default_size_token=str(default_size_token or "body"),
            aliases={str(k).strip().lower(): str(v).strip() for k, v in (aliases or {}).items()},
            metadata={str(k): str(v) for k, v in (metadata or {}).items()},
        )
        self._packs[normalized] = pack

    def register_size_token(self, token: str, size: int, *, override: bool = True) -> None:
        normalized = str(token or "").strip().lower()
        if not normalized:
            raise ValueError("size token is required")
        if not override and normalized in self._size_tokens:
            raise ValueError(f"size token '{normalized}' already exists")
        self._size_tokens[normalized] = max(8, int(size))

    def set_default_pack(self, name: str) -> None:
        normalized = str(name or "").strip().lower()
        if not normalized:
            raise ValueError("default icon pack is required")
        self._default_pack = normalized

    def list_packs(self) -> tuple[str, ...]:
        return tuple(sorted(self._packs.keys()))

    def get_pack(self, name: str | None = None) -> GlassIconPack | None:
        key = str(name or self._default_pack or "").strip().lower()
        if not key:
            return None
        return self._packs.get(key)

    def resolve_icon(
        self,
        icon_name: str,
        *,
        pack: str | None = None,
    ) -> GlassResolvedIcon:
        raw_name = str(icon_name or "").strip()
        if not raw_name:
            return GlassResolvedIcon(pack=str(pack or self._default_pack), icon_name="", path=None)

        icon_pack = self.get_pack(pack)
        if icon_pack is None or not icon_pack.root.exists():
            return GlassResolvedIcon(pack=str(pack or self._default_pack), icon_name=raw_name, path=None)

        normalized = raw_name.lower()
        mapped = icon_pack.aliases.get(normalized, raw_name)
        candidates = [icon_pack.root / mapped]
        if "." not in mapped:
            candidates.extend(
                (
                    icon_pack.root / f"{mapped}.svg",
                    icon_pack.root / f"{mapped}.png",
                    icon_pack.root / f"{mapped}.ico",
                )
            )
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return GlassResolvedIcon(pack=icon_pack.name, icon_name=mapped, path=candidate)
        return GlassResolvedIcon(pack=icon_pack.name, icon_name=mapped, path=None)

    def get_icon(
        self,
        icon_name: str,
        *,
        pack: str | None = None,
        fallback: Optional[QIcon] = None,
    ) -> QIcon:
        resolved = self.resolve_icon(icon_name, pack=pack)
        cache_key = f"{resolved.pack}::{resolved.icon_name}".lower()
        cached = self._icon_cache.get(cache_key)
        if cached is not None:
            return cached

        if resolved.path is None:
            return fallback or QIcon()
        icon = QIcon(str(resolved.path))
        self._icon_cache[cache_key] = icon
        return icon

    def resolve_size(self, token_or_size: str | int | None, *, fallback: int = 16) -> int:
        if token_or_size is None:
            return max(8, int(fallback))
        if isinstance(token_or_size, int):
            return max(8, int(token_or_size))
        normalized = str(token_or_size or "").strip().lower()
        if not normalized:
            return max(8, int(fallback))
        if normalized.isdigit():
            return max(8, int(normalized))
        return max(8, int(self._size_tokens.get(normalized, fallback)))

    def apply_icon(
        self,
        target: QAbstractButton | QWidget,
        icon_name: str,
        *,
        pack: str | None = None,
        size: int | str | None = None,
        fallback_size: int = 16,
        accessible_name: str | None = None,
        tooltip: str | None = None,
    ) -> None:
        icon = self.get_icon(icon_name, pack=pack)
        if icon.isNull():
            return
        resolved_size = self.resolve_size(size, fallback=fallback_size)
        theme_id = _resolve_theme_id(target)
        normal_tint, glow_tint, active_tint = _resolve_icon_tints(theme_id)
        normal_icon, active_icon = _build_button_icon_variants(
            icon,
            resolved_size,
            normal_tint=normal_tint,
            glow_tint=glow_tint,
            active_tint=active_tint,
        )
        if isinstance(target, QAbstractButton):
            target.setIcon(normal_icon)
            target.setIconSize(QSize(resolved_size, resolved_size))
            _bind_hover_icon_state(target, normal_icon, active_icon)
            if tooltip:
                target.setToolTip(tooltip)
            if accessible_name and not target.accessibleName():
                target.setAccessibleName(accessible_name)
            return
        set_icon = getattr(target, "setIcon", None)
        set_icon_size = getattr(target, "setIconSize", None)
        if callable(set_icon):
            set_icon(normal_icon)
        if callable(set_icon_size):
            set_icon_size(QSize(resolved_size, resolved_size))
        if isinstance(target, QLabel):
            target.setPixmap(_tint_pixmap(icon.pixmap(QSize(resolved_size, resolved_size)), normal_tint))
        if accessible_name and not target.accessibleName():
            target.setAccessibleName(accessible_name)
        if tooltip and hasattr(target, "setToolTip"):
            target.setToolTip(tooltip)


def _tint_pixmap(source: QPixmap, color: QColor) -> QPixmap:
    if source.isNull():
        return source
    target = QPixmap(source.size())
    target.fill(Qt.GlobalColor.transparent)
    painter = QPainter(target)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    painter.drawPixmap(0, 0, source)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(target.rect(), color)
    painter.end()
    return target


def _resolve_theme_id(target: QWidget | QAbstractButton | None) -> str:
    current = target
    while isinstance(current, QWidget):
        for key in ("themeId", "theme_id"):
            value = current.property(key)
            if str(value or "").strip():
                return str(value).strip().lower()
        current = current.parentWidget()
    return DEFAULT_THEME_ID


def _resolve_icon_tints(theme_id: str) -> tuple[QColor, QColor, QColor]:
    palette = get_palette(theme_id)
    normal = QColor(palette.text_primary)
    glow = QColor(palette.accent_soft)
    active = QColor(palette.accent)
    if normal.alpha() == 255:
        normal.setAlpha(236)
    if glow.alpha() == 255:
        glow.setAlpha(108)
    if active.alpha() == 255:
        active.setAlpha(252)
    return normal, glow, active


def _build_button_icon_variants(
    icon: QIcon,
    size: int,
    *,
    normal_tint: QColor,
    glow_tint: QColor,
    active_tint: QColor,
) -> tuple[QIcon, QIcon]:
    base = icon.pixmap(QSize(size, size))
    normal_pix = _tint_pixmap(base, normal_tint)
    glow_base = _tint_pixmap(base, glow_tint)
    active_pix = QPixmap(base.size())
    active_pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(active_pix)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        painter.drawPixmap(dx, dy, glow_base)
    painter.drawPixmap(0, 0, _tint_pixmap(base, active_tint))
    painter.end()
    return QIcon(normal_pix), QIcon(active_pix)


class _ButtonIconStateBinder(QObject):
    def __init__(self, button: QAbstractButton, normal_icon: QIcon, active_icon: QIcon) -> None:
        super().__init__(button)
        self._button = button
        self._normal_icon = normal_icon
        self._active_icon = active_icon
        self._hovered = False
        self._button.installEventFilter(self)
        toggled = getattr(self._button, "toggled", None)
        if toggled is not None:
            toggled.connect(self._sync_icon)
        self._sync_icon()

    def update_icons(self, normal_icon: QIcon, active_icon: QIcon) -> None:
        self._normal_icon = normal_icon
        self._active_icon = active_icon
        self._sync_icon()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if watched is self._button:
            if event.type() in {QEvent.Type.Enter, QEvent.Type.HoverEnter}:
                self._hovered = True
                self._sync_icon()
            elif event.type() in {QEvent.Type.Leave, QEvent.Type.HoverLeave}:
                self._hovered = False
                self._sync_icon()
        return False

    def _sync_icon(self) -> None:
        is_checked = bool(self._button.isChecked()) if self._button.isCheckable() else False
        active = self._hovered or is_checked or bool(self._button.isDown())
        self._button.setIcon(self._active_icon if active else self._normal_icon)


_BUTTON_ICON_BINDERS: dict[int, _ButtonIconStateBinder] = {}


def _bind_hover_icon_state(button: QAbstractButton, normal_icon: QIcon, active_icon: QIcon) -> None:
    key = id(button)
    binder = _BUTTON_ICON_BINDERS.get(key)
    if binder is None:
        _BUTTON_ICON_BINDERS[key] = _ButtonIconStateBinder(button, normal_icon, active_icon)
        return
    binder.update_icons(normal_icon, active_icon)


_REGISTRY = GlassIconRegistry()


def register_icon_pack(
    name: str,
    root: str | Path,
    *,
    default_size_token: str = "body",
    aliases: Mapping[str, str] | None = None,
    metadata: Mapping[str, str] | None = None,
    override: bool = True,
) -> None:
    _REGISTRY.register_pack(
        name,
        root,
        default_size_token=default_size_token,
        aliases=aliases,
        metadata=metadata,
        override=override,
    )


def register_icon_namespace(namespace: str, root: str | Path) -> None:
    register_icon_pack(namespace, root)


def set_default_icon_pack(name: str) -> None:
    _REGISTRY.set_default_pack(name)


def set_default_icon_namespace(namespace: str) -> None:
    set_default_icon_pack(namespace)


def get_default_icon_pack() -> str:
    return _REGISTRY.default_pack


def get_default_icon_namespace() -> str:
    return get_default_icon_pack()


def list_icon_packs() -> tuple[str, ...]:
    return _REGISTRY.list_packs()


def register_icon_size_token(token: str, size: int, *, override: bool = True) -> None:
    _REGISTRY.register_size_token(token, size, override=override)


def get_icon(
    icon_name: str,
    *,
    namespace: str | None = None,
    pack: str | None = None,
    fallback: Optional[QIcon] = None,
) -> QIcon:
    return _REGISTRY.get_icon(icon_name, pack=pack or namespace, fallback=fallback)


def apply_icon(
    target: QAbstractButton | QWidget,
    icon_name: str,
    *,
    namespace: str | None = None,
    pack: str | None = None,
    size: int | str | None = "body",
    fallback_size: int = 16,
    accessible_name: str | None = None,
    tooltip: str | None = None,
) -> None:
    _REGISTRY.apply_icon(
        target,
        icon_name,
        pack=pack or namespace,
        size=size,
        fallback_size=fallback_size,
        accessible_name=accessible_name,
        tooltip=tooltip,
    )


def _bootstrap_builtin_icon_pack() -> None:
    root = Path(__file__).resolve().parent / "assets" / "icons"
    if not root.exists():
        return
    aliases = {
        "minimize-2": "minus",
        "maximize-2": "plus",
        "square": "box",
        "target": "sparkles",
        "droplets": "sparkles",
        "link": "git-branch",
        "pin": "check",
        "rotate-ccw": "refresh-cw",
        "external-link": "arrow-right",
        "alert-circle": "alert-triangle",
        "minus-circle": "x-circle",
        "list": "menu",
        "trending-up": "arrow-up",
        "layout-dashboard": "layers",
        "panel-right": "menu",
        "sliders-horizontal": "settings",
        "mouse-pointer-click": "zap",
        "circle-dot": "check-circle",
        "toggle-left": "minus",
        "tag": "filter",
        "square-stack": "layers",
        "chevrons-up-down": "chevron-up",
        "heart": "check-circle",
    }
    register_icon_pack("glass", root, aliases=aliases, metadata={"origin": "builtin"}, override=True)
    set_default_icon_pack("glass")


_bootstrap_builtin_icon_pack()
