# ATLAS MASTER INDEX

Estado coordinador: **PROMOTED_FROM_INCOMING_WITH_WARNINGS**.

Este índice consolida los cuatro paquetes Ronda 2 recibidos en `docs/atlas/_incoming/**` y promueve la documentación validada a sus rutas finales. La integración es documental y de trazabilidad; no certifica release funcional de Mobile, Tablet o PC.

## Rutas finales

| Dominio | Ruta final | Estado |
|---|---|---|
| Mobile | `products/mobile/app/docs/atlas/` | Promovido con JSON normalizado por Coordinador |
| Tablet | `products/tablet/app/docs/atlas/` | Promovido con JSON normalizado por Coordinador |
| PC | `products/pc/app/docs/atlas/` | Promovido desde JSON canónico R2 |
| Shared Core | `docs/atlas/` | Promovido desde Shared Core R2 |

## Fuentes staging conservadas

| Dominio | Staging |
|---|---|
| Mobile | `docs/atlas/_incoming/mobile/` |
| Tablet | `docs/atlas/_incoming/tablet/` |
| PC | `docs/atlas/_incoming/pc/` |
| Shared Core | `docs/atlas/_incoming/shared-core/` |

## Dictamen por dominio

| Dominio | Dictamen | Advertencia principal |
|---|---|---|
| Mobile | Aprobado para atlas documental | PWA/assets PNG faltantes siguen siendo riesgo de release |
| Tablet | Aprobado para atlas documental | Release bloqueado por I03A y T04 hasta corregir verificadores |
| PC | Aprobado para atlas documental | Build/verificadores dependen de Shared Core y Prisma global en repo completo |
| Shared Core | Aprobado para atlas documental | Owners/pipelines finales quedan pendientes en algunos contratos |

## Regla de uso

Para cambios futuros, buscar primero una intención en el atlas de la app. Si aparece dependencia compartida, revisar Shared Core antes de tocar código. No usar `_incoming` como fuente final salvo para auditoría de entrega.
