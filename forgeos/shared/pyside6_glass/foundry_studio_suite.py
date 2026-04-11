from __future__ import annotations

"""Foundry Studio Suite for PySide6 Glass.

Third heavy injection layer.

Purpose:
- turn the foundry foundation and interaction layers into a practical authoring cockpit
- provide gallery, inspector, doctor, cookbook and export tooling in one disciplined shell
- keep live preview deterministic by rebuilding inside an owned stage host
- make recipe authoring feel like composition instead of widget wrestling
- provide future hooks for compile, diff, migrate and snapshot workflows
"""

from copy import deepcopy
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from PySide6.QtCore import QFileSystemWatcher, QObject, Qt, Signal
from PySide6.QtGui import QAction, QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .catalog import GlassCatalogEntry, register_catalog_entry
from .primitives import PanelHeader, QuickActionsStrip, StatCard
from .foundry_foundation import (
    BEAUTY_PROFILES,
    COLOR_STORIES,
    MOTION_PROFILES,
    build_foundry_preview,
    foundry_registry_snapshot,
    get_foundry_recipe,
    list_beauty_profiles,
    list_color_stories,
    list_foundry_recipes,
    list_layout_packs,
    list_motion_profiles,
    list_shell_packs,
    validate_foundry_recipe,
)
from .foundry_interaction import (
    INTERACTION_REFERENCE_NOTES,
    build_interaction_audit_console,
    list_interaction_profiles,
)

