# PRISMA Licensing · Guía Operador/Admin Canónica

**Fecha de cierre operativo:** 2026-07-05
**Repositorio:** `F:\repos\hitech-os`
**App principal:** `F:\repos\hitech-os\apps\terminal-de-venta-system`
**Manual operativo canónico:** `docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`
**Guía canónica:** `docs/ops/PRISMA_LICENSING_OPERATOR_ADMIN_GUIDE.md`
**Setup operativo real:** `PRISMA-SETUP-CLI-2026-000003`
**Cliente visible:** `Prisma Rey`
**Tenant ID:** `tenant_prisma_rey`
**Tenant slug:** `prisma-rey`
**Marcador interno:** `OPS-20260705-CLI000003-F13`

> Esta guía es para operar licencias PRISMA ya existentes. No es una receta para rehacer backend, crear LICFLOW paralelo, cambiar secrets, desplegar Worker o tocar D1. Aquí se administra el flujo live ya validado, con el pulso firme y sin aventar salsa al tablero eléctrico.

---

## 1. Resumen ejecutivo

El flujo customer-safe de licencias PRISMA para `Prisma Rey` quedó operativo y verificado.

Estado final confirmado:

| Elemento | Estado |
|---|---:|
| Setup real | `PRISMA-SETUP-CLI-2026-000003` |
| Cliente visible | `Prisma Rey` |
| Tenant | `tenant_prisma_rey` |
| Tenant slug | `prisma-rey` |
| Tablet POS Slot | `1/1` |
| PC Admin Slot | `1/1` |
| Mobile Companion Slot | `1/1` |
| Status customer-safe | OK en los 3 devices |
| Refresh customer-safe | OK en los 3 devices |
| Diagnostics sin token | `ADMIN_TOKEN_REQUIRED`, bloqueo seguro |
| `secretsExposed` | `false` |
| Admin token usado | No |
| Código tocado | No |
| Git tocado por claims/status/refresh | No |
| Deploy / D1 migration | No |

Conclusión operativa:

```text
Setup activo, tres devices reclamados, licencia activa, refresh OK y diagnostics protegido.
```

---

## 2. Principio madre del flujo

Antes de tocar algo vivo, separar tres capas:

| Capa | Qué permite | Qué NO permite |
|---|---|---|
| Customer-safe | Consultar setup, reclamar slots, consultar status, ejecutar refresh | Revoke admin, diagnostics internos reales, confirmed admin operations |
| Operator/admin gated | Operaciones administrativas con bridge server-side o token rotado explícitamente | Imprimir, recuperar, pegar o registrar admin token |
| Source/Git/deploy | Cambios en código, docs, Worker, D1, scripts y contratos | Mezclarse con operación live sin plan, evidencia y rollback |

Regla operativa:

```text
Si hay duda del contrato o payload, primero mesh fresco read-only. Luego POST.
```

Regla de cierre:

```text
Sin evidencia fresca, no se improvisa.
```

Dicho en cristiano: no se le echa chile al motor para ver si corre más rápido. Primero se lee contrato, luego se opera.

---

## 3. Estado base histórico

El cierre principal de licencias quedó operativo E2E antes de esta guía.

Evidencia base:

```text
F:\descargasf\licops 0407 2339 result.zip
F:\descargasf\autogit apply 0407 235212 result.zip
F:\descargasf\autogit merge 0407 235221 result.zip
```

Resultado base:

| Elemento | Estado |
|---|---:|
| `licops` | PASS |
| Live smoke | `40/40` |
| Native verifiers | `19/19` |
| Secret scan | `0 findings` |
| PR final de licencias | `#166` |
| Commit final de licencias | `0d96147c` |

Después se cerraron cambios posteriores con AutoGit:

```text
F:\descargasf\autogit plan 0507 061146.zip
F:\descargasf\autogit apply 0507 061332 result.zip
F:\descargasf\autogit merge 0507 061706 result.zip
```

Resultado:

| Elemento | Estado |
|---|---:|
| PR posterior | `#167` |
| HEAD después de merge | `f12e60a3` |
| Branch usada | `autogit/cerrar_cambios_actuales_prisma_s-20260705-061332` |
| Checks | PASS |

Regla para trabajo futuro:

```text
Antes de cualquier commit nuevo, correr AutoGit plan fresco.
```

Motivo: después de pruebas, documentación y paquetes operator-safe puede haber working tree dirty. No se asume árbol limpio.

