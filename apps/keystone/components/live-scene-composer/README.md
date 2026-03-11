# Live Scene Composer (Future Boundary)

Status: scaffold-only

This boundary is reserved for future write-capable live composition.

Rules:
- Runtime Debug Console must not depend on this module.
- Any mutation to runtime scene state must go through `runtime-mutation-bridge`.
- No debug-only diagnostics logic should be implemented here.

Current scope:
- Shared SceneLookModel typing/helpers moved here for future composer use.
- Contracts only; no full composer UI implemented.
