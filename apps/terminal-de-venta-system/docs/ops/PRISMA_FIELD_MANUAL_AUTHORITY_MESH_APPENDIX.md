# Field Manual Appendix: Authority Mesh Rule

## Rule

At the start of any PRISMA/hitech-os task that may produce code, scripts, CSS, ZIPs, repo changes, prompts for Codex, diagnostics, or visual work, run the Authority Mesh preflight first.

## Mandatory evidence

The result or diagnostic ZIP must include:

- `.governance/current/AUTHORITY_READSET.lock.json`
- `.governance/current/APP_IMPACT_MATRIX.md`
- `.governance/current/CONTRACT_AND_GATE_MATRIX.json`
- `.governance/current/MISSING_OR_UNMAPPED_RISK.md`
- `.governance/current/AGENT_PROMPT_ENVELOPE.md`

## Failure rule

If critical authority is missing, the work may still install tooling, but no patch should be created or presented as green. The missing authorities must be reported first.

## Live-process rule

Authority Mesh must not kill dev processes, free ports, start servers, or regenerate Prisma during hot work.

## Addendum 2026-06-18: app-root manual y Layer Map visual

AutoMesh debe buscar el manual operativo en estas dos rutas válidas:

```text
docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md
apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md
```

Si la ruta root falta pero la ruta app-root existe, no debe reportarse como autoridad crítica faltante. Debe registrarse como manual resuelto desde app-root.

Para tareas visuales o premium, el Mesh debe incluir siempre:

```text
LAYERS_MAP.md
LAYERS_MAP.json
```

Sin Layer Map, el Mesh es incompleto y no autoriza patch visual.
