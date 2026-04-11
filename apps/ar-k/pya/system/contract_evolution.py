from __future__ import annotations

CONTRACT_EVOLUTION_POLICY = {
    "additive_change": [
        "new optional field",
        "new enum value with backward-tolerant consumers",
        "new artifact family declared but not required for existing engines",
    ],
    "breaking_change": [
        "remove required field",
        "rename field",
        "tighten enum without migration",
        "change ownership of canonical registry without manifest and docs update",
    ],
    "deprecation": {
        "announce_in_docs": True,
        "keep_old_field_for_one_minor": True,
        "emit_validator_warning": True,
    },
    "coexistence": "multiple contract versions may coexist only when a compatibility adapter is declared in the contract registry",
    "authorizer": "system owner plus contracts owner review",
    "backward_compatibility_check": "doctor validates same-major contract compatibility and validator rejects undeclared breakage",
}
