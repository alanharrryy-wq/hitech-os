# PRISMA Web Guardrails

## Rol de esta app

`apps/external_interaction_template` queda como **PRISMA Web pública** para `https://eit.hitechrts.com` y origen local `http://127.0.0.1:3110`.

## Reglas obligatorias

1. Esta app es marketing, explicación y captura de interés. No contiene operación POS real.
2. No se guardan secretos, tokens, certificados ni `.env` reales.
3. No toca `apps/keystone`.
4. No toca `apps/external_interaction_forms`.
5. No toca `tools/infra/cloudflare`.
6. Toda página debe declarar audiencia, promesa y CTA.
7. Todo claim comercial debe clasificarse como actual, demo o roadmap antes de publicarse.
8. Toda vertical debe respetar: Tablet opera, PC gobierna, Mobile supervisa, Core registra, Control audita.
9. Toda vertical debe explicar entidad, evento, responsable, estado, evidencia, alerta, reporte e historial.
10. El build debe pasar antes de publicar.
11. El origen debe responder en puerto `3110` antes de revisar Cloudflare.

## Regla anti-humo

Si una promesa no apunta a una capacidad real, una demo o una decisión de roadmap, no se publica. Se manda a revisión, como debe ser, porque el humo solo sirve para encontrar fugas y asar carne.
