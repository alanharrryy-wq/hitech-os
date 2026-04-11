# ai_annotator

Purpose: Generate suggested annotations from evidence without mutating canonical truth.

Stage: `annotate`
Reads: `module_registry, boundary_registry, validation_report, switch_resolutions`
Writes: `annotations`

Forbidden moves:
- do not write outside declared ownership
- do not invent new states
- do not alter system or kernel without explicit review
