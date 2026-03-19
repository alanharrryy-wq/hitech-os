from __future__ import annotations

import os
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRegularExpression, Qt, QThread
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QApplication,
    QDockWidget,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHeaderView,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QScrollBar,
    QSizeGrip,
    QSplitter,
    QSplitterHandle,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QWidget,
)

try:
    from shiboken6 import isValid as qt_object_is_valid
except ImportError:  # pragma: no cover - PySide6 ships shiboken6
    def qt_object_is_valid(obj):
        return obj is not None

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens

_VISUAL_ROLE_PROP = 'visualRole'
_VISUAL_TIER_PROP = 'visualTier'
_VISUAL_PREMIUM_PROP = 'premium'
_VISUAL_REVEAL_PROP = 'visualReveal'
_VISUAL_SKIP_PROP = 'visualSkip'
_VISUAL_DOCK_CONTENT_PROP = 'dockContentRoot'
_VISUAL_CODE_SURFACE_PROP = 'codeSurface'

_VR_LAST_SKIN_PROP = '_hitech_visual_last_skin'
_VR_LAST_EFFECT_SKIN_PROP = '_hitech_visual_last_effect_skin'
_VR_LAST_EFFECT_KIND_PROP = '_hitech_visual_last_effect_kind'
_VR_LAST_ROLE_PROP = '_hitech_visual_last_role'
_VR_LAST_RUN_PROP = '_hitech_visual_last_run'
_VR_CODE_SKIN_PROP = '_hitech_visual_code_skin'
_VR_REVEAL_DONE_PROP = '_hitech_visual_reveal_done'

_KNOWN_PREMIUM_CLASS_NAMES = {
    'PanelCard',
    'ElevatedPanelCard',
    'InsetPanel',
    'MetricTile',
    'MetricRow',
    'MetricStrip',
    'StatCard',
    'InfoPill',
    'StatusPill',
    'FilterChip',
    'TagPill',
    'CountBadge',
    'SeverityBadge',
    'PropertyListCard',
    'ResultListItemCard',
    'PreviewSummaryCard',
    'StatusBanner',
    'HeroPanel',
    'LoadingPlaceholderSurface',
    'EmptyState',
    'SurfaceFrame',
    'ToolbarSurface',
}

_SKIP_CLASS_NAMES = {
    'QScrollBar',
    'QHeaderView',
    'QSplitterHandle',
    'QMenu',
    'QSizeGrip',
}

_NAME_ROLE_HINTS: tuple[tuple[str, str], ...] = (
    ('workspace', 'workspace-surface'),
    ('splitter', 'workspace-surface'),
    ('hero', 'hero-surface'),
    ('metric', 'metric-surface'),
    ('status', 'status-surface'),
    ('summary', 'summary-surface'),
    ('code', 'code-surface'),
    ('preview', 'code-surface'),
    ('toolbar', 'toolbar-surface'),
    ('menubar', 'toolbar-surface'),
    ('menu', 'toolbar-surface'),
    ('tabs', 'panel-surface'),
    ('panel', 'panel-surface'),
    ('card', 'panel-surface'),
    ('surface', 'panel-surface'),
    ('dock', 'dock-content-root'),
)

_SHADOW_PROFILES: dict[str, tuple[float, float]] = {
    'workspace-surface': (12.0, 1.0),
    'toolbar-surface': (10.0, 1.0),
    'hero-surface': (18.0, 3.0),
    'panel-surface': (14.0, 2.0),
    'metric-surface': (12.0, 2.0),
    'summary-surface': (12.0, 2.0),
    'status-surface': (8.0, 0.0),
    'premium-surface': (16.0, 2.0),
    'dock-content-root': (16.0, 2.0),
    'plugin-dock-root': (16.0, 2.0),
}

_SHADOW_DEFAULT_PROFILE = (12.0, 1.0)

_DEBUG_TRUE_VALUES = {'1', 'true', 'yes', 'on'}
_ALL_CHILD_PATTERN = QRegularExpression('.*')


@dataclass(slots=True)
class VisualRuntimeOptions:
    reason: str = 'runtime'
    debug: bool = False
    force_skin: bool = False
    force_effects: bool = False
    skip_internals: bool = True
    run_id: int = 0


