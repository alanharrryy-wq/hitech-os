---
title: PRISMA Visual Change Master Map
status: TARGET_FINAL_ARCHITECTURE_AND_OPERATING_CONTRACT
scope: Tablet, PC, Mobile, Web, Chart Lab, Control Center, Shared UI
owner_domain: PRISMA visual change operations
canonical_visual_authority: prisma-html
generated_for_review: 2026-08-31
---

# PRISMA Visual Change Master Map

## 0. Mandatory startup rule

**For every visual modification to any PRISMA application or surface, read this document before proposing, planning, authorizing, applying, or validating a visual change.**

This includes changes to:

- Tablet
- PC
- Mobile
- Web / EIT
- Chart Lab
- Control Center
- Shared UI
- visual tokens, recipes, materials, layers, adapters or projections used by those surfaces

This document is the **operator map and lifecycle contract**, not a replacement for the individual machine-readable authorities.

The individual authorities still win inside their own domain:

- Factory Ledger owns capability maturity, evidence, next gate and `doNotRebuild`.
- Authority Mesh owns task-exact authorization and protected scope.
- Code Atlas owns repository intelligence and observable source relationships.
- UIMAP owns the physical UI census / source map.
- NDC owns neutral meaning, scope, canonical identity and provenance concepts.
- RIFAT / prisma-ui owns exact visual location truth.
- Identity Dictionary owns neutral visual identity, recipes, tokens, materials and adapters.
- `visual-source-manifest.json` owns deterministic canonical-source → product-projection declarations.
- Runtime evidence proves what actually rendered.
- Change Assurance owns the evidence lifecycle from UNDERSTAND through PROVE.
- Factory Ledger records the resulting governed capability truth.

If this document conflicts with a machine-readable authority in its domain, the machine-readable authority wins and this document must be corrected.

---

# 1. The sentence that explains the whole system

> **NDC says what it means. Code Atlas says what exists. RIFAT says where it lands. Identity says how it should look. Mesh says what may be touched. The generic engine in prisma-html applies the authorized visual change. Runtime QA proves what happened. Factory Ledger remembers the governed truth.**

A second rule is equally important:

> **The neutral layer defines meaning. The specific layer defines location.**

And a third:

> **Discovery is not binding. Binding is not authorization. Authorization is not mutation. Mutation is not certification.**

---

# 2. Final desired PRISMA Master Map

The diagram below represents the **final target architecture**. The Generic Visual Application Engine is shown in its intended completed position even if implementation work is still pending at the time this document is first adopted.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              USER / OPERATOR                                 │
│                                                                              │
│  "Change visual object X on PC / Tablet / Mobile / Web / Chart Lab / CC"    │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 1. FACTORY LEDGER / UNIVERSAL ANTI-REWORK — PROPOSAL                       ║
║                                                                              ║
║ What already exists? What is mature? What must not be rebuilt?              ║
║ DONE / VERIFY / FIX / BUILD / EXTERNAL                                      ║
║ doNotRebuild / nextGate / evidence / doesNotProve                           ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │ PASS
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 2. AUTHORITY MESH / AUTOMESH v2                                             ║
║                                                                              ║
║ What authorities govern this exact task?                                    ║
║ Which surfaces, directories, contracts and layers are allowed?              ║
║ Which surfaces and paths are excluded/protected?                            ║
║ Is the authority bound to current canonical HEAD?                           ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │ PASS_COMPOSED_AUTHORITY_MESH
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            CODE ATLAS                                        │
│              repository intelligence / evidence engine                      │
├────────────────────────┬────────────────────────┬────────────────────────────┤
│ Repository intelligence│ UIMAP                  │ Change Assurance           │
│ files / dependencies   │ physical UI census     │ UNDERSTAND                 │
│ owners / provenance    │ routes / components    │ RESOLVE                    │
│ impact / unknowns      │ owners / CSS / slots   │ AUTHORIZE                  │
│                        │ selectors / layers      │ OBSERVE                    │
│                        │ source hashes           │ VERIFY                     │
│                        │                        │ PROVE                      │
└───────────────┬────────┴─────────────┬──────────┴────────────────────────────┘
                │                      │
                └──────────────┬───────┘
                               ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 3. NDC — NEUTRAL DATA CENTER                                               ║
