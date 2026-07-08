# PRISMA Support Surface Status Standard

Todas las superficies deben emitir estado homologado con:

```json
{
  "surface": "tablet",
  "visibleStatus": "Licencia activa, operacion bloqueada por asignacion de negocio.",
  "operationStatus": "blocked",
  "licenseStatus": "active",
  "assignmentStatus": "wrong_business",
  "customerId": "cust_demo",
  "businessId": "biz_demo",
  "storeId": "store_prisma_rey_centro",
  "deviceId": "tablet-pos-source-ready",
  "terminalId": "term_tablet_pos_001",
  "licenseId": "lic_demo",
  "plan": "TABLET_PRO",
  "primaryIssueCode": "LICENSE_ASSIGNMENT_WRONG_BUSINESS",
  "issues": [],
  "supportSummary": "Licencia activa, pero pertenece a otro negocio.",
  "nextStep": "Ingresar Setup Code del cliente correcto o refrescar licencia desde soporte.",
  "featuresAllowed": 0,
  "featuresBlocked": 1,
  "lastRefreshAt": null,
  "source": "support-resolver",
  "secretsExposed": false
}
```

## Regla anti-contradiccion

Si `operationStatus` es `blocked`, el encabezado visible debe decir bloqueo en
humano. No se permite mostrar:

- "lista para operar" junto con operacion bloqueada.
- "licencia activa" junto con "sin licencia local" sin explicar codigo.
- "no requiere accion" cuando hay bloqueo duro.
- funciones disponibles si todas estan bloqueadas sin issue principal.