STUDIO_SUITE_VERSION = "foundry.studio_suite.v1"
STUDIO_SUITE_CATEGORY = "Foundry Studio"
STUDIO_REFERENCE_NOTES = '## Studio Pattern 1\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 2\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 3\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 4\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 5\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 6\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 7\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 8\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 9\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 10\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 11\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 12\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 13\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 14\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 15\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 16\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 17\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 18\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 19\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 20\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 21\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 22\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 23\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 24\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 25\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 26\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 27\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 28\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 29\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 30\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 31\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 32\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 33\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 34\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 35\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 36\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 37\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 38\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 39\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 40\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 41\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 42\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 43\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 44\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 45\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 46\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 47\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 48\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 49\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 50\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 51\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 52\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 53\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 54\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 55\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 56\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 57\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 58\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 59\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.\n\n## Studio Pattern 60\n- Goal: make authoring gorgeous interfaces feel deterministic instead of artisanal chaos.\n- Rule: the studio edits variants, not live widget internals.\n- Rule: preview rebuilds must swap owned stage children, never stack fresh shells over old ones.\n- Rule: every recipe variant must declare beauty profile, color story, motion profile, density and interaction profile.\n- Rule: the doctor should flag missing empty/loading/error states, risky overlays and questionable hit targets before shipping.\n- Rule: export is pure JSON so future compilers, differs and code generators can consume it without GUI baggage.\n- Pattern: one preview stage, one outline, one inspector, one cookbook, one doctor, all cooperating like a pit crew.\n- Commentary: if a design studio starts behaving like a haunted house, it means the ownership model got sloppy long before the gradients looked sexy.'
STUDIO_COOKBOOK = [
  {
    "slug": "play_01",
    "title": "Signature Recipe Play 01",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_02",
    "title": "Signature Recipe Play 02",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_03",
    "title": "Signature Recipe Play 03",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_04",
    "title": "Signature Recipe Play 04",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_05",
    "title": "Signature Recipe Play 05",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_06",
    "title": "Signature Recipe Play 06",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_07",
    "title": "Signature Recipe Play 07",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_08",
    "title": "Signature Recipe Play 08",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_09",
    "title": "Signature Recipe Play 09",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_10",
    "title": "Signature Recipe Play 10",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_11",
    "title": "Signature Recipe Play 11",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_12",
    "title": "Signature Recipe Play 12",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_13",
    "title": "Signature Recipe Play 13",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_14",
    "title": "Signature Recipe Play 14",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_15",
    "title": "Signature Recipe Play 15",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_16",
    "title": "Signature Recipe Play 16",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_17",
    "title": "Signature Recipe Play 17",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_18",
    "title": "Signature Recipe Play 18",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_19",
    "title": "Signature Recipe Play 19",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_20",
    "title": "Signature Recipe Play 20",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_21",
    "title": "Signature Recipe Play 21",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_22",
    "title": "Signature Recipe Play 22",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_23",
    "title": "Signature Recipe Play 23",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_24",
    "title": "Signature Recipe Play 24",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_25",
    "title": "Signature Recipe Play 25",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_26",
    "title": "Signature Recipe Play 26",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_27",
    "title": "Signature Recipe Play 27",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_28",
    "title": "Signature Recipe Play 28",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_29",
    "title": "Signature Recipe Play 29",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_30",
    "title": "Signature Recipe Play 30",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_31",
    "title": "Signature Recipe Play 31",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_32",
    "title": "Signature Recipe Play 32",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_33",
    "title": "Signature Recipe Play 33",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_34",
    "title": "Signature Recipe Play 34",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_35",
    "title": "Signature Recipe Play 35",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_36",
    "title": "Signature Recipe Play 36",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_37",
    "title": "Signature Recipe Play 37",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_38",
    "title": "Signature Recipe Play 38",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_39",
    "title": "Signature Recipe Play 39",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_40",
    "title": "Signature Recipe Play 40",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_41",
    "title": "Signature Recipe Play 41",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_42",
    "title": "Signature Recipe Play 42",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_43",
    "title": "Signature Recipe Play 43",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_44",
    "title": "Signature Recipe Play 44",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_45",
    "title": "Signature Recipe Play 45",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_46",
    "title": "Signature Recipe Play 46",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_47",
    "title": "Signature Recipe Play 47",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_48",
    "title": "Signature Recipe Play 48",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_49",
    "title": "Signature Recipe Play 49",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_50",
    "title": "Signature Recipe Play 50",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_51",
    "title": "Signature Recipe Play 51",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_52",
    "title": "Signature Recipe Play 52",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_53",
    "title": "Signature Recipe Play 53",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_54",
    "title": "Signature Recipe Play 54",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_55",
    "title": "Signature Recipe Play 55",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_56",
    "title": "Signature Recipe Play 56",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_57",
    "title": "Signature Recipe Play 57",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_58",
    "title": "Signature Recipe Play 58",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_59",
    "title": "Signature Recipe Play 59",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_60",
    "title": "Signature Recipe Play 60",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_61",
    "title": "Signature Recipe Play 61",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_62",
    "title": "Signature Recipe Play 62",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_63",
    "title": "Signature Recipe Play 63",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_64",
    "title": "Signature Recipe Play 64",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_65",
    "title": "Signature Recipe Play 65",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_66",
    "title": "Signature Recipe Play 66",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_67",
    "title": "Signature Recipe Play 67",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_68",
    "title": "Signature Recipe Play 68",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_69",
    "title": "Signature Recipe Play 69",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_70",
    "title": "Signature Recipe Play 70",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_71",
    "title": "Signature Recipe Play 71",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_72",
    "title": "Signature Recipe Play 72",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_73",
    "title": "Signature Recipe Play 73",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_74",
    "title": "Signature Recipe Play 74",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_75",
    "title": "Signature Recipe Play 75",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_76",
    "title": "Signature Recipe Play 76",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_77",
    "title": "Signature Recipe Play 77",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_78",
    "title": "Signature Recipe Play 78",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_79",
    "title": "Signature Recipe Play 79",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  },
  {
    "slug": "play_80",
    "title": "Signature Recipe Play 80",
    "summary": "Composable playbook for premium internal tools with deliberate hierarchy, safe overlays and resilient layout behavior.",
    "when_to_use": "Use when the team wants lush visuals without gambling on broken resize or dead buttons.",
    "moves": [
      "Start from a shell pack that matches the job, not the mood board.",
      "Keep hero, navigation, workspace, side inspector and status lanes explicit.",
      "Prefer deferred side panels and lazy metrics tabs for heavy surfaces.",
      "Use interaction profiles to tune hit target sizes and focus travel.",
      "Run the doctor before exporting a variant so the studio catches sketchy choices early."
    ]
  }
]


@dataclass(frozen=True, slots=True)
class StudioCatalogEntrySpec:
    entry_id: str
    title: str
    subtitle: str
    description: str
    category: str = STUDIO_SUITE_CATEGORY
    tags: tuple[str, ...] = ("foundry", "studio", "gallery", "doctor", "tooling")
    status: str = "stable"
    keywords: tuple[str, ...] = ()
    best_for: str = "Recipe authoring, beauty tuning, safety review and export"
    use_when: str = "Use when teams need a cockpit for composing and validating recipe variants."
    sort_order: int = 930
    icon_name: str | None = "palette"


@dataclass(slots=True)
class StudioVariantSelection:
    recipe_id: str
    beauty_profile: str
    color_story: str
    motion_profile: str
    layout_pack: str
    shell_pack: str
    interaction_profile: str
    density: str
    theme_override: str = ""
    preset_override: str = ""
    compact_mode: bool = False
    diagnostics_open: bool = True
    cookbook_open: bool = True
    export_pretty: bool = True


