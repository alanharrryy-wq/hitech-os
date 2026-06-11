# PRISMA GovMesh2 Visual Capability Resolver

This package upgrades `tools/prisma-governance/authority_mesh.py` so the Authority Mesh natively generates visual availability/capability outputs for every task.

New outputs generated inside `.governance/current`:
- `VISUAL_CAPABILITY_MATRIX.json`
- `VISUAL_CAPABILITY_MATRIX.md`
- `VISUAL_STACK_DECISION.md`
- `APP_VISUAL_EXPLOITATION_MATRIX.md`

Rule:
- No premium/visual claim without visual capability matrix.
- No visual patch without visual stack decision.
- No multi-surface visual work without app visual exploitation matrix.
- Available visual capability means mandatory consideration, not blind mandatory use.

Safety:
- No process kill.
- No port cleanup.
- No dev server start.
- No Prisma hot regeneration.
- Rollback included.
