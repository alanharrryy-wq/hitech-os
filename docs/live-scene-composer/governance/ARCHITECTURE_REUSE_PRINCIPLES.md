# ARCHITECTURE REUSE PRINCIPLES

## Goal
Ensure the Live Scene Composer can power multiple projects without modifying the core.

## Design Principles

### 1. Separation of Authoring and Runtime
The Composer edits scenes but does not directly mutate runtime state.

### 2. Scene Graph as Canonical Model
Scene → Layout → Slot → Widget is the canonical hierarchy.

### 3. Explicit Extension Seams
All extensions occur through:
- Module SDK
- Runtime adapters
- Mutation bridge policies

### 4. Safe Mode Default
New environments start in Safe Mode. Advanced capabilities require explicit enablement.

### 5. Boundary Discipline
Core layers must never import project modules.