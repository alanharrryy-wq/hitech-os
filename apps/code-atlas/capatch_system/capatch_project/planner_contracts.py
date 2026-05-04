#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
@dataclass(slots=True)
class CapabilityPlan:
    capability_id: str; target_root: str; mode: str
    actions: list[dict[str,Any]]=field(default_factory=list)
    writes: list[str]=field(default_factory=list); verifiers: list[str]=field(default_factory=list); notes: list[str]=field(default_factory=list)
    def to_dict(self)->dict[str,Any]:
        return {"capability_id":self.capability_id,"target_root":self.target_root,"mode":self.mode,"actions":list(self.actions),"writes":list(self.writes),"verifiers":list(self.verifiers),"notes":list(self.notes)}
