from __future__ import annotations

from pya.contracts.enums import Stage

CANONICAL_STAGE_ORDER = [
    Stage.SCAN.value,
    Stage.REGISTRY.value,
    Stage.SWITCH.value,
    Stage.VALIDATE.value,
    Stage.ANNOTATE.value,
]

REQUIRED_STAGE_OUTPUTS = {
    Stage.SCAN.value: ["signals"],
    Stage.REGISTRY.value: ["module_registry", "boundary_registry", "contract_registry", "switch_registry", "query_index"],
    Stage.SWITCH.value: ["switch_resolutions"],
    Stage.VALIDATE.value: ["validation_report"],
    Stage.ANNOTATE.value: ["annotations"],
}
