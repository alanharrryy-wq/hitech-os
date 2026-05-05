# PRISMA Web Clean Canvas - EIT

Esta app reemplaza `apps/external_interaction_template` como lienzo limpio para la web pública de PRISMA.

## Rol

- Host público inicial: `https://eit.hitechrts.com`
- Origen local esperado: `http://127.0.0.1:3110`
- Carpeta: `apps/external_interaction_template`

## Scripts

```powershell
pnpm -C apps/external_interaction_template build
pnpm -C apps/external_interaction_template start
pnpm -C apps/external_interaction_template dev
pnpm -C apps/external_interaction_template typecheck
```

## Modelo de producto

```text
Tablet opera.
PC gobierna.
Mobile supervisa.
Core registra.
Control audita.
```

## Guardrails

Ver `PRISMA_WEB_GUARDRAILS.md`.
