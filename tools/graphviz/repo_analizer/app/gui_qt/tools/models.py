from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ToolSource = Literal["core", "plugin", "extension"]
ToolCategory = Literal[
    "analysis",
    "orchestration",
    "operations",
    "quality",
    "system",
    "other",
]
ToolState = Literal[
    "registered",
    "active",
    "inactive",
    "hidden",
    "suspended",
    "unloaded",
    "destroyed",
]


@dataclass(slots=True)
class ToolDescriptor:
    """Canonical product-level tool metadata."""

    tool_id: str
    display_name: str
    description: str = ""
    category: ToolCategory = "other"
    source: ToolSource = "plugin"
    icon_name: str = ""
    enabled: bool = True
    user_facing: bool = True
    feature_flag: str = ""
    tags: list[str] = field(default_factory=list)
    state: ToolState = "registered"


@dataclass(frozen=True, slots=True)
class ToolLaunchEntry:
    """Read model consumed by launcher/switcher surfaces."""

    tool_id: str
    display_name: str
    description: str
    category: ToolCategory
    icon_name: str
    enabled: bool
    active: bool
    visible: bool
    state: ToolState
    recent_rank: int
