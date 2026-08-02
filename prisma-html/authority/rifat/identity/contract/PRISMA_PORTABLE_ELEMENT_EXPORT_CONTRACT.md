# PRISMA Portable Element Export Contract

Status: `SOURCE_READY / INSTRUCTION_ONLY`

## Canonical chain

neutral meaning → identity profile → recipe/preset → surface adapter → known binding
→ portable instruction → future governed application

## Hard rules

1. Every export uses schema `prisma.identity.portable-element-export.v1`.
2. Every artifact carries all trace fields. Unknown bindings are `null`, never invented.
3. Missing concrete product bindings produce `BLOCKED_BY_MISSING_BINDING` or a more
   specific blocking status.
4. SHA-256 covers every top-level field except `exportId` and `integrity`.
5. Reimport verifies and inspects only. It never edits product runtime.
6. `runtimeMutationAllowed` is always `false`.
7. No artifact may claim visual certification, deployment or product application.
8. A future application engine must resolve authority, validate target hashes, create
   rollback, generate evidence and pass surface-specific visual gates.