@dataclass(slots=True)
class VisualRuntimeReport:
    reason: str
    discovered: int = 0
    skipped: int = 0
    skin_applied: int = 0
    effects_applied: int = 0
    failures: int = 0

    def merge(self, other: VisualRuntimeReport) -> None:
        self.discovered += other.discovered
        self.skipped += other.skipped
        self.skin_applied += other.skin_applied
        self.effects_applied += other.effects_applied
        self.failures += other.failures


@dataclass(slots=True)
class _VisualCandidate:
    widget: QWidget
    role: str
    reason: str


def _emit_log(logger: Callable[[str], None] | None, message: str) -> None:
    text = f'[visual-runtime] {message}'
    if callable(logger):
        try:
            logger(text)
            return
        except Exception:
            pass
    print(text)


def _is_live_qt_object(obj: object) -> bool:
    if obj is None:
        return False
    if not hasattr(obj, 'metaObject'):
        return False
    try:
        return bool(qt_object_is_valid(obj))
    except Exception:
        return False


def _coerce_text(value: object) -> str:
    if value is None:
        return ''
    try:
        return str(value).strip()
    except Exception:
        return ''


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _coerce_text(value).lower()
    if not text:
        return False
    return text in _DEBUG_TRUE_VALUES


def _is_ui_thread() -> bool:
    app = QApplication.instance()
    if app is None:
        return False
    app_thread = app.thread()
    current_thread = QThread.currentThread()
    return app_thread is not None and current_thread is app_thread


def _widget_debug_name(widget: QWidget) -> str:
    cls_name = type(widget).__name__
    obj_name = _coerce_text(widget.objectName())
    if obj_name:
        return f'{cls_name}#{obj_name}'
    return cls_name


def _iter_widget_subtree(root: QWidget):
    if not _is_live_qt_object(root):
        return

    queue: deque[QWidget] = deque([root])
    seen: set[int] = set()

    while queue:
        widget = queue.popleft()
        if not _is_live_qt_object(widget):
            continue

        key = id(widget)
        if key in seen:
            continue
        seen.add(key)
        yield widget

        try:
            children = widget.findChildren(
                QWidget,
                _ALL_CHILD_PATTERN,
                Qt.FindDirectChildrenOnly,
            )
        except Exception:
            continue

        for child in children:
            if _is_live_qt_object(child):
                queue.append(child)


def _is_known_premium_class(widget: QWidget) -> bool:
    try:
        for cls in type(widget).mro():
            if cls.__name__ in _KNOWN_PREMIUM_CLASS_NAMES:
                return True
    except Exception:
        pass
    return False


def _is_dock_content_root(widget: QWidget) -> bool:
    if _coerce_bool(widget.property(_VISUAL_DOCK_CONTENT_PROP)):
        return True
    parent = widget.parentWidget()
    return isinstance(parent, QDockWidget)


