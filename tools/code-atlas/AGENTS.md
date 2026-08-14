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
