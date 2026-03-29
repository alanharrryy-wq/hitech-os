from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any


def command_spec(
    name: str,
    title: str,
    description: str,
    *,
    shortcut: str,
    keywords: list[str],
    enabled: bool,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "title": title,
        "description": description,
        "shortcut": shortcut,
        "keywords": list(keywords),
        "payload": dict(payload or {}),
        "enabled": bool(enabled),
        "visible": True,
    }


def action_spec(
    action_id: str,
    title: str,
    description: str,
    *,
    keywords: list[str],
    enabled: bool,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "title": title,
        "description": description,
        "keywords": list(keywords),
        "payload": dict(payload or {}),
        "enabled": bool(enabled),
        "visible": True,
    }


def build_command_specs(
    snapshot: dict[str, Any],
    *,
    dispatcher_has: Callable[[str], bool],
) -> list[dict[str, Any]]:
    specs = []
    seen: set[str] = set()
    preview_relpath = snapshot["current_preview_relpath"]
    preview_payload = (
        {"relpath": preview_relpath, "line": 0, "add_history": True}
        if preview_relpath
        else {}
    )
    rows = (
        command_spec(
            "execute_search",
            "Run Search",
            "Execute the current repo search from host state.",
            shortcut="Return",
            keywords=["search", "query", "results"],
            enabled=dispatcher_has("execute_search"),
        ),
        command_spec(
            "export_results",
            "Export Results",
            "Export the active result set when results exist.",
            shortcut="Ctrl+E",
            keywords=["export", "results", "report"],
            enabled=dispatcher_has("export_results") and int(snapshot["results_count"]) > 0,
        ),
        command_spec(
            "navigate_back",
            "Navigate Back",
            "Move to the previous preview item.",
            shortcut="Alt+Left",
            keywords=["back", "history", "preview"],
            enabled=dispatcher_has("navigate_back") and bool(snapshot["nav_can_go_back"]),
        ),
        command_spec(
            "navigate_forward",
            "Navigate Forward",
            "Move to the next preview item.",
            shortcut="Alt+Right",
            keywords=["forward", "history", "preview"],
            enabled=dispatcher_has("navigate_forward")
            and bool(snapshot["nav_can_go_forward"]),
        ),
        command_spec(
            "open_file",
            "Open Preview File",
            "Open the current preview file using the canonical preview relpath when available.",
            shortcut="Ctrl+O",
            keywords=["preview", "open", "file"],
            payload=preview_payload,
            enabled=dispatcher_has("open_file") and bool(preview_relpath),
        ),
        command_spec(
            "add_bookmark",
            "Add Bookmark",
            "Bookmark the current preview target.",
            shortcut="Ctrl+D",
            keywords=["bookmark", "save", "preview"],
            enabled=dispatcher_has("add_bookmark") and bool(preview_relpath),
        ),
        command_spec(
            "remove_bookmark",
            "Remove Bookmark",
            "Remove the selected bookmark when the host exposes one.",
            shortcut="",
            keywords=["bookmark", "remove", "selection"],
            enabled=dispatcher_has("remove_bookmark") and int(snapshot["bookmarks_count"]) > 0,
        ),
    )
    for spec in rows:
        name = spec["name"]
        if name in seen:
            continue
        seen.add(name)
        specs.append(spec)
    return specs


def build_action_specs(
    snapshot: dict[str, Any],
    *,
    dispatcher_has: Callable[[str], bool],
) -> list[dict[str, Any]]:
    actions = []
    seen: set[str] = set()
    preview_relpath = snapshot["current_preview_relpath"]
    preview_payload = (
        {"relpath": preview_relpath, "line": 0, "add_history": True}
        if preview_relpath
        else {}
    )
    rows = (
        action_spec(
            "execute_search",
            "Search",
            "Run the current query.",
            keywords=["search", "query"],
            enabled=dispatcher_has("execute_search"),
        ),
        action_spec(
            "export_results",
            "Export",
            "Export the active result set.",
            keywords=["export", "results"],
            enabled=dispatcher_has("export_results") and int(snapshot["results_count"]) > 0,
        ),
        action_spec(
            "open_file",
            "Preview",
            "Open the canonical preview relpath.",
            keywords=["preview", "open"],
            payload=preview_payload,
            enabled=dispatcher_has("open_file") and bool(preview_relpath),
        ),
        action_spec(
            "navigate_back",
            "Back",
            "Navigate backward in preview history.",
            keywords=["back", "history"],
            enabled=dispatcher_has("navigate_back") and bool(snapshot["nav_can_go_back"]),
        ),
        action_spec(
            "navigate_forward",
            "Forward",
            "Navigate forward in preview history.",
            keywords=["forward", "history"],
            enabled=dispatcher_has("navigate_forward")
            and bool(snapshot["nav_can_go_forward"]),
        ),
        action_spec(
            "add_bookmark",
            "Bookmark",
            "Save the current preview to bookmarks.",
            keywords=["bookmark", "save"],
            enabled=dispatcher_has("add_bookmark") and bool(preview_relpath),
        ),
    )
    for action in rows:
        action_id = action["action_id"]
        if action_id in seen:
            continue
        seen.add(action_id)
        actions.append(action)
    return actions


__all__ = [
    "action_spec",
    "build_action_specs",
    "build_command_specs",
    "command_spec",
]
