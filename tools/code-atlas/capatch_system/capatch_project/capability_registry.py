#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    id: str; label: str; description: str; applies_to: tuple[str,...]
    writes: tuple[str,...]=field(default_factory=tuple); verifiers: tuple[str,...]=field(default_factory=tuple)
    def to_dict(self)->dict[str,Any]:
        return {"id":self.id,"label":self.label,"description":self.description,"applies_to":list(self.applies_to),"writes":list(self.writes),"verifiers":list(self.verifiers)}
CAPABILITY_REGISTRY={"dependency-map": CapabilityDefinition("dependency-map","Universal dependency map","Instala un analizador stdlib para Python, JS, TS, package.json, tsconfig y pnpm workspaces.",("python","javascript","typescript","node-app","node-monorepo","monorepo"),("tools/dependency_map/analyze_project.py","reports/dependency_map/"),("profile-detect","analyzer-json-smoke"))}
def list_capabilities()->list[dict[str,Any]]: return [v.to_dict() for v in sorted(CAPABILITY_REGISTRY.values(), key=lambda x:x.id)]
def get_capability(capability_id:str)->CapabilityDefinition:
    if capability_id not in CAPABILITY_REGISTRY: raise ValueError(f"Capability desconocida: {capability_id}. Disponibles: {', '.join(sorted(CAPABILITY_REGISTRY))}")
    return CAPABILITY_REGISTRY[capability_id]