@dataclass(slots=True)
class DoctorFinding:
    severity: str
    code: str
    title: str
    detail: str
    hint: str = ""


@dataclass(slots=True)
class RecipeSnapshot:
    recipe_id: str
    variant_name: str
    payload: dict[str, Any]
    findings: list[DoctorFinding] = field(default_factory=list)


@dataclass(slots=True)
class StudioToolSpec:
    tool_id: str
    title: str
    description: str
    hotkey: str = ""


class VariantPatchCommand(QUndoCommand):
    def __init__(self, workspace: "FoundryStudioWorkspace", before: StudioVariantSelection, after: StudioVariantSelection, text: str) -> None:
        super().__init__(text)
        self.workspace = workspace
        self.before = deepcopy(before)
        self.after = deepcopy(after)

    def undo(self) -> None:
        self.workspace.apply_selection(self.before, from_history=True)

    def redo(self) -> None:
        self.workspace.apply_selection(self.after, from_history=True)


class PreviewStageHost(QFrame):
    preview_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._layout = layout
        self._current: QWidget | None = None
        self._current_key = ""

    def set_preview(self, key: str, widget: QWidget) -> None:
        if self._current is not None:
            self._layout.removeWidget(self._current)
            self._current.setParent(None)
            self._current.deleteLater()
        self._current = widget
        self._current_key = key
        self._layout.addWidget(widget, 1)
        self.preview_changed.emit(key)

    def current_key(self) -> str:
        return self._current_key


class StudioDoctor(QObject):
    findings_changed = Signal(int)

    def inspect_payload(self, payload: Mapping[str, Any]) -> list[DoctorFinding]:
        findings: list[DoctorFinding] = []
        meta = dict(payload.get("meta") or {})
        experience = dict(payload.get("experience") or {})
        behavior = dict(payload.get("behavior") or {})
        regions = dict(payload.get("regions") or {})
        surfaces = list(payload.get("surfaces") or [])
        data = dict(payload.get("data") or {})
        if not meta.get("id"):
            findings.append(DoctorFinding("error", "meta.id", "Recipe id missing", "Every recipe needs a stable identifier.", "Set meta.id so exports and diffs stop guessing."))
        if experience.get("beauty_profile") not in BEAUTY_PROFILES:
            findings.append(DoctorFinding("error", "experience.beauty_profile", "Unknown beauty profile", "The selected beauty profile is not registered.", "Choose one of the built-in beauty profiles or register a new one."))
        if experience.get("color_story") not in COLOR_STORIES:
            findings.append(DoctorFinding("error", "experience.color_story", "Unknown color story", "The selected color story is not registered.", "Pick a valid story to keep theme resolution deterministic."))
        if experience.get("motion_profile") not in MOTION_PROFILES:
            findings.append(DoctorFinding("warning", "experience.motion_profile", "Motion profile unresolved", "Motion will fall back to defaults.", "Prefer an explicit profile so tempo remains intentional."))
        for region in ("main", "nav", "status"):
            if region not in regions:
                findings.append(DoctorFinding("warning", f"regions.{region}", f"Missing {region} region", "The shell can still render, but composition becomes guessy.", "Declare canonical regions even if some are visually quiet."))
        if not surfaces:
            findings.append(DoctorFinding("error", "surfaces", "No surfaces declared", "A recipe without surfaces is decorative scaffolding with nowhere to work.", "Add at least one hero, workspace or inspector surface."))
        else:
            for surface in surfaces:
                if not isinstance(surface, Mapping):
                    findings.append(DoctorFinding("error", "surfaces.item", "Surface payload malformed", "One of the surfaces is not a mapping.", "Keep surface definitions plain dicts for export stability."))
                    continue
                surface_id = str(surface.get("id") or "surface")
                states = surface.get("states") or {}
                if not states:
                    findings.append(DoctorFinding("warning", f"surface.{surface_id}.states", "No UI states declared", "Loading/empty/error fallbacks are missing for this surface.", "Declare states so failure modes still look designed."))
        ui_states = dict(data.get("ui_states") or {})
        for state_name in ("loading", "empty", "error"):
            if state_name not in ui_states:
                findings.append(DoctorFinding("warning", f"data.ui_states.{state_name}", f"Missing {state_name} treatment", "Global UI state treatment is absent.", "Add a treatment so the studio doctor can enforce graceful degradation."))
        perf = dict(behavior.get("performance") or {})
        if not perf.get("lazy_tabs", False):
            findings.append(DoctorFinding("info", "behavior.performance.lazy_tabs", "Lazy tabs disabled", "Tabs still work, but heavier views may feel wasteful.", "Enable lazy_tabs when recipes include charts, feeds or inspectors."))
        if not perf.get("deferred_panels", False):
            findings.append(DoctorFinding("info", "behavior.performance.deferred_panels", "Deferred panels disabled", "Side regions may initialize too early.", "Deferred side panels keep previews calmer and safer."))
        self.findings_changed.emit(len(findings))
        return findings


class DoctorPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(PanelHeader("Doctor", subtitle="Audit recipe safety and beauty contracts"))
        self.summary = QLabel("No findings yet")
        root.addWidget(self.summary)
        self.listing = QTreeWidget(self)
        self.listing.setHeaderLabels(["Severity", "Code", "Title", "Hint"])
        self.listing.setAlternatingRowColors(True)
        root.addWidget(self.listing, 1)
        self.detail = QTextEdit(self)
        self.detail.setReadOnly(True)
        root.addWidget(self.detail, 1)
        self._cache: list[DoctorFinding] = []
        self.listing.currentItemChanged.connect(self._on_item_changed)

    def set_findings(self, findings: Sequence[DoctorFinding]) -> None:
        self._cache = list(findings)
        self.listing.clear()
        self.detail.clear()
        self.summary.setText(f"{len(findings)} findings")
        for finding in findings:
            item = QTreeWidgetItem([finding.severity.upper(), finding.code, finding.title, finding.hint])
            self.listing.addTopLevelItem(item)
        if self.listing.topLevelItemCount():
            self.listing.setCurrentItem(self.listing.topLevelItem(0))

    def _on_item_changed(self, current: QTreeWidgetItem | None, previous: QTreeWidgetItem | None) -> None:
        if current is None:
            self.detail.clear()
            return
        index = self.listing.indexOfTopLevelItem(current)
        if index < 0 or index >= len(self._cache):
            self.detail.clear()
            return
        finding = self._cache[index]
        self.detail.setPlainText(f"Severity: {finding.severity}\nCode: {finding.code}\nTitle: {finding.title}\n\n{finding.detail}\n\nHint: {finding.hint or '—'}")


class CookbookPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(PanelHeader("Cookbook", subtitle="Playbooks for building pretty interfaces without stepping on rakes"))
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Search cookbook patterns…")
        root.addWidget(self.search)
        self.listing = QListWidget(self)
        root.addWidget(self.listing, 1)
        self.detail = QTextEdit(self)
        self.detail.setReadOnly(True)
        root.addWidget(self.detail, 1)
        self._entries = STUDIO_COOKBOOK
        self.search.textChanged.connect(self._rebuild)
        self.listing.currentRowChanged.connect(self._render)
        self._rebuild("")

    def _rebuild(self, needle: str) -> None:
        self.listing.clear()
        needle = needle.strip().lower()
        for entry in self._entries:
            blob = json.dumps(entry).lower()
            if needle and needle not in blob:
                continue
            item = QListWidgetItem(entry["title"])
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.listing.addItem(item)
        if self.listing.count():
            self.listing.setCurrentRow(0)
        else:
            self.detail.setPlainText("No cookbook entries match that search.")

    def _render(self, row: int) -> None:
        item = self.listing.item(row)
        if item is None:
            self.detail.clear()
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        moves = "\n".join(f"- {move}" for move in entry.get("moves", []))
        text = f"{entry['title']}\n\n{entry['summary']}\n\nWhen to use\n{entry['when_to_use']}\n\nMoves\n{moves}"
        self.detail.setPlainText(text)


class OutlinePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(PanelHeader("Recipe Outline", subtitle="Regions, surfaces and state cues"))
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(["Node", "Value"])
        root.addWidget(self.tree, 1)

    def set_payload(self, payload: Mapping[str, Any]) -> None:
        self.tree.clear()
        for section_name in ("meta", "experience", "shell", "regions", "surfaces", "behavior", "data", "quality"):
            value = payload.get(section_name)
            node = QTreeWidgetItem([section_name, type(value).__name__])
            self.tree.addTopLevelItem(node)
            self._append(node, value)
        self.tree.expandToDepth(1)

    def _append(self, parent_item: QTreeWidgetItem, value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                item = QTreeWidgetItem([str(key), self._render_value(child)])
                parent_item.addChild(item)
                self._append(item, child)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for index, child in enumerate(value):
                item = QTreeWidgetItem([f"[{index}]", self._render_value(child)])
                parent_item.addChild(item)
                self._append(item, child)

    @staticmethod
    def _render_value(value: Any) -> str:
        if isinstance(value, Mapping):
            return "dict"
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return f"list({len(value)})"
        text = str(value)
        return text if len(text) < 80 else text[:77] + "..."


class VariantInspectorPanel(QWidget):
    selection_requested = Signal(object)
    export_requested = Signal()
    refresh_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(PanelHeader("Variant Inspector", subtitle="Tune beauty, motion, layout and interaction"))
        self.form = QGridLayout()
        self.form.setHorizontalSpacing(8)
        self.form.setVerticalSpacing(8)
        root.addLayout(self.form)
        self.recipe = self._combo("Recipe", list_foundry_recipes())
        self.beauty = self._combo("Beauty", list_beauty_profiles())
        self.color = self._combo("Color", list_color_stories())
        self.motion = self._combo("Motion", list_motion_profiles())
        self.layout_pack = self._combo("Layout", list_layout_packs())
        self.shell_pack = self._combo("Shell", list_shell_packs())
        self.interaction = self._combo("Interaction", list_interaction_profiles())
        self.density = self._combo("Density", ["compact", "comfortable", "spacious"])
        row = self.form.rowCount()
        self.theme_override = QLineEdit(self)
        self.theme_override.setPlaceholderText("Optional theme override")
        self.form.addWidget(QLabel("Theme override"), row, 0)
        self.form.addWidget(self.theme_override, row, 1)
        row += 1
        self.preset_override = QLineEdit(self)
        self.preset_override.setPlaceholderText("Optional preset override")
        self.form.addWidget(QLabel("Preset override"), row, 0)
        self.form.addWidget(self.preset_override, row, 1)
        row += 1
        self.compact = QCheckBox("Compact mode", self)
        self.form.addWidget(self.compact, row, 0, 1, 2)
        row += 1
        self.diag_open = QCheckBox("Diagnostics dock open", self)
        self.diag_open.setChecked(True)
        self.form.addWidget(self.diag_open, row, 0, 1, 2)
        row += 1
        self.cookbook_open = QCheckBox("Cookbook dock open", self)
        self.cookbook_open.setChecked(True)
        self.form.addWidget(self.cookbook_open, row, 0, 1, 2)
        row += 1
        self.pretty = QCheckBox("Pretty export JSON", self)
        self.pretty.setChecked(True)
        self.form.addWidget(self.pretty, row, 0, 1, 2)
        self.actions = QuickActionsStrip(parent=self)
        self.apply_button = self.actions.add_action("Apply")
        self.export_button = self.actions.add_action("Export")
        self.refresh_button = self.actions.add_action("Rebuild")
        root.addWidget(self.actions)
        self.apply_button.clicked.connect(self._emit_selection)
        self.export_button.clicked.connect(self.export_requested.emit)
        self.refresh_button.clicked.connect(self.refresh_requested.emit)

    def _combo(self, label: str, items: Sequence[str]) -> QComboBox:
        combo = QComboBox(self)
        combo.addItems(list(items))
        row = self.form.rowCount()
        self.form.addWidget(QLabel(label), row, 0)
        self.form.addWidget(combo, row, 1)
        return combo

    def set_selection(self, selection: StudioVariantSelection) -> None:
        self._set_combo(self.recipe, selection.recipe_id)
        self._set_combo(self.beauty, selection.beauty_profile)
        self._set_combo(self.color, selection.color_story)
        self._set_combo(self.motion, selection.motion_profile)
        self._set_combo(self.layout_pack, selection.layout_pack)
        self._set_combo(self.shell_pack, selection.shell_pack)
        self._set_combo(self.interaction, selection.interaction_profile)
        self._set_combo(self.density, selection.density)
        self.theme_override.setText(selection.theme_override)
        self.preset_override.setText(selection.preset_override)
        self.compact.setChecked(selection.compact_mode)
        self.diag_open.setChecked(selection.diagnostics_open)
        self.cookbook_open.setChecked(selection.cookbook_open)
        self.pretty.setChecked(selection.export_pretty)

    def current_selection(self) -> StudioVariantSelection:
        return StudioVariantSelection(
            recipe_id=self.recipe.currentText(),
            beauty_profile=self.beauty.currentText(),
            color_story=self.color.currentText(),
            motion_profile=self.motion.currentText(),
            layout_pack=self.layout_pack.currentText(),
            shell_pack=self.shell_pack.currentText(),
            interaction_profile=self.interaction.currentText(),
            density=self.density.currentText(),
            theme_override=self.theme_override.text().strip(),
            preset_override=self.preset_override.text().strip(),
            compact_mode=self.compact.isChecked(),
            diagnostics_open=self.diag_open.isChecked(),
            cookbook_open=self.cookbook_open.isChecked(),
            export_pretty=self.pretty.isChecked(),
        )

    def _emit_selection(self) -> None:
        self.selection_requested.emit(self.current_selection())

    @staticmethod
    def _set_combo(combo: QComboBox, value: str) -> None:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)


class ExportPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(PanelHeader("Variant Export", subtitle="JSON payload ready for compiler or patch injector"))
        self.editor = QTextEdit(self)
        self.editor.setReadOnly(True)
        root.addWidget(self.editor, 1)

    def set_payload(self, payload: Mapping[str, Any], *, pretty: bool = True) -> None:
        text = json.dumps(payload, indent=2 if pretty else None, ensure_ascii=False)
        self.editor.setPlainText(text)


class RegistryPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(PanelHeader("Registry Snapshot", subtitle="What the foundry currently knows"))
        self.metrics = QGridLayout()
        root.addLayout(self.metrics)
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        root.addWidget(self.text, 1)

    def set_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        while self.metrics.count():
            item = self.metrics.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        pairs = [
            ("recipes", len(snapshot.get("recipes", []))),
            ("beauty", len(snapshot.get("beauty_profiles", []))),
            ("colors", len(snapshot.get("color_stories", []))),
            ("motion", len(snapshot.get("motion_profiles", []))),
            ("layout", len(snapshot.get("layout_packs", []))),
            ("shell", len(snapshot.get("shell_packs", []))),
        ]
        for idx, (label, value) in enumerate(pairs):
            card = StatCard(label, str(value), subtitle="registered", parent=self)
            self.metrics.addWidget(card, idx // 3, idx % 3)
        self.text.setPlainText(json.dumps(snapshot, indent=2, ensure_ascii=False))


class StudioFileWatcher(QObject):
    changed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self.changed)

    def watch(self, path: str) -> None:
        if path not in set(self._watcher.files()):
            self._watcher.addPath(path)