def detect_visual_role(widget: QWidget) -> str:
    explicit_role = _coerce_text(widget.property(_VISUAL_ROLE_PROP)).lower()
    if explicit_role:
        return explicit_role

    if isinstance(widget, QToolBar):
        return 'toolbar-surface'

    if isinstance(widget, QMenuBar):
        return 'toolbar-surface'

    if isinstance(widget, QStatusBar):
        return 'status-surface'

    if isinstance(widget, QTabWidget):
        return 'panel-surface'

    if isinstance(widget, QSplitter):
        return 'workspace-surface'

    if isinstance(widget, QDockWidget):
        return 'dock-shell'

    if _is_dock_content_root(widget):
        parent = widget.parentWidget()
        if isinstance(parent, QDockWidget) and parent.objectName().startswith('plugin_dock_'):
            return 'plugin-dock-root'
        return 'dock-content-root'

    visual_tier = _coerce_text(widget.property(_VISUAL_TIER_PROP)).lower()
    if visual_tier == 'premium':
        return 'premium-surface'
    if visual_tier == 'themed':
        return 'panel-surface'

    if _coerce_bool(widget.property(_VISUAL_PREMIUM_PROP)):
        return 'premium-surface'

    if _is_known_premium_class(widget):
        class_name = type(widget).__name__.lower()
        if 'hero' in class_name:
            return 'hero-surface'
        if 'metric' in class_name:
            return 'metric-surface'
        if 'status' in class_name:
            return 'status-surface'
        if 'summary' in class_name:
            return 'summary-surface'
        if 'panel' in class_name or 'card' in class_name or 'surface' in class_name:
            return 'panel-surface'
        return 'premium-surface'

    has_surface_shape = False
    try:
        has_surface_shape = widget.layout() is not None
    except Exception:
        has_surface_shape = False
    if not has_surface_shape:
        try:
            has_surface_shape = bool(
                widget.findChildren(
                    QWidget,
                    _ALL_CHILD_PATTERN,
                    Qt.FindDirectChildrenOnly,
                )
            )
        except Exception:
            has_surface_shape = False

    if has_surface_shape:
        object_name = _coerce_text(widget.objectName()).lower()
        for token, role in _NAME_ROLE_HINTS:
            if token in object_name:
                return role

    set_skin = getattr(widget, 'set_skin', None)
    if callable(set_skin):
        return 'skin-capable'

    class_name = type(widget).__name__
    object_name = _coerce_text(widget.objectName()).lower()
    if object_name.startswith('qt_'):
        return ''

    if class_name == 'QLabel':
        return 'semantic-label'

    if class_name in {
        'QLineEdit',
        'QComboBox',
        'QToolButton',
        'QPushButton',
        'QCheckBox',
        'QSpinBox',
    }:
        return 'semantic-control'

    parent = widget.parentWidget()
    if class_name == 'QWidget' and isinstance(parent, QToolBar):
        return 'semantic-container'

    return ''


def _candidate_reason(widget: QWidget, role: str) -> str:
    if role:
        return f'role:{role}'
    set_skin = getattr(widget, 'set_skin', None)
    if callable(set_skin):
        return 'set_skin'
    if _is_known_premium_class(widget):
        return 'known-premium-class'
    return ''


def _skip_reason(widget: QWidget, role: str, options: VisualRuntimeOptions) -> str:
    if not options.skip_internals:
        return ''

    if _coerce_bool(widget.property(_VISUAL_SKIP_PROP)):
        return 'visualSkip marker'

    class_name = type(widget).__name__
    if class_name in _SKIP_CLASS_NAMES and not role:
        return f'class {class_name}'

    if isinstance(widget, (QScrollBar, QHeaderView, QSplitterHandle, QMenu, QSizeGrip)) and not role:
        return f'internal {class_name}'

    object_name = _coerce_text(widget.objectName()).lower()
    if object_name.startswith('qt_') and not role:
        return 'qt internal objectName'

    if (
        isinstance(widget, QAbstractScrollArea)
        and not role
        and not callable(getattr(widget, 'set_skin', None))
    ):
        return 'generic scroll area'

    parent = widget.parentWidget()
    if (
        isinstance(parent, QAbstractScrollArea)
        and object_name.startswith('qt_scrollarea_')
        and not role
    ):
        return 'scroll area internal child'

    return ''


def _discover_candidates(
    root: QWidget,
    options: VisualRuntimeOptions,
    logger: Callable[[str], None] | None,
) -> tuple[list[_VisualCandidate], int]:
    discovered: list[_VisualCandidate] = []
    skipped = 0

    for widget in _iter_widget_subtree(root):
        role = detect_visual_role(widget)
        reason = _candidate_reason(widget, role)
        if not reason:
            continue

        skip_reason = _skip_reason(widget, role, options)
        if skip_reason:
            skipped += 1
            if options.debug:
                _emit_log(
                    logger,
                    f'skip {_widget_debug_name(widget)} ({skip_reason})',
                )
            continue

        discovered.append(_VisualCandidate(widget=widget, role=role, reason=reason))
        if options.debug:
            _emit_log(
                logger,
                f'discovered {_widget_debug_name(widget)} [{reason}]',
            )

    return discovered, skipped


def discover_visual_candidates(
    root: QWidget,
    options: VisualRuntimeOptions | None = None,
    logger: Callable[[str], None] | None = None,
) -> list[QWidget]:
    opts = options or VisualRuntimeOptions(reason='discover')
    candidates, _ = _discover_candidates(root, opts, logger)
    return [candidate.widget for candidate in candidates]


