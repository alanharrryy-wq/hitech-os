# PRISMA App Mobile - TWA Android Readiness

## Qué es esto

Esta entrega crea la base para que PRISMA App pueda convertirse después en una Android app publicable mediante TWA.

No es todavía una app lista para subir a Play Store. Es el plano y el cimiento. La tienda todavía no tiene cortina ni caja registradora, pero ya no estamos vendiendo desde una caja de huevo.

## Raíces

```text
products/mobile/app
products/mobile/android
```

## Por qué TWA

PRISMA App es principalmente companion móvil:

- consulta;
- pulso del negocio;
- alertas;
- reportes ligeros;
- visibilidad ejecutiva.

Ese perfil encaja bien con PWA/TWA antes de saltar a React Native o nativo puro.

## Qué falta para TWA real

1. Dominio productivo.
2. HTTPS.
3. Manifest estable.
4. Digital Asset Links.
5. Android wrapper.
6. Signing.
7. AAB.
8. Play Console.

## Package placeholder

```text
com.prisma.mobile
```

Ese package name es placeholder hasta decidir dominio/legal/branding definitivo.

## Internal testing

The Play Store release path must mention internal testing before production promotion.
