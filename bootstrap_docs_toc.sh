#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs}"
mkdir -p "$DOCS_DIR"

cat > "$DOCS_DIR/00_TOC.md" <<'EOF'
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

---

## Maintenance Rule

Whenever a major document is added, renamed, removed, or split:

1. update this TOC
2. update `README.md`
3. update `00_READING_PATHS.md` if the reading priorities changed

If those three files drift, onboarding quality drops fast.

---

## Summary

`00_TOC.md` is the master navigation map of the Live Scene Composer documentation set. It gives a category-based view of the full system, fast lookup paths by topic, and a stable reference point for new readers and reviewers.
EOF

cat > "$DOCS_DIR/00_READING_PATHS.md" <<'EOF'
# 00_READING_PATHS

## Purpose

This file defines the recommended reading paths for the Live Scene Composer documentation set based on:

- time available
- reader role
- depth required
- level of architectural risk

It exists because not everyone should read all 40 documents in the same order every time.

---

## Core Rule

When in doubt, start with:

- `01_PROJECT_OVERVIEW.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `19_DEPENDENCY_POLICY.md`

Those five documents usually prevent the most expensive misunderstandings.

---

# Reading Paths by Time Budget

## 30-Minute Onboarding Path

This is the minimum serious reading path for someone who needs to understand the project fast without reading the entire documentation set.

Read in this exact order:

1. `01_PROJECT_OVERVIEW.md`
2. `02_PRODUCT_VISION.md`
3. `03_GOALS_AND_NON_GOALS.md`
4. `05_SYSTEM_ARCHITECTURE.md`
5. `06_SYSTEM_BOUNDARIES.md`
6. `07_DOMAIN_MODEL.md`
7. `10_MUTATION_MODEL.md`
8. `19_DEPENDENCY_POLICY.md`
9. `20_PROTECTED_NODES.md`
10. `40_ARCHITECTURAL_DECISIONS.md`

### What this path gives you

- what the project is
- what it is not
- how it is structured
- how changes are supposed to happen
- what rules must not be broken

### Who should use it

- new contributors
- product people
- reviewers
- engineers joining the effort
- anyone about to touch a high-risk seam

---

## 2-Hour Deep Working Path

This path is for someone who is about to actually work on the project and needs enough context to avoid doing dumb shit.

Read in this exact order:

1. `01_PROJECT_OVERVIEW.md`
2. `02_PRODUCT_VISION.md`
3. `03_GOALS_AND_NON_GOALS.md`
4. `04_CORE_CONCEPTS.md`
5. `05_SYSTEM_ARCHITECTURE.md`
6. `06_SYSTEM_BOUNDARIES.md`
7. `07_DOMAIN_MODEL.md`
8. `08_STATE_MODEL.md`
9. `09_RUNTIME_MODEL.md`
10. `10_MUTATION_MODEL.md`
11. `11_MODULE_SYSTEM.md`
12. `12_MODULE_SDK.md`
13. `13_WIDGET_SYSTEM.md`
14. `14_SLOT_SYSTEM.md`
15. `15_LAYOUT_SYSTEM.md`
16. `16_PREFAB_SYSTEM.md`
17. `18_RUNTIME_MUTATION_BRIDGE.md`
18. `19_DEPENDENCY_POLICY.md`
19. `20_PROTECTED_NODES.md`
20. `21_DEVELOPER_GUIDE.md`
21. `22_CONTRIBUTING.md`
22. `24_TESTING_STRATEGY.md`
23. `28_SECURITY_MODEL.md`
24. `40_ARCHITECTURAL_DECISIONS.md`

### What this path gives you

- full architectural posture
- domain understanding
- mutation safety model
- extension model
- working rules
- review and test expectations

### Who should use it

- engineers implementing features
- core architecture workers
- tooling workers
- validation workers
- people writing Codex prompts for implementation

---

## Full Deep Read Path

This path is for people who need complete command of the system and do not want hidden surprises later.

Recommended order:

### Phase A — Foundation

1. `01_PROJECT_OVERVIEW.md`
2. `02_PRODUCT_VISION.md`
3. `03_GOALS_AND_NON_GOALS.md`
4. `04_CORE_CONCEPTS.md`
5. `05_SYSTEM_ARCHITECTURE.md`
6. `06_SYSTEM_BOUNDARIES.md`
7. `07_DOMAIN_MODEL.md`
8. `08_STATE_MODEL.md`
9. `09_RUNTIME_MODEL.md`
10. `10_MUTATION_MODEL.md`

### Phase B — System Design and Extensibility

11. `11_MODULE_SYSTEM.md`
12. `12_MODULE_SDK.md`
13. `13_WIDGET_SYSTEM.md`
14. `14_SLOT_SYSTEM.md`
15. `15_LAYOUT_SYSTEM.md`
16. `16_PREFAB_SYSTEM.md`
17. `17_CUSTOM_WIDGET_SANDBOX.md`
18. `18_RUNTIME_MUTATION_BRIDGE.md`
19. `19_DEPENDENCY_POLICY.md`
20. `20_PROTECTED_NODES.md`

### Phase C — Engineering Discipline

21. `21_DEVELOPER_GUIDE.md`
22. `22_CONTRIBUTING.md`
23. `23_CODE_STYLE.md`
24. `24_TESTING_STRATEGY.md`
25. `25_DEBUGGING_GUIDE.md`
26. `26_ERROR_HANDLING.md`
27. `27_PERFORMANCE_MODEL.md`
28. `28_SECURITY_MODEL.md`
29. `29_OPERATIONS_GUIDE.md`
30. `30_DEPLOYMENT_MODEL.md`

### Phase D — Product Usage and Long-Term Evolution

31. `31_USER_MANUAL.md`
32. `32_WORKFLOW_GUIDE.md`
33. `33_FEATURE_REFERENCE.md`
34. `34_UI_INTERACTION_MODEL.md`
35. `35_THEME_AND_STYLE_SYSTEM.md`
36. `36_DATA_BINDING_MODEL.md`
37. `37_VERSIONING_MODEL.md`
38. `38_CHANGELOG.md`
39. `39_ROADMAP.md`
40. `40_ARCHITECTURAL_DECISIONS.md`

### Who should use it

- project owners
- lead architects
- core maintainers
- long-term reviewers
- people designing future extension paths

---

# Reading Paths by Role

## Product / Design Path

Read:

1. `01_PROJECT_OVERVIEW.md`
2. `02_PRODUCT_VISION.md`
3. `03_GOALS_AND_NON_GOALS.md`
4. `04_CORE_CONCEPTS.md`
5. `31_USER_MANUAL.md`
6. `32_WORKFLOW_GUIDE.md`
7. `33_FEATURE_REFERENCE.md`
8. `34_UI_INTERACTION_MODEL.md`
9. `35_THEME_AND_STYLE_SYSTEM.md`
10. `39_ROADMAP.md`

### Why

This path helps product and design stay aligned with what the product should be, how users will use it, and how the experience should feel.

---

## Feature Engineer Path

Read:

1. `01_PROJECT_OVERVIEW.md`
2. `04_CORE_CONCEPTS.md`
3. `05_SYSTEM_ARCHITECTURE.md`
4. `06_SYSTEM_BOUNDARIES.md`
5. `07_DOMAIN_MODEL.md`
6. `08_STATE_MODEL.md`
7. `10_MUTATION_MODEL.md`
8. `11_MODULE_SYSTEM.md`
9. `12_MODULE_SDK.md`
10. `13_WIDGET_SYSTEM.md`
11. `14_SLOT_SYSTEM.md`
12. `15_LAYOUT_SYSTEM.md`
13. `16_PREFAB_SYSTEM.md`
14. `18_RUNTIME_MUTATION_BRIDGE.md`
15. `19_DEPENDENCY_POLICY.md`
16. `20_PROTECTED_NODES.md`
17. `21_DEVELOPER_GUIDE.md`
18. `23_CODE_STYLE.md`
19. `24_TESTING_STRATEGY.md`

### Why

This path helps feature engineers build without crossing the streams and turning the repo into una mamada.

---

## Core Architecture Path

Read:

1. `01_PROJECT_OVERVIEW.md`
2. `04_CORE_CONCEPTS.md`
3. `05_SYSTEM_ARCHITECTURE.md`
4. `06_SYSTEM_BOUNDARIES.md`
5. `07_DOMAIN_MODEL.md`
6. `08_STATE_MODEL.md`
7. `09_RUNTIME_MODEL.md`
8. `10_MUTATION_MODEL.md`
9. `11_MODULE_SYSTEM.md`
10. `12_MODULE_SDK.md`
11. `17_CUSTOM_WIDGET_SANDBOX.md`
12. `18_RUNTIME_MUTATION_BRIDGE.md`
13. `19_DEPENDENCY_POLICY.md`
14. `20_PROTECTED_NODES.md`
15. `28_SECURITY_MODEL.md`
16. `30_DEPLOYMENT_MODEL.md`
17. `40_ARCHITECTURAL_DECISIONS.md`

### Why

This path covers the high-impact seams where architecture dies or survives.

---

## Tooling / Validation Path

Read:

1. `05_SYSTEM_ARCHITECTURE.md`
2. `06_SYSTEM_BOUNDARIES.md`
3. `10_MUTATION_MODEL.md`
4. `18_RUNTIME_MUTATION_BRIDGE.md`
5. `19_DEPENDENCY_POLICY.md`
6. `20_PROTECTED_NODES.md`
7. `21_DEVELOPER_GUIDE.md`
8. `22_CONTRIBUTING.md`
9. `24_TESTING_STRATEGY.md`
10. `25_DEBUGGING_GUIDE.md`
11. `28_SECURITY_MODEL.md`
12. `29_OPERATIONS_GUIDE.md`
13. `30_DEPLOYMENT_MODEL.md`
14. `40_ARCHITECTURAL_DECISIONS.md`

### Why

This path is for people who need to keep the project honest, enforce rules, and catch drift before it spreads.

---

## Executive / Strategic Path

Read:

1. `01_PROJECT_OVERVIEW.md`
2. `02_PRODUCT_VISION.md`
3. `03_GOALS_AND_NON_GOALS.md`
4. `05_SYSTEM_ARCHITECTURE.md`
5. `19_DEPENDENCY_POLICY.md`
6. `20_PROTECTED_NODES.md`
7. `31_USER_MANUAL.md`
8. `33_FEATURE_REFERENCE.md`
9. `39_ROADMAP.md`
10. `40_ARCHITECTURAL_DECISIONS.md`

### Why

This path gives leadership or project owners the minimum deep context to make smart calls without reading every technical detail.

---

# Reading Paths by Task

## If you are about to write a Codex implementation prompt

Read:

- `01_PROJECT_OVERVIEW.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`

## If you are about to touch the bridge

Read:

- `08_STATE_MODEL.md`
- `09_RUNTIME_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `28_SECURITY_MODEL.md`
- `40_ARCHITECTURAL_DECISIONS.md`

