# PRISMA_TRI_SURFACE_VISUAL_CHANGE_CONTRACT_00A

## Estado

Documento de gobierno previo a cambios de código.

Este contrato define cómo deben evaluarse y entregarse las modificaciones visuales de PRISMA cuando existan tres superficies de producto activas:

1. PRISMA PC
2. PRISMA Tablet
3. PRISMA App / Mobile

El objetivo no es forzar que todo archivo visual cambie siempre en las tres superficies. El objetivo es impedir que una modificación visual altere una o dos superficies y deje la tercera fuera por accidente.

---

## 1. Problema que corrige

Las entregas móviles revisadas muestran que PRISMA App / Mobile existe como tercera superficie, pero actualmente vive instalada dentro del árbol de PC:

```text
products/pc/app/app/prisma-app/page.tsx
products/pc/app/app/prisma-app/prisma-app.module.css
```

Entregas previas de Mobile/Pulso también instalaron rutas como:

```text
products/pc/app/app/pulso/page.tsx
products/pc/app/app/pulso/prisma-pulso.module.css
```

Esto provoca una ambigüedad peligrosa:

```text
Mobile parece ser PC por ruta,
pero es una superficie visual distinta por producto.
```

Por esa razón, un cambio visual que diga “PC + Tablet” puede creer que cubrió el ecosistema, pero dejar fuera la experiencia móvil.

---

## 2. Regla madre

Toda modificación visual de PRISMA debe declarar impacto sobre las tres superficies:

```text
PC      -> tocar, validar o excluir con razón explícita
Tablet  -> tocar, validar o excluir con razón explícita
Mobile  -> tocar, validar o excluir con razón explícita
```

Una entrega visual queda bloqueada si omite una superficie sin justificarla.

---

## 3. Superficies canónicas

### 3.1 PC Backoffice

**Surface ID:**

```text
prisma.pc.backoffice
```

**Rol:**

Backoffice, inventario, auditoría, administración, reportes, sync y gobierno operativo.

**Rutas visuales conocidas:**

```text
products/pc/app/app/globals.css
products/pc/app/app/**/**/*.module.css
products/pc/app/components/**/*.css
products/pc/app/components/**/*.tsx
```

### 3.2 Tablet POS

**Surface ID:**

```text
prisma.tablet.pos
```

**Rol:**

Venta, caja, operación touch-first, ticket, stock local, corte operativo y uso offline.

**Rutas visuales conocidas:**

```text
products/tablet/app/app/globals.css
products/tablet/app/components/pos/pos.module.css
products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css
products/tablet/app/components/**/*.css
products/tablet/app/components/**/*.tsx
```

### 3.3 PRISMA App / Mobile

**Surface ID:**

```text
prisma.mobile.app
```

**Rol:**

Resumen móvil para dueño, encargado o supervisor: Hoy, Ventas, Caja, Inventario, Alertas, Reportes y MultiSucursal.

**Rutas visuales actuales:**

```text
products/pc/app/app/prisma-app/page.tsx
products/pc/app/app/prisma-app/prisma-app.module.css
products/pc/app/src/lib/prisma-app/**
products/pc/app/docs/prisma-app/**
```

**Rutas legacy a detectar mientras existan o aparezcan en backups/paquetes:**

```text
products/pc/app/app/pulso/page.tsx
products/pc/app/app/pulso/prisma-pulso.module.css
products/pc/app/src/lib/pulso/**
```

**Nota importante:**

Mientras Mobile viva bajo `products/pc/app`, no debe clasificarse automáticamente como PC. Debe tratarse como superficie independiente.

---

## 4. Capas visuales compartidas

Estas rutas no pertenecen a una sola superficie. Son capa común y cualquier cambio aquí debe evaluarse contra las tres superficies:

```text
products/shared-ui/prisma/tokens/prisma-theme.css
products/shared-ui/prisma/components/prisma-components.css
shared/contracts/ui/**
docs/design/**
docs/qa/**
tools/prisma/**
manifests/**
```

Si una modificación en `shared-ui` se valida sólo en PC y Tablet, queda incompleta.

---

## 5. Definición de cambio visual

Se considera cambio visual cualquier modificación que afecte una o más de estas áreas:

```text
color
tokens visuales
background
gradient
haze
glow
blur
glass
border
shadow
radius
spacing visual
layout visual
motion
z-index
mix-blend-mode
backdrop-filter
component skin
page shell
mobile frame
card hierarchy
CTA styling
active state
empty/error visual states
```

No importa si el cambio parece pequeño. Si afecta percepción visual, entra en este contrato.

---

## 6. Matriz obligatoria de cobertura

Toda entrega visual debe incluir una matriz con este formato:

| Superficie | Estado | Archivos revisados | Archivos tocados | Evidencia | Razón si no se toca |
|---|---|---|---|---|---|
| PC | TOUCHED / VALIDATED / EXCLUDED | lista | lista | checker/captura/resumen | texto |
| Tablet | TOUCHED / VALIDATED / EXCLUDED | lista | lista | checker/captura/resumen | texto |
| Mobile | TOUCHED / VALIDATED / EXCLUDED | lista | lista | checker/captura/resumen | texto |

### Estados permitidos

```text
TOUCHED
```

La superficie fue modificada por el paquete.

```text
VALIDATED
```

La superficie no necesitó cambios, pero fue revisada y se confirma que el cambio compartido no la rompe ni la deja fuera.

```text
EXCLUDED
```

La superficie queda fuera con razón explícita, por ejemplo: “esta entrega corrige sólo un copy local de Tablet y no toca tokens ni componentes compartidos”.

### Estado prohibido