---

## 4. Setup real activo

Setup operativo real:

```text
PRISMA-SETUP-CLI-2026-000003
```

Endpoint customer-safe de consulta:

```text
GET https://app.hitechrts.com/api/customer/setup/PRISMA-SETUP-CLI-2026-000003
```

Respuesta esperada:

```json
{
  "ok": true,
  "schemaVersion": "1.0.0",
  "setupCode": "PRISMA-SETUP-CLI-2026-000003",
  "setupUrl": "https://app.hitechrts.com/setup/PRISMA-SETUP-CLI-2026-000003",
  "qrPayload": "prisma://setup/PRISMA-SETUP-CLI-2026-000003",
  "customerId": "cust_prisma_rey",
  "tenantId": "tenant_prisma_rey",
  "tenantSlug": "prisma-rey",
  "businessId": "biz_prisma_rey",
  "businessName": "Prisma Rey",
  "packageCode": "PRISMA_TRIPLE_DEVICE_STARTER",
  "planCode": "TABLET_PC_MOBILE_MANAGED",
  "status": "active",
  "secretsExposed": false
}
```

Slots finales esperados:

```json
[
  {
    "surface": "tablet",
    "label": "Tablet POS Slot",
    "allowed": 1,
    "claimed": 1
  },
  {
    "surface": "pc",
    "label": "PC Admin Slot",
    "allowed": 1,
    "claimed": 1
  },
  {
    "surface": "mobile",
    "label": "Mobile Companion Slot",
    "allowed": 1,
    "claimed": 1
  }
]
```

---

## 5. No usar `PRISMA-SETUP-STARTER`

`PRISMA-SETUP-STARTER` es starter/placeholder/referencia. No es setup real.

Prueba observada:

```text
GET https://app.hitechrts.com/api/customer/setup/PRISMA-SETUP-STARTER
```

Resultado:

```json
{
  "ok": false,
  "status": "SETUP_NOT_FOUND",
  "customerMessage": "No encontramos este setup.",
  "nextStep": "Revisa el Setup Code o pide un link nuevo.",
  "secretsExposed": false
}
```

Regla:

```text
PRISMA-SETUP-STARTER nunca debe usarse para operación live.
```

---

## 6. Datos customer-safe vs datos prohibidos

### Datos customer-safe

Estos datos pueden aparecer en comandos, reportes y guías:

| Dato | Valor |
|---|---|
| Setup Code | `PRISMA-SETUP-CLI-2026-000003` |
| Business visible | `Prisma Rey` |
| Tenant | `tenant_prisma_rey` |
| Tenant slug | `prisma-rey` |
| Tablet device | `DEV-2026-000002` |
| PC device | `DEV-2026-000003` |
| Mobile device | `DEV-2026-000004` |
| Tablet register/fingerprint | `REG-EF564F-FE10E1` |
| PC register/fingerprint | `REG-7F54FA-C29DCC` |
| Mobile register/fingerprint | `REG-885EC6-EF66B1` |

### Datos prohibidos

No pedir, no imprimir, no guardar y no pegar:

```text
PRISMA_ADMIN_TOKEN
ADMIN_TOKEN
Authorization: Bearer ...
```

Regla:

```text
Las operaciones customer-safe no requieren admin token.
```

---

## 7. Regla crítica de `PRISMA_ADMIN_TOKEN`

Cloudflare Worker secrets son write-only. Eso significa que el token viejo no se lee ni se recupera.

Si se necesita un token admin nuevo, se genera localmente en memoria:

```python
import secrets
token = "prisma_" + secrets.token_urlsafe(48)
```

Fingerprint permitido:

```python
import hashlib
fingerprint = hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]
```

Luego se rota el secret sin imprimir el valor:

```text
wrangler secret put PRISMA_ADMIN_TOKEN
```

o con `npx wrangler`, pasando el valor por stdin desde un proceso seguro.

Fingerprint truncado observado en la última rotación operativa:

```text
aac47e57afec80b6
```

Reglas:

- No pedir token real en chat.
- No imprimir token.
- No guardar token en docs.
- No guardar token en logs.
- No guardar token en ZIPs.
- No guardar token en screenshots.
- No pegar token en navegador.
- No intentar recuperar un Cloudflare Worker secret viejo.
- Al rotar, el token anterior queda inválido.
- `READ_ONLY_ADMIN_TOKEN_PRESENT` sólo significa presencia detectable, no valor recuperable.

---

