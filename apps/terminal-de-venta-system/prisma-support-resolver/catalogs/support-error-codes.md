# Support Error Codes

Fuente canonica: `support-error-codes.json`.

## Categorias incluidas

- `license_assignment`: asignacion de licencia, firma, vencimiento, refresh y feature gates.
- `customer_setup`: Setup Code, Setup Link, Device Claim, slots y reemplazo.
- `runtime_local`: runtime identity, demo mode, device/store/business/terminal mismatch.
- `pos_terminal_cash`: terminal local, caja, DB local y bloqueo POS por licencia.
- `pc_admin`: PC Admin Slot, asignacion y contradicciones visuales.
- `mobile_app`: Mobile Companion Slot, asignacion y superficie de soporte movil.
- `cloud_gateway_d1`: health, route map, D1 drift, audit y admin token.
- `security`: secretos, private keys, tokens, env y bundle sin sanitizar.
- `escalation`: Codex, ChatGPT, aprobacion humana, onsite y bloqueo remoto.

## Caso canonico obligatorio

`LICENSE_ASSIGNMENT_WRONG_BUSINESS`

- Cliente: La licencia esta activa, pero pertenece a otro negocio.
- Tecnico: `license.businessId != runtime.businessId`.
- Resultado: `operationStatus: blocked`.
- Acciones seguras: diagnosticar, simular, exportar evidencia, Setup Claim o refresh si configurado.
- Acciones bloqueadas: reescritura manual ciega o edicion de licencia firmada.

## CROSS_SOURCE_IDENTITY_SPLIT

Detecta cuando PC/Admin, runtime local, licencia instalada, DB POS y/o activación firmada externa no apuntan al mismo cliente/negocio. La resolución debe elegir autoridad antes de mutar.
