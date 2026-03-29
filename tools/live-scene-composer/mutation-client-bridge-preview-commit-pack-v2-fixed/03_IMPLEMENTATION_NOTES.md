# Implementation Notes

This package keeps the mutation path intentionally small and explicit.

## Main constraints
- no direct UI-to-runtime writes
- preview and commit stay semantically separate
- target/source/mode/scope remain typed
- adapters stay replaceable
- rejection paths remain observable
- revert/discard stay explicit, never magical

## Intended layering
surface action -> typed mutation intent -> validation -> policy -> preview session / commit orchestration -> bridge adapter -> diagnostics / history

## Not included on purpose
- runtime internals
- scene persistence implementation
- actual bridge transport ownership
- global undo/redo productization
- server APIs
