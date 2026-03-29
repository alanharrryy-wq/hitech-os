## TBL_TOKENS_TAXONOMY

- **Version:** 1.0.0
- **Status:** draft
- **Authority:** warning
- **Scope:** Defines token layers and allowed reference relationships

| layer | description | can_reference |
| --- | --- | --- |
| base | Raw values (color, spacing, motion primitives) | none |
| semantic | Intent-driven tokens referencing base | base |
| component | Component-specific tokens referencing semantic | semantic |