```text
OMITTED
```

Una superficie no puede quedar ausente de la matriz.

---

## 7. Regla de exclusión

Una exclusión sólo es válida si incluye:

1. superficie excluida;
2. razón concreta;
3. confirmación de que no hay impacto por tokens/shared-ui;
4. fecha o paquete donde se reevaluará si aplica;
5. responsable lógico del criterio.

Ejemplo válido:

```text
Mobile queda EXCLUDED porque el paquete sólo corrige overflow local de Tablet POS en pos.module.css, sin tocar shared-ui, tokens, globals ni componentes comunes. Reevaluar en el próximo pass visual compartido.
```

Ejemplo inválido:

```text
No aplica.
```

Eso no es razón. Eso es barrer debajo del tapete con PowerPoint.

---

## 8. Reglas por tipo de cambio

### 8.1 Cambio en tokens compartidos

Si se toca:

```text
products/shared-ui/prisma/tokens/prisma-theme.css
```

Entonces PC, Tablet y Mobile deben quedar como `TOUCHED` o `VALIDATED`.

Mobile no puede quedar omitida sólo porque su ruta viva dentro de PC.

### 8.2 Cambio en componentes compartidos

Si se toca:

```text
products/shared-ui/prisma/components/prisma-components.css
```

Entonces debe revisarse si Mobile usa clases, variables o patrones equivalentes. Si Mobile tiene CSS propio que replica tarjetas, phone frames, badges o hero panels, debe validarse explícitamente.

### 8.3 Cambio local PC

Si se toca sólo PC Backoffice y no hay efecto en tokens/globales/shared-ui, Tablet y Mobile pueden quedar `EXCLUDED`, pero con razón.

### 8.4 Cambio local Tablet

Si se toca sólo Tablet POS y no hay efecto en tokens/globales/shared-ui, PC y Mobile pueden quedar `EXCLUDED`, pero con razón.

### 8.5 Cambio Mobile

Si se toca `/prisma-app` o rutas mobile equivalentes, PC no debe marcarse automáticamente como cubierto. PC debe validarse como shell contenedor y Mobile como producto visual independiente.

---

## 9. Regla “derivar, no inventar”

Las superficies visuales deben derivar de una misma intención visual PRISMA, no inventar recetas aisladas.

Queda prohibido:

```text
crear glows one-off sin presupuesto;
crear fondos premium distintos por ruta sin contrato;
crear variantes gold/glass por pantalla sin ownership;
duplicar haze local cuando ya existe haze de escena;
resolver Mobile como mockup aislado sin tokens compartidos;
```

Cada superficie puede adaptar la experiencia a su rol, pero debe declarar qué comparte y qué especializa.

---

## 10. Presupuesto visual transversal

Todo cambio visual debe declarar presupuesto aproximado de efectos:

| Capa | Propósito | Límite |
|---|---|---|
| Fondo / stage | atmósfera global | 1 escena dominante por pantalla |
| Panel | interpretar fondo | glass o solid, no ambos peleando |
| Card | enmarcar información | no reinventar clima propio |
| Contenido | informar | máximo contraste razonable |
| Glow/acento | jerarquizar | pocos acentos por pantalla |
| Motion | guiar | máximo una hero motion por pantalla |

Regla operacional:

```text
Si todo brilla, nada brilla.
```

---

## 11. Requisitos mínimos para entregas futuras

Toda entrega visual debe incluir:

```text
manifest con matriz tri-superficie
contrato o actualización de contrato si cambia alcance visual
checker o verificación que enumere las tres superficies
documentación de qué se tocó y qué se dejó fuera
rollback
backup
log único
```

Si la entrega modifica archivos reales del repo, debe seguir el estándar del proyecto:

```text
ZIP + instalador .py
--dry-run
--apply
--verify
--rollback
```

---

## 12. Gate de aceptación

Una entrega visual sólo se acepta si puede responder estas preguntas:

1. ¿Qué cambia visualmente?
2. ¿Qué superficie lo recibe?
3. ¿Qué superficie sólo se valida?
4. ¿Qué superficie se excluye y por qué?
5. ¿Se tocó shared-ui o tokens?
6. ¿Mobile fue evaluada como producto independiente?
7. ¿Hay riesgo de divergencia entre PC, Tablet y Mobile?
8. ¿El rollback revierte todos los archivos tocados?

Si falta la respuesta de Mobile, el paquete queda bloqueado.

---

## 13. Aplicación recomendada para el próximo pass 01G

Antes de crear `PRISMA_BLACK_VISUAL_REFINEMENT_01G`, se debe instalar o adoptar este contrato como criterio de revisión.

El 01G debe declarar:

```text
PC: TOUCHED o VALIDATED
Tablet: TOUCHED o VALIDATED
Mobile: TOUCHED o VALIDATED
```

Si Mobile todavía no está instalada en el repo objetivo, el paquete debe indicarlo como:

```text
Mobile: EXCLUDED
Razón: no existe ruta /prisma-app en este target-root.
Evidencia: búsqueda de rutas mobile sin resultados.
Reevaluación: primer paquete que instale PRISMA App debe registrarla como tercera superficie visual.
```

Si Mobile sí está instalada, no puede quedar fuera del inventario.

---

## 14. Resumen ejecutivo

PRISMA tiene tres experiencias visuales de producto:

```text
PC gobierna.
Tablet vende.
Mobile resume y alerta.
```

Aunque Mobile viva dentro del árbol técnico de PC, debe ser tratada como tercera superficie visual.

A partir de este contrato, ningún cambio visual compartido debe pasar como completo si sólo contempla dos superficies.