║                                                                              ║
║ What does this object mean in PRISMA, independently of an app?              ║
║                                                                              ║
║ Scope: TEN / BIZ / STO / DEV / LIC / ROLE / SURFACE / SESSION               ║
║ Meaning: ENT / EVT / ACT / STA / MET / ALT / EVD / CAP / CAN                ║
║ Provenance: source device / source surface / event / lineage / canonical     ║
║                                                                              ║
║ A UI component is a projection of neutral meaning, never the source of it.  ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │ neutral meaning
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 4. PRISMA-HTML — SINGLE EDITABLE VISUAL AUTHORITY                          ║
╠══════════════════════════╦══════════════════════════╦════════════════════════╣
║ Identity Dictionary      ║ RIFAT / prisma-ui        ║ Atlasfin              ║
║                          ║                          ║                        ║
║ visual meaning           ║ exact visual location    ║ human visual cockpit  ║
║ profiles                 ║ surface                  ║ inspect/select        ║
║ recipes                  ║ route                    ║ preview               ║
║ tokens                   ║ owner                    ║ export request        ║
║ materials                ║ region                   ║ status/evidence       ║
║ motion                   ║ editable slot            ║                        ║
║ states                   ║ component                ║ NEVER direct product  ║
║ surface adapters         ║ neutral/physical layer  ║ mutation              ║
╚════════════╤═════════════╩════════════╤═════════════╩════════════════════════╝
             │                          │
             └──────────────┬───────────┘
                            ▼
                 VISUAL SOURCE MANIFEST
                 canonical visual source
                         ↓
                 deterministic projection
                            │
                            ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 5. GENERATED VISUAL TARGET INDEX                                            ║
║                                                                              ║
║ Persistent bridge between the broad census and promoted semantic bindings.  ║
║                                                                              ║
║ physical target + NDC meaning + RIFAT coordinates + source hashes           ║
║                                                                              ║
║ Missing meaning/binding/layer stays explicit and BLOCKED.                   ║
║ Nothing is invented from naming intuition.                                  ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 6. IDENTITY / ELEMENT BINDING RESOLVER                                      ║
║                                                                              ║
║ Connects neutral visual meaning and a recipe to one or more exact targets.  ║
║                                                                              ║
║ RESOLVED only when required trace fields are directly proven.               ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │ RESOLVED
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 7. CODE ATLAS UI BRIDGE                                                     │
│                                                                              │
│ exact physical target + compatible recipe + current source                  │
│                                ↓                                             │
│ deterministic read-only plan                                                │
│ semantic diff                                                               │
│ operations                                                                  │
│ blocking reasons                                                            │
│                                                                              │
│ UI Bridge plans. It does not authorize itself and does not write product.   │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │ reviewed plan
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 8. FACTORY LEDGER ANTI-REWORK — MUTATION GATE                              ║
║                                                                              ║
║ Same canonical HEAD                                                         ║
║ fresh/revalidated exact-task Mesh                                            ║
║ 100% required authority coverage                                             ║
║ zero blockers                                                                ║
║ Layer Map present                                                            ║
║ exact target and scope allowed                                               ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │ PASS_ANTI_REWORK_GATE
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 9. GENERIC VISUAL APPLICATION ENGINE — prisma-html                          ║
║                                                                              ║
║ The canonical visual mutation engine.                                       ║
║                                                                              ║
║ preview → preflight → backup → patch canonical authority → project          ║
║ → verify hashes → collect evidence → idempotency → rollback on failure      ║
║                                                                              ║
║ It never discovers a target by intuition.                                   ║
║ It never expands surface scope by itself.                                   ║
║ It never edits a generated product projection manually.                     ║
║ It never converts UNKNOWN/BLOCKED into PASS.                                ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │ governed projection
                                   ▼
        ┌──────────────┬───────────┬──────────┬────────────┬──────────────┐
        ▼              ▼           ▼          ▼            ▼              ▼
     TABLET            PC        MOBILE      WEB        CHART LAB    CONTROL CENTER
        │              │           │          │            │              │
        └──────────────┴───────────┴──────────┴────────────┴──────────────┘
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 10. STATIC / SOURCE / GOVERNANCE VALIDATION                                 ║
║                                                                              ║
║ Visual Core / Identity / RIFAT / target index / bindings / projections      ║
║ scope / hashes / no-important / drift / generated-output parity             ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 11. RUNTIME VISUAL QA                                                       ║
║                                                                              ║
║ Mamastrophic / ScreensQA / browser evidence                                 ║
║ before + after / same route / same viewport / same target                   ║
║ states / geometry / pixels / collision / overflow                           ║
║ console / network / reduced motion / accessibility where applicable         ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 12. DOMAIN-SPECIFIC VERIFIERS / SENTINELS                                   ║
║                                                                              ║
║ Sync Sentinel, licensing gates, data/custody gates and other specialized    ║
║ verifiers run only when authority/impact says the visual change intersects  ║
║ their domain.                                                               ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 13. CHANGE ASSURANCE — OBSERVE / VERIFY / PROVE                             ║
║                                                                              ║
║ No evidence, no green.                                                       ║
║ Candidate != Authority                                                       ║
║ Impact Radius != Authorization                                               ║
║ Retrieval != Proof                                                          ║
║ UNKNOWN != PASS_WITH_WARNING                                                 ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 14. GITHUB ACTIONS / PR / CI / AUTOGIT                                     ║
║                                                                              ║
║ exact PR head / checks / evidence / merge guard                             ║
║ AutoMesh revalidation when main moves                                       ║
║ AutoGit may curate commit/PR flow but never becomes authority               ║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │ MERGE
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 15. POST-MERGE VERIFICATION                                                 ║
║                                                                              ║
║ Verify canonical main, relevant runtime/evidence gates and absence of drift.║
╚══════════════════════════════════╤═══════════════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║ 16. FACTORY LEDGER + EVIDENCE INDEX CLOSURE                                ║
║                                                                              ║
║ Record only truth that actually changed:                                    ║
║ maturity / evidence / nextGate / doNotRebuild / doesNotProve                ║
║                                                                              ║
║ The next agent starts here again instead of rebuilding completed work.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

