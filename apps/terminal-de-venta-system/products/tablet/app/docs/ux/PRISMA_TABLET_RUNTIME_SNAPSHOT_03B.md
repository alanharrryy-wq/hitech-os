# PRISMA Tablet Runtime Snapshot 03B

**Paquete:** `PRISMA_TABLET_RUNTIME_SNAPSHOT_03B`  
**Producto:** PRISMA Tablet POS  
**Tipo:** integración funcional Tablet  
**Estado:** listo para instalar/verificar  

---

## 1. Objetivo

Crear una sola lectura operativa para la Tablet. Esta lectura alimenta la shell y evita que cada pantalla invente su propio cuento sobre turno, conexión, pendientes, catálogo y ventas del día.

La meta es simple:

```text
Una Tablet.
Un estado operativo.
Una forma visible de decir qué pasa.
```

Sin esto, cada pantalla termina hablando como vecino de junta condominal: todos opinan, nadie sabe quién tiene la llave.

---

## 2. Qué instala

### Código UI

```text
components/tablet-shell/tablet-nav.ts
components/tablet-shell/prisma-tablet-shell.tsx
components/tablet-shell/prisma-tablet-shell.module.css
components/tablet-runtime/tablet-runtime-status-strip.tsx
components/tablet-runtime/tablet-runtime-panel.tsx
```

### Contrato cliente seguro

```text
src/lib/tablet-runtime-snapshot/shell-contract.ts
src/lib/tablet-runtime-snapshot/view-model.ts
src/lib/tablet-runtime-snapshot/visible-copy.ts
```

### Motor server de snapshot

```text
src/server/tablet-runtime-snapshot/index.ts
src/server/tablet-runtime-snapshot/build.ts
src/server/tablet-runtime-snapshot/queries.prisma.ts
src/server/tablet-runtime-snapshot/env.ts
src/server/tablet-runtime-snapshot/types.ts
```

### API

```text
app/api/tablet/runtime/snapshot/route.ts
```

### Alias y preview

```text
app/inventory/page.tsx
app/existencias/page.tsx
app/runtime-snapshot-preview/page.tsx
```

### Verificación

```text
tools/verify_tablet_runtime_snapshot_03b.mjs
tools/fixtures/tablet_runtime_snapshot_03b_scenarios.json
```

---

## 3. Decisión de navegación incluida

Este paquete también deja la navegación Tablet en la forma canonica de seis entradas:

```text
Inicio
Vender
Ventas de hoy
Catalogo
Existencias
Turno
```

Se mantiene fuera del menú principal:

```text
Cobro
Devoluciones
Sincronizacion
Exportar
```

Esas piezas siguen existiendo, pero como paneles, acciones contextuales o rutas secundarias. La caja no necesita parecer tablero de avión si lo que quiere el cajero es cobrar una Coca sin invocar al soporte técnico.

---

## 4. Snapshot operativo

El snapshot entrega:

```text
identity   -> negocio, tienda, terminal, operador
shift      -> turno abierto/cerrado/revisión
connection -> en línea, sin conexión, pendientes o revisar
catalog    -> catálogo listo, vacío o con existencias a revisar
sales      -> tickets, venta total, unidades y ticket promedio del día
capabilities -> venta local, catálogo local, pendientes visibles, exportación contextual
warnings   -> advertencias del modo operativo
```

Contrato:

```text
schemaVersion: tablet-runtime-snapshot.03b
localSalesAllowed: true
pcRequiredForBasicSale: false
```

Esto respeta la regla madre: Tablet vende sola. PC gobierna cuando toca, pero no le da permiso a la Tablet para vender.

---

## 5. API de diagnóstico

Endpoint:

```text
GET /api/tablet/runtime/snapshot
```

Parámetros opcionales:

```text
businessId
terminalId
operatorId
operatorName
date
```

Respuesta esperada:

```json
{
  "ok": true,
  "data": {
    "snapshot": {
      "schemaVersion": "tablet-runtime-snapshot.03b",
      "localSalesAllowed": true,
      "pcRequiredForBasicSale": false
    }
  }
}
```

---

## 6. Por qué importa

Antes, la shell podía mostrar un estado y otra pantalla otro. Eso es veneno operativo: el cajero ve “listo”, luego abre ventas y resulta que hay pendientes, turno cerrado o catálogo vacío.

Con este paquete:

- la shell tiene chips consistentes;
- los pendientes viven como estado superior;
- turno y conexión ya no dependen de copy suelto;
- catálogo y existencias se conectan a una lectura única;
- el API deja una superficie estable para Home 03C.

---

## 7. No alcance

No toca:

```text
schema.prisma
shared-kernel
PC
Mobile
sync real con PC
proveedores
compras
recepción formal
```

No crea base de datos nueva. No mete backoffice pesado en Tablet. No mete magia de humo.

---

## 8. Siguiente paso

El siguiente paquete lógico es:

```text
PRISMA_TABLET_HOME_SCREEN_03C
```

Home debe consumir este snapshot para mostrar un inicio operativo real: turno, ventas del día, pendientes, catálogo, existencias y CTA dominante hacia Vender o Abrir turno.
