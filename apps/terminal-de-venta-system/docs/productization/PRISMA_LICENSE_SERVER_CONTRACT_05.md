# PRISMA License Server Contract 05

## 1. Propósito

Definir el contrato del servidor real de licencias antes de implementarlo, porque escribir backend sin contrato es como ponerle turbo a una combi sin frenos.

## 2. Entidades mínimas

### Customer

```json
{
  "customerId": "cus_001",
  "legalName": "Abarrotes Don Prisma",
  "billingStatus": "active",
  "createdAt": "2026-04-29T00:00:00.000Z"
}
```

### Business

```json
{
  "businessId": "biz_001",
  "customerId": "cus_001",
  "displayName": "Sucursal Centro",
  "status": "active"
}
```

### Device

```json
{
  "deviceId": "dev_tablet_001",
  "terminalId": "tablet_caja_01",
  "businessId": "biz_001",
  "installationFingerprint": "sha256:...",
  "activatedAt": "2026-04-29T00:00:00.000Z",
  "lastSeenAt": "2026-04-29T00:00:00.000Z",
  "status": "active"
}
```

### License

```json
{
  "licenseId": "lic_001",
  "customerId": "cus_001",
  "businessId": "biz_001",
  "plan": "TABLET_PC_REQUIRED",
  "state": "active",
  "validFrom": "2026-04-29T00:00:00.000Z",
  "validUntil": "2026-05-29T00:00:00.000Z",
  "offlineGraceDays": 7,
  "limits": {
    "terminals": 6,
    "branches": 3
  },
  "features": {
    "pos.sale.complete": true,
    "pc.dashboard.view": true
  },
  "keyId": "prod-2026-01",
  "signatureAlgorithm": "ed25519"
}
```

## 3. Endpoints mínimos

### GET /health

Debe responder rápido, sin tocar lógica pesada.

```json
{
  "ok": true,
  "service": "prisma-license-server",
  "version": "0.1.0"
}
```

### POST /licenses/activate

Entrada:

```json
{
  "customerId": "cus_001",
  "businessId": "biz_001",
  "terminalId": "tablet_caja_01",
  "deviceId": "dev_tablet_001",
  "installationFingerprint": "sha256:...",
  "requestedPlan": "TABLET_PRO"
}
```

Errores esperados:

```text
CUSTOMER_NOT_FOUND
BUSINESS_NOT_FOUND
PLAN_NOT_ALLOWED
DEVICE_LIMIT_EXCEEDED
DEVICE_SUSPENDED
LICENSE_REVOKED
INVALID_FINGERPRINT
```

### POST /licenses/refresh

Debe devolver la última licencia firmada válida para el dispositivo.

### POST /licenses/revoke

Operación administrativa. Debe auditar actor y razón.

### POST /licenses/suspend

Operación administrativa reversible. Debe permitir razón y fecha.

### GET /licenses/current

Consulta operativa por `deviceId`, `terminalId` o `licenseId`.

### GET /customers/:id/licenses

Lista licencias por cliente.

## 4. Reglas de seguridad

- El servidor firma, el cliente verifica.
- La private key nunca se empaqueta en app cliente.
- La app cliente debe rechazar firma inválida.
- Producción no acepta licencias unsigned.
- Revoked gana sobre active aunque el archivo local diga otra cosa.
- Suspended bloquea extras, no necesariamente venta básica si la política comercial permite gracia.

## 5. Auditoría mínima

Eventos requeridos:

```text
license.activated
license.refreshed
license.refresh_failed
license.suspended
license.revoked
license.renewed
license.upgraded
license.downgraded
device.activated
device.limit_exceeded
signature.issued
signature.rejected
```
