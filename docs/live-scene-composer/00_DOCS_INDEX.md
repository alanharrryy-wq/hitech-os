# 00_DOCS_INDEX

## Quick Index

This file is the fast navigation index for the Live Scene Composer documentation set.

If you want the project overview and reading guidance, open:

- `README.md`

If you want the documents by number and category, use the index below.

---

## 01-10 Foundation

1. `01_PROJECT_OVERVIEW.md` - project definition and purpose
2. `02_PRODUCT_VISION.md` - long-term product intent
3. `03_GOALS_AND_NON_GOALS.md` - scope discipline
4. `04_CORE_CONCEPTS.md` - canonical vocabulary and concepts
5. `05_SYSTEM_ARCHITECTURE.md` - top-level architecture shape
6. `06_SYSTEM_BOUNDARIES.md` - ownership and boundary rules
7. `07_DOMAIN_MODEL.md` - scene/layout/slot/widget model
8. `08_STATE_MODEL.md` - baseline, draft, preview, UI state
9. `09_RUNTIME_MODEL.md` - runtime relationship model
10. `10_MUTATION_MODEL.md` - mutation semantics and flow

---

## 11-20 Architecture and Extensibility

11. `11_MODULE_SYSTEM.md` - modular growth model
12. `12_MODULE_SDK.md` - SDK for modules
13. `13_WIDGET_SYSTEM.md` - widget responsibilities and behavior
14. `14_SLOT_SYSTEM.md` - slot hosting rules
15. `15_LAYOUT_SYSTEM.md` - layout structure and editing
16. `16_PREFAB_SYSTEM.md` - prefab definition and insertion
17. `17_CUSTOM_WIDGET_SANDBOX.md` - bounded custom widget model
18. `18_RUNTIME_MUTATION_BRIDGE.md` - write-governance boundary
19. `19_DEPENDENCY_POLICY.md` - allowed and forbidden dependency rules
20. `20_PROTECTED_NODES.md` - high-impact seams and contracts

---

## 21-30 Development and Operations

21. `21_DEVELOPER_GUIDE.md` - how engineers should work in the repo
22. `22_CONTRIBUTING.md` - contribution rules
23. `23_CODE_STYLE.md` - naming and implementation style
24. `24_TESTING_STRATEGY.md` - testing priorities and layers
25. `25_DEBUGGING_GUIDE.md` - debugging approach
26. `26_ERROR_HANDLING.md` - failure and containment rules
27. `27_PERFORMANCE_MODEL.md` - performance expectations
28. `28_SECURITY_MODEL.md` - authority and security boundaries
29. `29_OPERATIONS_GUIDE.md` - operational handling
30. `30_DEPLOYMENT_MODEL.md` - release and rollout discipline

---

## 31-40 Product Usage and Evolution

31. `31_USER_MANUAL.md` - end-user manual
32. `32_WORKFLOW_GUIDE.md` - recommended usage workflows
33. `33_FEATURE_REFERENCE.md` - feature map
34. `34_UI_INTERACTION_MODEL.md` - interaction behavior and surface roles
35. `35_THEME_AND_STYLE_SYSTEM.md` - visual style and theme logic
36. `36_DATA_BINDING_MODEL.md` - future-safe data binding rules
37. `37_VERSIONING_MODEL.md` - compatibility and versioning approach
38. `38_CHANGELOG.md` - meaningful project changes over time
39. `39_ROADMAP.md` - project evolution plan
40. `40_ARCHITECTURAL_DECISIONS.md` - major architectural decisions and rationale

---

## 41-46 Governance, Reuse, and Evidence

41. `41_ARCHITECTURE_GUARD_DOC_RULES.md` - enforceable docs-to-code architecture rules
42. `42_ARCHITECTURE_ARTIFACTS.md` - architecture evidence package and regeneration guidance
43. `governance/REUSABLE_CORE_BOUNDARY.md` - reusable core vs project-specific seam definition
44. `governance/ARCHITECTURE_REUSE_PRINCIPLES.md` - reusable-core design principles
45. `governance/MODULE_INTEGRATION_CONTRACT.md` - extension/module contract for safe growth
46. `governance/SELECTION_MODEL_V1.md` - canonical selection model v1 for editor focus

---

## Fast Start Paths

### Read first if you are new

- `01_PROJECT_OVERVIEW.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`

### Read first if you are building features

- `07_DOMAIN_MODEL.md`
- `08_STATE_MODEL.md`
- `11_MODULE_SYSTEM.md`
- `12_MODULE_SDK.md`
- `13_WIDGET_SYSTEM.md`
- `14_SLOT_SYSTEM.md`
- `15_LAYOUT_SYSTEM.md`
- `16_PREFAB_SYSTEM.md`
- `governance/SELECTION_MODEL_V1.md`

### Read first if you are touching risky architecture

- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`
- `41_ARCHITECTURE_GUARD_DOC_RULES.md`
- `42_ARCHITECTURE_ARTIFACTS.md`
- `governance/REUSABLE_CORE_BOUNDARY.md`

### Read first if you are extending the product to new projects

- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `08_STATE_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `40_ARCHITECTURAL_DECISIONS.md`
- `governance/REUSABLE_CORE_BOUNDARY.md`
- `governance/ARCHITECTURE_REUSE_PRINCIPLES.md`
- `governance/MODULE_INTEGRATION_CONTRACT.md`

---

## Index Maintenance Rule

If you add, remove, rename, or substantially change major docs, update this file and `README.md` in the same change.

If you change boundary wiring, bridge contracts, dependency policy, or protected seams, regenerate the architecture artifacts package in the same change set.
