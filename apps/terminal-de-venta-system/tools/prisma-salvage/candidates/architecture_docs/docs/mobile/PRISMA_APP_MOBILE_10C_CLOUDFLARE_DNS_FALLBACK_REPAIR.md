# PRISMA_APP_MOBILE_10C_CLOUDFLARE_DNS_FALLBACK_REPAIR

## Motivo

La app movil ya compila y responde en local en `http://127.0.0.1:3140/prisma-app`, pero el smoke publico falla con `404` en `https://prisma.hitechrts.com/prisma-app`.

El error observado al correr 10B fue:

```text
ERROR: Could not bind DNS route for prisma.hitechrts.com to tunnel engine. cloudflared exit=1
```

## Diagnostico

El comando DNS de `cloudflared` puede fallar cuando el registro ya existe, cuando requiere overwrite o cuando el CLI/certificado no puede modificar DNS desde la terminal. Ese error no debe impedir aplicar la ruta local en `config.yml`, porque el 404 publico tambien puede venir de un servicio `cloudflared` corriendo con config vieja o con `ImagePath` desalineado.

## Reparacion 10C

- Tolerar fallo de DNS por defecto.
- Probar `--overwrite-dns` y `-f`.
- Insertar/actualizar ingress antes del catch-all `http_status:404`.
- Forzar `ImagePath` del servicio para usar el `config.yml` correcto.
- Reiniciar servicio.
- Probar public smoke.

## Resultado esperado

`https://prisma.hitechrts.com/prisma-app` debe responder `2xx/3xx` cuando:

1. el origen local 3140 esta vivo;
2. el DNS del hostname apunta al tunnel `engine`;
3. el servicio `cloudflared` corre con la config correcta;
4. el ingress contiene `prisma.hitechrts.com -> http://127.0.0.1:3140` antes del fallback.
