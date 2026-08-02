---
title: PRISMA HTML Field Manual de Aprendizaje Operativo
status: LIVING
owner: PRISMA HTML / Ops
created: 2026-07-21
scope:
  - standalone-html
  - atlasfin
  - visual-glass
  - packaging
  - cloudflare-pages
principle: "Aprender una vez; no volver a pagar la misma multa operacional."
---

# PRISMA HTML Field Manual de Aprendizaje Operativo

Este manual conserva el aprendizaje del trabajo realizado sobre el proyecto HTML independiente. No sustituye manifests, contratos ni reportes; registra las trampas que ya mordieron una vez para que no regresen con bigote falso.

## Reglas obligatorias

1. `F:\repos\hitech-os-prisma-html\prisma-html` es la raíz canónica del proyecto vivo.
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
