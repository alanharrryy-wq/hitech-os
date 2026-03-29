# ERROR_BOUNDARIES

## Dominios de error

| Error domain | Ejemplos | Owner | Impacto esperado | Comportamiento permitido |
| --- | --- | --- | --- | --- |
| `validation` | payload inválido, schema mismatch | `<contract-owner>` | rechazo del request | devolver error contractual |
| `runtime` | fallo de handler, excepción de aplicación | `<runtime-owner>` | degradación local | fault del producto, no del host |
| `external_io` | red, FS, subprocess, timeout | `<adapter-owner>` | reintento o degradación | aplicar policy, nunca colgar el host |
| `persistence` | snapshot corrupto, migración fallida | `<state-owner>` | restore abortado, possible degrade | bloquear activate si es necesario |
| `security_policy` | permiso faltante, policy denegada | `<security-owner>` | acción rechazada | emitir evidencia y denial explícito |

## Reglas

- Nunca tragar excepciones sin evidencia.
- Nunca propagar una excepción de producto hasta tumbar el host.
- Todo boundary debe mapear errores a envelopes contractuales.
- Todo timeout tiene owner y acción de cierre.
- Si el producto entra a `faulted`, debe quedar evidencia observable.

## Retry policy

| Caso | Se reintenta | Máximo | Backoff | Evidencia |
| --- | --- | --- | --- | --- |
| lectura transitoria | sí/no | `<n>` | `<policy>` | log + metric |
| subprocess timeout | sí/no | `<n>` | `<policy>` | diagnostics |
| schema mismatch | no | 0 | N/A | compatibility error |

## Stop-the-line cases

- corrupción confirmada de estado;
- fuga de procesos;
- violación de policy de seguridad;
- incompatibilidad contractual mayor;
- acceso detectado a internals del host.
