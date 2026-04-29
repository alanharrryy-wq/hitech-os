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
