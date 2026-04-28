# Tablet POS Visual QA

Estado: canon listo para codigo.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Criterios visuales para el POS tactil antes de implementar pantalla final.


Required screens: `/pos`, `/catalog`, `/sales/today`, `/inventory/low-stock`, `/events/outbox`, `/settings/export`.

Layout: top zone runtime/sync/terminal status; left/main zone search and fast product list; right zone cart/ticket; bottom zone large primary actions.

Tablet-only components: `TouchProductSearch`, `TouchCart`, `TouchNumpad`, `CheckoutButton`, `TicketSummary`, `OfflineBanner`, `OutboxMiniPanel`.

Acceptance: boton de cobrar grande, total visible, ticket siempre visible o a un toque, errores no tecnicos, estado offline/sync visible y confirmacion clara de ticket cerrado.
