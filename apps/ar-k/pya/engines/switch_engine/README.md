# switch_engine

Purpose: Resolve effective switch state with deterministic precedence and traceability.

Stage: `switch`
Reads: `module_registry, switch_registry`
Writes: `switch_resolutions`

Forbidden moves:
- do not write outside declared ownership
- do not invent new states
- do not alter system or kernel without explicit review