def _build_code_surface_qss(tokens: SkinTokens) -> str:
    return (
        f"QPlainTextEdit {{ background: {tokens.code_bg}; color: {tokens.code_text}; "
        f"selection-background-color: {tokens.selection}; border: 1px solid {tokens.border}; }}"
    )


def _should_style_code_surface(widget: QWidget, role: str) -> bool:
    if not isinstance(widget, QPlainTextEdit):
        return False
    if role in {'code-surface', 'summary-surface'}:
        return True
    if _coerce_bool(widget.property(_VISUAL_CODE_SURFACE_PROP)):
        return True
    object_name = _coerce_text(widget.objectName()).lower()
    return object_name in {
        'previewcodesurface',
        'statstextsurface',
        'logtextsurface',
        'filesummarysurface',
    }


def maybe_apply_skin(
    widget: QWidget,
    tokens: SkinTokens,
    options: VisualRuntimeOptions,
    logger: Callable[[str], None] | None,
    role: str,
) -> bool:
    applied = False

    set_skin = getattr(widget, 'set_skin', None)
    if callable(set_skin):
        last_skin = _coerce_text(widget.property(_VR_LAST_SKIN_PROP))
        if options.force_skin or last_skin != tokens.name:
            try:
                set_skin(tokens)
                widget.setProperty(_VR_LAST_SKIN_PROP, tokens.name)
                applied = True
                if options.debug:
                    _emit_log(
                        logger,
                        f'skin applied to {_widget_debug_name(widget)}',
                    )
            except Exception as exc:
                _emit_log(
                    logger,
                    f'skin failed for {_widget_debug_name(widget)}: {exc}',
                )
        elif options.debug:
            _emit_log(
                logger,
                f'skin unchanged for {_widget_debug_name(widget)}',
            )

    if _should_style_code_surface(widget, role):
        code_skin = _coerce_text(widget.property(_VR_CODE_SKIN_PROP))
        if options.force_skin or code_skin != tokens.name:
            try:
                widget.setStyleSheet(_build_code_surface_qss(tokens))
                widget.setProperty(_VR_CODE_SKIN_PROP, tokens.name)
                applied = True
                if options.debug:
                    _emit_log(
                        logger,
                        f'code surface skin applied to {_widget_debug_name(widget)}',
                    )
            except Exception as exc:
                _emit_log(
                    logger,
                    f'code surface skin failed for {_widget_debug_name(widget)}: {exc}',
                )

    return applied


def _ensure_shadow(
    widget: QWidget,
    tokens: SkinTokens,
    role: str,
    options: VisualRuntimeOptions,
    logger: Callable[[str], None] | None,
) -> bool:
    effect_kind = f'shadow:{role}'
    if not options.force_effects:
        last_effect_skin = _coerce_text(widget.property(_VR_LAST_EFFECT_SKIN_PROP))
        last_effect_kind = _coerce_text(widget.property(_VR_LAST_EFFECT_KIND_PROP))
        if last_effect_skin == tokens.name and last_effect_kind == effect_kind:
            if options.debug:
                _emit_log(
                    logger,
                    f'effect unchanged for {_widget_debug_name(widget)}',
                )
            return False

    blur, y_offset = _SHADOW_PROFILES.get(role, _SHADOW_DEFAULT_PROFILE)
    color = QColor(tokens.shadow)
    changed = False

    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        effect = QGraphicsDropShadowEffect(widget)
        widget.setGraphicsEffect(effect)
        changed = True

    if abs(float(effect.blurRadius()) - float(blur)) > 0.01:
        effect.setBlurRadius(blur)
        changed = True

    offset = effect.offset()
    if abs(float(offset.x()) - 0.0) > 0.01 or abs(float(offset.y()) - float(y_offset)) > 0.01:
        effect.setOffset(0.0, y_offset)
        changed = True

    if effect.color() != color:
        effect.setColor(color)
        changed = True

    widget.setProperty(_VR_LAST_EFFECT_SKIN_PROP, tokens.name)
    widget.setProperty(_VR_LAST_EFFECT_KIND_PROP, effect_kind)

    if changed and options.debug:
        _emit_log(
            logger,
            f'shadow applied to {_widget_debug_name(widget)}',
        )
    return changed


