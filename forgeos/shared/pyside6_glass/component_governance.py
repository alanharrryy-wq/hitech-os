from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtWidgets import QListWidget, QTableWidget, QTextEdit, QWidget


APPROVED_COMPONENT_KEYS: frozenset[str] = frozenset(
    {
        'glass_panel_template',
        'glass_panel_frame',
        'glass_workspace_tabs',
        'dashboard_data_surface',
        'dashboard_table',
        'dashboard_feed',
        'dashboard_payload',
        'status_pill',
        'panel_header',
        'stat_card',
    }
)


@dataclass(frozen=True, slots=True)
class ComponentGovernanceIssue:
    code: str
    message: str
    widget_class: str
    object_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'code': self.code,
            'message': self.message,
            'widget_class': self.widget_class,
            'object_name': self.object_name,
        }


def mark_component(
    widget: QWidget,
    *,
    component_key: str,
    status: str = 'Primary',
) -> QWidget:
    key = str(component_key or '').strip().lower()
    if key:
        widget.setProperty('componentKey', key)
    widget.setProperty('componentCatalogStatus', str(status or 'Primary'))
    widget.setProperty('componentApproved', bool(key in APPROVED_COMPONENT_KEYS))
    return widget


def is_component_approved(widget: QWidget) -> bool:
    approved = widget.property('componentApproved')
    if approved is True:
        return True
    key = str(widget.property('componentKey') or '').strip().lower()
    return key in APPROVED_COMPONENT_KEYS


def validate_widget_tree(root: QWidget) -> list[ComponentGovernanceIssue]:
    issues: list[ComponentGovernanceIssue] = []
    forbidden_types = (QTableWidget, QListWidget, QTextEdit)
    for widget in root.findChildren(QWidget):
        if isinstance(widget, forbidden_types) and not is_component_approved(widget):
            issues.append(
                ComponentGovernanceIssue(
                    code='raw_qt_surface',
                    message='raw Qt data widget found without approved system wrapper',
                    widget_class=widget.__class__.__name__,
                    object_name=str(widget.objectName() or ''),
                )
            )
    return issues


__all__ = [
    'APPROVED_COMPONENT_KEYS',
    'ComponentGovernanceIssue',
    'is_component_approved',
    'mark_component',
    'validate_widget_tree',
]

