# PRISMA App móvil 18 - Roadmap de madurez operativa

## Estado actual detectado

La app móvil ya existe como producto independiente en `products/mobile/app`. Tiene rutas API móviles, tablero visual, PWA, instalación, caché local y data-plane que consulta Tablet y PC. El problema era de madurez de producto: quedaban archivos heredados de maqueta, validadores antiguos y textos que la hacían sonar inconclusa.

## Calificación de madurez

| Área | Antes | Después de esta inyección | Siguiente bloqueo real |
|---|---:|---:|---|
| Producto móvil independiente | 8/10 | 9/10 | Mantener frontera con Tablet y PC |
| Data-plane conectado | 6/10 | 7/10 | Completar caja real y branch registry |
| Limpieza productiva | 4/10 | 8/10 | Gate permanente en CI/local |
| PWA instalable | 8/10 | 8/10 | Dominio final y assetlinks reales |
| UX ejecutiva para dueño | 7/10 | 7.5/10 | Estados vacíos y acciones por rol |
| Observabilidad | 5/10 | 6.5/10 | Logs de fetch, latencia y fuente por widget |
| Seguridad | 3/10 | 3/10 | Auth, permisos y exposición segura de endpoints |
| Release interno | 5/10 | 6.5/10 | Smoke con Tablet/PC corriendo |

## Iteraciones recomendadas

### Iteración 18 - Limpieza productiva y datos conectados
- Retirar código heredado de maqueta.
- Corregir caché de snapshot.
- Reportar fuente honesta: conectado, parcial u offline.
- Quitar copy visible de número de iteración o instalación.
- Dejar gate local para que no regresen residuos.

### Iteración 19 - Caja real y corte operativo móvil
- Conectar `cashCurrent` a cortes/turnos reales de Tablet.
- Separar efectivo, tarjeta, transferencia y retiros.
- Alertar diferencia de caja con umbrales configurables.

### Iteración 20 - Inventario accionable para dueño
- Convertir stock bajo en acciones.
- Mostrar top SKUs y quiebres con prioridad de venta perdida.
- Vincular inventario con ventas recientes.

### Iteración 21 - Multi-sucursal gobernada
- Definir registry de sucursales/terminales.
- Separar una tienda, varias tiendas y PC administrado.
- Mostrar ranking y salud por sucursal solo cuando PC lo soporte.

### Iteración 22 - Seguridad y permisos
- Agregar sesión de dueño/encargado.
- Proteger `/api/mobile/*`.
- Separar permisos de lectura, caja, inventario y alertas.

### Iteración 23 - Observabilidad y release
- Medir latencia por upstream.
- Registrar fuente de cada KPI.
- Generar smoke report con Tablet/PC vivos.
- Capturas de App móvil, Tablet y PC por iteración.

## Definition of Done

1. Runtime sin residuos de maqueta.
2. Todas las cards dicen de dónde viene el dato.
3. Si Tablet cae, la app informa estado parcial sin inventar venta.
4. Si PC cae, la app mantiene lectura Tablet y marca backoffice no disponible.
5. Caja viene de turnos/cortes reales.
6. Inventario bajo genera acción clara.
7. Endpoints móviles tienen auth y permisos.
8. `pnpm run verify:production-data` pasa.
9. `pnpm run check:all` pasa con Tablet/PC disponibles.
10. Cada entrega deja backup, log, verify y rollback.