# 3. Tool ownership map

| System / tool | Canonical job | Reads | Produces | May mutate product? |
|---|---|---|---|---|
| Factory Ledger | Capability maturity and anti-rework truth | Ledger + evidence indexes | gate decision, capability status | No |
| Universal anti-rework gate | Blocks duplicate/rebuild work | Ledger + request + Mesh when mutation | PASS/BLOCKED | No |
| Authority Mesh | Task-exact authority | repo, contracts, Ledger trust anchors, Layer Map | readset, impact, gate matrix, authority evidence | No |
| AutoMesh v2 | Remote composition/revalidation of Mesh | prior authority + current HEAD | rebound/fresh authority evidence | No |
| Code Atlas core | Repository intelligence | source tree and declared evidence | graph, impact, provenance, unknowns | No |
| UIMAP | Physical UI census | app source, routes, CSS, owners | source UI records/batches | No |
| NDC | Neutral meaning and scope | NDC canon/curation | semantic IDs, scope/provenance model | No product mutation |
| RIFAT / prisma-ui | Exact visual location truth | governed surfaces/routes/owners/slots/layers | visual coordinates | Authority only |
| Identity Dictionary | Visual meaning | profiles/tokens/recipes/assets/adapters | compiled visual identity | Authority only |
| Atlasfin | Human control cockpit | Identity/RIFAT/evidence | selection, preview, portable intent/request | No direct product write |
| Visual Source Manifest | Projection contract | RIFAT canonical sources + product outputs | source/output map + hashes | Describes projection |
| Target Index | Persistent physical application address book | UIMAP + Visual Control + NDC/RIFAT evidence | compact surface indexes | Generated only |
| Binding Resolver | Semantic-to-target certification | target index + Identity + RIFAT | RESOLVED/BLOCKED binding envelope | No |
| UI Bridge | Deterministic source planning | resolved target + recipes + source | plan + semantic diff | No |
| Generic Visual Application Engine | Governed visual mutation | authorized plan + Mesh + hashes + manifest | canonical authority mutation + projection + rollback/evidence | **Yes, only after gates** |
| Visual Core | Readiness computation | Identity/RIFAT/projection/evidence | readiness and blockers | No |
| Mamastrophic | Runtime/browser evidence | running surface | captures/probes/evidence | No source mutation |
| ScreensQA | Visual regression/evidence | running surface | screenshots/reports | No source mutation |
| Sync Sentinel | Sync/runtime verification when relevant | isolated/runtime contracts | sync evidence | No visual source mutation |
| Change Assurance | UNDERSTAND→PROVE evidence lifecycle | Code Atlas + evidence | reproducible proof/bundles | No authority invention |
| GitHub Actions | Execution rail | exact commit/PR | checks/artifacts | Workflow-controlled |
| AutoGit | Git/PR curator | worktree/branch/check state | commit/PR workflow | Git logistics only |
| GovOS | Governance documentation canon in its domain | governance docs | governed documentation | Docs only |
| Field Manual | Operational learning memory | prior lessons | practical rules/learning | Not machine authority |
| Control Center | Runtime/local operations cockpit | launcher/runtime state | launch/stop/status/evidence | Operational only |

---

# 4. NDC is not optional in the visual path

NDC belongs between physical discovery and visual projection because a visible object needs a neutral meaning before a specific app implementation is allowed to masquerade as the concept itself.

Wrong:

```text
TB_POS_SALE
PC_SALE_PANEL
MB_SALE_WIDGET
```

as three competing canonical concepts.

Correct:

```text
ENT.sale
EVT.sale.created
ACT.sale.checkout
MET.sales.today
```

projected into:

```text
SURF.tb.pos
SURF.pc.sales_control
SURF.mb.owner_home
SURF.cl.sales_trend
```

and finally located by implementation IDs such as:

```text
TB-POS-PAY-COBRAR-BTN-01
PC-SALES-MAIN-TBL-01
MB-HOME-KPI-01
CL-SALES-CH-01
```

For visual-only concepts, the same separation applies:

```text
neutral visual meaning
        ↓
identity recipe/profile
        ↓
surface adapter
        ↓
specific route/region/slot/component/layer
```

A physical UIMAP target may be fully discovered but remain **SEMANTIC_PENDING** until its NDC/visual meaning is proven.

---

# 5. Census, binding and application are different things

The broad UI census is not the element-binding registry.

```text
CENSUS / UIMAP
"this physically exists"
        ↓
TARGET INDEX
"this is its persistent proven address"
        ↓
NDC / VISUAL MEANING
"this is what it means"
        ↓
BINDING
"this meaning is certified to this exact target"
        ↓
APPLICATION
"an authorized recipe may be applied here"
        ↓
RUNTIME CERTIFICATION
"the intended result actually rendered"
```

