
from __future__ import annotations

"""
Foundry Interaction Safety for PySide6 Glass.

Second heavy injection layer.

Purpose:
- make overlays and decorative layers safe by default
- centralize page lifetime and navigation so widgets stop climbing over each other
- formalize focus travel, shortcut routing and modal lifecycles
- surface audit findings before they become user rage
- keep gorgeous interfaces usable when recipes get lush and layered
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Sequence
import json
from weakref import WeakKeyDictionary

from PySide6.QtCore import QObject, Qt, QEvent, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .catalog import GlassCatalogEntry, register_catalog_entry
from .config import get_template_preset
from .primitives import LoadingStateCard, PanelHeader, QuickActionsStrip
from .template import GlassPanelTemplate
from .foundry_foundation import FoundryContractSplitter

INTERACTION_SAFETY_VERSION = "foundry.interaction_safety.v1"
INTERACTION_CATALOG_CATEGORY = "Foundry Interaction"

INTERACTION_PROFILES: dict[str, dict[str, Any]] = {
    "operator_dense": {
        "title": "Operator Dense",
        "description": "Fast, compact keyboard-heavy interaction profile for operations consoles.",
        "focus_policy": "explicit",
        "hover_energy": "low",
        "shortcut_scope": "window",
        "overlay_style": "restrained",
        "tab_travel": "guided",
        "minimum_hit_size": 32,
        "preferred_hit_size": 40,
        "opaque_resize": false,
        "children_collapsible": false,
        "sheet_width": 520,
        "glass_chrome": "tight"
    },
    "analyst_review": {
        "title": "Analyst Review",
        "description": "Review-friendly interaction rhythm with calmer motion and richer focus signaling.",
        "focus_policy": "explicit",
        "hover_energy": "subtle",
        "shortcut_scope": "window",
        "overlay_style": "soft",
        "tab_travel": "guided",
        "minimum_hit_size": 36,
        "preferred_hit_size": 44,
        "opaque_resize": false,
        "children_collapsible": false,
        "sheet_width": 560,
        "glass_chrome": "balanced"
    },
    "executive_touch": {
        "title": "Executive Touch",
        "description": "Bigger hit targets, lower cognitive friction and very safe modal behavior.",
        "focus_policy": "strong",
        "hover_energy": "low",
        "shortcut_scope": "window",
        "overlay_style": "soft",
        "tab_travel": "wide",
        "minimum_hit_size": 40,
        "preferred_hit_size": 48,
        "opaque_resize": false,
        "children_collapsible": false,
        "sheet_width": 600,
        "glass_chrome": "lux"
    },
    "diagnostic_lab": {
        "title": "Diagnostic Lab",
        "description": "Debug-first profile with aggressive audit messaging and deeper interaction tracing.",
        "focus_policy": "strong",
        "hover_energy": "medium",
        "shortcut_scope": "application",
        "overlay_style": "clear",
        "tab_travel": "guided",
        "minimum_hit_size": 34,
        "preferred_hit_size": 40,
        "opaque_resize": false,
        "children_collapsible": false,
        "sheet_width": 640,
        "glass_chrome": "utilitarian"
    }
}
OVERLAY_PATTERNS: dict[str, dict[str, Any]] = {
    "status_banner": {
        "pass_through": true,
        "elevation": 10,
        "scrim": false,
        "corner_radius": 16,
        "shadow": 0.15
    },
    "toast_stack": {
        "pass_through": true,
        "elevation": 20,
        "scrim": false,
        "corner_radius": 18,
        "shadow": 0.22
    },
    "context_sheet": {
        "pass_through": false,
        "elevation": 40,
        "scrim": true,
        "corner_radius": 22,
        "shadow": 0.35
    },
    "command_palette": {
        "pass_through": false,
        "elevation": 50,
        "scrim": true,
        "corner_radius": 24,
        "shadow": 0.38
    },
    "diagnostic_overlay": {
        "pass_through": true,
        "elevation": 30,
        "scrim": false,
        "corner_radius": 14,
        "shadow": 0.18
    },
    "drawer_left": {
        "pass_through": false,
        "elevation": 45,
        "scrim": true,
        "corner_radius": 0,
        "shadow": 0.3
    },
    "drawer_right": {
        "pass_through": false,
        "elevation": 45,
        "scrim": true,
        "corner_radius": 0,
        "shadow": 0.3
    }
}
SURFACE_ROLE_GROUPS: dict[str, list[str]] = {
    "page": [
        "shell",
        "scroll_surface",
        "centered_surface",
        "split_surface"
    ],
    "overlay": [
        "sheet",
        "dialog",
        "toast",
        "banner",
        "palette"
    ],
    "support": [
        "audit_panel",
        "focus_map",
        "shortcut_legend",
        "trace_console"
    ]
}
INTERACTION_REFERENCE_NOTES = "## Safety Pattern 1\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 2\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 3\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 4\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 5\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 6\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 7\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 8\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 9\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 10\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 11\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 12\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 13\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 14\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 15\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 16\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 17\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 18\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 19\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 20\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 21\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 22\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 23\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 24\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 25\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 26\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 27\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 28\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 29\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 30\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 31\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 32\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 33\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 34\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 35\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 36\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 37\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 38\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 39\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n\n\n## Safety Pattern 40\n- Goal: Keep interaction predictable even when visual ornament gets rich.\n- Rule: Decorative layers must be pass-through by default.\n- Rule: Navigation containers own page lifetime; pages do not raise themselves above siblings.\n- Rule: Focus order is declared or synthesized from geometry, never left to luck in dense workspaces.\n- Rule: Splitters restore safely and clamp invalid ratios before users see broken geometry.\n- Rule: Every modal surface publishes an exit action, Escape shortcut, and visible close affordance.\n- Rule: Audit output must explain not only that something failed, but why it is risky to users.\n- Commentary: In a recipe-driven UI platform, beauty should be a passenger riding on rails, not a drunk unicycle rolling through the input stack.\n"
CATALOG_PAYLOADS: tuple[dict[str, Any], ...] = tuple([
    {
        "entry_id": "interaction_profile_operator_dense",
        "title": "Interaction Profile \u00b7 Operator Dense",
        "subtitle": "Fast, compact keyboard-heavy interaction profile for operations consoles.",
        "description": "Preview the Operator Dense interaction contract, overlay posture, focus routing and safety audit defaults.",
        "keywords": [
            "interaction",
            "focus",
            "overlay",
            "operator_dense",
            "foundry"
        ],
        "icon_name": "shield",
        "sort_order": 921
    },
    {
        "entry_id": "interaction_profile_analyst_review",
        "title": "Interaction Profile \u00b7 Analyst Review",
        "subtitle": "Review-friendly interaction rhythm with calmer motion and richer focus signaling.",
        "description": "Preview the Analyst Review interaction contract, overlay posture, focus routing and safety audit defaults.",
        "keywords": [
            "interaction",
            "focus",
            "overlay",
            "analyst_review",
            "foundry"
        ],
        "icon_name": "shield",
        "sort_order": 922
    },
    {
        "entry_id": "interaction_profile_executive_touch",
        "title": "Interaction Profile \u00b7 Executive Touch",
        "subtitle": "Bigger hit targets, lower cognitive friction and very safe modal behavior.",
        "description": "Preview the Executive Touch interaction contract, overlay posture, focus routing and safety audit defaults.",
        "keywords": [
            "interaction",
            "focus",
            "overlay",
            "executive_touch",
            "foundry"
        ],
        "icon_name": "shield",
        "sort_order": 923
    },
    {
        "entry_id": "interaction_profile_diagnostic_lab",
        "title": "Interaction Profile \u00b7 Diagnostic Lab",
        "subtitle": "Debug-first profile with aggressive audit messaging and deeper interaction tracing.",
        "description": "Preview the Diagnostic Lab interaction contract, overlay posture, focus routing and safety audit defaults.",
        "keywords": [
            "interaction",
            "focus",
            "overlay",
            "diagnostic_lab",
            "foundry"
        ],
        "icon_name": "shield",
        "sort_order": 924
    },
    {
        "entry_id": "interaction_audit_console",
        "title": "Audit Console",
        "subtitle": "Dead click, tiny hit-target and overlay-collision auditing",
        "description": "Runs the safety auditor over a composed shell and surfaces suspicious hit areas, blocking overlays and focus drift.",
        "keywords": [
            "audit",
            "focus",
            "hit-test",
            "overlay"
        ],
        "icon_name": "activity",
        "sort_order": 960
    },
    {
        "entry_id": "interaction_shortcut_router",
        "title": "Shortcut Router",
        "subtitle": "Context-aware keyboard intents and discoverability",
        "description": "Shows how shortcut intents can be routed by active page and mode without turning the app into spaghetti shortcuts.",
        "keywords": [
            "shortcut",
            "keyboard",
            "router"
        ],
        "icon_name": "command",
        "sort_order": 961
    },
    {
        "entry_id": "interaction_overlay_portal",
        "title": "Overlay Portal",
        "subtitle": "Pass-through d\u00e9cor and blocking sheets without click theft",
        "description": "Demonstrates how decorative layers remain transparent to input while modal surfaces intentionally capture it.",
        "keywords": [
            "overlay",
            "portal",
            "sheet",
            "scrim"
        ],
        "icon_name": "layers",
        "sort_order": 962
    }
])


@dataclass(frozen=True, slots=True)
class SafetyFinding:
    code: str
    severity: str
    message: str
    widget_path: str = ""
    recommendation: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class OverlaySpec:
    overlay_id: str
    title: str
    role: str = "sheet"
    pass_through: bool = False
    scrim: bool = False
    close_on_escape: bool = True
    close_on_scrim_click: bool = True
    width: int | None = None
    height: int | None = None
    alignment: str = "center"
    style_key: str = "context_sheet"
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FocusTargetSpec:
    object_name: str
    title: str
    page_id: str = ""
    required: bool = True
    tab_group: str = "main"


@dataclass(frozen=True, slots=True)
class ShortcutIntent:
    intent_id: str
    title: str
    sequence: str
    page_id: str = "*"
    mode: str = "*"
    enabled: bool = True
    description: str = ""


@dataclass(frozen=True, slots=True)
class PageSpec:
    page_id: str
    title: str
    subtitle: str = ""
    icon_name: str | None = None
    tags: tuple[str, ...] = ()
    audit_hint: str = ""


@dataclass(frozen=True, slots=True)
class InteractionCatalogEntrySpec:
    entry_id: str
    title: str
    subtitle: str
    description: str
    builder: Callable[[QWidget | None], QWidget]
    category: str = INTERACTION_CATALOG_CATEGORY
    tags: tuple[str, ...] = ("interaction", "foundry", "safety")
    status: str = "experimental"
    keywords: tuple[str, ...] = ()
    best_for: str = ""
    use_when: str = ""
    sort_order: int = 900
    icon_name: str | None = "shield"


class PassThroughDecoration(QFrame):
    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(_safe_name(f"pass_through_{title or 'decoration'}"))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setProperty("role", "interaction_pass_through_decoration")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        if title:
            label = QLabel(title, self)
            label.setProperty("role", "panel_subtitle")
            layout.addWidget(label)
        self._body = QLabel("Decorative overlay only. Input passes through.", self)
        self._body.setWordWrap(True)
        layout.addWidget(self._body)

    def set_note(self, text: str) -> None:
        self._body.setText(text)


class InteractionScrim(QFrame):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("interaction_scrim")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.82)
        self.setGraphicsEffect(effect)

    def mousePressEvent(self, event):  # noqa: N802
        self.clicked.emit()
        event.accept()


class SafeOverlaySurface(QFrame):
    requested_close = Signal(str)

    def __init__(self, spec: OverlaySpec, content: QWidget | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.spec = spec
        self.setObjectName(_safe_name(f"overlay_{spec.overlay_id}"))
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setMinimumSize(280, 180)
        if spec.width:
            self.setFixedWidth(spec.width)
        if spec.height:
            self.setFixedHeight(spec.height)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        header = QHBoxLayout()
        title = QLabel(spec.title, self)
        title.setProperty("role", "panel_title")
        header.addWidget(title)
        header.addStretch(1)
        close_btn = QToolButton(self)
        close_btn.setText("✕")
        close_btn.setAutoRaise(True)
        close_btn.clicked.connect(lambda: self.requested_close.emit(spec.overlay_id))
        header.addWidget(close_btn)
        layout.addLayout(header)
        self._content_host = QWidget(self)
        self._content_layout = QVBoxLayout(self._content_host)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        if content is not None:
            self._content_layout.addWidget(content)
        else:
            self._content_layout.addWidget(QLabel("Overlay content host", self._content_host))
        layout.addWidget(self._content_host, 1)
        self._escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self._escape_shortcut.activated.connect(lambda: self.requested_close.emit(spec.overlay_id))
        self._escape_shortcut.setEnabled(spec.close_on_escape)


class OverlayPortal(QWidget):
    overlay_changed = Signal(str, bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layers: dict[str, SafeOverlaySurface] = {}
        self._specs: dict[str, OverlaySpec] = {}
        self._scrim = InteractionScrim(self)
        self._scrim.hide()
        self._scrim.clicked.connect(self._close_topmost_blocking)
        self._decorations: dict[str, PassThroughDecoration] = {}
        self.hide()

    def resizeEvent(self, event):  # noqa: N802
        self._scrim.setGeometry(self.rect())
        self._realign_layers()
        super().resizeEvent(event)

    def register_overlay(self, spec: OverlaySpec, content_factory: Callable[[QWidget | None], QWidget] | None = None) -> SafeOverlaySurface:
        if spec.overlay_id in self._layers:
            return self._layers[spec.overlay_id]
        content = content_factory(self) if content_factory else QTextEdit(self)
        if isinstance(content, QTextEdit):
            content.setPlainText(f"Overlay {spec.overlay_id} ready.\n\nRole: {spec.role}\nStyle: {spec.style_key}")
            content.setReadOnly(True)
        surface = SafeOverlaySurface(spec, content=content, parent=self)
        surface.hide()
        surface.requested_close.connect(self.close_overlay)
        if spec.pass_through:
            surface.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            surface.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._layers[spec.overlay_id] = surface
        self._specs[spec.overlay_id] = spec
        return surface

    def register_decoration(self, decoration_id: str, decoration: PassThroughDecoration) -> None:
        decoration.setParent(self)
        decoration.hide()
        decoration.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._decorations[decoration_id] = decoration

    def show_decoration(self, decoration_id: str) -> None:
        decoration = self._decorations.get(decoration_id)
        if decoration is None:
            return
        decoration.setGeometry(self.rect())
        decoration.show()
        decoration.raise_()
        self.show()

    def hide_decoration(self, decoration_id: str) -> None:
        decoration = self._decorations.get(decoration_id)
        if decoration is None:
            return
        decoration.hide()
        self._refresh_visibility()

    def show_overlay(self, overlay_id: str) -> None:
        layer = self._layers.get(overlay_id)
        spec = self._specs.get(overlay_id)
        if layer is None or spec is None:
            raise KeyError(f"overlay not registered: {overlay_id}")
        if spec.scrim and not spec.pass_through:
            self._scrim.show()
            self._scrim.raise_()
        layer.show()
        layer.raise_()
        self._realign_layers()
        self.show()
        self.overlay_changed.emit(overlay_id, True)

    def close_overlay(self, overlay_id: str) -> None:
        layer = self._layers.get(overlay_id)
        if layer is None:
            return
        layer.hide()
        self.overlay_changed.emit(overlay_id, False)
        self._refresh_visibility()

    def _refresh_visibility(self) -> None:
        blocking = any(layer.isVisible() and self._specs[overlay_id].scrim and not self._specs[overlay_id].pass_through for overlay_id, layer in self._layers.items())
        self._scrim.setVisible(blocking)
        any_visible = blocking or any(layer.isVisible() for layer in self._layers.values()) or any(d.isVisible() for d in self._decorations.values())
        self.setVisible(any_visible)

    def _close_topmost_blocking(self) -> None:
        for overlay_id in reversed(list(self._layers.keys())):
            layer = self._layers[overlay_id]
            spec = self._specs[overlay_id]
            if layer.isVisible() and spec.scrim and not spec.pass_through and spec.close_on_scrim_click:
                self.close_overlay(overlay_id)
                return

    def _realign_layers(self) -> None:
        portal_rect = self.rect()
        for overlay_id, layer in self._layers.items():
            if not layer.isVisible():
                continue
            spec = self._specs[overlay_id]
            width = min(spec.width or max(420, portal_rect.width() - 48), max(280, portal_rect.width() - 24))
            height = min(spec.height or max(220, portal_rect.height() - 80), max(180, portal_rect.height() - 24))
            if spec.alignment == "right_sheet":
                layer.setGeometry(portal_rect.width() - width - 20, 20, width, height)
            elif spec.alignment == "left_sheet":
                layer.setGeometry(20, 20, width, height)
            elif spec.alignment == "bottom_sheet":
                layer.setGeometry((portal_rect.width() - width) // 2, portal_rect.height() - height - 20, width, height)
            else:
                layer.setGeometry((portal_rect.width() - width) // 2, (portal_rect.height() - height) // 2, width, height)


class FocusCircuit(QObject):
    focus_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._targets: list[QWidget] = []
        self._title_by_name: dict[str, str] = {}

    def register(self, widget: QWidget, title: str | None = None) -> None:
        if widget in self._targets:
            return
        if not widget.objectName():
            widget.setObjectName(_safe_name(title or widget.__class__.__name__))
        self._targets.append(widget)
        self._title_by_name[widget.objectName()] = title or widget.objectName()
        widget.installEventFilter(self)

    def wire(self) -> None:
        previous = None
        for widget in self._targets:
            if previous is not None:
                QWidget.setTabOrder(previous, widget)
            previous = widget

    def eventFilter(self, obj, event):  # noqa: N802
        if event.type() == QEvent.Type.FocusIn and isinstance(obj, QWidget):
            self.focus_changed.emit(obj.objectName() or obj.__class__.__name__)
        return super().eventFilter(obj, event)


class ShortcutRouter(QObject):
    intent_triggered = Signal(str)

    def __init__(self, host: QWidget, parent: QObject | None = None) -> None:
        super().__init__(parent or host)
        self._host = host
        self._shortcuts: list[tuple[ShortcutIntent, QShortcut]] = []
        self._active_page = "*"
        self._active_mode = "*"

    def set_context(self, page_id: str = "*", mode: str = "*") -> None:
        self._active_page = page_id or "*"
        self._active_mode = mode or "*"
        for intent, shortcut in self._shortcuts:
            page_ok = intent.page_id in ("*", self._active_page)
            mode_ok = intent.mode in ("*", self._active_mode)
            shortcut.setEnabled(intent.enabled and page_ok and mode_ok)

    def register_intent(self, intent: ShortcutIntent, callback: Callable[[], None]) -> None:
        shortcut = QShortcut(QKeySequence(intent.sequence), self._host)
        shortcut.activated.connect(lambda intent_id=intent.intent_id, cb=callback: self._dispatch(intent_id, cb))
        self._shortcuts.append((intent, shortcut))
        self.set_context(self._active_page, self._active_mode)

    def _dispatch(self, intent_id: str, callback: Callable[[], None]) -> None:
        callback()
        self.intent_triggered.emit(intent_id)

    def describe(self) -> list[dict[str, str]]:
        return [{"intent_id": intent.intent_id, "title": intent.title, "sequence": intent.sequence, "page_id": intent.page_id, "mode": intent.mode} for intent, _ in self._shortcuts]


class SafePageHost(QWidget):
    page_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pages: dict[str, QWidget] = {}
        self._focus: WeakKeyDictionary[QWidget, FocusCircuit] = WeakKeyDictionary()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.nav_list = QListWidget(self)
        self.nav_list.setMaximumWidth(240)
        self.nav_list.currentRowChanged.connect(self._on_row_changed)
        layout.addWidget(self.nav_list)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack, 1)

    def add_page(self, spec: PageSpec, page: QWidget, focus_circuit: FocusCircuit | None = None) -> None:
        self._pages[spec.page_id] = page
        self.stack.addWidget(page)
        item = QListWidgetItem(spec.title)
        item.setData(Qt.ItemDataRole.UserRole, spec.page_id)
        item.setToolTip(spec.subtitle)
        self.nav_list.addItem(item)
        if focus_circuit is not None:
            self._focus[page] = focus_circuit
        if self.stack.count() == 1:
            self.nav_list.setCurrentRow(0)

    def _on_row_changed(self, row: int) -> None:
        if row < 0:
            return
        item = self.nav_list.item(row)
        page_id = item.data(Qt.ItemDataRole.UserRole)
        page = self._pages[page_id]
        self.stack.setCurrentWidget(page)
        focus = self._focus.get(page)
        if focus is not None:
            focus.wire()
        self.page_changed.emit(page_id)

    def current_page_id(self) -> str:
        item = self.nav_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else ""


class InteractionSafetyAuditor(QObject):
    audit_completed = Signal(list)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.minimum_hit_size = 32
        self.preferred_hit_size = 40

    def audit_widget_tree(self, root: QWidget) -> list[SafetyFinding]:
        findings: list[SafetyFinding] = []
        for widget in _iter_widgets(root):
            findings.extend(self._audit_widget(widget))
        self.audit_completed.emit(findings)
        return findings

    def _audit_widget(self, widget: QWidget) -> list[SafetyFinding]:
        findings: list[SafetyFinding] = []
        name = widget.objectName() or widget.__class__.__name__
        geom = widget.rect()
        if _is_interactive(widget):
            if geom.width() < self.minimum_hit_size or geom.height() < self.minimum_hit_size:
                findings.append(SafetyFinding("tiny_hit_target", "warning", f"Interactive widget '{name}' is smaller than the minimum hit size.", _widget_path(widget), f"Grow the control to at least {self.minimum_hit_size}x{self.minimum_hit_size}.", {"width": geom.width(), "height": geom.height()}))
            elif geom.width() < self.preferred_hit_size or geom.height() < self.preferred_hit_size:
                findings.append(SafetyFinding("tight_hit_target", "info", f"Interactive widget '{name}' is clickable but tighter than the preferred hit size.", _widget_path(widget), f"Consider growing it toward {self.preferred_hit_size}x{self.preferred_hit_size}.", {"width": geom.width(), "height": geom.height()}))
        if widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) and _is_interactive(widget):
            findings.append(SafetyFinding("interactive_transparent", "error", f"Interactive widget '{name}' is marked transparent for mouse events.", _widget_path(widget), "Remove pass-through behavior from controls that users must interact with."))
        if isinstance(widget, QSplitter) and widget.childrenCollapsible():
            findings.append(SafetyFinding("splitter_collapsible", "warning", f"Splitter '{name}' allows child collapse to zero.", _widget_path(widget), "Set childrenCollapsible to False or explicitly manage legal collapsed states."))
        if widget.focusPolicy() == Qt.FocusPolicy.NoFocus and _is_interactive(widget):
            findings.append(SafetyFinding("no_focus_policy", "info", f"Interactive widget '{name}' has no keyboard focus policy.", _widget_path(widget), "Use TabFocus or StrongFocus for controls that should be reachable by keyboard."))
        return findings


class AuditConsole(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.header = PanelHeader("Interaction Audit", subtitle="Findings for focus, overlays, splitters and hit targets.", icon_name="shield", parent=self)
        layout.addWidget(self.header)
        self.editor = QTextEdit(self)
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor, 1)

    def set_findings(self, findings: Sequence[SafetyFinding]) -> None:
        if not findings:
            self.editor.setPlainText("No interaction safety findings. Clean as a whistle.")
            return
        blocks = []
        for finding in findings:
            blocks.append(f"[{finding.severity.upper()}] {finding.code}\nPath: {finding.widget_path or '(unknown)'}\nMessage: {finding.message}\nRecommendation: {finding.recommendation or '(none)'}\nDetails: {json.dumps(finding.details, ensure_ascii=False)}")
        self.editor.setPlainText("\n\n".join(blocks))


class InteractionWorkbench(QWidget):
    def __init__(self, profile_id: str = "operator_dense", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.profile_id = profile_id if profile_id in INTERACTION_PROFILES else "operator_dense"
        self.profile = INTERACTION_PROFILES[self.profile_id]
        self.auditor = InteractionSafetyAuditor(self)
        self.router = ShortcutRouter(self, self)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)
        self.template = GlassPanelTemplate(self, config=get_template_preset("dashboard"), title=f"Interaction Safety · {self.profile['title']}", subtitle=self.profile["description"], eyebrow="INTERACTION")
        root.addWidget(self.template, 1)
        self.page_host = SafePageHost(self.template)
        self.portal = OverlayPortal(self.template)
        self.portal.setGeometry(self.template.rect())
        self.portal.raise_()
        self.portal.hide()
        self.template.installEventFilter(self)
        self.audit_console = AuditConsole(self.template)
        self.trace_console = QTextEdit(self.template)
        self.trace_console.setReadOnly(True)
        self.trace_console.setPlainText("Trace console ready.")
        self.trace_console.setMinimumHeight(140)
        self.template.slots.main_slot.addWidget(self.page_host, 1)
        self.template.slots.side_slot.addWidget(self.audit_console, 1)
        self.template.slots.status_slot.addWidget(self.trace_console)
        self._build_pages()
        self._build_actions()
        self._build_overlays()
        self._wire_shortcuts()
        QTimer.singleShot(120, self.run_audit)

    def eventFilter(self, obj, event):  # noqa: N802
        if obj is self.template and event.type() == QEvent.Type.Resize:
            self.portal.setGeometry(self.template.rect())
        return super().eventFilter(obj, event)

    def _build_pages(self) -> None:
        for page_id, title, subtitle in [("overview", "Overview", "Healthy baseline page with explicit focus order."), ("controls", "Controls", "Dense controls, splitters and keyboard travel."), ("overlays", "Overlays", "Pass-through décor and blocking sheets.")]:
            page = QWidget(self.page_host)
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layout.setSpacing(10)
            page_layout.addWidget(QLabel(subtitle, page))
            focus = FocusCircuit(page)
            if page_id == "controls":
                splitter = FoundryContractSplitter(Qt.Orientation.Horizontal, page)
                left = QTextEdit(page)
                left.setObjectName("controls_text_left")
                left.setPlainText("Editable region A")
                right = QTextEdit(page)
                right.setObjectName("controls_text_right")
                right.setPlainText("Editable region B")
                splitter.addWidget(left)
                splitter.addWidget(right)
                splitter.setChildrenCollapsible(False)
                splitter.setSizes([420, 320])
                page_layout.addWidget(splitter, 1)
                focus.register(left, "Left Editor")
                focus.register(right, "Right Editor")
            else:
                primary = QPushButton(f"Primary action for {page_id}", page)
                primary.setObjectName(f"{page_id}_primary_button")
                secondary = QPushButton(f"Secondary action for {page_id}", page)
                secondary.setObjectName(f"{page_id}_secondary_button")
                note = QTextEdit(page)
                note.setObjectName(f"{page_id}_notes")
                note.setPlainText(f"Notes for {page_id} page.")
                page_layout.addWidget(primary)
                page_layout.addWidget(secondary)
                page_layout.addWidget(note, 1)
                focus.register(primary, f"{page_id} primary")
                focus.register(secondary, f"{page_id} secondary")
                focus.register(note, f"{page_id} notes")
            focus.focus_changed.connect(lambda name, pid=page_id: self._log(f"Focus → {pid} :: {name}"))
            self.page_host.add_page(PageSpec(page_id=page_id, title=title, subtitle=subtitle), page, focus)
        self.page_host.page_changed.connect(lambda page_id: self.router.set_context(page_id=page_id, mode="normal"))

    def _build_actions(self) -> None:
        actions = QuickActionsStrip(self.template)
        actions.add_action("Audit", icon_name="shield", on_click=lambda: self.run_audit())
        actions.add_action("Decor", icon_name="sparkles", on_click=lambda: self._toggle_decor())
        actions.add_action("Sheet", icon_name="layers", on_click=lambda: self.portal.show_overlay("sheet"))
        actions.add_action("Palette", icon_name="command", on_click=lambda: self.portal.show_overlay("palette"))
        self.template.slots.hero_slot.addWidget(actions)

    def _build_overlays(self) -> None:
        self.portal.register_decoration("hero_glow", PassThroughDecoration("Hero Glow", self.portal))
        self.portal.register_overlay(OverlaySpec("sheet", "Context Sheet", role="sheet", scrim=True, width=self.profile["sheet_width"], alignment="right_sheet", style_key="context_sheet"), content_factory=lambda parent: _overlay_text_widget("Context Sheet", "Blocking sheet used for deliberate secondary work without click theft from ornamental layers.", parent))
        self.portal.register_overlay(OverlaySpec("palette", "Command Palette", role="palette", scrim=True, width=680, alignment="center", style_key="command_palette"), content_factory=lambda parent: _overlay_text_widget("Command Palette", "Keyboard-first command plane with explicit close affordances and no zombie overlays.", parent))
        self.portal.register_overlay(OverlaySpec("toast", "Toast Stack", role="toast", scrim=False, pass_through=True, width=420, alignment="bottom_sheet", style_key="toast_stack"), content_factory=lambda parent: _overlay_text_widget("Toast Stack", "Pass-through transient notifications that should never block the workspace behind them.", parent))
        self.portal.overlay_changed.connect(lambda overlay_id, visible: self._log(f"Overlay {overlay_id} -> {'open' if visible else 'closed'}"))

    def _wire_shortcuts(self) -> None:
        intents = [ShortcutIntent("run_audit", "Run Audit", "Ctrl+Shift+A"), ShortcutIntent("show_sheet", "Show Sheet", "Ctrl+."), ShortcutIntent("show_palette", "Show Palette", "Ctrl+K"), ShortcutIntent("goto_overview", "Go Overview", "Alt+1"), ShortcutIntent("goto_controls", "Go Controls", "Alt+2"), ShortcutIntent("goto_overlays", "Go Overlays", "Alt+3")]
        self.router.register_intent(intents[0], self.run_audit)
        self.router.register_intent(intents[1], lambda: self.portal.show_overlay("sheet"))
        self.router.register_intent(intents[2], lambda: self.portal.show_overlay("palette"))
        self.router.register_intent(intents[3], lambda: self.page_host.nav_list.setCurrentRow(0))
        self.router.register_intent(intents[4], lambda: self.page_host.nav_list.setCurrentRow(1))
        self.router.register_intent(intents[5], lambda: self.page_host.nav_list.setCurrentRow(2))
        self.router.intent_triggered.connect(lambda intent_id: self._log(f"Shortcut → {intent_id}"))
        self.router.set_context(page_id=self.page_host.current_page_id() or "overview", mode="normal")

    def _toggle_decor(self) -> None:
        if any(decoration.isVisible() for decoration in self.portal._decorations.values()):
            self.portal.hide_decoration("hero_glow")
            self._log("Decoration disabled")
            return
        self.portal.show_decoration("hero_glow")
        self._log("Decoration enabled")

    def run_audit(self) -> None:
        findings = self.auditor.audit_widget_tree(self.template)
        self.audit_console.set_findings(findings)
        self.template.set_status_text(f"Audit completed: {len(findings)} finding(s).")
        self._log(f"Audit completed with {len(findings)} finding(s)")

    def _log(self, text: str) -> None:
        current = self.trace_console.toPlainText().strip()
        lines = [line for line in current.splitlines() if line.strip()]
        lines.append(text)
        self.trace_console.setPlainText("\n".join(lines[-18:]))


def _safe_name(text: str) -> str:
    cleaned = [char.lower() if char.isalnum() else "_" for char in text.strip()]
    joined = "".join(cleaned).strip("_")
    return joined or "unnamed"


def _iter_widgets(root: QWidget) -> Iterable[QWidget]:
    yield root
    for child in root.findChildren(QWidget):
        yield child


def _widget_path(widget: QWidget) -> str:
    parts: list[str] = []
    current: QWidget | None = widget
    while current is not None:
        name = current.objectName() or current.__class__.__name__
        parts.append(name)
        current = current.parentWidget()
    return " / ".join(reversed(parts))


def _is_interactive(widget: QWidget) -> bool:
    return isinstance(widget, (QPushButton, QToolButton, QTextEdit))


def _overlay_text_widget(title: str, body: str, parent: QWidget | None = None) -> QWidget:
    host = QWidget(parent)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    label = QLabel(title, host)
    label.setProperty("role", "panel_title")
    text = QTextEdit(host)
    text.setReadOnly(True)
    text.setPlainText(body)
    layout.addWidget(label)
    layout.addWidget(text, 1)
    return host


def list_interaction_profiles() -> list[str]:
    return sorted(INTERACTION_PROFILES.keys())


def get_interaction_profile(profile_id: str) -> dict[str, Any]:
    if profile_id not in INTERACTION_PROFILES:
        raise KeyError(f"unknown interaction profile: {profile_id}")
    return dict(INTERACTION_PROFILES[profile_id])


def build_interaction_preview(profile_id: str = "operator_dense", parent: QWidget | None = None) -> GlassPanelTemplate:
    host = GlassPanelTemplate(parent, config=get_template_preset("dashboard"), title=f"Interaction Preview · {profile_id}", subtitle=INTERACTION_PROFILES.get(profile_id, INTERACTION_PROFILES['operator_dense'])["description"], eyebrow="INTERACTION")
    workbench = InteractionWorkbench(profile_id=profile_id, parent=host)
    host.slots.main_slot.addWidget(workbench, 1)
    host.slots.side_slot.addWidget(LoadingStateCard("Interaction contracts ready", parent=host))
    host.set_status_text(f"Interaction preview '{profile_id}' loaded.")
    return host


def build_interaction_audit_console(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("dashboard"), title="Audit Console", subtitle="Inspect click safety, focus travel and splitters.", eyebrow="AUDIT")
    template.slots.main_slot.addWidget(InteractionWorkbench("diagnostic_lab", parent=template), 1)
    template.set_status_text("Diagnostic audit console loaded.")
    return template


def build_interaction_overlay_portal(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("dashboard"), title="Overlay Portal", subtitle="Pass-through décor plus blocking sheets.", eyebrow="OVERLAY")
    workbench = InteractionWorkbench("analyst_review", parent=template)
    template.slots.main_slot.addWidget(workbench, 1)
    workbench.portal.show_decoration("hero_glow")
    workbench.portal.show_overlay("toast")
    template.set_status_text("Overlay portal preview loaded.")
    return template


def build_interaction_shortcut_router(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("dashboard"), title="Shortcut Router", subtitle="Discoverable keyboard intents with context routing.", eyebrow="SHORTCUTS")
    workbench = InteractionWorkbench("operator_dense", parent=template)
    template.slots.main_slot.addWidget(workbench, 1)
    legend = QTextEdit(template)
    legend.setReadOnly(True)
    legend.setPlainText(json.dumps(workbench.router.describe(), indent=2, ensure_ascii=False))
    template.slots.side_slot.addWidget(legend)
    template.set_status_text("Shortcut router preview loaded.")
    return template


def iter_foundry_interaction_catalog_specs() -> tuple[InteractionCatalogEntrySpec, ...]:
    entries: list[InteractionCatalogEntrySpec] = []
    for spec in CATALOG_PAYLOADS:
        profile_id = spec["entry_id"].replace("interaction_profile_", "") if spec["entry_id"].startswith("interaction_profile_") else None
        if spec["entry_id"] == "interaction_audit_console":
            builder = build_interaction_audit_console
        elif spec["entry_id"] == "interaction_shortcut_router":
            builder = build_interaction_shortcut_router
        elif spec["entry_id"] == "interaction_overlay_portal":
            builder = build_interaction_overlay_portal
        else:
            builder = lambda parent, pid=profile_id or "operator_dense": build_interaction_preview(pid, parent)
        entries.append(InteractionCatalogEntrySpec(entry_id=spec["entry_id"], title=spec["title"], subtitle=spec["subtitle"], description=spec["description"], builder=builder, keywords=tuple(spec.get("keywords", [])), icon_name=spec.get("icon_name", "shield"), sort_order=int(spec.get("sort_order", 900)), best_for="interaction hardening, overlays, focus, keyboard travel", use_when="you want luxurious interfaces that still behave like disciplined tools"))
    return tuple(entries)


def build_foundry_interaction_catalog_entry(spec: InteractionCatalogEntrySpec, parent: QWidget | None = None) -> QWidget:
    return spec.builder(parent)


def register_builtin_foundry_interaction() -> tuple[str, ...]:
    registered: list[str] = []
    for spec in iter_foundry_interaction_catalog_specs():
        try:
            register_catalog_entry(GlassCatalogEntry(entry_id=spec.entry_id, title=spec.title, subtitle=spec.subtitle, description=spec.description, category=spec.category, tags=spec.tags, status=spec.status, keywords=spec.keywords, best_for=spec.best_for, use_when=spec.use_when, sort_order=spec.sort_order, icon_name=spec.icon_name, builder=spec.builder))
            registered.append(spec.entry_id)
        except Exception:
            registered.append(spec.entry_id)
    return tuple(registered)


def interaction_registry_snapshot() -> dict[str, Any]:
    return {"version": INTERACTION_SAFETY_VERSION, "profiles": list_interaction_profiles(), "overlays": sorted(OVERLAY_PATTERNS.keys()), "catalog_entries": [spec.entry_id for spec in iter_foundry_interaction_catalog_specs()]}


def build_interaction_demo_app(parent: QWidget | None = None) -> QWidget:
    return InteractionWorkbench(parent=parent)