## If you are about to build UI features

Read:

- `31_USER_MANUAL.md`
- `32_WORKFLOW_GUIDE.md`
- `33_FEATURE_REFERENCE.md`
- `34_UI_INTERACTION_MODEL.md`
- `35_THEME_AND_STYLE_SYSTEM.md`
- plus the relevant system docs for the feature area

## If you are about to touch slots/widgets/layout

Read:

- `07_DOMAIN_MODEL.md`
- `13_WIDGET_SYSTEM.md`
- `14_SLOT_SYSTEM.md`
- `15_LAYOUT_SYSTEM.md`
- `16_PREFAB_SYSTEM.md`
- `10_MUTATION_MODEL.md`

---

# Permanent “Do Not Skip” Docs

These are the documents nobody touching serious code should skip:

- `01_PROJECT_OVERVIEW.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`

If someone skips these and then toca arquitectura, ya sabemos cómo acaba la película 😅

---

# Maintenance Rule

Whenever one of the following changes materially:

- project identity
- boundaries
- domain model
- mutation behavior
- bridge contract
- dependency policy
- protected nodes
- roadmap
- key architectural decisions

update:

- `README.md`
- `00_TOC.md`
- `00_READING_PATHS.md`

These three files should always agree on reading priorities.

---

## Summary

`00_READING_PATHS.md` defines the fastest correct ways to understand the Live Scene Composer documentation set. It gives onboarding paths by time, by role, and by task so that contributors can get enough context without drowning—or worse, building blind.
EOF

echo "[OK] Generated reading tree files in: $DOCS_DIR"
echo "[OK] Files created:"
ls -1 "$DOCS_DIR"/00_TOC.md "$DOCS_DIR"/00_READING_PATHS.md