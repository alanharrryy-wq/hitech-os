# PRISMA_TRI_SURFACE_VISUAL_CHANGE_CONTRACT_00B_PRODUCT_ROOT_AUTONOMY_PATCH

## Estado

Adenda correctiva sobre `PRISMA_TRI_SURFACE_VISUAL_CHANGE_CONTRACT_00A`.

Esta adenda no reemplaza el contrato 00A. Lo endurece con dos decisiones:

1. PRISMA App / Mobile deja de vivir canónicamente dentro de PC.
2. Tablet POS queda protegida como producto autónomo de venta standalone.

---

## Surface IDs canónicos

Los IDs del contrato 00A se conservan sin renombrar:

```text
prisma.pc.backoffice
prisma.tablet.pos
prisma.mobile.app
```

Queda prohibido reemplazarlos por nombres como `pc_asset`, `pos_standalone` o `pulse_asset`. La autonomía de producto se declara como metadata de rol, no como ID nuevo.

---

## INVARIANTE DE AUTONOMÍA TABLET

```text
Tablet POS es la superficie primaria de venta standalone.

Ningún contrato visual, checker, manifest, documentación o paquete de gobierno puede describir a Tablet como dependiente de PC o App móvil para vender.

Tablet debe poder vender sola.
Tablet debe poder funcionar sola.
Tablet no necesita PC para venta básica.
Tablet no necesita PRISMA App para venta básica.
```

PC y App móvil pueden observar, administrar, auditar, reportar, acompañar o sincronizar cuando aplica, pero no habilitan ni bloquean la venta local básica de Tablet.

---

## INVARIANTE DE NO-JERARQUÍA VISUAL

```text
La cobertura visual tri-superficie no implica jerarquía de producto.
PC, Tablet y Mobile se validan como superficies visuales independientes.
```

La ubicación técnica de Mobile dentro de `products/pc/app` fue provisional. Desde esta entrega, la ubicación canónica es:

```text
products/mobile/app
```

Cualquier ruta mobile bajo `products/pc/app` queda legacy/provisional y debe retirarse o justificarse explícitamente.

---

## Rol correcto de cada superficie

| Superficie | Surface ID | Rol correcto |
|---|---|---|
| PC Backoffice | `prisma.pc.backoffice` | Asset administrativo y control avanzado cuando aplica. |
| Tablet POS | `prisma.tablet.pos` | POS autónomo de venta standalone. |
| PRISMA App / Mobile | `prisma.mobile.app` | Asset companion de consulta, pulso, alertas y reportes ligeros. |
| Shared contracts | N/A | Pegamento contractual, no jefe runtime. |

---

## Lenguaje canónico

Usar:

```text
Tablet vende sola.
PC administra cuando existe.
PRISMA App consulta, resume y alerta.
```

Evitar:

```text
PC gobierna.
Tablet opera subordinada a PC.
Mobile es parte de PC.
```

---

## Aplicación obligatoria

Todo ZIP futuro que toque visuales, rutas, manifest, docs de producto o navegación debe declarar cobertura tri-superficie y mantener Mobile en `products/mobile/app`, salvo que haya una migración aprobada por contrato nuevo.