## 8. Contrato confirmado para reclamar devices

Endpoint customer-safe:

```text
POST https://app.hitechrts.com/api/customer/devices/claim
```

Este endpoint no requiere admin token.

Contrato confirmado:

```json
{
  "setupCode": "string",
  "surface": "tablet | pc | mobile",
  "deviceId": "string",
  "deviceName": "string opcional",
  "installationFingerprint": "string opcional",
  "appVersion": "string opcional",
  "operatorLabel": "string opcional"
}
```

Campos obligatorios:

```json
{
  "setupCode": true,
  "surface": true,
  "deviceId": true
}
```

Campos opcionales seguros:

```json
{
  "deviceName": true,
  "installationFingerprint": true,
  "appVersion": true,
  "operatorLabel": true
}
```

Campos que NO deben enviarse:

```text
PRISMA_ADMIN_TOKEN
ADMIN_TOKEN
Authorization
Bearer
```

---

## 9. Flujo operador para reclamar un slot

### Preflight mínimo

Antes de mandar `POST /api/customer/devices/claim`:

1. Consultar setup.
2. Confirmar `ok=true`.
3. Confirmar `secretsExposed=false`.
4. Confirmar que el slot objetivo existe.
5. Confirmar `allowed=1`.
6. Confirmar `claimed=0`.
7. Confirmar contrato fresco si hay duda.
8. Confirmar que el payload no contiene palabras visibles prohibidas ni secrets.

### Si el slot ya está `claimed=1`

No repetir claim a ciegas.

Acción:

1. Consultar setup.
2. Consultar status del `deviceId` esperado.
3. Confirmar que el device reclamado corresponde al esperado.
4. Si corresponde, marcar PASS idempotente.
5. Si no corresponde, detener y documentar conflicto.

---

## 10. Tablet POS Slot

Dispositivo:

```json
{
  "humanCode": "DEV-2026-000002",
  "deviceType": "tablet_pos",
  "roleCode": "counter",
  "registerCode": "REG-EF564F-FE10E1",
  "clientCode": "CLI-2026-000003",
  "clientName": "Prisma Rey"
}
```

Payload usado:

```json
{
  "setupCode": "PRISMA-SETUP-CLI-2026-000003",
  "surface": "tablet",
  "deviceId": "DEV-2026-000002",
  "deviceName": "Tablet POS - Prisma Rey",
  "installationFingerprint": "REG-EF564F-FE10E1",
  "appVersion": "prisma-operator-claim-20260705",
  "operatorLabel": "OPS-20260705-CLI000003-F13"
}
```

Resultado:

```text
VERDICT=PASS
REASON=TABLET_CLAIMED_AND_VERIFIED
```

Device reclamado:

```json
{
  "deviceId": "DEV-2026-000002",
  "surface": "tablet",
  "status": "claimed",
  "claimId": "claim_8cf16a08-feb4-41a8-b7b5-91720aeab723"
}
```

Estado final:

```json
{
  "surface": "tablet",
  "label": "Tablet POS Slot",
  "allowed": 1,
  "claimed": 1
}
```

---

## 11. PC Admin Slot

Dispositivo:

```json
{
  "humanCode": "DEV-2026-000003",
  "deviceType": "pc_register",
  "registerCode": "REG-7F54FA-C29DCC",
  "status": "pending_registration",
  "clientCode": "CLI-2026-000003",
  "clientName": "Prisma Rey"
}
```

Payload usado:

```json
{
  "setupCode": "PRISMA-SETUP-CLI-2026-000003",
  "surface": "pc",
  "deviceId": "DEV-2026-000003",
  "deviceName": "PC Admin - Prisma Rey",
  "installationFingerprint": "REG-7F54FA-C29DCC",
  "appVersion": "prisma-operator-claim-20260705",
  "operatorLabel": "OPS-20260705-CLI000003-F13"
}
```

Resultado:

```json
{
  "deviceId": "DEV-2026-000003",
  "surface": "pc",
  "status": "claimed",
  "claimId": "claim_ddccf667-2e8e-4e87-9a6a-1133c64cc93c",
  "resultCode": "LICENSE_STATUS_OK"
}
```

Estado final:

```json
{
  "surface": "pc",
  "allowed": 1,
  "claimed": 1
}
```

---

## 12. Mobile Companion Slot

Dispositivo:

