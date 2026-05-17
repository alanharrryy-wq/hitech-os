# ATLAS PC RUNTIME DELIVERY - Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

## Alcance

Este documento registra runtime, build, delivery, Prisma, package scripts, validadores y dependencias externas confirmadas en el snapshot de PC. No modifica código funcional ni toca rutas finales.

## Identidad runtime

| Campo | Valor confirmado |
|---|---|
| Root lógico | `products/pc/app` |
| Package | `@hitech/pc` |
| Version | `6.1.1` |
| Framework | Next `16.1.6` |
| React | `18.3.1` |
| TypeScript | `5.8.2` |
| Prisma client | `5.21.1` |
| Node engine | `>=20.0.0 <26.0.0` |
| Dev port | `3130` |
| Start port | `3130` |

## Scripts package confirmados

| Script | Comando | Clasificación |
|---|---|---|
| `dev` | `next dev -p 3130` | Runtime local PC |
| `build` | `next build --webpack` | Build Next |
| `start` | `next start -p 3130` | Runtime producción/local |
| `typecheck` | `tsc --noEmit` | Validación TS |
| `check:package` | `python tools/validate_package.py .` | Validación package PC |
| `check:all` | `python tools/validate_package.py . && tsc --noEmit` | Validación compuesta |
| `db:canonical:generate` | `python ../../../tooling/scripts/generate_prisma_canonical.py pc` | Dependencia externa tooling/Prisma canónico |
| `db:canonical:migrate` | tooling externo | Dependencia externa |

## Next config detectado

El ZIP confirma configuración de Next con señales de monorepo y dependencia externa:

| Config | Estado |
|---|---|
| `outputFileTracingRoot` | Apunta al root del sistema sobre `products/pc/app/../../..` |
| `externalDir` | `true` |
| `reactStrictMode` | `true` |
| `turbopackRoot` | system root |
| `typedRoutes` | `false` |

Interpretación: PC se ejecuta como app dentro de un árbol mayor y necesita dependencias fuera del root de PC.

## TypeScript paths confirmados

| Alias | Target | Clasificación |
|---|---|---|
| `@/*` | `./src/*` | Interno PC |
| `@components/*` | `./components/*` | Interno PC |
| `@shared-kernel/*` | `../../../shared/twin-kernel/src/*` | Dependencia externa compartida |

## Prisma runtime

### Confirmado

- Existe `products/pc/app/prisma/schema.prisma`.
- Existe `products/pc/app/src/server/prisma/client.ts`.
- `@prisma/client` está en dependencias.
- Los repositorios server usan Prisma.
- Los scripts de `db:canonical:*` apuntan a tooling externo.

### Clasificación correcta

| Pieza | Clasificación |
|---|---|
| Repositorios PC | Propiedad funcional PC |
| Uso de Prisma client | Runtime externo usado por PC |
| Schema local `products/pc/app/prisma/schema.prisma` | Stub/transicional detectado |
| Schema canónico | Externo/global, pendiente de confirmar en repo completo |
| Migraciones/generadores canónicos | Externos/globales |

## Fallback DB detectado

El atlas Ronda 2 conserva el hallazgo de fallback hacia una base canónica local bajo tooling/data cuando `DATABASE_URL` no está definido. Esto se documenta como mecanismo runtime detectado, no como contrato final validado.

Pendiente: confirmar en repo completo si ese fallback es aceptado para desarrollo, CI o solo compatibilidad local.

## Dependencias externas runtime

| Dependencia | Motivo |
|---|---|
| Prisma canónico | Scripts y schema transicional apuntan a definición externa |
| `@prisma/client` | Cliente runtime de repositorios |
| `shared/twin-kernel` | Contratos de módulos `TwinModuleManifest` vía alias |
| `shared/licensing` | Feature gates/licensing |
| `shared/tri-db` | Referencias de delivery/data global |
| `shared-ui/prisma` | CSS tokens/componentes |
| `styles/prisma-visual-os` | Capas Visual OS globales |
| `global_context/docs/contracts/**` | Contratos de arquitectura/eventos/export/errors como contexto global |

## Verificación package

`tools/validate_package.py` está presente y fue usado como referencia de calidad. La validación aislada del snapshot puede fallar cuando espera dependencias externas no incluidas. Eso no significa código PC roto; significa que el ZIP no contiene todo el monorepo.

## Herramientas y verificadores runtime

| Herramienta | Uso detectado |
|---|---|
| `tools/validate_package.py` | Valida estructura package PC |
| `tools/smoke_pc_i01_routes.mjs` | Smoke de rutas |
| `tools/db_summary.py` | Resumen DB |
| `tools/run_pc_suppliers_lifecycle_scenarios_02.mjs` | Escenarios lifecycle proveedores |
| `tools/verify*.mjs` | Verificadores por release/iteración PC |

## Delivery boundaries

### Permitido para esta entrega

- Subir atlas y metadatos a `docs/atlas/_incoming/pc/`.
- Marcar dependencias externas.
- Documentar pendientes.
- Emitir `atlas.pc.json` con schema canónico.

### Prohibido y no realizado

- Modificar `products/pc/app/docs/atlas/`.
- Modificar código funcional PC.
- Tocar Mobile o Tablet.
- Tocar Shared Core.
- Atribuir ownership de Prisma canónico o Shared Kernel a PC.

## Estado esperado de CI

No se afirma pass de CI desde el ZIP porque faltan dependencias externas. Para validar en repo completo se recomienda, fuera de esta entrega:

```bash
cd products/pc/app
npm install
npm run check:package
npm run typecheck
npm run build
```

Y, si aplica en el entorno real:

```bash
npm run db:canonical:generate
npm run db:canonical:migrate
```

## Riesgos runtime

| Riesgo | Estado |
|---|---|
| Dependencias externas ausentes en snapshot parcial | Pendiente de repo completo |
| Prisma canónico no incluido | Pendiente de confirmar |
| Assets públicos faltantes | Pendiente de resolver |
| Verificadores no ejecutados end-to-end | Pendiente de CI/runtime real |
| Fallback DB local | Pendiente de clasificación final |

## Conclusión

PC corre como app Next dentro de un monorepo más grande. Su runtime propio está en `products/pc/app`, pero varios cables gruesos entran desde fuera: Prisma canónico, twin-kernel, licensing, tri-db y Visual OS global. Esta ronda deja esos cables etiquetados, no los mete a la caja de PC como si fueran enchufe propio.