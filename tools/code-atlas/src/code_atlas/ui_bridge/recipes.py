from __future__ import annotations
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_sha256, read_json


def _recipe_objects(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and data.get("recipeId"):
        return [data]
    if isinstance(data, dict):
        for key in ("recipes", "items", "entries"):
            value = data.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict) and x.get("recipeId")]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict) and x.get("recipeId")]
    return []


class RecipeRepository:
    def __init__(self):
        self.by_id: dict[str, dict[str, Any]] = {}
        self.sources: dict[str, str] = {}
        self.priorities: dict[str, int] = {}

    @staticmethod
    def _priority(recipe: dict[str, Any]) -> int:
        schema = str(recipe.get("schema", ""))
        return {
            "prisma.identity.portable-element-export.v2": 400,
            "prisma.identity.full-stack-recipe.v1": 300,
            "prisma.identity.portable-element-export.v1": 200,
            "prisma.identity.recipe-coverage-matrix.v1": 100,
        }.get(schema, 0)

    def add_path(self, raw: str | Path) -> None:
        path = Path(raw)
        candidates = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for candidate in candidates:
            if not candidate.is_file(): continue
            try: data = read_json(candidate)
            except Exception: continue
            for recipe in _recipe_objects(data):
                recipe_id = str(recipe["recipeId"])
                enriched = dict(recipe)
                enriched.setdefault("canonicalPayloadSha256", canonical_sha256(recipe))
                source = candidate.as_posix()
                priority = self._priority(enriched)
                previous_priority = self.priorities.get(recipe_id, -1)
                previous_source = self.sources.get(recipe_id, "")
                if priority < previous_priority or (
                    priority == previous_priority and previous_source and source >= previous_source
                ):
                    continue
                self.by_id[recipe_id] = enriched
                self.sources[recipe_id] = source
                self.priorities[recipe_id] = priority

    @classmethod
    def load(cls, paths: Iterable[str | Path]) -> "RecipeRepository":
        repo = cls()
        for path in paths: repo.add_path(path)
        return repo

    def compatible(self, component: dict[str, Any]) -> list[dict[str, Any]]:
        compatibility = component.get("recipeCompatibility")
        explicit: list[str] = []
        if isinstance(compatibility, dict):
            for key in ("recipeIds", "compatibleRecipeIds", "recipes"):
                value = compatibility.get(key)
                if isinstance(value, list): explicit.extend(str(v) for v in value)
            if compatibility.get("recipeId"): explicit.append(str(compatibility["recipeId"]))
        if component.get("recipeId"): explicit.append(str(component["recipeId"]))
        out: list[dict[str, Any]] = []
        for recipe_id in explicit:
            if recipe_id in self.by_id: out.append(self.by_id[recipe_id])
        if out: return sorted(out, key=lambda r: str(r.get("recipeId")))
        component_ui_id = component.get("componentUiId")
        component_id = component.get("componentId")
        widget_type = component.get("widgetTypeId")
        for recipe in self.by_id.values():
            target = recipe.get("target", {}) if isinstance(recipe.get("target"), dict) else {}
            if component_ui_id and target.get("componentUiId") == component_ui_id:
                out.append(recipe); continue
            applies = recipe.get("compatibleComponentIds", [])
            if component_id and isinstance(applies, list) and component_id in applies:
                out.append(recipe); continue
            widgets = recipe.get("compatibleWidgetTypeIds", [])
            if widget_type and isinstance(widgets, list) and widget_type in widgets:
                out.append(recipe)
        return sorted({str(r["recipeId"]): r for r in out}.values(), key=lambda r: str(r.get("recipeId")))
