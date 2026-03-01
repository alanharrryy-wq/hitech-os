## TBL_GOVERNANCE_SCALE

- **Version:** 1.0.0
- **Status:** draft
- **Authority:** warning
- **Scope:** Defines escalation ladder for governance enforcement and CI blocking

| level | stage | ci_blocking |
| --- | --- | --- |
| 1 | lint_warning | false |
| 2 | deprecated_notice | false |
| 3 | build_warning | false |
| 4 | build_error | true |
| 5 | codemod_required | true |