Therefore a surface can be heavily or fully censused while still having only a subset of application-ready semantic bindings.

**Never interpret `bindingCount` as `component census count`.**

---

# 6. Generated Visual Target Index

## Purpose

The Target Index prevents broad discovery from being repeated and prevents compact binding registries from pretending to be the entire UI census.

Proposed canonical generated layout:

```text
prisma-html/
  authority/
    rifat/
      prisma-ui/
        visual-control/
          target-index/
            manifest.json
            tablet.jsonl
            pc.jsonl
            mobile.jsonl
            web.jsonl
            chart-lab.jsonl
            control-center.jsonl
            shared-ui.jsonl
```

The index is generated, deterministic and never hand-edited.

## Minimum record

```json
{
  "surfaceId": "SURF.pc.catalog",
  "interfaceId": "IFC.pc.catalog",
  "routeId": "ROUTE.pc.catalog",
  "routePath": "/catalog",
  "regionId": "ZONE.pc.catalog.primary",
  "slotId": "SLOT.pc.catalog.primary.workspace",
  "componentId": "WGT.pc.catalog.workspace",
  "componentUiId": "PC-...-01",
  "ownerId": "OWN.pc.catalog.workspace",
  "ownerFile": "apps/.../component.tsx",
  "ownerSymbol": "ProductMediaWorkspace",
  "renderSourceFile": "apps/.../component.tsx",
  "renderSymbol": "ProductMediaWorkspace",
  "visualTargets": [
    {
      "styleSourceFile": "apps/.../component.module.css",
      "selector": ".workspace",
      "visualTargetId": "VT...."
    }
  ],
  "implementationLayerId": "products.pc....workspace",
  "neutralMeaningId": null,
  "bindingId": null,
  "layerId": null,
  "adapterId": "ADP.PC.ADMIN.V2",
  "sourceHashes": {},
  "evidenceRefs": [],
  "targetResolutionStatus": "SOURCE_RESOLVED",
  "semanticStatus": "SEMANTIC_PENDING",
  "applicationReadiness": "BLOCKED",
  "blockingReasons": [
    "NEUTRAL_MEANING_NOT_CERTIFIED",
    "BINDING_NOT_CERTIFIED",
    "CANONICAL_LAYER_NOT_CERTIFIED"
  ]
}
```

Null is valid evidence. Invented IDs are not.

---

# 7. Master Component Readiness model

Every visual object should be expressible through a single readiness chain:

```text
DISCOVERED
   ↓
PHYSICAL_RESOLVED
   ↓
SEMANTIC_RESOLVED
   ↓
VISUAL_CONTROL_RESOLVED
   ↓
BINDING_CERTIFIED
   ↓
RECIPE_COMPATIBLE
   ↓
PROJECTION_RESOLVED
   ↓
AUTHORITY_PREFLIGHT_ELIGIBLE
   ↓
APPLY_ELIGIBLE
   ↓
SOURCE_APPLIED
   ↓
RUNTIME_VISUAL_PENDING
   ↓
VISUAL_CERTIFIED
```

Alternative fail-closed states include:

```text
UNMAPPED
PARTIAL
BLOCKED_BY_CONFLICT
BLOCKED_BY_MISSING_OWNER
BLOCKED_BY_MISSING_SOURCE
BLOCKED_BY_MISSING_LAYER
BLOCKED_BY_MISSING_BINDING
BLOCKED_BY_AMBIGUOUS_BINDING
BLOCKED_BY_SCOPE
BLOCKED_BY_DRIFT
BLOCKED_BY_STALE_AUTHORITY
BLOCKED_BY_NO_CANONICAL_VISUAL_SOURCE
BLOCKED_BY_RECIPE_INCOMPATIBILITY
BLOCKED_BY_RUNTIME_EVIDENCE
DRIFTED
```

No state may be silently upgraded.

---

# 8. The Generic Visual Application Engine

## 8.1 Canonical home

The generic mutation engine belongs under `prisma-html`, because `prisma-html` is the single editable visual authority.

Target structure:

```text
prisma-html/
  tools/
    visual_application/
      __init__.py
      engine.py
      preflight.py
      request.py
      resolver.py
      projection.py
      rollback.py
      evidence.py
      integrity.py
      safety.py
      writers/
        __init__.py
        css.py
        css_module.py
        json_tokens.py
        generated_projection.py
      validators/
        request_validator.py
        target_validator.py
        plan_validator.py
        projection_validator.py
        evidence_validator.py
```

Schemas:

```text
prisma-html/
  authority/
    rifat/
      identity/
        contract/
          application/
            PRISMA_VISUAL_APPLICATION_REQUEST_V1.schema.json
            PRISMA_VISUAL_APPLICATION_RESULT_V1.schema.json
            PRISMA_VISUAL_APPLICATION_EVIDENCE_V1.schema.json
            PRISMA_VISUAL_APPLICATION_ROLLBACK_V1.schema.json
```

