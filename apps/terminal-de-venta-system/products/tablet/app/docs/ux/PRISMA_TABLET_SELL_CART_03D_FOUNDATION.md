# PRISMA Tablet Sell Cart 03D Foundation

**Paquete:** incluido en `PRISMA_TABLET_RUNTIME_SNAPSHOT_HOME_CART_03B_03C_03D`  
**Superficie:** `/pos`  
**Tipo:** fundación funcional de carrito  

---

## Objetivo

Sacar la lógica delicada del carrito fuera del componente visual `PosScreen`.

Antes, sumar, restar, remover y limpiar vivía directo en la pantalla. Eso funciona al principio, como ponerle una silla al puesto y decir que ya es restaurante. Pero cuando llega cobro real, bloqueo de doble toque, validación de stock, persistencia y confirmación de venta, esa lógica se vuelve una maraña.

Este paquete crea:

```text
src/lib/pos/cart-engine.ts
src/lib/pos/cart-view-model.ts
```

Y conecta esos motores con:

```text
components/pos/pos-screen.tsx
components/pos/pos-ticket-panel.tsx
src/lib/pos/cart-state.ts
```

---

## Qué aporta

### Motor puro de carrito

```text
addProductToCart
incrementCartLine
decrementCartLine
removeCartLine
clearCart
sanitizeCart
validateCartForCheckout
buildCheckoutPayload
hydrateCart
serializeCart
```

Estas funciones no dependen de React, DOM ni navegador. Eso permite probarlas y reutilizarlas sin perseguir estados como cucaracha en cocina.

### View model del ticket

```text
buildCartPanelViewModel
buildCartLineViewModel
```

El panel de ticket ya no calcula todo como puesto de tacos con libreta. Recibe un modelo preparado:

- total;
- piezas;
- líneas;
- disponibilidad;
- razón de bloqueo;
- estado para cobro.

---

## Reglas de negocio iniciales

```text
No agregar producto sin id.
No agregar producto inactivo.
No permitir cantidad menor a 1.
No permitir cantidad mayor a 999 por línea.
Consolidar productos duplicados.
Bloquear cobro si alguna línea supera existencia.
Bloquear cobro si total <= 0.
Persistir carrito con versionado v3.
```

---

## Por qué esta fundación va antes de Cobro 03E

Cobro no debe depender de un carrito blandito.

Antes de confirmar venta, necesitamos saber:

```text
qué líneas son válidas;
cuántas piezas hay;
cuánto se cobra;
si hay stock suficiente;
qué payload se mandará al API;
si el botón puede activarse;
por qué está deshabilitado.
```

Esto lo prepara 03D.

---

## No alcance

No confirma venta.
No crea ticket cerrado.
No implementa pago real.
No toca schema.prisma.
No toca shared-kernel.
No toca PC ni Mobile.

---

## Criterios de aceptación

```text
PosScreen usa addProductToCart.
PosScreen usa incrementCartLine.
PosScreen usa decrementCartLine.
PosScreen usa removeCartLine.
PosScreen usa clearCart.
PosTicketPanel usa buildCartPanelViewModel.
El botón COBRAR usa checkoutReady.
El botón COBRAR explica razón con title.
cart-engine no usa Date.now ni Math.random.
cart-engine no toca DOM.
```

---

## Siguiente paso

El siguiente paquete puede ser:

```text
PRISMA_TABLET_PAYMENT_PANEL_03E
```

Ahí el panel de cobro debe consumir `validateCartForCheckout` y `buildCheckoutPayload` para evitar doble cobro, tickets vacíos y cantidades inválidas.
