# PRISMA Device Activation Contract 05

## 1. Propósito

Una licencia comercial no debe vivir flotando como bolsa del Oxxo en estacionamiento. Debe estar ligada a cliente, negocio y dispositivo.

## 2. Identidad mínima

Cada activación debe guardar:

```text
deviceId
terminalId
businessId
customerId
installationFingerprint
activatedAt
lastSeenAt
plan
licenseId
status
```

## 3. Fingerprint

El fingerprint debe construirse con señales estables y no invasivas. No debe depender de datos frágiles como `cwd`.

Sugerido:

```text
sha256(machine-guid + app-install-id + terminal-id + business-id)
```

El `app-install-id` debe crearse una vez y persistirse localmente.

## 4. Límites por plan

```text
TABLET_SOLO:
  terminals: 1
  branches: 1

TABLET_PRO:
  terminals: 2
  branches: 1

TABLET_PC_REQUIRED:
  terminals: 6
  branches: 3
```

## 5. Estados de dispositivo

```text
pending
active
suspended
revoked
replaced
```

## 6. Reset controlado

Reset de dispositivo debe requerir actor admin, razón, timestamp, device anterior, device nuevo, auditoría y límite de resets por periodo.

## 7. Decisiones de enforcement

- Si se excede límite de terminales: bloquear activación nueva.
- Si device está suspended: bloquear extras y refresh normal.
- Si device está revoked: rechazar licencia.
- Si server no responde: conservar última licencia válida y aplicar offline grace.
- Si firma falla: rechazo duro.

## 8. Evidencia esperada

Cada activación debe dejar rastro en:

```text
license.activated
device.activated
device.limit_exceeded
license.refresh_succeeded
license.refresh_failed
```
