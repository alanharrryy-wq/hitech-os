# ATLAS TABLET VISUAL - Ronda 2

## Alcance visual

Este documento describe sólo las superficies visuales confirmadas para Tablet/POS dentro del ZIP. No transfiere propiedad de Visual OS, Shared UI ni estilos globales externos a Tablet.

## Frontera visual

| Elemento | Clasificación |
| --- | --- |
| `components/**` de Tablet | Propiedad funcional/visual Tablet dentro del paquete |
| `app/globals.css` | Hoja global Tablet que importa dependencias externas |
| `shared-ui/prisma/**` | Dependencia externa |
| `styles/prisma-visual-os/**` | Dependencia externa |
| `config/prisma-visual-os/**` | Dependencia externa |
| Packshots públicos | Assets consumidos por Tablet; disponibilidad completa pendiente de confirmar contra repo completo |

## Superficies visuales confirmadas

| Ruta | Uso visual |
| --- | --- |
| `/pos` | POS táctil principal, énfasis en operación rápida |
| `/checkout` | Cierre de venta |
| `/sales/today` | Lista de tickets/ventas del día |
| `/sales/today/[saleId]` | Detalle de ticket |
| `/sales/today/[saleId]/return` | Devolución desde ticket |
| `/returns` | Flujo de devoluciones |
| `/shift` | Estado, apertura y cierre de turno |
| `/sync` | Estado de sincronización |
| `/offline` | Auditoría offline/export/outbox |
| `/release-gate` | Estado operativo de release |
| `/runtime-snapshot-preview` | Preview de runtime snapshot |
| `/visual-os`, `/visual-os/pro`, `/visual-os/realtime`, `/visual-os/detached` | Referencias y controles visuales, sujetos a Visual OS externo |
| `/referencia-visual`, `/prisma-dark-pos-reference` | Referencias visuales internas del paquete |

## Componentes visuales por dominio

### POS y checkout

- Componentes de carrito, búsqueda/resolución de productos, lectura de códigos y totalización.
- Deben tratarse como UI operativa de Tablet, no como Backoffice.
- El foco visual es operación táctil: blancos grandes, estados claros, feedback rápido.

### Ventas y tickets

- `components/sales/**` cubre lista y detalle de tickets.
- Hallazgo corregido en esta ronda: el atlas marca como fallo vigente que `verify:i03a-ticket-detail` espera llamada directa a `/api/pos/sales/detail` y enlace con `encodeURIComponent(saleId)`.
- No se documenta como resuelto; se documenta como bloqueo verificable.

### Offline/export

- `components/offline/offline-export-audit-screen.tsx` consume auditoría offline.
- Hallazgo corregido en esta ronda: el atlas marca como fallo vigente `T04-008 screen renders outbox`.
- La pantalla sí cubre exports/movements según verificador, pero outbox visible queda pendiente.

### Licencia

- `components/license/**` consume contrato externo `shared/licensing`.
- Tablet presenta banners/cards/status, pero no posee la lógica fuente de licenciamiento.

## CSS y tokens

El ZIP confirma imports globales hacia dependencias compartidas y Visual OS externo. Por regla de ownership, se documentan como consumo externo:

- `../../../shared-ui/prisma/tokens/prisma-theme.css`
- `../../../shared-ui/prisma/components/prisma-components.css`
- `../../../../styles/prisma-visual-os/prisma-visual-layers.css`

Tablet puede documentar cómo consume esas capas, pero no duplicarlas ni reclamarlas como propias.

## Assets públicos

`analysis/tablet_public_asset_manifest.json` declara 246 entradas, incluyendo packshots PNG en `products/tablet/app/public/pos-packshots`. En el snapshot revisado, la disponibilidad de binarios pesados debe confirmarse en el repo completo antes de declarar cobertura final.

## Estados visuales que deben mantenerse explícitos

- Loading no permanente.
- Error humano y visible.
- Estado no encontrado para ticket.
- Foco/aria en filas clicables.
- Outbox visible en offline una vez corregido T04.
- Estados de licencia sin asumir lógica compartida.

## Recomendación de evolución

Antes de mover estos documentos a rutas finales, cerrar I03A y T04. Sin eso, cualquier sello visual de release listo sería como pintar la fachada mientras falta la puerta: se ve bonito, pero se mete la lluvia.