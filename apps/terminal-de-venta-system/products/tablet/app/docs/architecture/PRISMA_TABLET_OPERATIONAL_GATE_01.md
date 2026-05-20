# PRISMA Tablet Operational Gate 01

Regla canónica: `canSell` solo es verdadero cuando hay turno/caja abierta localmente en Tablet.

- Caja cerrada: `Vender` no se muestra en navegación operativa, `/pos` muestra estado claro de caja cerrada, agregar producto y cobrar quedan bloqueados.
- Caja abierta: `Vender` aparece y el POS puede operar con carrito válido.
- `SHIFT_NOT_OPEN` bloquea la venta; el cliente no abre turno automáticamente ni reintenta la venta.
- Tablet conserva soberanía local: no depende de PC, Mobile, nube ni base canónica para vender.

La superficie reusable vive en `src/lib/operational-gate/can-sell.ts` para separar decisiones visibles y ejecutables sin esparcir condiciones en componentes.
