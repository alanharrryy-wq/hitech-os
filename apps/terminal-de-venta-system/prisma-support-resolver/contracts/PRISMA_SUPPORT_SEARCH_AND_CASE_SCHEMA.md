# PRISMA Support Search And Case Schema

## Busqueda universal

`POST /api/support/search` acepta `query`, `surface`, `category` y `code`.
Debe buscar por datos humanos y tecnicos: cliente, negocio, email, telefono,
customerId, businessId, licenseId, deviceId, terminalId, setupCode, plan,
estado de licencia, codigo de error y superficie.

Si la respuesta viene de fallback/source-ready, debe decirlo con
`sourceMode:"fallback_honest"` o `sourceMode:"source_ready"`.

## Case export

`POST /api/support/export-case` debe producir un caso sanitizado con:

- `support-case.json`
- `support-case.md`
- `issues.json`
- `surface-status.json`
- `customer-summary.json`
- `device-summary.json`
- `resolution-plan.json` si aplica
- `dry-run.json` si aplica
- `apply-result.json` si aplica
- redaction report
- `CONTINUATION.md`

Nunca incluye tokens, `.env`, private keys, Authorization headers, dumps ni DB completa.
