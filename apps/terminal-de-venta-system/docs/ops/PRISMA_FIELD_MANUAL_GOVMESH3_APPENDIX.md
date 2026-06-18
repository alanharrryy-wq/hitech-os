# Field Manual Appendix: GovMesh3

Before any PRISMA visual/premium task, run Authority Mesh with the exact task. The result must include GovMesh3 outputs.

Operational rule:

- The implementation must use all `must_use` capabilities unless blocked by a stronger authority.
- It should use `should_use` capabilities when compatible with the target screen.
- It must evaluate `consider_required` capabilities and explain use/rejection.
- It may only use `bounded_optional` or `high_risk_optional` capabilities with layer budget, performance and governance evidence.
- It must not use `forbidden_for_scope` capabilities.

Do not accept fake premium work that only adds blur, shadow or radius without the used/rejected matrix and visual evidence.

## Addendum 2026-06-18: cierre preflight Tablet POS `/pos`

Para un patch premium de Tablet POS `/pos`, GovMesh3 sólo autoriza implementación cuando:

- `.governance/current` está limpio;
- `posctx.py` fresco confirma route owners y CSS owners;
- Authority Mesh se generó para el task exacto después del estado Git actual;
- el Mesh incluye `LAYERS_MAP.md` y `LAYERS_MAP.json`;
- el scope incluye Tablet y excluye PC, Mobile, Chart Lab y Shared UI salvo autoridad explícita.

No reutilizar un Mesh viejo después de cambios en `main`, limpieza de governance o cambios de HEAD.