## 8.2 What Code Atlas continues to own

Code Atlas remains read-only in this path:

```text
tools/code-atlas/src/code_atlas/ui_bridge/
  resolver.py
  planner.py
  drift.py
  repository.py
  recipes.py
```

It discovers, resolves and plans.

It does not become visual authority and does not gain a general product writer.

## 8.3 Golden compatibility path

The existing Cobrar application is retained as a golden historical/reference transaction.

The generic engine must prove parity against the certified Cobrar case before the Cobrar-specific implementation can be reduced to a compatibility wrapper.

Do not delete historical certified evidence.

## 8.4 Required application modes

```text
preview
apply
verify
rollback
```

`preview` must never mutate.

`apply` requires current gated authorization.

`verify` verifies exact post-application state and evidence.

`rollback` restores exact BEFORE bytes and reruns relevant validation.

## 8.5 Preflight checks

Before any write, require:

```text
Factory Ledger PROPOSAL PASS
fresh/revalidated exact-task Authority Mesh
Factory Ledger MUTATION PASS
Layer Map present
exact target SOURCE_RESOLVED
neutral meaning certified where required
binding RESOLVED
canonical layer certified
surface adapter compatible
recipe compatible
UI Bridge plan reviewed
plan digest valid
source hashes current
canonical visual source declared
projection output declared
surface scope allowed
excluded surfaces untouched
backup destination available
BEFORE evidence present where required
```

One failure means no mutation.

## 8.6 Write policy

The engine edits the canonical visual authority source.

It does **not** manually edit deterministic generated product projections.

```text
prisma-html canonical source
           ↓
Generic Visual Application Engine
           ↓
deterministic projection generator
           ↓
product runtime output
```

If no canonical visual source is declared:

```text
BLOCKED_BY_NO_CANONICAL_VISUAL_SOURCE
```

The next task is source promotion/governance, not an ad-hoc runtime patch.

## 8.7 Initial writer scope

V1 should support only deterministic visual formats with bounded risk:

```text
CSS
CSS Modules
governed JSON tokens/recipes
declared generated projections
```

Do not treat arbitrary TSX/DOM structure or business handlers as visual-only mutation.

Structural React changes require a separate governed implementation path and corresponding product/domain validation.

## 8.8 Safety invariants

```text
no !important
no surface expansion
no unknown target guessing
no direct generated-output editing
no mutation on stale source hash
no mutation without rollback
no pass from static-only evidence when runtime visual evidence is required
no functional-smoke-only visual certification
no hidden skipped state
no product-wide READY from one target certification
```

---

# 9. Full visual change procedure, step 1 through final closure

## Step 1 — Normalize the user request

Convert the request into a bounded task:

```text
surface
route or route family
visual intent
known target if supplied
included scope
explicit exclusions
functional-risk note
```

Example:

```text
surface: PC
route: /catalog
intent: modify primary workspace visual recipe
exclude: Tablet, Mobile, Web, Chart Lab, Control Center, Shared UI
```

Do not identify a CSS file from intuition yet.

## Step 2 — Resolve current canonical HEAD

All proof-bearing governance and mutation must bind to current canonical repository HEAD.

## Step 3 — Read Factory Ledger and run anti-rework PROPOSAL

Determine relevant canonical capability IDs.

Classify requested actions:

```text
REUSE
VERIFY
ADVANCE
FIX
BUILD
REBUILD
EXTERNAL
```

If the capability is absent, contradictory, stale or shadow-only, stop.

If `DONE + doNotRebuild=true`, reuse or advance to `nextGate`. Do not rebuild.

## Step 4 — Read this Master Map and applicable operational memory

For a visual task, this document is mandatory.

Then read the Field Manual and task-specific authorities selected by governance.

## Step 5 — Generate/revalidate task-exact Authority Mesh

Require:

```text
PASS_COMPOSED_AUTHORITY_MESH
correct current HEAD
required authority threshold satisfied
zero blockers
Layer Map present
surface inclusion/exclusion explicit
```

If `main` moves, use AutoMesh v2 revalidation.

Do not blindly keep or discard old authority.

## Step 6 — Reuse the existing census before rediscovery

Search existing UIMAP / Visual Control / target-index evidence.

If the exact target is already source-resolved and source hashes remain current:

```text
DO NOT RUN BROAD REDISCOVERY
```

Use the existing proven target.

If required evidence is missing or stale, run only the minimum fresh discovery needed.

## Step 7 — Resolve physical target with Code Atlas/UIMAP

Prove the exact chain:

```text
surface
route
region
slot
component
componentUiId
owner
render source
visual target
selector
physical implementation layer
source hashes
```

Do not proceed with ambiguous target selection.

## Step 8 — Resolve neutral meaning with NDC

Determine the neutral meaning/scope that the visible object projects.

If no current NDC meaning exists and the task requires one, mark `SEMANTIC_PENDING`.

Do not derive canonical semantics from the app name.

## Step 9 — Resolve visual location with RIFAT/prisma-ui

Prove:

