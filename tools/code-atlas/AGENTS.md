# Code Atlas agent rules

- Reusable Code Atlas execution is environment-neutral and product-neutral by default.
- Project-specific values belong in explicit profiles or adapters, never generic core defaults.
- `CODE_ATLAS_PROJECT_ROOT`, `CODE_ATLAS_OUTPUT_ROOT`, `CODE_ATLAS_RESULT_ROOT`, and `CODE_ATLAS_PROFILE` are the canonical runtime inputs.
- Never assume a drive letter, developer home, repository name, product path, local port, domain, or fixed surface taxonomy in reusable code.
- Product adapters are opt-in only. Generic entrypoints must not select one implicitly.
- Keep `code-atlas.py` compatible unless a separately governed migration authorizes replacement.
- New reusable features go under `src/code_atlas/*`; product-specific compatibility belongs behind explicit adapter/profile boundaries.
- No fake green. Source readiness, runtime evidence and production certification are distinct.
- No source, Git, DB, process, port, deployment, or dependency mutation from read-only analysis paths.
- Any installation or replacement workflow must preserve rollback and evidence under the operator-configured output location.

## PRISMA / hitech-os Authority Mesh adapter rules

These rules apply only when Code Atlas is being consumed by PRISMA/hitech-os governance. They do not become defaults of the reusable neutral engine.

- Read `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md` and `apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md` before governed PRISMA repository mutation.
- Use a fresh task-exact Authority Mesh for the exact change when required by PRISMA governance. Do not reuse a generic or neighboring task's Mesh.
- If canonical `main` moves, treat it as a drift event. Run AutoMesh v2 revalidation rather than unconditionally destroying authority or silently reusing stale evidence.
- Only `PASS_ALREADY_CURRENT` or `PASS_NO_RELEVANT_DRIFT` evidence bound/rebound to the current HEAD may continue without a full Mesh. Relevant or non-ancestor drift requires a fresh full Mesh. Invalid prior evidence fails closed.
- `CANDIDATE` retrieval never becomes authority through convenience, repetition or semantic similarity.
- For visual work, missing governed surface Mesh / `LAYERS_MAP.json` is a blocker. Functional PASS is not visual proof.
- Cross-platform pin verification must use the certified repository-inventory Git blob identity relationship. Do not weaken tests to hide CRLF differences.
- Revalidation artifacts are evidence. Preserve digest/manifest/chain validation and ZIP traversal/symlink/collision/size protections.
- Independent read-only revalidations may run concurrently when isolated by request/task. Mutation/merge gates remain governed by current authority and actual overlap.
- A successful AutoMesh run, revalidation, CI run or source merge does not set `productionCertified=true`.
