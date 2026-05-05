# PRISMA App Mobile - Play Store Readiness

## Estado

Esta entrega deja la ruta técnica preparada para Play Store, pero no hace publicación real.

La arquitectura correcta queda así:

```text
products/mobile/app      # Next.js / PWA mobile
products/mobile/android  # futuro wrapper Android/TWA
```

## Reglas

- Mobile no vuelve a PC.
- Mobile no es módulo de PC.
- Tablet no depende de Mobile ni de PC para vender.
- PC es asset de backoffice/control avanzado cuando aplica.
- Mobile es asset companion para consulta, pulso, alertas y reportes ligeros.

## Android App Bundle

Para Google Play, el artefacto final debe ser Android App Bundle:

```text
.aab
```

Esta entrega no genera `.aab` porque todavía no hay dominio productivo, signing key ni configuración final de tienda.

## Target SDK

La ruta Android debe planearse con target SDK **API 35** o superior para nuevas publicaciones actuales.

## Digital Asset Links

Para una TWA real, el dominio productivo debe servir:

```text
https://<domain>/.well-known/assetlinks.json
```

El archivo local incluido es plantilla:

```text
products/mobile/app/public/.well-known/assetlinks.template.json
```

No es prueba productiva hasta que tenga:

- package name final;
- fingerprint SHA-256 real;
- dominio real con HTTPS.

## Checklist previo a Play Store

- [ ] Dominio oficial de PRISMA App.
- [ ] Hosting HTTPS.
- [ ] `assetlinks.json` real servido desde el dominio.
- [ ] Android wrapper TWA generado.
- [ ] Signing key segura.
- [ ] SHA-256 real en Digital Asset Links.
- [ ] `.aab` generado.
- [ ] Privacy policy pública.
- [ ] Data safety form.
- [ ] Internal testing track.
- [ ] Capturas y ficha de Play Store.

## Verificación local

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app verify:playstore-readiness
```