```json
{
  "humanCode": "DEV-2026-000004",
  "deviceType": "mobile",
  "registerCode": "REG-885EC6-EF66B1",
  "status": "pending_registration",
  "clientCode": "CLI-2026-000003",
  "clientName": "Prisma Rey"
}
```

Payload usado:

```json
{
  "setupCode": "PRISMA-SETUP-CLI-2026-000003",
  "surface": "mobile",
  "deviceId": "DEV-2026-000004",
  "deviceName": "Mobile Companion - Prisma Rey",
  "installationFingerprint": "REG-885EC6-EF66B1",
  "appVersion": "prisma-operator-claim-20260705",
  "operatorLabel": "OPS-20260705-CLI000003-F13"
}
```

Resultado:

```json
{
  "deviceId": "DEV-2026-000004",
  "surface": "mobile",
  "status": "claimed",
  "claimId": "claim_9fc900b6-dd88-4937-9309-aa4d4e1e9303",
  "resultCode": "LICENSE_STATUS_OK"
}
```

Estado final:

```json
{
  "surface": "mobile",
  "allowed": 1,
  "claimed": 1
}
```

---

## 13. Claim triple: estado final

Resultado del claim PC + Mobile:

```text
VERDICT=PASS
REASON=PC_AND_MOBILE_CLAIMED_AND_VERIFIED
```

Resumen:

```json
{
  "claimedSurfacesThisRun": ["pc", "mobile"],
  "postCount": 2,
  "adminTokenUsed": false,
  "authorizationHeaderSent": false,
  "secretsExposed": false
}
```

Estado final:

```json
{
  "tablet": {
    "allowed": 1,
    "claimed": 1
  },
  "pc": {
    "allowed": 1,
    "claimed": 1
  },
  "mobile": {
    "allowed": 1,
    "claimed": 1
  }
}
```

---

## 14. License status customer-safe

Endpoint:

```text
GET /api/customer/license/status?setupCode=<SETUP_CODE>&deviceId=<DEVICE_ID>
```

Devices validados:

```text
DEV-2026-000002
DEV-2026-000003
DEV-2026-000004
```

Resultado:

| Surface | Device | Status | License |
|---|---|---:|---:|
| Tablet | `DEV-2026-000002` | `claimed` | `active` |
| PC | `DEV-2026-000003` | `claimed` | `active` |
| Mobile | `DEV-2026-000004` | `claimed` | `active` |

Licencia:

```json
{
  "planCode": "TABLET_PC_MOBILE_MANAGED",
  "status": "active",
  "state": "active",
  "validUntil": "2027-07-05T13:57:27.689Z",
  "signed": false
}
```

---

## 15. License refresh customer-safe

Endpoint:

```text
POST /api/customer/license/refresh
```

Payload mínimo por device:

```json
{
  "setupCode": "PRISMA-SETUP-CLI-2026-000003",
  "deviceId": "DEV-2026-00000X"
}
```

Resultado:

| Surface | Device | Refresh |
|---|---|---:|
| Tablet | `DEV-2026-000002` | `LICENSE_REFRESHED` |
| PC | `DEV-2026-000003` | `LICENSE_REFRESHED` |
| Mobile | `DEV-2026-000004` | `LICENSE_REFRESHED` |

Resultado final:

```text
VERDICT=PASS
REASON=STATUS_REFRESH_PASS_DIAGNOSTICS_SANITIZED_OR_SAFELY_GATED
```

---

## 16. Diagnostics protegido

Endpoint:

```text
/api/support/diagnostics
```

Resultado sin admin token:

```json
{
  "ok": false,
  "status": "ADMIN_TOKEN_REQUIRED"
}
```

Interpretación:

Esto es correcto. Diagnostics está protegido por admin token y no entrega información sensible en modo customer-safe.

Regla:

```text
ADMIN_TOKEN_REQUIRED en diagnostics sin token es PASS de seguridad, no falla.
```

---

## 17. Seguridad confirmada

Resumen:

```json
{
  "adminTokenUsed": false,
  "authorizationHeaderSent": false,
  "tokenValuePrinted": false,
  "secretsExposed": false,
  "gitWrite": false,
  "localFilesModified": false,
  "deploy": false,
  "d1Migration": false,
  "playwright": false,
  "mamastrophic": false
}
```

Freno absoluto:

```text
Si secretsExposed=true, detener operación.
```

No se continúa con claim, refresh, diagnostics ni confirmed operations cuando `secretsExposed` sea `true`.

---

## 18. Evidencias generadas en el flujo operador