```text
surfaceId
routeId
ownerId
regionId
slotId
componentUiId
layerId / implementationLayerId
```

Location does not define meaning.

## Step 10 — Resolve visual intent with Identity Dictionary

Select or author only under authority:

```text
identity profile
recipe
preset
tokens
material
motion
states
adapter
```

Profile or recipe activation changes authority intent only. It does not directly mutate product runtime.

## Step 11 — Resolve/promote the element binding

The binding connects:

```text
neutral visual meaning
+
recipe/profile
+
surface
+
exact target coordinates
+
certified layer
```

A binding becomes `RESOLVED` only from direct evidence.

If the broad census is complete but the binding is missing, do not recensus the surface. Promote the missing semantic/binding contract only.

## Step 12 — Build deterministic UI Bridge plan

Code Atlas UI Bridge receives:

```text
resolved target
compatible recipe
current source
adapter
binding
layer
```

and emits:

```text
PLAN
semantic diff
operations
blocking reasons
checksum
```

No source mutation occurs.

## Step 13 — Review exact impact

Verify the planned operation touches only authorized canonical visual source files and generated outputs declared by the projection manifest.

If the plan crosses an excluded surface or protected scope, stop.

## Step 14 — Run anti-rework MUTATION gate

Require:

```text
current HEAD
PASS Mesh
100% required authority coverage where required
zero blockers
Layer Map present
request/artifact digests
visualMutation=true
```

No prose override.

## Step 15 — Capture BEFORE evidence

Where runtime visual proof is required, capture the exact target before mutation using the same route, viewport, browser/device configuration and state model intended for AFTER comparison.

Record source hashes.

## Step 16 — Generic Application Engine preview

Generate deterministic patch and result preview.

Preview must contain:

```text
target
canonical source
generated output
selectors/units
property operations
before hashes
expected after hashes when deterministic
scope
rollback manifest plan
```

No mutation.

## Step 17 — Generic Application Engine apply

On exact reviewed plan:

```text
verify all preconditions again
write exact backups
patch canonical authority atomically
run declared projection
verify product output
verify hashes
record transaction
```

If any write/verification step fails, automatically rollback exact affected bytes.

## Step 18 — Static/source validation

Run the narrow applicable gates:

```text
Visual Core
Identity Dictionary
RIFAT authority
target index
binding resolver
projection parity
scope
zero-important
source drift
Atlasfin static validation where applicable
```

Static PASS is not visual PASS.

## Step 19 — Runtime visual QA

Capture AFTER using the same target setup.

Require as applicable:

```text
same route
same viewport
same browser/device
same target
expected visual change present
geometry acceptable
no overflow/collision
required states checked
no new console errors
no target network failures
reduced-motion behavior
accessibility invariants
```

Skipped states must remain explicit.

## Step 20 — Domain-specific verification

Use Authority Mesh/impact evidence to decide whether additional gates apply.

Examples:

```text
Sync Sentinel
licensing
custody/data
runtime contracts
shared dependency regressions
```

Do not run every tool ceremonially when the affected domain is unrelated.

## Step 21 — Change Assurance OBSERVE / VERIFY / PROVE

Produce reproducible evidence tied to source snapshot/provenance.

No evidence, no green.

## Step 22 — PR and exact-SHA CI

Run gates against one exact PR head.

Do not add cosmetic closing commits after the final certification without rerunning required gates.

## Step 23 — Revalidate if main moves

Use AutoMesh v2:

```text
PASS_ALREADY_CURRENT
PASS_NO_RELEVANT_DRIFT
BLOCKED_RELEVANT_DRIFT
BLOCKED_NON_ANCESTOR_DRIFT
BLOCKED_INVALID_PRIOR_AUTHORITY
```

Only valid rebound/fresh authority may continue.

## Step 24 — Merge guard and merge

Merge only the reviewed, certified exact scope.

AutoGit may help with Git mechanics but does not grant authority.

## Step 25 — Post-merge verification

Verify actual canonical `main`.

Run the required post-merge checks when evidence or contracts require them.

## Step 26 — Factory Ledger / Evidence Index closure

Update Ledger/evidence only if capability truth actually changed.

Record:

```text
status/maturity
state label
evidence
nextGate
doNotRebuild
doesNotProve
allowed/forbidden actions or claims where applicable
```

This creates the anti-rework starting point for the next task.

---

# 10. Surface readiness Bingo

The system must generate a single master view instead of forcing operators to infer readiness from unrelated files.

Recommended columns:

| Field | Meaning |
|---|---|
| Surface | Tablet / PC / Mobile / Web / Chart Lab / Control Center / Shared |
| Census current | Broad UIMAP/current physical discovery is valid |
| Route resolved | Route identity proven |
| Owner resolved | Canonical source owner proven |
| Region resolved | Visual region proven |
| Slot resolved | Editable slot proven |
| Visual target resolved | Exact style target/selector proven |
| Physical layer resolved | Implementation layer proven |
| NDC meaning | Neutral meaning proven |
| Binding | Semantic target binding certified |
| Recipe | Compatible governed recipe exists |
| Projection | Canonical source → runtime output resolved |
| Authority eligible | Target can enter exact Mesh/application preflight |
| Generic apply | Generic engine supports this target format |
| Source applied | Latest authorized application transaction |
| Runtime visual | Runtime evidence status |
| Final status | DISCOVERED → VISUAL_CERTIFIED or explicit BLOCKED state |

