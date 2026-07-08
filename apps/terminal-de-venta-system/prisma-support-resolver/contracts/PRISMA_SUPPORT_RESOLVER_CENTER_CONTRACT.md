# PRISMA Support Resolver Center Contract

## Proposito

Support Resolver Center es la autoridad fisica para diagnosticar, simular,
resolver y exportar casos de soporte de licencias, runtime identity, customer
setup, device activation, POS/caja y Cloud License Gateway.

## Flujo obligatorio

1. Diagnosticar: `POST /api/support/diagnose`
2. Simular: `POST /api/support/resolve/simulate`
3. Confirmar: operador confirma la accion segura
4. Resolver: `POST /api/support/resolve/apply`
5. Validar: resultCode y evidence sanitizada
6. Exportar: `POST /api/support/export-case`

`simulate` nunca muta. `apply` requiere confirmacion explicita, evidencia
suficiente, accion permitida y `secretsExposed:false`.

## Prohibiciones

- No deploy Cloudflare.
- No D1 migration.
- No D1 dump.
- No imprimir tokens.
- No leer ni copiar private keys.
- No modificar licencia firmada a mano sin contrato valido.
- No borrar DB local.
- No resetear repo.
- No limpiar archivos a ciegas.

## Resultado homologado

Toda salida de diagnostico debe producir `SupportIssue` y, cuando aplique,
`SurfaceStatus`.
