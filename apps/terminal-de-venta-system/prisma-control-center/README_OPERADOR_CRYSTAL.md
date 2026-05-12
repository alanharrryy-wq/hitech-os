# PRISMA Crystal Ops Console - README Operador

## Estado del release

Este Control Center integra cinco capas:

1. Crystal Shell UI
2. Data Core vivo
3. Black-box Command
4. Cloudflare + Control Actions
5. Ultra Polish + Release

## URLs locales principales

- Panel: http://127.0.0.1:3150
- Health API: http://127.0.0.1:3150/api/health
- Incidents API: http://127.0.0.1:3150/api/incidents
- Black-box summary: http://127.0.0.1:3150/api/blackbox/summary
- Ops Cloudflare: http://127.0.0.1:3150/api/ops/cloudflare
- Release status: http://127.0.0.1:3150/api/release/status
- Latest report: http://127.0.0.1:3150/latest/health.html

## Operacion normal

1. Abre el panel local.
2. Revisa Health Score y estado general.
3. Si hay DEGRADED, abre Cloudflare + Control Actions.
4. Usa Run Health solo en local.
5. Revisa Black-box Command para timeline y evidencia.
6. Usa Release Check para validar integridad final.

## Seguridad

- En modo publico se redactan rutas y datos sensibles.
- Run Health es accion local.
- Black-box conserva evidencia y timeline auditable.

## Rollback

Cada iteracion deja manifest en F:\descargasf.
Para rollback, cambia $MODE = "rollback" en el wrapper correspondiente y ejecútalo.

## Pendiente operativo conocido

Si control.hitechrts.com sigue en 404 o DEGRADED, revisar cloudflared, config.yml, DNS y service binding al puerto 3150.
