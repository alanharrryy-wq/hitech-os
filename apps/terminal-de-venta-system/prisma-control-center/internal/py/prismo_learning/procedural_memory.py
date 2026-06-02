# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Procedural memory: protocol recipes and historical success."""
from __future__ import annotations
from typing import Any
from .memory_store import read_store, write_store

DEFAULT_RECIPES = [
    {"recipe_id": "qa_failure_investigation", "when": ["playwright_fail", "visual_regression"], "protocol_chain": ["visual_qa_summary", "diagnostic", "evidence_trail", "decision_checklist"], "success_score": 0.82},
    {"recipe_id": "safe_public_summary", "when": ["public", "external"], "protocol_chain": ["public_safe_summary", "executive_brief"], "success_score": 0.78},
    {"recipe_id": "learning_engine_status", "when": ["learning", "status"], "protocol_chain": ["evidence_trail", "neural_graph", "decision_checklist"], "success_score": 0.74},
]


def load_recipes(base=None) -> list[dict[str, Any]]:
    store = read_store("procedural", {"schema_version": "1.0.0", "recipes": DEFAULT_RECIPES}, base)
    recipes = store.get("recipes") or DEFAULT_RECIPES
    return list(recipes)


def upsert_recipe(recipe: dict[str, Any], base=None) -> dict[str, Any]:
    store = read_store("procedural", {"schema_version": "1.0.0", "recipes": DEFAULT_RECIPES}, base)
    rid = recipe.get("recipe_id")
    recipes = [r for r in store.get("recipes", []) if r.get("recipe_id") != rid]
    recipes.insert(0, recipe)
    store["recipes"] = recipes
    write_store("procedural", store, base)
    return recipe


def recipes_for_signal(signal: str, base=None) -> list[dict[str, Any]]:
    low = signal.lower()
    return [r for r in load_recipes(base) if low in " ".join(r.get("when", [])).lower()]