Evidencia de mesh, claims y verificaciones:

```text
F:\descargasf\licmesh fresh 0507 083902 result.zip
F:\descargasf\tablet claim 0507 084842 result.zip
F:\descargasf\pcmobile mesh 0507 085634 result.zip
F:\descargasf\pc mobile claim 0507 085915 result.zip
F:\descargasf\licsetup 0507 085944 result.zip
F:\descargasf\status refresh diag 0507 090852 result.zip
```

Evidencia de regla token/docs:

```text
F:\descargasf\tokmap 0507 073836 result.zip
F:\descargasf\toknfix1 0507 081938 result.zip
```

Evidencia histórica de cierre source/Git:

```text
F:\descargasf\licops 0407 2339 result.zip
F:\descargasf\autogit apply 0407 235212 result.zip
F:\descargasf\autogit merge 0407 235221 result.zip
F:\descargasf\autogit plan 0507 061146.zip
F:\descargasf\autogit apply 0507 061332 result.zip
F:\descargasf\autogit merge 0507 061706 result.zip
```

---

## 19. Qué ve el operador cuando todo va bien

### Setup

- `ok=true`
- `status=active`
- `businessName=Prisma Rey`
- `secretsExposed=false`

### Slots

- Tablet POS Slot `1/1`
- PC Admin Slot `1/1`
- Mobile Companion Slot `1/1`

### Status

- Device status `claimed`
- License `active`
- Plan `TABLET_PC_MOBILE_MANAGED`

### Refresh

- `LICENSE_REFRESHED`

### Diagnostics sin token

- `ADMIN_TOKEN_REQUIRED`

Ese último punto es sano: significa que el endpoint admin está cerrado con candado, no con mecate.

---

## 20. Qué significa cada falla común

| Falla | Significado | Acción segura |
|---|---|---|
| `SETUP_NOT_FOUND` | Setup equivocado, expirado o ambiente incorrecto | Revisar setupCode/base URL; no crear otro setup sin autorización |
| `SLOT_ALREADY_CLAIMED` | El slot ya está usado | Consultar status del device esperado |
| `DEVICE_ALREADY_CLAIMED` | El device ya está asociado | Confirmar que sea el device esperado |
| HTTP 400/422 en claim | Payload no coincide con contrato | Recolectar mesh fresco; no inventar campos |
| `ADMIN_TOKEN_REQUIRED` en diagnostics | Bloqueo seguro esperado | Marcar PASS de seguridad si no se mandó token |
| `secretsExposed=true` | Falla crítica de exposición | Detener operación y preservar evidencia |
| Working tree dirty | Hay cambios locales pendientes | AutoGit plan fresco antes de commit |
| Token ausente en PowerShell | Normal si no se cargó localmente | No pedir token; usar bridge o rotación autorizada |
| `PRISMA-SETUP-STARTER` not found | Correcto, no es setup real | Usar `PRISMA-SETUP-CLI-2026-000003` |

---

## 21. Reglas para próximos pasos

### Permitido sin admin token

- Consultar setup.
- Consultar status.
- Ejecutar refresh customer-safe.
- Verificar diagnostics protegido.
- Generar mesh fresco read-only.
- Documentar evidencia.

### Requiere preflight propio

- Simulation / Dry Run.
- Confirmed License Operation.
- Revoke.
- Device Replacement Flow.
- Customer Portal / Magic Link operativo.
- Billing / Renewal / Grace.
- Cualquier cambio que pueda mutar estado administrativo.

### Requiere autorización explícita

- Rotar `PRISMA_ADMIN_TOKEN`.
- Deploy Worker.
- D1 migration.
- Git commit/push/merge.
- Revoke real.
- Confirmed operation real.
- Cambios de secrets.
- Operaciones destructivas o irreversibles.

---

## 22. Simulation / Dry Run

Siguiente paso recomendado después del customer-safe closure:

```text
Simulation / Dry Run
```

Reglas:

1. Mesh fresco antes.
2. No confirmed operation todavía.
3. No admin token salvo justificación.
4. No cambios permanentes sin reporte claro.
5. Un solo ZIP final.
6. `secretsExposed=false`.
7. Si el endpoint exige admin token, detener y explicar.

Resultado esperado:

```text
SIMULATION_READY o DRY_RUN_PASS
```

Si requiere admin token:

```text
ADMIN_TOKEN_REQUIRED
```

y se marca como gated seguro, no como falla de seguridad.

