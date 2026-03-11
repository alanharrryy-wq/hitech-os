# 00_TOC

## Purpose

This file is the master table of contents for the Live Scene Composer documentation set.

Use this file when you want:

- a quick map of the full documentation
- a category-based lookup
- a fast way to find the right document without guessing
- a stable navigation surface for onboarding and review

For reading by priority and time budget, open:

- `00_READING_PATHS.md`

---

## Full Documentation Map

### Foundation and Core Project Definition

1. `01_PROJECT_OVERVIEW.md` — project definition, purpose, and identity
2. `02_PRODUCT_VISION.md` — long-term product vision and intended experience
3. `03_GOALS_AND_NON_GOALS.md` — scope control, intent, and anti-scope drift
4. `04_CORE_CONCEPTS.md` — canonical vocabulary and model concepts
5. `05_SYSTEM_ARCHITECTURE.md` — top-level architectural structure
6. `06_SYSTEM_BOUNDARIES.md` — ownership and boundary rules
7. `07_DOMAIN_MODEL.md` — domain entities and relationships
8. `08_STATE_MODEL.md` — baseline, draft, preview, and UI state categories
9. `09_RUNTIME_MODEL.md` — composer/runtime relationship model
10. `10_MUTATION_MODEL.md` — mutation semantics, flow, and governance

---

### Architecture, Extensibility, and Safety

11. `11_MODULE_SYSTEM.md` — module architecture and lifecycle
12. `12_MODULE_SDK.md` — module extension contract and contribution APIs
13. `13_WIDGET_SYSTEM.md` — widget identity, responsibilities, and editing behavior
14. `14_SLOT_SYSTEM.md` — slot hosting rules and bounded composition logic
15. `15_LAYOUT_SYSTEM.md` — layout structure and editing model
16. `16_PREFAB_SYSTEM.md` — prefab definitions, insertion, and reuse
17. `17_CUSTOM_WIDGET_SANDBOX.md` — bounded custom widget execution model
18. `18_RUNTIME_MUTATION_BRIDGE.md` — controlled write boundary and bridge governance
19. `19_DEPENDENCY_POLICY.md` — allowed and forbidden dependency relationships
20. `20_PROTECTED_NODES.md` — high-impact seams and elevated-review surfaces

---

### Engineering, Validation, and Operations

21. `21_DEVELOPER_GUIDE.md` — local development expectations and workflow
22. `22_CONTRIBUTING.md` — contribution rules and review discipline
23. `23_CODE_STYLE.md` — implementation style and naming standards
24. `24_TESTING_STRATEGY.md` — testing layers, priorities, and evidence model
25. `25_DEBUGGING_GUIDE.md` — debugging approach and failure isolation reasoning
26. `26_ERROR_HANDLING.md` — error categories, rejection rules, and containment
27. `27_PERFORMANCE_MODEL.md` — responsiveness and bounded cost expectations
28. `28_SECURITY_MODEL.md` — authority, restrictions, and safe extension posture
29. `29_OPERATIONS_GUIDE.md` — system health, incident classification, and operations
30. `30_DEPLOYMENT_MODEL.md` — rollout, risk tiers, and deployment discipline

---

### Product Use, UX, and Evolution

31. `31_USER_MANUAL.md` — end-user guide
32. `32_WORKFLOW_GUIDE.md` — recommended usage patterns and task flows
33. `33_FEATURE_REFERENCE.md` — structured feature catalog
34. `34_UI_INTERACTION_MODEL.md` — canvas/structure/inspector interaction rules
35. `35_THEME_AND_STYLE_SYSTEM.md` — style layers, themes, and visual treatment
36. `36_DATA_BINDING_MODEL.md` — future-safe data binding principles
37. `37_VERSIONING_MODEL.md` — compatibility and versioning expectations
38. `38_CHANGELOG.md` — meaningful project evolution log
39. `39_ROADMAP.md` — strategic sequencing and growth plan
40. `40_ARCHITECTURAL_DECISIONS.md` — major decisions and rationale history
41. `41_ARCHITECTURE_GUARD_DOC_RULES.md` — enforceable docs/code architecture guard rules
42. `42_ARCHITECTURE_ARTIFACTS.md` — architecture evidence package guide and regeneration workflow

---

### Architecture Artifacts Package

- `architecture-artifacts/README.md` — package purpose and usage
- `architecture-artifacts/GRAPH_LEGEND.md` — node/edge notation
- `architecture-artifacts/live-scene-composer-architecture-boundaries.dot` — strategic graph source
- `architecture-artifacts/live-scene-composer-architecture-deps.dot` — tactical graph source
- `architecture-artifacts/dependency-inventory.json` — machine-readable architecture edge inventory
- `architecture-artifacts/protected-nodes-map.json` — machine-readable protected seam map
- `architecture-artifacts/ARTIFACT_MANIFEST.json` — artifact package manifest

---

## Fast Lookup by Topic

### If the question is “What is this project?”
Read:

- `01_PROJECT_OVERVIEW.md`
- `02_PRODUCT_VISION.md`
- `03_GOALS_AND_NON_GOALS.md`

### If the question is “How is the system structured?”
Read:

- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `08_STATE_MODEL.md`

### If the question is “How do changes happen safely?”
Read:

- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`

### If the question is “How do I build features safely?”
Read:

- `11_MODULE_SYSTEM.md`
- `12_MODULE_SDK.md`
- `21_DEVELOPER_GUIDE.md`
- `22_CONTRIBUTING.md`
- `24_TESTING_STRATEGY.md`

### If the question is “How should the product feel to users?”
Read:

- `31_USER_MANUAL.md`
- `32_WORKFLOW_GUIDE.md`
- `33_FEATURE_REFERENCE.md`
- `34_UI_INTERACTION_MODEL.md`
- `35_THEME_AND_STYLE_SYSTEM.md`

### If the question is “How do we keep this thing sane long-term?”
Read:

- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `28_SECURITY_MODEL.md`
- `30_DEPLOYMENT_MODEL.md`
- `37_VERSIONING_MODEL.md`
- `40_ARCHITECTURAL_DECISIONS.md`
- `42_ARCHITECTURE_ARTIFACTS.md`

---

## Recommended Permanent Top-Level Reading Set

If someone should only read the minimum set that protects the project from becoming a cagadero, the permanent minimum set is:

- `01_PROJECT_OVERVIEW.md`
- `04_CORE_CONCEPTS.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`
- `42_ARCHITECTURE_ARTIFACTS.md`

---

## Maintenance Rule

Whenever a major document is added, renamed, removed, or split:

1. update this TOC
2. update `README.md`
3. update `00_READING_PATHS.md` if the reading priorities changed
4. update `42_ARCHITECTURE_ARTIFACTS.md` and `architecture-artifacts/ARTIFACT_MANIFEST.json` when artifact structure changes

If those three files drift, onboarding quality drops fast.

---

## Summary

`00_TOC.md` is the master navigation map of the Live Scene Composer documentation set. It gives a category-based view of the full system, fast lookup paths by topic, and a stable reference point for new readers and reviewers.
