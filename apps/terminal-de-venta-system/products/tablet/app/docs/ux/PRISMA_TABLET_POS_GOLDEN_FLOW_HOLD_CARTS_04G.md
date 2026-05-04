# PRISMA Tablet POS Golden Flow 04G - Guardar y recuperar tickets

## Objetivo

Convertir el flujo `/pos` en un flujo más cercano al POS real de piso: el cajero puede escanear/buscar, mantener el carrito visible, guardar un ticket atorado, recuperar tickets guardados y ver una validación previa antes de cobrar.

Esto implementa una parte concreta del flujo dorado:

```text
Venta scan-first
→ carrito siempre visible
→ guardar ticket trabado
→ recuperar ticket guardado
→ pre-cobro con validaciones visibles
→ cobrar sin perder contexto
```

## Alcance instalado

### 1. Scan-first inteligente

El campo principal de búsqueda ahora trata entradas con forma de código como intento de resolución directa:

- códigos numéricos de 6 a 14 dígitos;
- códigos alfanuméricos operativos tipo SKU/código interno;
- si no resuelve como código, cae a búsqueda normal.

Esto evita que el cajero tenga que distinguir entre “buscar” y “resolver código” cuando trae lector o captura rápida.

### 2. Conteos reales en búsqueda

La barra de búsqueda recibe:

- productos visibles;
- productos activos;
- estado del catálogo.

Antes el componente podía mostrar ceros aunque sí hubiera productos cargados, que era una pequeña mentira con corbata.

### 3. Tickets guardados

Se agrega una cola local de tickets guardados en `localStorage`:

```text
prisma.tablet.pos.heldCarts.v1
```

Cada ticket guardado conserva:

- id;
- etiqueta operativa;
- hora;
- líneas;
- piezas;
- total;
- origen `pos`.

Límite operativo: 12 tickets guardados.

### 4. Acción touchs operativos

| Acción touch | Acción |
|---|---|
| `F2` | abrir cobro |
| `Enter` | confirmar pago cuando el panel está abierto |
| `Escape` | cerrar panel de cobro |
| `Guardar` | guardar ticket activo desde botón touch |
| `F5` | limpiar ticket activo |
| `Recuperar` | recuperar ticket guardado desde tarjeta touch si el carrito actual está vacío |

### 5. Aduana del ticket

El ticket ahora muestra una sección `CheckoutDiagnostic` antes del total:

- `Listo para cobrar` cuando pasa validaciones;
- `Aduana del ticket` cuando falta algo;
- razón visible tomada de `validateCartForCheckout`.

### 6. Stock visible por línea

Cada línea del ticket muestra señal de stock:

- disponible;
- bajo;
- insuficiente/sin existencia.

Esto hace que el bloqueo de cobro no se sienta como magia negra de TypeScript.

## Archivos tocados

```text
products/tablet/app/src/lib/pos/held-carts.ts
products/tablet/app/components/pos/pos-screen.tsx
products/tablet/app/components/pos/pos-ticket-panel.tsx
products/tablet/app/components/pos/pos-payment-keyboard-bridge.tsx
products/tablet/app/components/pos/pos.module.css
products/tablet/app/tools/verify_pos_golden_flow_hold_carts_04g.mjs
products/tablet/app/docs/ux/PRISMA_TABLET_POS_GOLDEN_FLOW_HOLD_CARTS_04G.md
products/tablet/app/docs/qa/PRISMA_TABLET_POS_GOLDEN_FLOW_HOLD_CARTS_04G_ACCEPTANCE.md
```

## Fuera de alcance

Este paquete no implementa:

- persistencia server-side de tickets guardados;
- turnos reales;
- permisos de manager;
- devoluciones desde ticket;
- sync hacia PC de tickets en espera.

Es una capa local de productividad de caja. La persistencia canónica seguirá siendo venta cerrada + eventos/outbox.
