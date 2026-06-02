"""PRISMO render block contracts blueprint.

Fix2 semantic contract:
- procedural_steps is explicitly allowed.
- procedural_recipe remains allowed as a recipe-level alias.
- raw HTML, scripts, iframes, full raw JSON and output format dropdowns are forbidden.
"""
from __future__ import annotations

from typing import Any, Dict


ALLOWED_RENDER_BLOCKS = {
    "hero_response",
    "executive_brief",
    "next_action",
    "action_bar",
    "checklist",
    "timeline",
    "risk_matrix",
    "evidence_board",
    "flow_diagram",
    "decision_summary",
    "protocol_ladder",
    "authority_strip",
    "comparison_board",
    "insight_chips",
    "detail_drawer",
    "memory_card",
    "memory_trace",
    "procedural_steps",
    "procedural_recipe",
    "episodic_trace",
    "semantic_fact_grid",
    "visual_recipe_card",
    "governance_notice",
    "operational_status",
    "chart_spec_preview",
    "question_stack",
    "recommendation_ladder",
    "feedback_panel",
}

FORBIDDEN_RENDER_BLOCKS = {
    "raw_html",
    "script",
    "iframe",
    "raw_json_main",
    "full_graph_main",
    "giant_table_main",
    "output_format_dropdown",
    "unbounded_markdown",
}


def normalize_render_block_type(block_type: str) -> str:
    if block_type == "procedural_recipe":
        return "procedural_recipe"
    return block_type


def assert_render_block(block: Dict[str, Any]) -> bool:
    block_type = normalize_render_block_type(block.get("type", ""))
    if block_type in FORBIDDEN_RENDER_BLOCKS:
        raise ValueError(f"Forbidden block: {block_type}")
    if block_type not in ALLOWED_RENDER_BLOCKS:
        raise ValueError(f"Unknown block: {block_type}")
    return True
