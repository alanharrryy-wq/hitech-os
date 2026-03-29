# 27_PERFORMANCE_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Performance goals, sources of cost, and performance-aware design rules

---

## Purpose

This document defines the performance model for Live Scene Composer. It exists because a live visual authoring product lives or dies on responsiveness. If the product feels sluggish, delayed, or unstable under normal editing, users stop trusting it quickly.

Performance should not be treated as “optimize later” decoration.
The basic performance model should shape architecture from the start.

---

## Performance Principles

The product should optimize for:

- responsive interaction
- fast selection feedback
- predictable preview updates
- bounded recomputation
- local rendering work where possible
- graceful degradation under load
- architecture-aware performance, not hacks

The goal is not perfect micro-optimization.
The goal is a responsive system whose performance characteristics remain understandable.

---

## Primary Performance Sensitivities

The most performance-sensitive areas are likely:

- selection changes
- canvas interaction
- drag / resize / reorder workflows
- inspector updates
- structure synchronization
- preview rendering
- runtime observation and mapping
- module contribution loading or reactivity
- future custom widget isolation surfaces

These areas should be designed with cost awareness.

---

## Performance Goals by Experience

### Selection should feel immediate

Selecting a widget or slot should quickly update:

- visual selection state
- handles and overlays
- structure highlighting
- inspector context

Users should not feel like selection is a batch job.

### Direct manipulation should feel live

Dragging, resizing, and reordering should feel smooth enough that the system reads as interactive, not transactional.

### Preview should remain credible

Preview updates should be timely and consistent enough that users believe the system is showing the real current draft state.

### Shell stability should remain intact

Performance issues in one module or one widget type should not freeze the entire Composer shell whenever possible.

---

## Major Sources of Performance Cost

### Scene model recomputation

Expensive scene model recalculation can make normal editing feel delayed.
Updates should prefer targeted recalculation over broad invalidation where possible.

### Inspector recalculation

If every selection change causes heavy recomputation across unrelated inspector modules, responsiveness will degrade quickly.

### Canvas overlay churn

Handles, guides, hover state, and bounds overlays can become expensive if they redraw too broadly or too often.

### Runtime mapping and measurement

Reading runtime-observed state can be costly if done excessively, synchronously, or without good scoping.

### Module-wide reactivity

If every module re-renders or recomputes for every small state change, modularity becomes expensive instead of helpful.

### Heavy widget rendering

Some widgets, especially charts and future custom widgets, may introduce significant rendering cost.

---

## Performance-Aware Architectural Rules

### Rule 1: Keep domain and interaction state scoped

Not every interaction change should invalidate the full scene or the full shell.

### Rule 2: Prefer targeted invalidation

Selection changes should update the necessary surfaces, not everything.

### Rule 3: Avoid all-knowing global render paths

A single giant render path that depends on all state is a performance trap.

### Rule 4: Treat expensive runtime reads carefully

Runtime measurement and mapping should be explicit and bounded.

### Rule 5: Keep module contributions local

Modules should respond to the context they need, not to broad product state they do not own.

---

## Selection Performance

Selection is one of the most frequent actions in the product.
It must remain cheap.

The system should aim to ensure that selection updates:

- do not trigger full scene recomputation
- do not cause unrelated module churn
- do not create broad layout recalculation unless required
- keep inspector target resolution reasonably bounded

If selection is slow, the whole product feels broken.

---

## Drag and Resize Performance

Drag and resize interactions should favor:

- low-latency local feedback
- bounded mutation or preview scheduling
- careful separation between interaction-phase updates and accepted-state transitions
- efficient overlay rendering

The system should avoid a model where every pixel movement becomes a giant global recalculation.

---

## Structure and Inspector Coordination

Structure and inspector synchronization matters for usability, but it should be implemented carefully.

A good approach favors:

- lightweight target resolution
- memoized or scoped contribution activation
- avoiding full tree rerender on small unrelated changes
- explicit boundaries between structure view state and domain state

---

## Module Performance Responsibility

Modules are not exempt from performance discipline.

A module should:

- subscribe narrowly
- compute only what it needs
- clean up properly
- avoid broad polling
- avoid expensive recomputation on every selection tick

A module that behaves like a global observer of everything will eventually make the product feel heavy.

---

## Chart and Rich Widget Performance

Charts and other visually complex widgets deserve special attention.

Possible concerns include:

- rerender cost
- layout thrash
- expensive data formatting
- heavy prop transformations
- unnecessary redraws during selection or hover

The authoring system should not treat all widgets as equally cheap.

---

## Future Custom Widget Performance

Custom widgets introduce additional performance risk.

The sandbox model should consider:

- isolation overhead
- messaging overhead
- rendering cost
- failure containment
- slot-bounded repaint or refresh behavior

Custom extension must not be allowed to make the core authoring shell unpredictably sluggish.

---

## Performance Anti-Patterns

The system must reject:

- global rerender on small local interactions
- hidden broad subscriptions in every module
- synchronous heavy runtime measurements in hot paths
- coupling preview correctness to expensive full-tree recomputation
- using performance hacks that break architecture semantics
- “works on my machine” as performance validation

---

## Performance Validation

Performance should be validated through:

- interaction-focused profiling
- targeted render or recomputation inspection
- smoke checks for obvious regressions
- careful review of hot paths
- evidence when major performance-sensitive seams change

This does not require premature obsession, but it does require awareness.

---

## Summary

The performance model for Live Scene Composer should prioritize responsive interaction, bounded recomputation, and local cost control. Selection, canvas interaction, preview, runtime mapping, and module contributions are the main areas to watch. The system should be designed so that normal authoring feels immediate and stable without sacrificing architectural clarity.