def _should_apply_reveal(widget: QWidget, role: str) -> bool:
    if role in _SHADOW_PROFILES:
        return False
    return _coerce_bool(widget.property(_VISUAL_REVEAL_PROP))


def _apply_reveal_once(
    widget: QWidget,
    options: VisualRuntimeOptions,
    logger: Callable[[str], None] | None,
) -> bool:
    if not options.force_effects and _coerce_bool(widget.property(_VR_REVEAL_DONE_PROP)):
        if options.debug:
            _emit_log(
                logger,
                f'reveal unchanged for {_widget_debug_name(widget)}',
            )
        return False

    effect = widget.graphicsEffect()
    if effect is not None and not isinstance(effect, QGraphicsOpacityEffect):
        if options.debug:
            _emit_log(
                logger,
                f'reveal skipped for {_widget_debug_name(widget)} (graphics effect in use)',
            )
        return False

    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    effect.setOpacity(0.0)
    animation = QPropertyAnimation(effect, b'opacity', widget)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setDuration(160)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.start()
    widget._visual_runtime_reveal_animation = animation  # type: ignore[attr-defined]
    widget.setProperty(_VR_REVEAL_DONE_PROP, True)

    if options.debug:
        _emit_log(
            logger,
            f'reveal applied to {_widget_debug_name(widget)}',
        )
    return True


def maybe_apply_effects(
    widget: QWidget,
    tokens: SkinTokens,
    options: VisualRuntimeOptions,
    logger: Callable[[str], None] | None,
    role: str,
) -> bool:
    applied = False

    resolved_role = role or detect_visual_role(widget)
    if resolved_role in _SHADOW_PROFILES:
        applied = _ensure_shadow(widget, tokens, resolved_role, options, logger) or applied

    if _should_apply_reveal(widget, resolved_role):
        applied = _apply_reveal_once(widget, options, logger) or applied

    return applied


def mark_processed(widget: QWidget, role: str, options: VisualRuntimeOptions) -> None:
    try:
        widget.setProperty(_VR_LAST_ROLE_PROP, role)
        if options.run_id > 0:
            widget.setProperty(_VR_LAST_RUN_PROP, options.run_id)
    except Exception:
        pass


def _is_widget_thread_safe(widget: QWidget) -> bool:
    if not _is_live_qt_object(widget):
        return False
    try:
        return widget.thread() is QThread.currentThread()
    except Exception:
        return False


def apply_visual_runtime(
    root: QWidget,
    tokens: SkinTokens,
    options: VisualRuntimeOptions | None = None,
    logger: Callable[[str], None] | None = None,
) -> VisualRuntimeReport:
    opts = options or VisualRuntimeOptions(reason='runtime')
    report = VisualRuntimeReport(reason=opts.reason)

    if not _is_live_qt_object(root):
        if opts.debug:
            _emit_log(logger, 'skipping runtime: root is not a live widget')
        return report

    if not _is_ui_thread():
        _emit_log(logger, f'skipping runtime "{opts.reason}" outside UI thread')
        return report

    if not _is_widget_thread_safe(root):
        _emit_log(logger, f'skipping runtime "{opts.reason}" for foreign-thread widget')
        return report

    candidates, skipped = _discover_candidates(root, opts, logger)
    report.discovered = len(candidates)
    report.skipped = skipped

    for candidate in candidates:
        widget = candidate.widget
        role = candidate.role or detect_visual_role(widget)
        mark_processed(widget, role, opts)
        try:
            if maybe_apply_skin(widget, tokens, opts, logger, role):
                report.skin_applied += 1
        except Exception as exc:
            report.failures += 1
            _emit_log(
                logger,
                f'skin processing failed for {_widget_debug_name(widget)}: {exc}',
            )

        try:
            if maybe_apply_effects(widget, tokens, opts, logger, role):
                report.effects_applied += 1
        except Exception as exc:
            report.failures += 1
            _emit_log(
                logger,
                f'effect processing failed for {_widget_debug_name(widget)}: {exc}',
            )

    if opts.debug:
        _emit_log(
            logger,
            (
                f'run "{opts.reason}": discovered={report.discovered}, '
                f'skipped={report.skipped}, skinned={report.skin_applied}, '
                f'effects={report.effects_applied}, failures={report.failures}'
            ),
        )

    return report


