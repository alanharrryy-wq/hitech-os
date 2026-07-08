# Prisma Support Resolver Center

Estado: canonical root source-ready.

Este root centraliza soporte, licencias, customer setup, activacion de dispositivos,
runtime identity, diagnostico, codigos de error, evidencia sanitizada y acciones
resolutivas para Tablet, PC, Mobile y Prisma Cloud Center.

## Reglas de autoridad

- No reemplaza `shared/licensing`; lo consume como contrato vivo de licencias y
  customer setup.
- No reemplaza `Prisma Cloud Ctr`; lo extiende como superficie operadora 3160.
- No copia secretos ni evidencia externa cruda.
- `F:\PRISMA_CTX\LICENSING` queda como referencia local externa sanitizable; no
  se copia `private-key.pem`, tokens, dumps, `.env` ni headers de autorizacion.
- Las acciones reales deben pasar por diagnostico, simulacion, confirmacion,
  aplicacion segura, validacion y evidencia sanitizada.

## Estado de integracion

- `AUTHORITY_MAP.md` define la fuente canonica por concepto.
- `DUPLICATE_MAP.md` identifica duplicados y legacy activo.
- `DEPRECATION_MAP.md` evita que fuentes viejas compitan como autoridad.
- `MIGRATION_REPORT.md` registra que se uso, corrigio, fusiono, creo o bloqueo.
- `catalogs/support-error-codes.json` es el catalogo canonico de codigos.
- `schemas/support-issue.schema.json` y `schemas/surface-status.schema.json`
  definen la salida homologada para soporte y superficies.

## Decision por pieza

Toda pieza importante relacionada con licencias, soporte, runtime, customer
setup, device activation, diagnostics o resolver actions debe caer en una de
estas etiquetas:

`USE_AS_IS`, `USE_AND_CONNECT`, `MOVE_TO_CANONICAL`, `MERGE_INTO_CANONICAL`,
`FIX_EXISTING`, `EXTEND_EXISTING`, `CREATE_MISSING`, `DEPRECATE_DUPLICATE`,
`RETIRE_UNSAFE`, `MOVE_TO_TRASH_OLD_WITH_MANIFEST`, `BLOCK_SECRET_RISK`.
