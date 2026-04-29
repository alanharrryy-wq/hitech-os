---
title: PRISMA Runtime Config Acceptance Checklist
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Runtime Config Acceptance Checklist

## 1. Checklist documental

- [ ] Existe runtime boundary doc.
- [ ] Existe path policy.
- [ ] Existe customer layout contract.
- [ ] Existe config schema contract.
- [ ] Existe environment policy.
- [ ] Existe data outside repo policy.
- [ ] Existe migration roadmap.

## 2. Checklist schemas

- [ ] `runtime-config.schema.json` valida.
- [ ] `paths.schema.json` valida.
- [ ] `device-identity.schema.json` valida.
- [ ] `local-agent-config.schema.json` valida.
- [ ] `backup-policy.schema.json` valida.
- [ ] `update-state.schema.json` valida.

## 3. Checklist instalacion

- [ ] dry-run no modifica.
- [ ] apply crea archivos.
- [ ] apply hace backup si reemplaza.
- [ ] verify valida JSON.
- [ ] rollback restaura.
- [ ] log unico queda en `F:\descargasf`.

## 4. Checklist anti-caos

- [ ] no toca DB;
- [ ] no toca runtime Tablet;
- [ ] no toca runtime PC;
- [ ] no toca rutas Next;
- [ ] no requiere GitHub;
- [ ] no usa cwd como contrato;
- [ ] no empaqueta basura.
