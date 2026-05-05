# PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B

**Tipo:** contrato operativo + guardian de cambios visuales  
**Estado:** canónico para cambios visuales posteriores  
**Proyecto:** PRISMA / Terminal de Venta  
**Raíz esperada:** `F:\repos\hitech-os\apps\terminal-de-venta-system`  
**Propósito:** evitar que una modificación visual cubra sólo dos superficies y deje fuera la tercera por accidente.

---

## 1. Decisión corregida

PRISMA no usa una jerarquía donde PC sea padre de Tablet o Mobile.

La regla correcta es:

```text
Tablet vende sola.
Tablet funciona sola.
Tablet no necesita PC para vender.
Tablet no necesita App móvil para vender.
PC es un asset de backoffice/control avanzado.
App móvil es un asset de pulso, consulta y alertas.
Shared contracts son el contrato común, no un jefe runtime.
```

Este contrato corrige cualquier frase ambigua donde PC aparezca como autoridad padre, Tablet como dependiente para vender, o Mobile como pantalla absorbida por PC.

---

## 2. Superficies oficiales

| ID canónico | Nombre humano | Rol | Autonomía |
|---|---|---|---|
| `prisma.tablet.pos` | Tablet POS | Venta, caja, ticket, operación local, eventos/outbox | **Primaria y standalone** |
| `prisma.pc.backoffice` | PC Backoffice | Administración, inventario, auditoría, compras, dashboard, reconciliación | Asset complementario |
| `prisma.mobile.app` | App móvil / Pulso | Consulta ligera, alertas, pulso operativo, seguimiento ejecutivo | Asset complementario |

La App móvil vive canónicamente en `products/mobile/app`; si aparece una ruta histórica bajo PC, debe tratarse como legacy y no como PC.

---

## 3. Invariante de autonomía Tablet

Ningún contrato visual, checker, manifest, README, entregable o paquete de gobierno puede describir a Tablet como dependiente de PC o App móvil para vender.

Tablet POS debe mantenerse como superficie autónoma de venta local.

PC y App móvil pueden observar, administrar, auditar, reportar, alertar, sincronizar o enriquecer la operación. No deben habilitar ni bloquear la venta local básica de Tablet.

---

## 4. Invariante de no-jerarquía visual

La cobertura visual tri-superficie no implica jerarquía de producto.

PC, Tablet y App móvil se validan como superficies visuales independientes.

La ubicación histórica de Mobile dentro de `products/pc/app` no convierte Mobile en PC.

---

## 5. Rutas por superficie

### Tablet POS standalone

```text
products/tablet/app/**
```

### PC Backoffice asset

```text
products/pc/app/**
```

Excepto rutas que pertenecen a App móvil/Pulso.

### App móvil / Pulso asset

