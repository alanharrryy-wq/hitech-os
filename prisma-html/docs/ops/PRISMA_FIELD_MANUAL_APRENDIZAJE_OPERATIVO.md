---
title: PRISMA HTML Field Manual de Aprendizaje Operativo
status: LIVING
owner: PRISMA HTML / Ops
created: 2026-07-21
last_updated: 2026-08-30
scope:
  - standalone-html
  - viscore1
  - rifat
  - atlasfin
  - visual-glass
  - packaging
  - cloudflare-pages
principle: "Aprender una vez; no volver a pagar la misma multa operacional."
---

# PRISMA HTML Field Manual de Aprendizaje Operativo

Este manual conserva el aprendizaje del trabajo realizado sobre PRISMA HTML y su autoridad visual. No sustituye manifests, contratos ni reportes; registra las trampas que ya mordieron una vez para que no regresen con bigote falso.

Para operación completa de VISCORE1, usar también `PRISMA_VISUAL_AUTHORITY_RUNBOOK.md`.

## Reglas obligatorias

1. En el repo integrado `hitech-os`, el workspace VISCORE vive en `<repo-root>\prisma-html`. La ruta histórica `F:\repos\hitech-os-prisma-html\prisma-html` sólo aplica cuando se trabaja explícitamente sobre el proyecto standalone separado; no asumirla para operaciones del monorepo.
2. `F:\descargasf` conserva ZIPs, resultados, logs y diagnósticos.
3. `F:\Trash-old` conserva backups y rollback.
4. Un PASS estático no significa certificación visual.
5. Todo cambio visual premium requiere Authority Mesh y Layer Map frescos.
6. No agregar `!important` para vencer la cascada por flojera.
7. El 0% de glass debe apagar fondo, borde, halo, sombra y blur del owner correspondiente.
8. Los overlays temporales tienen un solo owner de Gaussian blur: el backdrop. Los paneles internos no duplican blur.
9. No copiar backups históricos, ZIPs de resultados, bases vivas, secretos ni cachés al repo.
10. Cloudflare Pages, Worker/D1 y Tunnel son familias distintas. No mezclar comandos ni configuraciones.
11. Ningún deploy debe matar procesos, liberar puertos, reiniciar `cloudflared` ni tocar los runtimes PRISMA.
12. No declarar URL pública ni deploy PASS sin respuesta HTTP y evidencia de deployment.
13. No editar a mano proyecciones de producto declaradas como generated/manual-edits-forbidden en `authority/rifat/visual-source-manifest.json`.
14. No editar a mano `FILES_MANIFEST.json`; regenerarlo sólo después de terminar todos los cambios de `prisma-html`.
15. Un SHA certificado no se vuelve a tocar antes del merge. Si cambia el head o cambia `main`, se reconcilia y se certifica de nuevo.

## Aprendizajes confirmados

### 2026-07-20 · Integración Atlas completa

**Tipo:** SOURCE_INTEGRATION / EVIDENCE

El proyecto base no contenía `extras/atlasfin`. La integración estable agregó 27 páginas, 26 secciones y 418 elementos, enlazó el Atlas desde la portada y actualizó validadores y manifests.

**Regla:** el Atlas es una superficie aislada; sus CSS, JS, assets, gobierno y reportes viven bajo `extras/atlasfin/`.

### 2026-07-20 · Glass 0% y cascada

**Tipo:** VISUAL_LEARNING

Se corrigieron owners canónicos de glass, 11 grupos de selectores duplicados en el host y comportamiento de teclado del dropdown. La validación fuente y el harness Chromium pasaron, pero la evidencia de host desplegado no existe.

**Regla:** no reinterpretar un harness inline como certificación de producción.

### 2026-07-21 · Error de package root temporal

**Tipo:** PACKAGING_LEARNING / COMMAND_FAILS

Un wrapper copió el motor Python a `%TEMP%`; el motor buscó `PACKAGE_MANIFEST.json` junto al archivo temporal y falló antes de modificar el proyecto.

**Causa real:** el package root fue inferido desde `__file__` en vez de pasarse explícitamente.

**Regla:** todo motor temporal recibe `--package-root` y valida manifiesto, payload y evidencia antes de tocar archivos.

### 2026-07-21 · Premium overlay patch

**Tipo:** VISUAL_LEARNING / ROLLBACK_RECIPE

