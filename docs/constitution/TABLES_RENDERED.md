# Rendered Constitution Tables

Generated from canonical JSON tables.

## TBL_DASHBOARD_STRUCTURE

- **Version:** 1.0.0
- **Status:** draft
- **Authority:** informational
- **Scope:** Defines structural narrative layers for dashboards (overview → filter → details)

| layer | purpose |
| --- | --- |
| overview | High-level KPIs and state summary |
| filter | User control and segmentation |
| details | Drilldown and contextual narrative |

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

## TBL_VRT_POLICY

- **Version:** 1.0.0
- **Status:** draft
- **Authority:** warning
- **Scope:** Defines visual regression strictness levels and snapshot behavior

| mode | pixel_strict | motion_disabled |
| --- | --- | --- |
| strict | true | true |
| relaxed | false | true |

