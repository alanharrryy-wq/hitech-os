# PRISMA Authority Mesh cartridge

Authority Mesh is not a universal Capatch dependency. It is a cartridge/provider used when a PRISMA/hitech-os task needs repo authority before patching.

When active, this cartridge expects the job context to include authority evidence such as:

- `AUTHORITY_READSET.lock.json`
- `APP_IMPACT_MATRIX.md`
- `CONTRACT_AND_GATE_MATRIX.json`
- `MISSING_OR_UNMAPPED_RISK.md`
- `AGENT_PROMPT_ENVELOPE.md`
- `AUTHORITY_MESH_REPORT.md`

Without those inputs, PRISMA premium/app-wide patches should stop before mutation.