---

## 23. Confirmed License Operation

No ejecutar confirmed operation sin autorización explícita.

Antes debe existir:

- Mesh fresco.
- Endpoint exacto.
- Payload exacto.
- Qué estado muta.
- Cómo se verifica.
- Qué rollback o compensación existe.
- Riesgo de duplicidad.
- Evidencia esperada.
- Confirmación del usuario.

Regla:

```text
Dry Run no autoriza Confirmed Operation automáticamente.
```

---

## 24. Revoke, replacement, portal y billing

Estos bloques son posteriores y deben tratarse como flujos separados.

### Revoke

Requiere:

- Preflight.
- Confirmación explícita.
- Estado antes/después.
- Identificación exacta del device/licencia.
- Plan de recuperación o renovación.

### Device Replacement Flow

Requiere:

- Device viejo.
- Device nuevo.
- Superficie.
- Motivo.
- Confirmación de slot transferido.
- Status final.

### Customer Portal / Magic Link

Requiere:

- No admin token en cliente.
- Magic link seguro.
- Expiración.
- No secretos en URL pública.
- Verificación de `secretsExposed=false`.

### Billing / Renewal / Grace

Requiere:

- Plan vigente.
- Ventana de renovación.
- Estado commercial-state.
- Grace period.
- Evidencia antes/después.
- No simulación confundida con operación confirmada.

---

## 25. Checklist rápido para operador

Antes:

```text
[ ] SetupCode correcto
[ ] Base URL correcta
[ ] secretsExposed=false
[ ] Slot objetivo existe
[ ] Payload confirmado
[ ] No admin token
[ ] No Authorization header
[ ] No palabras visibles prohibidas
[ ] Un solo ZIP final
```

Después:

```text
[ ] Slot claimed 1/1
[ ] Status device claimed
[ ] License active
[ ] Refresh LICENSE_REFRESHED
[ ] Diagnostics gated o sanitizado
[ ] secretsExposed=false
[ ] ZIP final guardado
[ ] Git no tocado
```

---

## 26. Comandos/ZIPs operator-safe: estándar

Todo paquete futuro debe cumplir:

- PowerShell wrapper + motor Python embebido.
- Una sola pegada.
- Un solo ZIP final en `F:\descargasf`.
- Sin carpetas finales sueltas.
- Logs/reportes dentro del ZIP.
- Progress visible.
- Rollback incluido si modifica archivos o estado reversible.
- No fake green.
- No Git, deploy, D1 ni secrets salvo autorización.
- No Playwright/Mamastrophic salvo petición explícita.
- No matar procesos.
- Excepción conocida: launcher 3160 puede resetear/free port 3160 si se pide para ese flujo.

---

## 27. Estado final canónico

```text
PRISMA Licensing para Prisma Rey quedó customer-safe operativo:
- Setup activo.
- Tablet POS Slot reclamado.
- PC Admin Slot reclamado.
- Mobile Companion Slot reclamado.
- Status OK en los tres devices.
- Refresh OK en los tres devices.
- Diagnostics protegido por admin token.
- secretsExposed=false.
- Admin token no usado.
- Código no tocado por el flujo de claim/status/refresh.
- Git no tocado por el flujo de claim/status/refresh.
- Deploy no ejecutado.
- D1 migration no ejecutada.
```

---

## 28. Glosario rápido

| Término | Significado |
|---|---|
| Setup Code | Código customer-safe para resolver el setup |
| Slot | Cupo por superficie: tablet, pc, mobile |
| Claim | Registro/asociación de un device a un slot |
| DeviceId | Identificador del device reclamado |
| InstallationFingerprint | Huella segura del registro local |
| Refresh | Renovación/actualización customer-safe del estado de licencia |
| Diagnostics | Endpoint protegido para diagnóstico admin |
| `secretsExposed` | Bandera crítica de exposición de secretos |
| Dry Run | Simulación sin operación confirmada |
| Confirmed Operation | Operación real que puede mutar estado administrativo |
| Bridge server-side | Ruta segura para operar admin sin exponer token al cliente |

---

## 29. Regla final

Si el sistema responde claro y customer-safe, se opera.

Si pide admin token, se documenta como gated y se detiene.

Si algo expone secretos, se apaga la música.

Si falta contrato, se recolecta mesh.

Y si alguien quiere meter otro LICFLOW desde cero, primero se le quita el teclado tantito, porque este flujo ya está vivo y confirmado.
