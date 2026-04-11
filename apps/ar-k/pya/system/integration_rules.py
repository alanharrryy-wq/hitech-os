from __future__ import annotations

INTEGRATION_RULES = {
    "engine_registration_flow": [
        "discover manifest",
        "validate manifest contract",
        "validate compatibility",
        "check ownership and write paths",
        "load entrypoint",
        "run engine tests",
        "run kernel smoke",
        "run sample integration",
    ],
    "smoke_expectations": [
        "signals emitted",
        "registries materialized",
        "switches resolved",
        "validation report created",
        "annotations created",
    ],
    "admission_checks": [
        "stage declared",
        "ownership respected",
        "no conflicting writer",
        "required contracts declared",
        "compatibility matrix satisfied",
    ],
}
