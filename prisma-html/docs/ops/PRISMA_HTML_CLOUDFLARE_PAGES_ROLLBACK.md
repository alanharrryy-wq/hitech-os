# PRISMA HTML · Cloudflare Pages Rollback

## Rollback local

El paquete de migración crea backup en `F:\Trash-old` y entrega `ROLLBACK.ps1`. Ese rollback restaura archivos locales y no toca Cloudflare.

## Rollback de Pages

Cloudflare Pages permite revertir producción a un deployment anterior desde el dashboard:

1. Abrir Workers & Pages.
2. Abrir el proyecto Pages.
3. Entrar a Deployments.
4. En el deployment estable, abrir el menú de tres puntos.
5. Elegir `Rollback to this deployment` y confirmar.

Sólo deployments de producción exitosos son destinos válidos. Los previews no sirven como rollback target.

## Evidencia mínima

Registrar:

- deployment actual;
- deployment objetivo;
- URL pública;
- timestamp;
- respuesta HTTP posterior;
- razón del rollback.

No borrar deployments como sustituto de rollback.