No hand-maintained percentages.

Counts and statuses must be generated from current authority/evidence.

---

# 11. Current architecture vs final target architecture

## Already-existing foundations

The final design reuses existing foundations instead of rebuilding them:

```text
Factory Ledger
Universal anti-rework gate
Authority Mesh / AutoMesh
Code Atlas
UIMAP
NDC canon
RIFAT / prisma-ui
Identity Dictionary
Atlasfin
Visual Source Manifest
Visual Core
UI Bridge resolver/planner
runtime visual evidence pattern
Mamastrophic / ScreensQA
Change Assurance
GitHub Actions
AutoGit
Factory Ledger closure
```

## Target additions / generalization

The intended missing/generalized layer is:

```text
persistent generated Visual Target Index
system-wide binding promotion workflow
Generic Visual Application Engine in prisma-html
generic application request/result/evidence schemas
generic preview/apply/verify/rollback
surface readiness Bingo generated from current truth
```

The architecture must not claim these are implemented merely because they appear in the final-state diagram.

Implementation status belongs in Factory Ledger and generated readiness evidence.

---

# 12. Proposed repository changes to adopt this Master Map

## New canonical operator document

Target path:

```text
prisma-html/docs/ops/PRISMA_VISUAL_CHANGE_MASTER_MAP.md
```

This should be the only maintained copy.

## Files that should reference it

After the appropriate governed documentation/authority task authorizes the change:

```text
AGENTS.md
prisma-html/README.md
prisma-html/docs/ops/README.md
prisma-html/docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md
prisma-html/CONTINUATION.md
apps/terminal-de-venta-system/docs/ops/README.md
apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md
```

The root `AGENTS.md` rule should state:

> **Before any visual modification to any PRISMA surface, read `prisma-html/docs/ops/PRISMA_VISUAL_CHANGE_MASTER_MAP.md`, then run the required Factory Ledger/Authority Mesh workflow before editing.**

The Field Manual should record this as an operational startup rule, not as a competing authority.

The visual runbook should point to this document as the architecture/lifecycle overview and continue to own detailed visual-authority operating commands.

---

# 13. Files intended for the Generic Application Engine

Create, under a separately authorized implementation task:

```text
prisma-html/tools/build_visual_target_index.py

prisma-html/tools/visual_application/
  __init__.py
  engine.py
  preflight.py
  request.py
  resolver.py
  projection.py
  rollback.py
  evidence.py
  integrity.py
  safety.py
  writers/
    __init__.py
    css.py
    css_module.py
    json_tokens.py
    generated_projection.py
  validators/
    request_validator.py
    target_validator.py
    plan_validator.py
    projection_validator.py
    evidence_validator.py

prisma-html/authority/rifat/identity/contract/application/
  PRISMA_VISUAL_APPLICATION_REQUEST_V1.schema.json
  PRISMA_VISUAL_APPLICATION_RESULT_V1.schema.json
  PRISMA_VISUAL_APPLICATION_EVIDENCE_V1.schema.json
  PRISMA_VISUAL_APPLICATION_ROLLBACK_V1.schema.json
```

Modify only where required:

```text
prisma-html/tools/identity_binding_resolver_core.py
prisma-html/tools/visual_core.py
prisma-html/authority/rifat/identity/registries/element-bindings.registry.json
prisma-html/docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md
prisma-html/README.md
.github/workflows/viscore1-cert.yml
tools/code-atlas/tests/test_ui_bridge_v1.py
```

Retain the Cobrar-specific certified path until generic parity is proven.

Do not delete certified evidence or historical transactions.

---

# 14. Definition of Done for the Generic Visual Application Engine

The engine is not DONE merely because `apply` writes a CSS file.

It is complete only when:

```text
1. It consumes exact resolved target records, never guesses.
2. It consumes current validated UI Bridge plans.
3. It requires valid mutation authority.
4. It validates all source hashes before mutation.
5. It patches canonical visual authority, not generated outputs directly.
6. It deterministically regenerates declared projections.
7. It supports preview/apply/verify/rollback.
8. It backs up exact bytes before mutation.
9. It is idempotent.
10. It automatically restores exact prior bytes on failed application.
11. It prevents surface expansion.
12. It rejects stale bindings/layers/targets.
13. It rejects unsupported writer kinds.
14. It has native negative tests.
15. It proves parity against the certified Cobrar golden transaction.
16. It produces sanitized reproducible evidence.
17. It integrates with Visual Core readiness.
18. It never turns source/static PASS into runtime visual certification.
19. It survives relevant-drift / AutoMesh revalidation semantics.
20. Factory Ledger records the real achieved maturity and doNotRebuild state.
```

---

