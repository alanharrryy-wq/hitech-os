# 09_RUNTIME_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Runtime-facing behavior and the composer's relationship to the real runtime

---

## Purpose

This document defines how Live Scene Composer should relate to the runtime. It exists to prevent a recurring class of mistakes: treating the runtime as either irrelevant to authoring or as a free-for-all target for arbitrary writes.

The runtime matters deeply, but it must be engaged through disciplined boundaries.

---

## Runtime Model Summary

Live Scene Composer is built on top of the real runtime, but it is not allowed to own the runtime, rewrite the runtime’s architectural rules, or mutate runtime internals directly at will.

The composer must:

- observe enough runtime information to provide true live authoring
- align its visual editing experience with real rendered output
- route write-capable changes through runtime-mutation-bridge
- preserve separation between authoring intent and runtime effect

---

## Core Runtime Principle

The runtime must not depend on the composer.
The composer may depend on runtime capabilities only through controlled, bounded integration seams.

This is one of the most important architectural principles in the system.

---

## Runtime Relationship Types

The composer may have several kinds of relationship with runtime-facing systems.

### 1. Observation

Reading runtime-facing information such as:

- visual bounds
- render identifiers
- region mappings
- measured layout facts
- scene render state relevant to authoring alignment

Observation helps the composer stay accurate.

### 2. Presentation coupling

The canvas must show the real rendered result or a faithful runtime-backed representation. The composer is therefore presentation-coupled to the runtime outcome, even if the domain model is distinct.

### 3. Controlled write-capable interaction

When the composer initiates changes that affect runtime-facing state, those changes must pass through runtime-mutation-bridge.

This is the only acceptable write relationship.

---

## Runtime as Execution Environment, Not Ownership Target

The runtime is the environment in which the scene ultimately renders and behaves.
The composer is a client of this environment for authoring purposes.

The composer should not assume:

- unrestricted ownership of runtime state
- privilege to call arbitrary runtime internals
- license to infer stable architecture from current runtime implementation details

The runtime is an integration partner, not a dumping ground for authoring shortcuts.

---

## Runtime Observation Needs

To support quality authoring, the composer likely needs access to:

- element bounds and coordinates
- slot region mapping
- layer ordering information where relevant to selection or overlays
- scene render state for accurate preview
- stable references or adapters that map authoring entities to runtime instances

These reads should be routed through appropriate adapter or contract layers where possible.

---

## Runtime Write Model

The runtime write model must remain governed.

### Rule

If a composer action causes a write-capable effect on runtime-facing state, that action must go through **runtime-mutation-bridge**.

### Why

This enables:

- validation
- auditing
- policy enforcement
- safe mode / advanced mode decisions
- reversibility expectations
- clearer testing and reasoning

### Prohibited pattern

UI control -> direct runtime state mutation -> hope for the best

That pattern is banned.

---

## Runtime Adapter Seams

The runtime should be accessed through explicit adapter seams where needed.

Adapter seams may help with:

- mapping scene entities to runtime representations
- translating layout intents into runtime-friendly operations
- reading scene runtime facts
- applying validated mutation results to runtime-facing paths

Adapters are valuable because they preserve explicitness and make integration behavior testable.

---

## Preview Semantics in Runtime Context

Live authoring requires that preview feel real.
However, runtime-facing preview must remain semantically distinct from accepted commit.

The system must support the idea that:

- something can be visibly previewed
- without yet being accepted as baseline
- without silently becoming persistent accepted truth

If the runtime view cannot reflect that distinction, trust degrades.

---

## Runtime Failure Isolation

The runtime model must assume that authoring interactions can fail.

Failure examples:

- invalid mutation requests
- adapter mismatch
- stale runtime mapping
- broken widget rendering
- future custom widget execution failure
- unsupported preview transition

Expected response:

- fail clearly
- fail locally where possible
- preserve broader scene integrity
- preserve product shell stability
- avoid global collapse for local authoring errors

---

## Runtime Debug Console Relationship

Runtime Debug Console may inspect runtime internals more directly for diagnostics purposes, but that does not grant the composer the same rights.

The composer may reuse shared infrastructure from console-core, but must not inherit debug-specific mutation habits or diagnostic privilege as if it were authoring authority.

These are different products with different responsibilities.

---

## Runtime Modes and Safety

The runtime-facing behavior of the composer should be sensitive to mode.

### Safe Mode

Safe Mode should permit only bounded, validated, policy-approved authoring operations.

### Advanced Mode

Advanced Mode may enable more powerful behavior later, but only through deliberate, explicit expansion of the contract model. It should not become a loophole for bypassing architecture.

---

## Runtime Invariants

The following invariants must hold:

1. The runtime does not depend on the composer for its core functioning.
2. The composer does not write directly to runtime internals.
3. Runtime-observed facts may influence authoring but do not replace the scene model.
4. Preview and commit remain distinguishable.
5. Bridge validation remains the gate for write-capable runtime effect.
6. Failures in authoring should not globally destabilize the runtime.
7. Debug privileges do not automatically transfer to authoring flows.

---

## Runtime Anti-Patterns

The following are architecture failures:

- direct composer writes into runtime internals
- route bindings that mount authoring through debug-only flows
- using runtime inspection paths as authoring mutation paths
- treating observed render structure as the sole source of composition truth
- bypassing bridge validation because “it’s just UI”
- assuming advanced runtime knowledge is a substitute for explicit authoring contracts

---

## Summary

Live Scene Composer is runtime-aware and runtime-backed, but not runtime-owning. It must observe enough of the real runtime to make visual authoring true, while routing all write-capable changes through runtime-mutation-bridge. The runtime is a controlled integration partner, not an unrestricted authoring substrate.
