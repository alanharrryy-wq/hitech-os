---
title: PRISMA Installation Dry Run Expectations
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---

# PRISMA Installation Dry Run Expectations

## 1. preflight

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[preflight] OK ruta validada
[preflight] OK acción planificada
[preflight] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 2. detect_existing

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[detect_existing] OK ruta validada
[detect_existing] OK acción planificada
[detect_existing] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 3. backup_plan

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[backup_plan] OK ruta validada
[backup_plan] OK acción planificada
[backup_plan] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 4. copy_plan

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[copy_plan] OK ruta validada
[copy_plan] OK acción planificada
[copy_plan] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 5. json_validation

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[json_validation] OK ruta validada
[json_validation] OK acción planificada
[json_validation] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 6. manifest_validation

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[manifest_validation] OK ruta validada
[manifest_validation] OK acción planificada
[manifest_validation] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 7. verify_expected_files

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[verify_expected_files] OK ruta validada
[verify_expected_files] OK acción planificada
[verify_expected_files] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 8. rollback_plan

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[rollback_plan] OK ruta validada
[rollback_plan] OK acción planificada
[rollback_plan] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 9. log_summary

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[log_summary] OK ruta validada
[log_summary] OK acción planificada
[log_summary] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

## 10. operator_notes

Qué debe probar el instalador:

- repo root existe;
- product root existe;
- ZIP existe;
- payload trae rutas esperadas;
- no hay archivos prohibidos;
- las carpetas destino pueden crearse;
- si un archivo existe, habrá backup antes de reemplazar;
- JSON parsea correctamente;
- verify puede correr sin red;
- rollback puede restaurar archivos previos.

Salida esperada en log:

```text
[operator_notes] OK ruta validada
[operator_notes] OK acción planificada
[operator_notes] OK sin cambios destructivos
```

Bloqueadores:

| Bloqueador | Acción |
|---|---|
| product root no existe | detener |
| zip no existe | detener |
| JSON inválido | detener |
| backup no se puede crear | detener |
| archivo prohibido en payload | detener |
| ruta fuera del product root | detener |

Comentario operativo: dry-run debe ser lo bastante claro para que el usuario no instale a ciegas. Si dry-run no explica qué hará, es como firmar contrato en servilleta mojada.

