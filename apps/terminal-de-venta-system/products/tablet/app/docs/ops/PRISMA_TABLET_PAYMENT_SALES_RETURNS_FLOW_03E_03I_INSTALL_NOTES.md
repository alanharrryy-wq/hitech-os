# PRISMA Tablet - Notas de instalación 03E-03I

## Intención

Este paquete instala la ruta crítica de caja posterior al carrito: Cobro, Ticket cerrado, Ventas de hoy, Detalle y Devolución contextual.

## Qué revisar antes de aplicar

- El ZIP anterior 03B/03C/03D debe estar aplicado.
- La Tablet debe conservar el menú de seis entradas.
- `/pos` debe existir.
- `/sales/today` puede no estar completo todavía; este paquete lo completa.

## Comando dry-run

```powershell
python F:\descargasf\install_prisma_tablet_payment_sales_returns_flow_03e_03f_03g_03h_03i.py --dry-run
```

## Comando apply + verify

```powershell
python F:\descargasf\install_prisma_tablet_payment_sales_returns_flow_03e_03f_03g_03h_03i.py --apply --verify
```

## Comando verify

```powershell
python F:\descargasf\install_prisma_tablet_payment_sales_returns_flow_03e_03f_03g_03h_03i.py --verify
```

## Comando rollback

```powershell
python F:\descargasf\install_prisma_tablet_payment_sales_returns_flow_03e_03f_03g_03h_03i.py --rollback
```

## Validación visual mínima

```text
/pos
/sales/today
/sales/today/<ticket>
/sales/today/<ticket>/return
/checkout
/returns
```

## Resultado esperado

Después de aplicar, Cobro debe seguir dentro de Vender. Ventas de hoy debe ser una pantalla propia. Devolución debe nacer desde Detalle de ticket. Ninguna de esas acciones debe inflar el menú principal.

## Nota de control adicional

Este paquete queda marcado como cambio local de Tablet. Si una iteración futura toca contratos compartidos, nombres de eventos globales, PC, Mobile o schema, debe tratarse como cambio twin y no como parche aislado de caja. Cobro vive dentro de Vender; Devoluciones nacen desde ticket; Exportar y Pendientes no son pestañas principales.

## Checklist de frontera

- No crear nueva base de datos.
- No tocar PC ni Mobile.
- No tocar shared-kernel.
- No tocar schema.prisma.
- No meter Proveedores, Compras ni Recepción formal en Tablet.
- Mantener Cobro dentro de Vender y Devolución desde ticket.
- Confirmar que el rollback restaura archivos modificados y retira archivos nuevos.
