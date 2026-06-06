# PRISMA Liquid Glass Optical Proof 0206

Status: strict Liquid Glass Capsule Spec v1 applied to `components/prisma-glass-capsule`.

Material rules now enforced:
- Root shell and both optical frames do **not** use backdrop blur.
- The only backdrop-filter zone is `.refraction`.
- Central lens blur is `1.5px`, below the hard max of `3px`.
- Capsule sells the glass through double frame, central lens, specular highlight, subtle underglow, and thinking-only liquid sheen.
- Pill text/icons stay above optical layers at `z-index: 10`.

Verifier:
- `products/pc/app/tools/verify_prisma_glass_capsules_optical_bench_0206.mjs`
- runnable with `pnpm -C products/pc/app verify:glass-capsules:proof` or directly with `node` from the PC app root.