class FoundryStudioWorkspace(QWidget):
    selection_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.undo_stack = QUndoStack(self)
        self.doctor = StudioDoctor(self)
        self.file_watcher = StudioFileWatcher(self)
        self.file_watcher.changed.connect(self._on_watched_file_changed)
        self.selection = self._build_default_selection()
        self._last_export_path = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.chrome = QuickActionsStrip(parent=self)
        self.action_apply = self.chrome.add_action("Apply variant")
        self.action_export = self.chrome.add_action("Export snapshot")
        self.action_rebuild = self.chrome.add_action("Rebuild preview")
        self.action_undo = self.chrome.add_action("Undo")
        self.action_redo = self.chrome.add_action("Redo")
        root.addWidget(self.chrome)

        self.shell = QSplitter(Qt.Orientation.Horizontal, self)
        self.shell.setChildrenCollapsible(False)
        root.addWidget(self.shell, 1)

        self.sidebar = QTabWidget(self)
        self.inspector = VariantInspectorPanel(self)
        self.outline = OutlinePanel(self)
        self.registry = RegistryPanel(self)
        self.export_panel = ExportPanel(self)
        self.sidebar.addTab(self.inspector, "Inspector")
        self.sidebar.addTab(self.outline, "Outline")
        self.sidebar.addTab(self.registry, "Registry")
        self.sidebar.addTab(self.export_panel, "Export")
        self.shell.addWidget(self.sidebar)

        self.stage_tabs = QTabWidget(self)
        self.preview_host = PreviewStageHost(self)
        self.preview_scroll = QScrollArea(self)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setWidget(self.preview_host)
        self.stage_tabs.addTab(self.preview_scroll, "Preview")
        self.audit_console = build_interaction_audit_console(None)
        self.stage_tabs.addTab(self.audit_console, "Interaction Notes")
        self.notes = QTextEdit(self)
        self.notes.setReadOnly(True)
        self.notes.setPlainText(STUDIO_REFERENCE_NOTES + "\n\n" + INTERACTION_REFERENCE_NOTES)
        self.stage_tabs.addTab(self.notes, "Reference")
        self.shell.addWidget(self.stage_tabs)
        self.shell.setStretchFactor(0, 0)
        self.shell.setStretchFactor(1, 1)
        self.shell.setSizes([380, 1180])

        self.doctor_panel = DoctorPanel(self)
        self.cookbook_panel = CookbookPanel(self)

        self.action_apply.clicked.connect(lambda: self.apply_selection(self.inspector.current_selection()))
        self.action_export.clicked.connect(self.export_current_snapshot)
        self.action_rebuild.clicked.connect(self.rebuild_preview)
        self.action_undo.clicked.connect(self.undo_stack.undo)
        self.action_redo.clicked.connect(self.undo_stack.redo)
        self.inspector.selection_requested.connect(self.apply_selection)
        self.inspector.export_requested.connect(self.export_current_snapshot)
        self.inspector.refresh_requested.connect(self.rebuild_preview)

        self.inspector.set_selection(self.selection)
        self.rebuild_preview()

    def _build_default_selection(self) -> StudioVariantSelection:
        recipe_id = list_foundry_recipes()[0]
        payload = get_foundry_recipe(recipe_id).payload
        return StudioVariantSelection(
            recipe_id=recipe_id,
            beauty_profile=str(payload.get("experience", {}).get("beauty_profile", list_beauty_profiles()[0])),
            color_story=str(payload.get("experience", {}).get("color_story", list_color_stories()[0])),
            motion_profile=str(payload.get("experience", {}).get("motion_profile", list_motion_profiles()[0])),
            layout_pack=list_layout_packs()[0],
            shell_pack=list_shell_packs()[0],
            interaction_profile=list_interaction_profiles()[0],
            density=str(payload.get("meta", {}).get("density", "comfortable")),
            diagnostics_open=True,
            cookbook_open=True,
            export_pretty=True,
        )

    def _build_variant_payload(self, selection: StudioVariantSelection) -> dict[str, Any]:
        payload = deepcopy(get_foundry_recipe(selection.recipe_id).payload)
        payload.setdefault("meta", {})["density"] = selection.density
        payload.setdefault("experience", {})["beauty_profile"] = selection.beauty_profile
        payload.setdefault("experience", {})["color_story"] = selection.color_story
        payload.setdefault("experience", {})["motion_profile"] = selection.motion_profile
        payload.setdefault("behavior", {})["layout_pack"] = selection.layout_pack
        payload.setdefault("behavior", {})["shell_pack"] = selection.shell_pack
        payload.setdefault("behavior", {})["interaction_profile"] = selection.interaction_profile
        if selection.theme_override:
            payload.setdefault("shell", {}).setdefault("window", {})["theme_override"] = selection.theme_override
        if selection.preset_override:
            payload.setdefault("behavior", {})["preset_override"] = selection.preset_override
        payload.setdefault("quality", {}).setdefault("beauty_checks", {})["studio_reviewed"] = True
        if selection.compact_mode:
            rhythm = payload.setdefault("experience", {}).setdefault("rhythm", {})
            rhythm["spacing_scale"] = min(float(rhythm.get("spacing_scale", 1.0)), 0.92)
            rhythm["surface_layering"] = max(float(rhythm.get("surface_layering", 0.8)), 0.78)
        return validate_foundry_recipe(payload)

    def apply_selection(self, selection: StudioVariantSelection, *, from_history: bool = False) -> None:
        old = deepcopy(self.selection)
        self.selection = deepcopy(selection)
        self.inspector.set_selection(self.selection)
        if not from_history and old != self.selection:
            self.undo_stack.push(VariantPatchCommand(self, old, self.selection, "Apply studio variant"))
            return
        self.rebuild_preview()
        self.selection_changed.emit(self.selection)

    def rebuild_preview(self) -> None:
        payload = self._build_variant_payload(self.selection)
        findings = self.doctor.inspect_payload(payload)
        self.doctor_panel.set_findings(findings)
        self.outline.set_payload(payload)
        self.export_panel.set_payload(payload, pretty=self.selection.export_pretty)
        self.registry.set_snapshot(foundry_registry_snapshot())
        preview = build_foundry_preview(payload)
        key = f"{self.selection.recipe_id}:{self.selection.beauty_profile}:{self.selection.color_story}"
        self.preview_host.set_preview(key, preview)

    def export_current_snapshot(self) -> None:
        payload = self._build_variant_payload(self.selection)
        self.export_panel.editor.setPlainText(json.dumps(payload, indent=2 if self.selection.export_pretty else None, ensure_ascii=False))
        self._last_export_path = str(Path.cwd() / f"{self.selection.recipe_id}.variant.json")
        QMessageBox.information(self, "Variant snapshot ready", f"Snapshot prepared. Suggested path:\n{self._last_export_path}")

    def attach_manifest_file(self, path: str) -> None:
        self.file_watcher.watch(path)

    def _on_watched_file_changed(self, path: str) -> None:
        self.notes.append(f"\n[watch] changed: {path}")


class FoundryStudioSuiteWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Foundry Studio Suite")
        self.resize(1660, 980)
        self.workspace = FoundryStudioWorkspace(self)
        self.setCentralWidget(self.workspace)
        self._build_docks()
        self._build_toolbar()

    def _build_docks(self) -> None:
        self.doctor_dock = QDockWidget("Doctor", self)
        self.doctor_dock.setObjectName("FoundryStudioDoctorDock")
        self.doctor_dock.setWidget(self.workspace.doctor_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.doctor_dock)
        self.cookbook_dock = QDockWidget("Cookbook", self)
        self.cookbook_dock.setObjectName("FoundryStudioCookbookDock")
        self.cookbook_dock.setWidget(self.workspace.cookbook_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.cookbook_dock)
        self.tabifyDockWidget(self.doctor_dock, self.cookbook_dock)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Studio", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction(self._make_action("Apply", self.workspace.rebuild_preview))
        toolbar.addAction(self._make_action("Export", self.workspace.export_current_snapshot))
        toolbar.addAction(self._make_action("Undo", self.workspace.undo_stack.undo))
        toolbar.addAction(self._make_action("Redo", self.workspace.undo_stack.redo))
        toolbar.addSeparator()
        toolbar.addAction(self.doctor_dock.toggleViewAction())
        toolbar.addAction(self.cookbook_dock.toggleViewAction())

    def _make_action(self, title: str, slot: Any) -> QAction:
        action = QAction(title, self)
        action.triggered.connect(slot)
        return action


def list_studio_tools() -> list[StudioToolSpec]:
    return [
        StudioToolSpec("gallery", "Recipe Gallery", "Browse recipe variants and compare direction."),
        StudioToolSpec("inspector", "Variant Inspector", "Tune beauty, color, motion, layout and interaction."),
        StudioToolSpec("doctor", "Recipe Doctor", "Audit structural and safety problems before export."),
        StudioToolSpec("cookbook", "Cookbook", "Read compositional moves and safer build patterns."),
        StudioToolSpec("export", "JSON Export", "Emit payloads ready for compiler, diff or patch tools."),
    ]


def build_studio_variant(selection: StudioVariantSelection) -> dict[str, Any]:
    workspace = FoundryStudioWorkspace()
    payload = workspace._build_variant_payload(selection)
    workspace.deleteLater()
    return payload


def build_foundry_studio_suite(parent: QWidget | None = None) -> FoundryStudioWorkspace:
    return FoundryStudioWorkspace(parent)


def build_foundry_studio_suite_window(parent: QWidget | None = None) -> FoundryStudioSuiteWindow:
    return FoundryStudioSuiteWindow(parent)


def build_foundry_studio_suite_demo_app() -> FoundryStudioSuiteWindow:
    return FoundryStudioSuiteWindow()


def studio_suite_registry_snapshot() -> dict[str, Any]:
    return {
        "version": STUDIO_SUITE_VERSION,
        "tools": [asdict(tool) for tool in list_studio_tools()],
        "recipes": list_foundry_recipes(),
        "beauty_profiles": list_beauty_profiles(),
        "color_stories": list_color_stories(),
        "motion_profiles": list_motion_profiles(),
        "layout_packs": list_layout_packs(),
        "shell_packs": list_shell_packs(),
        "interaction_profiles": list_interaction_profiles(),
    }


def iter_foundry_studio_suite_catalog_specs() -> list[StudioCatalogEntrySpec]:
    return [
        StudioCatalogEntrySpec(
            entry_id="foundry_studio_suite",
            title="Foundry Studio Suite",
            subtitle="Gallery, doctor and export cockpit",
            description="Author recipe variants, inspect payloads, run audits and export clean JSON snapshots.",
            keywords=("foundry", "studio", "doctor", "gallery", "variant"),
        ),
        StudioCatalogEntrySpec(
            entry_id="foundry_studio_cookbook",
            title="Foundry Cookbook",
            subtitle="Composition plays and design safety notes",
            description="Browse recurring patterns for building polished interfaces that still behave themselves.",
            keywords=("cookbook", "patterns", "beauty", "safety"),
            sort_order=931,
        ),
    ]


def build_foundry_studio_suite_catalog_entry(spec: StudioCatalogEntrySpec, parent: QWidget | None = None) -> QWidget:
    if spec.entry_id == "foundry_studio_cookbook":
        return CookbookPanel(parent)
    return build_foundry_studio_suite(parent)


def register_builtin_foundry_studio_suite() -> None:
    for spec in iter_foundry_studio_suite_catalog_specs():
        register_catalog_entry(
            GlassCatalogEntry(
                entry_id=spec.entry_id,
                title=spec.title,
                subtitle=spec.subtitle,
                description=spec.description,
                category=spec.category,
                tags=spec.tags,
                status=spec.status,
                keywords=spec.keywords,
                best_for=spec.best_for,
                use_when=spec.use_when,
                sort_order=spec.sort_order,
                icon_name=spec.icon_name,
                builder=lambda parent=None, entry_spec=spec: build_foundry_studio_suite_catalog_entry(entry_spec, parent),
            )
        )
