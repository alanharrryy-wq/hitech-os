# 90 End-to-End Mutation UI Wiring Overview

The UI wiring layer exists to connect authoring surfaces to the mutation path without turning the UI into a policy engine.

The core path is:

1. selection context resolves the active authoring target
2. a surface emits a typed UI action envelope
3. the envelope is converted into a typed mutation intent
4. the mutation path validates source, target, mode, and scope
5. preview or commit is routed through the bridge
6. compare/apply state is updated from preview session lineage
7. diagnostics and evidence are emitted for review

This keeps the UI expressive while preserving the bridge as the write boundary.
