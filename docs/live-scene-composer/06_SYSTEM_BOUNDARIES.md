# 06_SYSTEM_BOUNDARIES

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: Ownership boundaries, import discipline, and cross-system responsibility control

---

## Purpose

This document defines the major boundaries in the Live Scene Composer ecosystem and the rules that preserve them. It exists because boundaries are easier to state than to preserve, and once blurred they are expensive to restore.

A system with weak boundaries eventually replaces design with accidental coupling.
This document exists to prevent that.

---

## Boundary Summary

The system must preserve these top-level boundaries:

- **console-core**: shared infrastructure
- **runtime-debug-console**: diagnostics product
- **live-scene-composer**: authoring product
- **runtime-mutation-bridge**: runtime write governance boundary

Surrounding runtime and scene ecosystems may be integrated, but they do not erase these ownership lines.

---

## Boundary 1: console-core

### Purpose

console-core is the only shared infrastructure layer intended for sibling product reuse.

### Allowed responsibilities

- shell primitives
- layout primitives
- registry primitives
- event infrastructure
- lifecycle helpers
- shared runtime invariants
- genuinely shared diagnostics helpers
- common product-shell building blocks that remain product-neutral

### Forbidden responsibilities

- runtime-debug-specific product logic
- composer-specific authoring logic
- mutation policy logic that belongs in the bridge
- scene authoring semantics
- direct ownership of prefab, slot, or widget composition systems
- product-specific routing shortcuts

### Boundary rule

If a concern is shared only because current code placement is convenient, it does not belong here.

---

## Boundary 2: runtime-debug-console

### Purpose

runtime-debug-console is the diagnostic sibling product.

### Allowed responsibilities

- runtime inspection
- overlays and layer visibility aids
- performance diagnostics
- event monitoring
- runtime state visualization
- safe operational debug controls

### Forbidden responsibilities

- visual scene authoring
- scene composition
- layout editing as authoring functionality
- prefab insertion
- general style editing for composition
- custom widget authoring
- composer module registration

### Boundary rule

runtime-debug-console may inspect the scene and runtime but must not become the place where scene composition is authored.

---

## Boundary 3: live-scene-composer

### Purpose

live-scene-composer is the authoring sibling product.

### Allowed responsibilities

- scene composition shell
- canvas interaction
- selection
- structure tree
- inspector
- layout authoring
- slot and widget composition
- prefab insertion
- appearance editing
- chart styling and visual treatment
- draft / compare / revert workflows
- bounded custom widget systems
- authoring-specific module registration

### Forbidden responsibilities

- bypassing runtime-mutation-bridge
- absorbing runtime diagnostics concerns
- mutating runtime internals directly
- reclassifying shared infrastructure as product-specific by stealth
- inheriting debug routes or runtime-debug registration flows

### Boundary rule

The composer owns authoring, not diagnostics, and not unrestricted runtime access.

---

## Boundary 4: runtime-mutation-bridge

### Purpose

runtime-mutation-bridge is the enforcement boundary between authoring intent and write-capable runtime effect.

### Allowed responsibilities

- mutation contracts
- validation
- mutation allowlists
- source and target checks
- safe mode / advanced mode gating
- preview / commit / revert semantics at mutation level
- adapter routing to downstream runtime-facing systems

### Forbidden responsibilities

- becoming the general owner of authoring UI
- housing broad product logic unrelated to mutation governance
- becoming a hidden substitute for scene modeling
- bypassing its own policies through privileged shortcuts

### Boundary rule

All write-capable composer mutations must pass through the bridge, and the bridge must remain a real policy boundary rather than a naming ornament.

---

## Read vs Write Boundary

A useful distinction in the system is the difference between reading and writing.

### Read-oriented relationships

Read-oriented relationships may include:

- reading runtime state for inspection
- reading scene structure for composition
- reading visual bounds for interaction overlays
- reading allowed capabilities or contract metadata

Read access still needs discipline, but it is not equivalent to write authority.

### Write-oriented relationships

Write-oriented relationships are more sensitive and must be explicitly governed. Examples include:

- changing widget props
- changing layout or positioning
- applying style changes
- inserting or removing widget instances
- committing draft changes to accepted state

These changes must pass through runtime-mutation-bridge when they affect runtime-facing state.

---

## Ownership Boundaries Inside the Composer

Even within live-scene-composer, ownership must remain explicit.

### Scene model owns

- overall scene composition structure
- scene-level metadata
- top-level layout reference
- slot registry association
- widget instance inclusion

### Layout owns

- structural placement
- ordering
- spatial relationships
- layout node hierarchy

### Slots own

- bounded region semantics
- host constraints
- widget acceptance policy
- capacity and insertion rules

### Widgets own

- instance-level content props
- style props
- widget-specific runtime bindings where applicable

### Inspector owns

- presentation of editable properties for a current selection
- it does not own composition truth by itself

### Canvas owns

- direct interaction and live feedback surface
- it does not own domain truth either

This separation matters because flattening these roles produces unmaintainable state.

---

## Boundary Violation Examples

The following are examples of unacceptable boundary violations:

1. A composer panel registered through runtime-debug-console paths
2. A shared console-core helper that knows about widget prefab policy
3. A composer UI directly calling runtime internals without bridge validation
4. A runtime-debug overlay mutating scene layout in authoring ways
5. A slot system that secretly behaves like a layout tree
6. A widget instance that performs unrestricted global side effects
7. A route-binding shortcut that mounts composer inside debug-specific flows

These are not harmless conveniences. They are architecture debt.

---

## Boundary Preservation Techniques

The project should actively preserve boundaries through:

- file and package structure
- import discipline
- dependency policy
- architecture guard checks
- registration seam tests
- mutation-path tests
- protected-node tracking
- clear documentation and ownership rules

Good intentions alone are not enough.

---

## Boundary Review Questions

When reviewing a change, ask:

1. Which boundary does this code belong to?
2. Which boundary does it now depend on?
3. Is that dependency read-only, write-capable, or mixed?
4. Is this concern truly shared or merely reused?
5. Does this change blur the debug/composer distinction?
6. Does this bypass the mutation bridge?
7. Would this make future wiring easier or more dangerous?

If the answers are fuzzy, the boundary is probably being weakened.

---

## Summary

System boundaries in Live Scene Composer are a core part of product and architecture correctness. console-core is shared infrastructure only. runtime-debug-console is diagnostics only. live-scene-composer is authoring only. runtime-mutation-bridge governs write-capable mutations. These lines must be preserved in naming, imports, runtime paths, and ownership decisions.
