# REUSABLE_CORE_BOUNDARY

## Purpose
Define what belongs to the reusable Live Scene Composer core and what belongs to project-specific layers.

## Core (Reusable Across Projects)
- Composer Shell
- Scene Model (Scene -> Layout -> Slot -> Widget)
- Selection Model
- Structure Tree Layer
- Inspector Layer
- Mutation Intent Client
- Module Registration System
- Runtime Adapter Interface
- Safe / Advanced Mode Handling

## Project-Specific Layer
Projects should implement:
- Runtime adapters
- Domain widgets
- Project modules
- Bridge command policies
- Validation rules and schemas

## Non-Negotiable Rules
1. Selection is UI interaction state, never domain truth.
2. Domain writes must pass through the Runtime Mutation Bridge.
3. Scene graph structure cannot be bypassed.
4. Modules must register via the SDK seam.
5. Core must not depend on project modules.

## Protected Nodes
The following areas require strict discipline:
- Scene Model contracts
- Mutation bridge contracts
- Provider seams
- Module SDK
- Dependency policy rules

## Development Sequence
1. Selection Model
2. Structure + Inspector integration
3. Mutation intent layer
4. Bridge command interface
5. Safe modules
6. Runtime adapters
