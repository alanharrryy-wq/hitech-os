# CAN PATCH DECISION

`YES_SAFE_TO_PATCH_SOURCE_REGISTRIES_ONLY`

Allowed:
- Code Atlas evidence ingestion registers.
- Source-only Atlas resolver improvements.
- Documentation/registry updates that preserve production red truth.

Blocked without explicit gate:
- Production green claims.
- Runtime/server/port work.
- Prisma hot generation/migration execution.
- App surface changes outside declared scope.
- Raw DB export in evidence ZIPs.
