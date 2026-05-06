# PRISMA Support Bundle Local 04 — Secret Redaction Policy


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Versión documental: `1.1.0`  
> Fecha: `2026-04-28`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: docs, schemas, examples, test-cases, manifest y checksums.  
> Restricción: no instala runtime, no crea rutas Next, no toca DB, no toca `.env`, no ejecuta sync remoto y no procesa pagos.

## Base que no se contradice

Este paquete asume que ya existen y quedan como piso:

- `PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00`: contratos base de customer operations, remote ops, updates, soporte, plugins, licencias y frontera de no procesamiento bancario.
- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01`: separación repo / release / runtime cliente, reglas de `ProgramData`, logs, backups, config y prohibición de depender de `cwd`.
- `PRISMA_LICENSE_LOCAL_MOCK_02`: planes, feature flags mock, entitlements, offline grace y contrato local de licencia.

Nada de este paquete invalida lo anterior. Esto no viene a patear la mesa, viene a poner mantel, cubiertos y letrero de “no meter los dedos al enchufe”.


## Principios

1. Redactar antes de persistir.
2. Redactar antes de comprimir.
3. Redactar antes de mostrar preview.
4. No escribir secretos en logs del generador.
5. Si el redactor falla, el bundle no se genera.

## Formatos de redacción

| Tipo | Salida |
| --- | --- |
| token | <redacted:token:sha256-prefix-8> |
| password | <redacted:password> |
| api key | <redacted:api-key:sha256-prefix-8> |
| connection string | <redacted:connection-string> |
| user path | C:\\Users\\<redacted>\\... |
| customer data | <redacted:customer-data> |

## Ejemplo

Entrada:

```text
DATABASE_URL=postgres://user:pass@host:5432/db
Authorization: Bearer abc.def.ghi
customerPhone=5512345678
```

Salida:

```text
DATABASE_URL=<redacted:connection-string>
Authorization: Bearer <redacted:token:sha256-prefix-8>
customerPhone=<redacted:customer-data>
```

## Stop conditions

- Redactor falla silenciosamente.
- Bundle se genera con errores de redacción.
- Preview guarda secretos.
- Manifest no indica reglas aplicadas.
- Logs del generador contienen secretos.