```text
products/mobile/app/**

### Rutas Mobile legacy a retirar si reaparecen

```text
products/pc/app/app/prisma-app/**
products/pc/app/src/lib/prisma-app/**
products/pc/app/docs/prisma-app/**
products/pc/app/app/pulso/**
products/pc/app/src/lib/pulso/**
```

Las rutas `pulso` son legacy y deben reportarse si aparecen.

### Capa visual compartida

```text
products/shared-ui/prisma/**
shared/contracts/ui/**
docs/design/**
docs/qa/**
tools/prisma/**
manifests/**
```

La capa compartida no pertenece a una sola superficie.

---

## 6. Estados obligatorios de cobertura

Cada entrega visual debe declarar estas tres superficies:

```text
prisma.tablet.pos
prisma.pc.backoffice
prisma.mobile.app
```

Estados válidos:

```text
TOUCHED
VALIDATED
EXCLUDED
```

Estado prohibido:

```text
OMITTED
```

También queda prohibido omitir la superficie completa de la matriz.

---

## 7. Regla de impacto visual

Si se toca una ruta específica de superficie, esa superficie debe quedar como `TOUCHED`.

Ejemplos:

- Si se toca `products/tablet/app/**`, Tablet debe ser `TOUCHED`.
- Si se toca `products/pc/app/app/prisma-app/**`, App móvil debe ser `TOUCHED`.
- Si se toca `products/pc/app/app/pulso/**`, App móvil debe ser `TOUCHED` y el legacy debe quedar reportado.
- Si se toca PC fuera de rutas Mobile/Pulso, PC debe ser `TOUCHED`.

---

## 8. Regla de shared visual

Si una entrega visual toca:

```text
products/shared-ui/prisma/**
```

entonces las tres superficies deben quedar como:

```text
TOUCHED
```

o

```text
VALIDATED
```

Ninguna puede quedar `EXCLUDED`.

Esto evita el clásico: “toqué tokens compartidos, pero App móvil no aplica”. Sí aplica, mi cielo, porque los tokens compartidos no distinguen sentimientos.

---

## 9. Exclusiones válidas

`EXCLUDED` sólo es válido cuando incluye:

- razón concreta;
- confirmación de que no se tocó shared visual;
- reevaluación futura o paquete donde se revisará;
- responsable lógico;
- evidencia mínima.

Frases inválidas:

```text
No aplica.
N/A.
No se tocó.
Luego vemos.
```

Una exclusión sin razón real equivale a omisión con sombrero.

---

## 10. Manifest mínimo de cambio visual

Cada paquete visual futuro debe traer un objeto compatible con este contrato:

```json
{
  "package": "PRISMA_BLACK_VISUAL_REFINEMENT_01G",
  "changeType": "visual",
  "autonomyPolicy": {
    "tabletSellsStandalone": true,
    "tabletDoesNotRequirePc": true,
    "tabletDoesNotRequireMobile": true,
    "pcIsBackofficeAsset": true,
    "mobileIsPulseAsset": true,
    "noAssetRequiredForTabletSale": true
  },
  "changedFiles": [],
  "surfaceCoverage": [
    {
      "surface": "prisma.tablet.pos",
      "state": "VALIDATED",
      "reviewedFiles": [],
      "touchedFiles": [],
      "evidence": "checker, diff review, screenshot, or summary",
      "exclusionReason": null,
      "reevaluation": null,
      "owner": "visual-governance"
    },
    {
      "surface": "prisma.pc.backoffice",
      "state": "VALIDATED",
      "reviewedFiles": [],
      "touchedFiles": [],
      "evidence": "checker, diff review, screenshot, or summary",
      "exclusionReason": null,
      "reevaluation": null,
      "owner": "visual-governance"
    },
    {
      "surface": "prisma.mobile.app",
      "state": "VALIDATED",
      "reviewedFiles": [],
      "touchedFiles": [],
      "evidence": "checker, diff review, screenshot, or summary",
      "exclusionReason": null,
      "reevaluation": null,
      "owner": "visual-governance"
    }
  ]
}
```

---

## 11. Guardian obligatorio

Este paquete instala:

```text
tools/prisma/prisma_tri_surface_visual_guardian_00b.py
```

Ese guardian debe usarse antes de aceptar paquetes visuales futuros.

Ejemplo conceptual:

```text
python tools/prisma/prisma_tri_surface_visual_guardian_00b.py --root <target-root> --manifest <manifest.json> --text
```

El guardian falla si:

- falta Tablet;
- falta PC;
- falta App móvil;
- aparece `OMITTED`;
- se toca Mobile pero Mobile no está `TOUCHED`;
- se toca Tablet pero Tablet no está `TOUCHED`;
- se toca PC pero PC no está `TOUCHED`;
- se toca shared-ui visual y alguna superficie queda `EXCLUDED`;
- se excluye una superficie sin razón concreta;
- falta evidencia;
- el manifest niega la autonomía standalone de Tablet;
- el manifest intenta presentar PC o App móvil como requisito para vender en Tablet.

---

## 12. Frase canónica de PRISMA

Usar esta frase en futuros docs:

```text
Tablet es el POS autónomo de venta.
PC es un asset de backoffice y control avanzado.
App móvil es un asset de pulso, consulta y alertas.
Shared contracts mantienen consistencia sin imponer dependencia runtime.
Ningún asset debe convertirse en requisito para que Tablet venda localmente.
```

---

## 13. No-goals de este paquete

Este paquete no debe:

- rediseñar PC;
- rediseñar Tablet;
- rediseñar App móvil;
- modificar CSS visual;
- tocar TS/TSX de producto;
- cambiar layout;
- cambiar UX;
- cambiar datos;
- instalar demo data;
- alterar rutas runtime.

Es un candado de gobierno. No es una fiesta de CSS con música alta.

---

## 14. Definition of Done

El contrato se considera instalado cuando:

1. existe este documento;
2. existe el contrato JSON;
3. existe el template de manifest visual;
4. existe el guardian `.py`;
5. existe el manifest de instalación;
6. el instalador puede ejecutar `--dry-run`, `--apply`, `--verify` y `--rollback`;
7. el guardian valida su propio manifest;
8. el paquete puede revertirse sin depender del directorio actual.