# 15. Golden operating examples

## Example A — PC target already censused but binding pending

```text
User asks for visual change
↓
Ledger proposal
↓
Mesh
↓
reuse current PC UIMAP / Visual Control target
↓
DO NOT broad-recensus PC
↓
resolve NDC meaning
↓
author/certify missing identity-layer + binding
↓
UI Bridge plan
↓
mutation gate
↓
Generic Application Engine
↓
PC projection
↓
runtime visual QA
↓
Change Assurance
↓
PR/merge
↓
Ledger
```

## Example B — target physically missing

```text
User asks for target
↓
Ledger + Mesh
↓
UIMAP cannot prove target
↓
UNMAPPED / BLOCKED
↓
target-specific discovery or source task
```

Do not invent a component ID, binding or layer.

## Example C — runtime differs from RIFAT

```text
RIFAT source hash != product output hash
↓
inspect exact-copy drift and Git/current authority
↓
if runtime contains legitimate newer governed work:
    reconcile/promote without downgrade
else:
    restore deterministic projection from canonical authority
↓
refresh hashes mechanically
↓
revalidate
```

Never overwrite a legitimate newer runtime merely to make a validator green.

---

# 16. Operator quick path

For every visual task, remember:

```text
LEDGER
  ↓
ANTI-REWORK PROPOSAL
  ↓
MASTER MAP
  ↓
MESH + LAYER MAP
  ↓
REUSE CENSUS
  ↓
CODE ATLAS / UIMAP
  ↓
NDC MEANING
  ↓
RIFAT LOCATION
  ↓
IDENTITY RECIPE
  ↓
BINDING
  ↓
UI BRIDGE PLAN
  ↓
ANTI-REWORK MUTATION
  ↓
GENERIC ENGINE IN PRISMA-HTML
  ↓
DETERMINISTIC PRODUCT PROJECTION
  ↓
STATIC VALIDATION
  ↓
RUNTIME VISUAL QA
  ↓
DOMAIN VERIFIERS IF IMPACTED
  ↓
CHANGE ASSURANCE
  ↓
PR / EXACT SHA
  ↓
MERGE / POST-MERGE
  ↓
FACTORY LEDGER
```

---

# 17. Permanent anti-confusion rules

1. **A census is not a binding registry.**
2. **A binding registry is not the full UI inventory.**
3. **A physical target can be known while semantic binding remains pending.**
4. **NDC meaning must not be inferred from an app-specific filename.**
5. **RIFAT location must not become neutral meaning.**
6. **Code Atlas plans and observes; it does not become visual authority.**
7. **Atlasfin operates visual authority but does not write product directly.**
8. **The Generic Visual Application Engine belongs in `prisma-html`.**
9. **Generated product outputs are projections, not competing editable authorities.**
10. **Factory Ledger and Mesh bracket the work: proposal before planning, mutation gate before writing.**
11. **Broad rediscovery is forbidden when current exact evidence already proves the target.**
12. **UNKNOWN, PARTIAL and BLOCKED are valid outcomes.**
13. **Functional PASS is not visual PASS.**
14. **Static/source-ready is not runtime visual certification.**
15. **One certified target does not certify a whole surface.**
16. **No final visual claim without reproducible runtime evidence where the contract requires it.**
17. **No visual task starts by editing CSS. It starts by resolving governed truth.**

---

# 18. Source authorities this document is designed to connect

This map is intended to be read together with the current versions of:

```text
PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md
PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json
PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json

apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md
apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md

apps/terminal-de-venta-system/docs/ndc/00_NDC_README.md
apps/terminal-de-venta-system/docs/ndc/*

tools/code-atlas/README.md
tools/code-atlas/CODE_ATLAS_CHANGE_ASSURANCE_CONTRACT.json
tools/code-atlas/src/code_atlas/app_map/uimap/*
tools/code-atlas/src/code_atlas/ui_bridge/*

prisma-html/README.md
prisma-html/authority/rifat/identity/contract/PRISMA_VISUAL_CORE_CONTRACT.md
prisma-html/authority/rifat/identity/*
prisma-html/authority/rifat/prisma-ui/*
prisma-html/authority/rifat/visual-source-manifest.json
prisma-html/docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md
prisma-html/tools/visual_core.py
prisma-html/extras/atlasfin/*

tools/Plawright Mamastrophic/*
apps/terminal-de-venta-system/.prisma-ui/*
.github/workflows/*
autogit/*
docs/govos/*
```

The task-exact Authority Mesh determines which subset is actually required for a specific change.

---

# 19. Final doctrine

PRISMA visual work should never again be a loose sequence of:

```text
find CSS
change CSS
refresh browser
hope
```

The final operating model is:

```text
know existing capability
authorize the task
reuse the census
identify neutral meaning
resolve exact visual coordinates
select governed visual intent
certify the binding
plan deterministically
authorize mutation
apply through the canonical visual engine
project deterministically
prove runtime outcome
close evidence and maturity
```

That is how a visual change becomes a traceable PRISMA operation instead of an isolated styling edit.
