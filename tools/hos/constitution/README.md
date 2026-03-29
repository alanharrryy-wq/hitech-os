# tools/hos/constitution

Validator utilities for HITECH OS Constitution.

- `validate_tables.py` validates:
  - JSON Schema compliance
  - invariants (columns, rows, enums, types)
  - strict gating behavior

Dependency:
- `jsonschema` (pip)

Example:
```bash
pip install jsonschema
python tools/hos/constitution/validate_tables.py --root .
```
