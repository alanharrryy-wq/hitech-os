---
title: PRISMA License Operation Matrix
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
---

# PRISMA License Operation Matrix


## Matriz de operacion por estado

| Estado | Venta local basica | Premium/plugins | Exportacion | Soporte |
|---|---:|---:|---:|---:|
| `dev` | si | si | si | si |
| `trial` | si | si | si | si |
| `active` | si | si | si | si |
| `offline_grace` | si | no | si | si |
| `past_due_external` | si | no | si | si |
| `suspended` | limitada | no | si | si |
| `expired` | limitada | no | si | si |
| `revoked` | limitada | no | si | si |

## Lectura

La suspension no debe convertirse en secuestro de datos. La app puede limitar acciones futuras, pero debe permitir respaldo, exportacion y soporte.

## Matrix addendum 2026-05-19

| Estado operativo | Venta local basica | Lectura correcta |
|---|---:|---|
| `refresh_disabled` | depende de licencia/caja, no del refresh | Informativo: servidor remoto no configurado |
| `missing` + fallback permitido | si, limitada | Continuidad local documentada |
| `invalid` / tampered | no | Bloqueo de seguridad, requiere diagnostico |
| `wrong_business` / `wrong_store` | no | Licencia asignada a otro negocio o tienda |
| `wrong_device` / `wrong_terminal` / `unassigned` | no | Equipo no asignado a esta licencia |
| `exceeded_limit` | no | Limite de terminales/dispositivos excedido |
| `SHIFT_NOT_OPEN` | no | Caja cerrada; no autoabrir turno |

La decision final de POS es: licencia/capacidad permite `pos.sale.complete` + caja/turno abierto + carrito valido.