def process_dock_widget(
    dock: QDockWidget,
    tokens: SkinTokens,
    options: VisualRuntimeOptions | None = None,
    logger: Callable[[str], None] | None = None,
) -> VisualRuntimeReport:
    opts = options or VisualRuntimeOptions(reason='dock-runtime')
    if not _is_live_qt_object(dock):
        return VisualRuntimeReport(reason=opts.reason)

    dock.setProperty(_VISUAL_ROLE_PROP, 'dock-shell')
    content = dock.widget()
    if _is_live_qt_object(content):
        if not _coerce_text(content.property(_VISUAL_ROLE_PROP)):
            if dock.objectName().startswith('plugin_dock_'):
                content.setProperty(_VISUAL_ROLE_PROP, 'plugin-dock-root')
            else:
                content.setProperty(_VISUAL_ROLE_PROP, 'dock-content-root')
        content.setProperty(_VISUAL_DOCK_CONTENT_PROP, True)

    return apply_visual_runtime(dock, tokens, options=opts, logger=logger)


class VisualRuntimeCoordinator:
    """Central runtime coordinator for automated visual integration."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self._run_counter = 0

    def discover_visual_candidates(
        self,
        root: QWidget,
        *,
        debug: bool | None = None,
    ) -> list[QWidget]:
        options = self._build_options('discover', force=False, debug=debug)
        return discover_visual_candidates(root, options=options, logger=self._log)

    def apply_visual_runtime(
        self,
        root: QWidget,
        tokens: SkinTokens | None = None,
        *,
        reason: str = 'subtree-runtime',
        force: bool = False,
        debug: bool | None = None,
    ) -> VisualRuntimeReport:
        return self.process_subtree(
            root,
            tokens=tokens,
            reason=reason,
            force=force,
            debug=debug,
        )

    def process_subtree(
        self,
        root: QWidget | None,
        tokens: SkinTokens | None = None,
        *,
        reason: str = 'subtree-runtime',
        force: bool = False,
        debug: bool | None = None,
    ) -> VisualRuntimeReport:
        options = self._build_options(reason, force=force, debug=debug)
        active_tokens = tokens or getattr(self.main, '_skin_tokens', None)
        if not _is_live_qt_object(root) or active_tokens is None:
            return VisualRuntimeReport(reason=options.reason)
        return apply_visual_runtime(
            root,
            active_tokens,
            options=options,
            logger=self._log,
        )

    def process_dock_widget(
        self,
        dock: QDockWidget | None,
        tokens: SkinTokens | None = None,
        *,
        reason: str = 'dock-runtime',
        force: bool = False,
        debug: bool | None = None,
    ) -> VisualRuntimeReport:
        options = self._build_options(reason, force=force, debug=debug)
        active_tokens = tokens or getattr(self.main, '_skin_tokens', None)
        if not isinstance(dock, QDockWidget) or active_tokens is None:
            return VisualRuntimeReport(reason=options.reason)
        return process_dock_widget(
            dock,
            active_tokens,
            options=options,
            logger=self._log,
        )

    def process_shell_surfaces(
        self,
        tokens: SkinTokens | None = None,
        *,
        reason: str = 'shell-runtime',
        force: bool = False,
        debug: bool | None = None,
    ) -> VisualRuntimeReport:
        options = self._build_options(reason, force=force, debug=debug)
        active_tokens = tokens or getattr(self.main, '_skin_tokens', None)
        summary = VisualRuntimeReport(reason=options.reason)
        if active_tokens is None:
            return summary

        central = self.main.centralWidget()
        if _is_live_qt_object(central):
            central_report = apply_visual_runtime(
                central,
                active_tokens,
                options=options,
                logger=self._log,
            )
            summary.merge(central_report)

        for dock in self._iter_shell_docks():
            dock_report = process_dock_widget(
                dock,
                active_tokens,
                options=self._build_options(
                    f'{reason}:{dock.objectName() or "dock"}',
                    force=force,
                    debug=debug,
                ),
                logger=self._log,
            )
            summary.merge(dock_report)

        for toolbar in self._iter_shell_toolbars():
            toolbar_report = apply_visual_runtime(
                toolbar,
                active_tokens,
                options=self._build_options(
                    f'{reason}:{toolbar.objectName() or "toolbar"}',
                    force=force,
                    debug=debug,
                ),
                logger=self._log,
            )
            summary.merge(toolbar_report)

        menu_bar = self.main.menuBar()
        if _is_live_qt_object(menu_bar):
            menu_report = apply_visual_runtime(
                menu_bar,
                active_tokens,
                options=self._build_options(
                    f'{reason}:menubar',
                    force=force,
                    debug=debug,
                ),
                logger=self._log,
            )
            summary.merge(menu_report)

        status_bar = self.main.statusBar()
        if _is_live_qt_object(status_bar):
            status_report = apply_visual_runtime(
                status_bar,
                active_tokens,
                options=self._build_options(
                    f'{reason}:statusbar',
                    force=force,
                    debug=debug,
                ),
                logger=self._log,
            )
            summary.merge(status_report)

        if options.debug:
            self._log(
                (
                    f'summary "{reason}": discovered={summary.discovered}, '
                    f'skipped={summary.skipped}, skinned={summary.skin_applied}, '
                    f'effects={summary.effects_applied}, failures={summary.failures}'
                )
            )
        return summary

    def _iter_shell_docks(self) -> tuple[QDockWidget, ...]:
        docks: list[QDockWidget] = []
        seen: set[int] = set()

        for name in (
            'explorer_dock',
            'results_dock',
            'inspector_dock',
            'bookmarks_dock',
        ):
            dock = getattr(self.main, name, None)
            if isinstance(dock, QDockWidget) and _is_live_qt_object(dock):
                key = id(dock)
                if key not in seen:
                    seen.add(key)
                    docks.append(dock)

        try:
            dynamic_docks = self.main.findChildren(
                QDockWidget,
                _ALL_CHILD_PATTERN,
                Qt.FindDirectChildrenOnly,
            )
        except Exception:
            dynamic_docks = []

        for dock in dynamic_docks:
            if not _is_live_qt_object(dock):
                continue
            key = id(dock)
            if key in seen:
                continue
            seen.add(key)
            docks.append(dock)

        return tuple(docks)

    def _iter_shell_toolbars(self) -> tuple[QToolBar, ...]:
        toolbars: list[QToolBar] = []
        seen: set[int] = set()

        for name in ('workspace_toolbar', 'command_toolbar'):
            toolbar = getattr(self.main, name, None)
            if isinstance(toolbar, QToolBar) and _is_live_qt_object(toolbar):
                key = id(toolbar)
                if key not in seen:
                    seen.add(key)
                    toolbars.append(toolbar)

        try:
            dynamic_toolbars = self.main.findChildren(
                QToolBar,
                _ALL_CHILD_PATTERN,
                Qt.FindDirectChildrenOnly,
            )
        except Exception:
            dynamic_toolbars = []

        for toolbar in dynamic_toolbars:
            if not _is_live_qt_object(toolbar):
                continue
            key = id(toolbar)
            if key in seen:
                continue
            seen.add(key)
            toolbars.append(toolbar)

        return tuple(toolbars)

    def _build_options(
        self,
        reason: str,
        *,
        force: bool,
        debug: bool | None,
    ) -> VisualRuntimeOptions:
        self._run_counter += 1
        return VisualRuntimeOptions(
            reason=reason,
            debug=self._resolve_debug(debug),
            force_skin=force,
            force_effects=force,
            run_id=self._run_counter,
        )

    def _resolve_debug(self, debug: bool | None) -> bool:
        if isinstance(debug, bool):
            return debug

        env_value = os.environ.get('HITECH_VISUAL_RUNTIME_DEBUG', '').strip().lower()
        if env_value in _DEBUG_TRUE_VALUES:
            return True

        settings = getattr(self.main, 'settings', None)
        if settings is not None:
            try:
                raw = settings.value('visual_runtime_debug', False)
                if _coerce_bool(raw):
                    return True
            except Exception:
                pass

        return _coerce_bool(getattr(self.main, 'visual_runtime_debug', False))

    def _log(self, message: str) -> None:
        logger = getattr(self.main, 'log', None)
        if callable(logger):
            try:
                logger(message)
                return
            except Exception:
                pass
        print(message)
