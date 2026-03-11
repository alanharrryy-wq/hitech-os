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
- `42_ARCHITECTURE_ARTIFACTS.md`

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

### Architecture Evidence Package

- `41_ARCHITECTURE_GUARD_DOC_RULES.md`
- `42_ARCHITECTURE_ARTIFACTS.md`
- `architecture-artifacts/README.md`
- `architecture-artifacts/GRAPH_LEGEND.md`
- `architecture-artifacts/live-scene-composer-architecture-boundaries.dot`
- `architecture-artifacts/live-scene-composer-architecture-deps.dot`
- `architecture-artifacts/dependency-inventory.json`
- `architecture-artifacts/protected-nodes-map.json`
- `architecture-artifacts/ARTIFACT_MANIFEST.json`

---

## Architecture Artifacts

The architecture artifacts package is the evidence layer for boundary and dependency governance.

Primary entry points:

- `42_ARCHITECTURE_ARTIFACTS.md`
- `architecture-artifacts/README.md`
- `architecture-artifacts/GRAPH_LEGEND.md`

For strategic communication, use the boundaries graph.
For engineering review and implementation work, use the tactical dependencies graph.

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
