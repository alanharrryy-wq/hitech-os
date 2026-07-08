# Evidence Export Contract

`POST /api/support/export-case` devuelve metadatos sanitizados y una lista de
archivos esperados. La implementacion puede escribirlos en un directorio seguro
cuando el operador autorice exportacion.

El contrato minimo del response es:

```json
{
  "ok": true,
  "resultCode": "SUPPORT_CASE_EXPORTED",
  "files": ["support-case.json", "support-case.md"],
  "redaction": { "secretsExposed": false },
  "secretsExposed": false
}
```
