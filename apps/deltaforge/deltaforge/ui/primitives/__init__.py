from deltaforge.ui.primitives.buttons import CommandButton
from deltaforge.ui.primitives.busy_dialog import BusyDialog
from deltaforge.ui.primitives.chip import Chip
from deltaforge.ui.primitives.confirm_dialog import ConfirmDialog
from deltaforge.ui.primitives.detail_block import KeyValueDetailBlock
from deltaforge.ui.primitives.diff_block import DiffBlockContainer
from deltaforge.ui.primitives.empty_state import EmptyStatePanel
from deltaforge.ui.primitives.hairline_separator import HairlineSeparator
from deltaforge.ui.primitives.kv_block import KVBlock
from deltaforge.ui.primitives.list_surface import ListSurface
from deltaforge.ui.primitives.log_surface import LogSurface
from deltaforge.ui.primitives.section_card import SectionCard
from deltaforge.ui.primitives.shell import MainShellFrame
from deltaforge.ui.primitives.status_pill import StatusPill
from deltaforge.ui.primitives.tab_style import TabStyle

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
