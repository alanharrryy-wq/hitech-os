# Tablet Twin Parity Plan

## Rol de la app Tablet

La Tablet debe ser la herramienta de operación: vender, cobrar, registrar turno, procesar devoluciones, consultar stock, trabajar offline y generar eventos limpios.

No debe convertirse en backoffice chiquito. Eso sería meterle una oficina completa a una mochila y luego sorprenderse de que pesa.

## Lo que Tablet ya trae fuerte

- Ventas.
- Checkout.
- Turno/caja operativa.
- Devoluciones.
- Stock operativo.
- Sync.
- Health route, error boundary y not-found.
- QA por incrementos con escenarios y evidencias.

## Lo que Tablet necesita para emparejarse mejor

1. **Catálogo operativo ligero**
   - Consulta por barcode/SKU.
   - Indicador de precio vigente.
   - Incidencia de producto no encontrado.

2. **Recepción ligera**
   - Confirmación física rápida.
   - Foto/evidencia futura si aplica.
   - Discrepancia enviada a PC.

3. **Estados offline más contractuales**
   - Permitido.
   - Bloqueado.
   - Encolado.
   - Pendiente de supervisor.

4. **Mayor trazabilidad hacia PC**
   - Cada venta, devolución, cierre de turno y ajuste operativo debe dejar evento visible para PC.

## Contrato Tablet recomendado

| Campo | Recomendación |
|---|---|
| `surface` | `tablet` |
| `role` | `operation` |
| `mustExpose` | captura, velocidad, offline, estado de sync |
| `mustNotOwn` | reglas maestras de catálogo, permisos, compras o fiscal |
| `parityRule` | toda acción sensible debe generar evento auditable en PC |

## Próximo incremento recomendado

Fortalecer Tablet con catálogo operativo y recepción ligera, pero solo después de declarar el contrato de paridad para no crear mini-backoffice clandestino.
