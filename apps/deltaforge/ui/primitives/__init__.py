from ui.primitives.buttons import CommandButton
from ui.primitives.busy_dialog import BusyDialog
from ui.primitives.chip import Chip
from ui.primitives.confirm_dialog import ConfirmDialog
from ui.primitives.detail_block import KeyValueDetailBlock
from ui.primitives.diff_block import DiffBlockContainer
from ui.primitives.empty_state import EmptyStatePanel
from ui.primitives.hairline_separator import HairlineSeparator
from ui.primitives.kv_block import KVBlock
from ui.primitives.list_surface import ListSurface
from ui.primitives.log_surface import LogSurface
from ui.primitives.section_card import SectionCard
from ui.primitives.shell import MainShellFrame
from ui.primitives.status_pill import StatusPill
from ui.primitives.tab_style import TabStyle

# Compatibility aliases. Do not add new code against these names.
ActionCommandButton = CommandButton
ChipLabel = Chip
PaneSectionCard = SectionCard
SessionStatusPill = StatusPill
ThinSeparator = HairlineSeparator

__all__ = [
    "ActionCommandButton",
    "BusyDialog",
    "Chip",
    "ChipLabel",
    "CommandButton",
    "ConfirmDialog",
    "DiffBlockContainer",
    "EmptyStatePanel",
    "HairlineSeparator",
    "KVBlock",
    "KeyValueDetailBlock",
    "ListSurface",
    "LogSurface",
    "MainShellFrame",
    "PaneSectionCard",
    "SectionCard",
    "SessionStatusPill",
    "StatusPill",
    "TabStyle",
    "ThinSeparator",
]
