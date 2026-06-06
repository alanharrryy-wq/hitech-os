# Tablet Fuji Visible Fix 1

Este fix hace visible el fondo Fuji Cloudglass en las rutas donde normalmente se ve la Tablet operativa: `/`, `/pos` y `/checkout`.

Motivo: el paquete anterior cambió el shell raíz, pero POS y checkout tenían shells propios con assets distintos. Ahí estaba el fantasma, no en el verificador.

Reglas conservadas:

- No modifica motores POS/checkout.
- No modifica componentes de venta.
- No toca DB, sync, Prisma schema, PC ni mobile.
- Sólo aplica atmósfera visual, assets y overrides de paneles glass en shells de ruta.