El parche premium agregó owners focalizados para Product Card/CAFÉ, Circular Progress y overlays. La instalación fue idempotente y el rollback restauró 5/5 rutas. El usuario revirtió el parche antes de migrar al repo canónico.

**Regla:** al migrarlo, rebasar contra la base corregida, validar fuente/Atlas y generar nueva evidencia del repo canónico. La revisión humana de capturas sigue siendo necesaria.

### 2026-07-21 · Cloudflare no es una sola cosa

**Tipo:** GOVERNANCE_LEARNING / CLOUD

Los archivos encontrados separan tres familias:

- Cloudflare Pages para sitios estáticos.
- Worker + D1 para LICFLOW3 y servicios de licencia.
- Cloudflare Tunnel para runtimes locales vivos.

**Regla:** `prisma-html` usa Pages. No usa el Worker LICFLOW3 ni los launchers de Tunnel para publicar su contenido estático.

### 2026-07-21 · Launchers peligrosos

**Tipo:** SAFETY

`kill_everything.ps1`, `_launcher_common.ps1` y launchers del antiguo Control Center pueden matar procesos, liberar puertos o reiniciar `cloudflared`.

**Regla:** no trasladar ni ejecutar esos launchers dentro de este repo.

## Criterio de cierre visual

Para declarar una mejora visual cerrada se requiere:

- validación fuente;
- validación Atlas;
- capturas desktop y móvil;
- comprobación de rutas y assets;
- revisión humana de las capturas;
- si está desplegado, health check de la URL pública.

### 2026-07-26 · VISREC2 V2 sin expansión de controles

**Tipo:** SOURCE_EXTENSION / GOVERNANCE / UX

VISREC2 evolucionó a recetas V2 con visual stack, estados, variantes, adaptadores,
assets, aliases, migración e inspección read-only. La complejidad se resolvió en
registries y motores internos; se preservó exactamente el conjunto de controles
visibles de V1 y no se agregaron sliders, selectores ni controles individuales.

**Regla:** una capacidad interna nueva no justifica un control nuevo. Exponer sólo
decisiones humanas necesarias y mantener compatibilidad, binding, cobertura y
readiness como semáforos separados.

### 2026-08-30 · PR #475: RIFAT no puede arreglar drift degradando un runtime legítimo

**Tipo:** GOVERNANCE_LEARNING / EVIDENCE_LEARNING / VISUAL_LEARNING

**Contexto:** El gate `validate_rifat_authority.py` detectó drift en proyecciones Mobile y PC. Los runtime CSS actuales habían cambiado legítimamente en trabajos posteriores a la consolidación inicial de RIFAT, mientras los snapshots canónicos de RIFAT habían quedado atrás.

**Resultado observado:** El cierre correcto no fue copiar la autoridad vieja sobre producto. Se verificó la genealogía, se promovieron los bytes actuales legítimos de Mobile y PC hacia sus fuentes RIFAT correspondientes y desapareció `exact-copy visual projection drift`.

Después quedaron únicamente cuatro errores de hash en `visual-source-manifest.json`: source/output para Mobile y source/output para PC. Como ya no existía exact-copy drift, los bytes source/output eran iguales y sólo los digests declarados estaban obsoletos.

**Causa real:** Había dos capas de drift distintas:

1. drift real de bytes entre fuente RIFAT y proyección;
2. metadata hash stale después de reconciliar los bytes.

**Regla nueva:**

- Si existe `exact-copy visual projection drift`, investigar historia y autoridad antes de copiar nada.
- Si el runtime actual es un cambio legítimo más nuevo, no hacer downgrade para conseguir verde.
- Si hay hash mismatch pero no exact-copy drift, actualizar sólo hashes desde bytes reales.
- Regenerar `FILES_MANIFEST.json` al final, nunca antes del último cambio de `prisma-html`.
- Si `main` avanza después de un green, reconciliar `main` y volver a certificar.
- Una vez verde el SHA final, no agregar commits cosméticos antes del merge.

**Evidencia:** PR #475 se certificó sobre un único head SHA con VISCORE1, CI, ForgeOS y repo-navigation-guard verdes, y se fusionó después con protección de expected head SHA.

**Rollback probado:** N/A para la documentación. La reparación de autoridad evitó modificar/degradar los runtimes de producto.

**Deuda cerrada:** El procedimiento completo quedó formalizado en `docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md`.
