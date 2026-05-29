# SAFETY REVIEW V5

## Clear no nuclear

Clear default se mantiene como `generated-only by ledger`. No se expone factory clear en la UI principal.

## Candados

- PIN default 030303.
- PIN configurable.
- Mutaciones públicas bloqueadas.
- Backup antes de Clear.
- Evidence después de operación.
- Rollback con PIN.
- License real reset excluido por default.

## Riesgos restantes

- SMTP real depende de configuración local.
- La inyección real debe probarse primero con dry-run y DB de prueba.
- El primer uso en repo real debe considerarse prueba controlada.
