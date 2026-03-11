#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs}"
mkdir -p "$DOCS_DIR"

cat > "$DOCS_DIR/README.md" <<'EOF'
# Live Scene Composer Documentation

## Purpose of This Documentation Set

This documentation set defines the canonical product, architecture, development, operations, and usage model for **Live Scene Composer**.

It exists to make the project:

- understandable
- buildable
- governable
- extensible
- testable
- harder to accidentally damage

This is not a pile of optional notes.
These documents are part of the operating system of the project.

---

## Project Summary

**Live Scene Composer** is a live visual authoring workspace built on top of the real runtime.

Its core model is:

**Scene -> Layout -> Slots -> Widgets**

It is designed to support:

- live visual editing
- layout changes
- text and typography editing
- styling and appearance changes
- chart editing and replacement
- prefab insertion
- bounded future custom widgets
- draft, compare, revert, and commit workflows
- modular growth through governed extension surfaces

It is **not** the same product as **Runtime Debug Console**.

---

## Non-Negotiable System Rules

The following rules should be treated as project law:

1. **Runtime Debug Console and Live Scene Composer are separate sibling products.**
2. **`console-core` is the only canonical shared infrastructure layer.**
3. **All write-capable composer mutations must go through `runtime-mutation-bridge`.**
4. **The runtime must not depend on the Composer.**
5. **The Composer must remain modular, bounded, and architecture-governed.**
6. **Scene -> Layout -> Slots -> Widgets is the canonical mental model.**

If a future change weakens one of these rules, it should be treated as a serious architecture event.

---

## Documentation Reading Order

If someone has never seen the project before, the recommended reading order is:

1. `01_PROJECT_OVERVIEW.md`
2. `02_PRODUCT_VISION.md`
3. `03_GOALS_AND_NON_GOALS.md`
4. `04_CORE_CONCEPTS.md`
5. `05_SYSTEM_ARCHITECTURE.md`
6. `06_SYSTEM_BOUNDARIES.md`
7. `07_DOMAIN_MODEL.md`
8. `10_MUTATION_MODEL.md`
9. `19_DEPENDENCY_POLICY.md`
10. `20_PROTECTED_NODES.md`

That sequence gives the fastest path to understanding the project correctly.

---

## Critical Docs

If time is limited, read these first:

- `01_PROJECT_OVERVIEW.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`

These documents define the project’s foundation.

---

## Reading Paths by Role

### For Product / Design

Start with:

- `01_PROJECT_OVERVIEW.md`
- `02_PRODUCT_VISION.md`
- `03_GOALS_AND_NON_GOALS.md`
- `31_USER_MANUAL.md`
- `32_WORKFLOW_GUIDE.md`
- `33_FEATURE_REFERENCE.md`
- `34_UI_INTERACTION_MODEL.md`
- `35_THEME_AND_STYLE_SYSTEM.md`
- `39_ROADMAP.md`

### For Architecture / Core Engineering

Start with:

- `04_CORE_CONCEPTS.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `08_STATE_MODEL.md`
- `09_RUNTIME_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`

### For Feature Engineers

Start with:

- `07_DOMAIN_MODEL.md`
- `08_STATE_MODEL.md`
- `11_MODULE_SYSTEM.md`
- `12_MODULE_SDK.md`
- `13_WIDGET_SYSTEM.md`
- `14_SLOT_SYSTEM.md`
- `15_LAYOUT_SYSTEM.md`
- `16_PREFAB_SYSTEM.md`
- `21_DEVELOPER_GUIDE.md`
- `23_CODE_STYLE.md`
- `24_TESTING_STRATEGY.md`

### For Tooling / Validation

Start with:

- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `21_DEVELOPER_GUIDE.md`
- `22_CONTRIBUTING.md`
- `24_TESTING_STRATEGY.md`
- `25_DEBUGGING_GUIDE.md`
- `28_SECURITY_MODEL.md`
- `29_OPERATIONS_GUIDE.md`
- `30_DEPLOYMENT_MODEL.md`
- `40_ARCHITECTURAL_DECISIONS.md`

### For New Contributors

Minimum starter pack:

- `01_PROJECT_OVERVIEW.md`
- `03_GOALS_AND_NON_GOALS.md`
- `04_CORE_CONCEPTS.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `21_DEVELOPER_GUIDE.md`
- `22_CONTRIBUTING.md`
- `23_CODE_STYLE.md`

