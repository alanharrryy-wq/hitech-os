# PRISMA Tablet Home Screen 03C

**Paquete:** incluido en `PRISMA_TABLET_RUNTIME_SNAPSHOT_HOME_03B_03C`  
**Pantalla:** `/`  
**Producto:** PRISMA Tablet POS  

---

## Objetivo

Convertir Inicio en una pantalla operativa real, alimentada por el Runtime Snapshot 03B.

Inicio ya no debe ser una vitrina de tarjetas bonitas ni un museo de placeholders. Debe contestar, sin vueltas:

```text
¿Puedo vender?
¿El turno está abierto?
¿Cuánto se vendió hoy?
¿Hay pendientes?
¿El catálogo está listo?
¿Hay existencias con presión?
¿Cuál es el siguiente toque correcto?
```

La pantalla debe llevar al operador a la acción correcta sin hacerlo jugar serpientes y escaleras con la navegación.

---

## Fuente de verdad

Home consume:

```text
getTabletRuntimeSnapshot(readRuntimeSnapshotInput())
```

Y renderiza:

```text
TabletHomeScreen
```

La shell recibe el mismo snapshot, para que el hero, los chips superiores y las métricas hablen el mismo idioma.

---

## Componentes

```text
components/tablet-home/tablet-home-screen.tsx
components/tablet-home/tablet-home.module.css
src/lib/tablet-home/home-view-model.ts
```

El view model decide:

- CTA principal;
- métricas visibles;
- alertas;
- checklist operativo;
- prioridad de acciones.

---

## Reglas de UX

Si el turno está cerrado:

```text
CTA principal: Abrir turno
```

Si el turno está abierto y todo está bien:

```text
CTA principal: Ir a vender
```

Si hay pendientes:

```text
Mostrar alerta: Pendientes por enviar
```

Si hay catálogo vacío o existencias presionadas:

```text
Mostrar alerta accionable hacia Catálogo o Existencias
```

No mostrar términos técnicos como `outbox`, `payload`, `schema`, `runtime`, `query`, `mutation` en la UI visible.

---

## Por qué esta pantalla importa

Inicio es la puerta del changarro. Si la puerta ya está chueca, todo lo demás se siente improvisado.

Esta versión convierte Home en el tablero mínimo de arranque para operación Tablet:

- estado del turno;
- venta del día;
- ticket promedio;
- pendientes;
- catálogo;
- existencias;
- CTA correcto.

---

## No alcance

No implementa todavía:

```text
venta punta a punta nueva
cobro integrado final
turno robusto nuevo
sincronización real con PC
proveedores
compras
recepción formal
```

Home sólo ordena la entrada y consume el contrato 03B.
