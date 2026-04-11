from __future__ import annotations

OWNERSHIP_MATRIX = {
    "signals": {"writer": "scanner", "readers": ["registry_builder", "switch_engine", "contract_validator", "ai_annotator"]},
    "module_registry": {"writer": "registry_builder", "readers": ["scanner", "switch_engine", "contract_validator", "ai_annotator"]},
    "boundary_registry": {"writer": "registry_builder", "readers": ["switch_engine", "contract_validator", "ai_annotator"]},
    "contract_registry": {"writer": "registry_builder", "readers": ["contract_validator", "ai_annotator", "switch_engine"]},
    "switch_registry": {"writer": "registry_builder", "readers": ["switch_engine", "contract_validator", "ai_annotator"]},
    "switch_resolutions": {"writer": "switch_engine", "readers": ["contract_validator", "ai_annotator"]},
    "validation_report": {"writer": "contract_validator", "readers": ["ai_annotator", "switch_engine", "registry_builder"]},
    "annotations": {"writer": "ai_annotator", "readers": ["contract_validator", "registry_builder", "switch_engine"]},
    "query_index": {"writer": "registry_builder", "readers": ["switch_engine", "contract_validator", "ai_annotator"]},
    "snapshots": {"writer": "registry_builder", "readers": ["contract_validator", "ai_annotator"]},
    "deltas": {"writer": "registry_builder", "readers": ["contract_validator", "ai_annotator"]},
}

ENGINE_RESPONSIBILITIES = {
    "scanner": {
        "role": "discover structure and emit signals",
        "forbidden": ["canonicalize registries", "resolve switches", "publish validated judgments", "write annotations"],
    },
    "registry_builder": {
        "role": "consolidate observations into canonical registries",
        "forbidden": ["resolve effective switch state", "publish validation verdicts", "generate AI annotations"],
    },
    "switch_engine": {
        "role": "resolve effective switch state with deterministic precedence",
        "forbidden": ["rewrite canonical registries", "invent undeclared context", "publish validation verdicts", "generate annotations"],
    },
    "contract_validator": {
        "role": "judge schema, reference, and policy compliance",
        "forbidden": ["rewrite canonical registries", "resolve switches", "promote AI suggestions to canonical truth"],
    },
    "ai_annotator": {
        "role": "summarize and suggest from evidence without mutating truth",
        "forbidden": ["write canonical registries", "rewrite identity", "override validator verdicts", "resolve switches"],
    },
}


def get_writer(registry_name: str) -> str:
    return OWNERSHIP_MATRIX[registry_name]["writer"]


def may_read(engine_id: str, registry_name: str) -> bool:
    if registry_name not in OWNERSHIP_MATRIX:
        return True
    policy = OWNERSHIP_MATRIX[registry_name]
    return engine_id == policy["writer"] or engine_id in policy["readers"]


def may_write(engine_id: str, registry_name: str) -> bool:
    return registry_name in OWNERSHIP_MATRIX and OWNERSHIP_MATRIX[registry_name]["writer"] == engine_id