---

## Documentation Map

### Foundation

- `01_PROJECT_OVERVIEW.md`
- `02_PRODUCT_VISION.md`
- `03_GOALS_AND_NON_GOALS.md`
- `04_CORE_CONCEPTS.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `08_STATE_MODEL.md`
- `09_RUNTIME_MODEL.md`
- `10_MUTATION_MODEL.md`

### Architecture and Extensibility

- `11_MODULE_SYSTEM.md`
- `12_MODULE_SDK.md`
- `13_WIDGET_SYSTEM.md`
- `14_SLOT_SYSTEM.md`
- `15_LAYOUT_SYSTEM.md`
- `16_PREFAB_SYSTEM.md`
- `17_CUSTOM_WIDGET_SANDBOX.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`

### Development and Operations

- `21_DEVELOPER_GUIDE.md`
- `22_CONTRIBUTING.md`
- `23_CODE_STYLE.md`
- `24_TESTING_STRATEGY.md`
- `25_DEBUGGING_GUIDE.md`
- `26_ERROR_HANDLING.md`
- `27_PERFORMANCE_MODEL.md`
- `28_SECURITY_MODEL.md`
- `29_OPERATIONS_GUIDE.md`
- `30_DEPLOYMENT_MODEL.md`

### Product Usage and Evolution

- `31_USER_MANUAL.md`
- `32_WORKFLOW_GUIDE.md`
- `33_FEATURE_REFERENCE.md`
- `34_UI_INTERACTION_MODEL.md`
- `35_THEME_AND_STYLE_SYSTEM.md`
- `36_DATA_BINDING_MODEL.md`
- `37_VERSIONING_MODEL.md`
- `38_CHANGELOG.md`
- `39_ROADMAP.md`
- `40_ARCHITECTURAL_DECISIONS.md`

---

## Document Ownership Guidance

These docs should not be treated as anonymous files.

Suggested ownership pattern:

- **Product / Design**
  - overview, vision, goals, workflow, feature reference, UI interaction, roadmap

- **Architecture / Core**
  - architecture, boundaries, domain, state, runtime, mutation, bridge, dependency policy, protected nodes, decisions

- **Engineering / Tooling**
  - module system, SDK, developer guide, code style, testing, deployment, operations

- **Security / Validation**
  - sandbox, security model, error handling, protected nodes, dependency policy

Ownership can be shared, but never ambiguous.

---

## Maintenance Rules

Update documentation when any of the following changes materially:

- product identity
- domain model
- state model
- mutation behavior
- bridge contract
- dependency direction
- provider or adapter seams
- module SDK
- protected nodes
- roadmap or versioning strategy

Do not postpone meaningful doc updates “until later.”
That is how the docs stop being useful.

---

## How to Use This Set in Practice

### When starting a new feature

Read:

- relevant domain docs
- relevant boundary docs
- dependency policy
- protected nodes if high-impact seams are involved

### When reviewing a PR

Check:

- whether docs remain correct
- whether a protected node changed
- whether dependency direction changed
- whether mutation behavior changed

### When onboarding someone new

Give them:

- the critical docs list
- the role-specific reading path
- the architecture decisions file

---

## Suggested Additions

If the project keeps growing, useful future additions may include:

- generated dependency graph references
- architecture guard usage docs
- module registry reference
- bridge command catalog
- scene schema examples
- prefab catalog guide

These are optional expansions, not blockers.

---

## Final Note

This documentation set is meant to keep **Live Scene Composer** from becoming another vague tooling blob.

Use it to preserve:

- product clarity
- architectural boundaries
- mutation safety
- modularity
- long-term sanity

If the code and the docs disagree, that is a real issue and should be resolved directly.
EOF

cat > "$DOCS_DIR/00_DOCS_INDEX.md" <<'EOF'
# 00_DOCS_INDEX

## Quick Index

This file is the fast navigation index for the Live Scene Composer documentation set.

If you want the project overview and reading guidance, open:

- `README.md`

If you want the documents by number and category, use the index below.

---

## 01–10 Foundation

1. `01_PROJECT_OVERVIEW.md` — project definition and purpose
2. `02_PRODUCT_VISION.md` — long-term product intent
3. `03_GOALS_AND_NON_GOALS.md` — scope discipline
4. `04_CORE_CONCEPTS.md` — canonical vocabulary and concepts
5. `05_SYSTEM_ARCHITECTURE.md` — top-level architecture shape
6. `06_SYSTEM_BOUNDARIES.md` — ownership and boundary rules
7. `07_DOMAIN_MODEL.md` — scene/layout/slot/widget model
8. `08_STATE_MODEL.md` — baseline, draft, preview, UI state
9. `09_RUNTIME_MODEL.md` — runtime relationship model
10. `10_MUTATION_MODEL.md` — mutation semantics and flow

---

## 11–20 Architecture and Extensibility

11. `11_MODULE_SYSTEM.md` — modular growth model
12. `12_MODULE_SDK.md` — SDK for modules
13. `13_WIDGET_SYSTEM.md` — widget responsibilities and behavior
14. `14_SLOT_SYSTEM.md` — slot hosting rules
15. `15_LAYOUT_SYSTEM.md` — layout structure and editing
16. `16_PREFAB_SYSTEM.md` — prefab definition and insertion
17. `17_CUSTOM_WIDGET_SANDBOX.md` — bounded custom widget model
18. `18_RUNTIME_MUTATION_BRIDGE.md` — write-governance boundary
19. `19_DEPENDENCY_POLICY.md` — allowed and forbidden dependency rules
20. `20_PROTECTED_NODES.md` — high-impact seams and contracts

---

## 21–30 Development and Operations

21. `21_DEVELOPER_GUIDE.md` — how engineers should work in the repo
22. `22_CONTRIBUTING.md` — contribution rules
23. `23_CODE_STYLE.md` — naming and implementation style
24. `24_TESTING_STRATEGY.md` — testing priorities and layers
25. `25_DEBUGGING_GUIDE.md` — debugging approach
26. `26_ERROR_HANDLING.md` — failure and containment rules
27. `27_PERFORMANCE_MODEL.md` — performance expectations
28. `28_SECURITY_MODEL.md` — authority and security boundaries
29. `29_OPERATIONS_GUIDE.md` — operational handling
30. `30_DEPLOYMENT_MODEL.md` — release and rollout discipline

---

## 31–40 Product Usage and Evolution

31. `31_USER_MANUAL.md` — end-user manual
32. `32_WORKFLOW_GUIDE.md` — recommended usage workflows
33. `33_FEATURE_REFERENCE.md` — feature map
34. `34_UI_INTERACTION_MODEL.md` — interaction behavior and surface roles
35. `35_THEME_AND_STYLE_SYSTEM.md` — visual style and theme logic
36. `36_DATA_BINDING_MODEL.md` — future-safe data binding rules
37. `37_VERSIONING_MODEL.md` — compatibility and versioning approach
38. `38_CHANGELOG.md` — meaningful project changes over time
39. `39_ROADMAP.md` — project evolution plan
40. `40_ARCHITECTURAL_DECISIONS.md` — major architectural decisions and rationale

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

### Read first if you are touching risky architecture

- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`

---

## Index Maintenance Rule

If you add, remove, rename, or substantially change major docs, update this file and `README.md` in the same change.
EOF

echo "[OK] Generated docs index files in: $DOCS_DIR"
echo "[OK] Files created:"
ls -1 "$DOCS_DIR"/README.md "$DOCS_DIR"/00_DOCS_INDEX.md