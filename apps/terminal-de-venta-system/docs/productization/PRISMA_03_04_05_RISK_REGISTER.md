# PRISMA 03-04-05 — Risk Register


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: documentación y contratos.  
> Prohibido: runtime, DB, `.env`, comunicación remota, pagos, ejecución de plugins y updates reales.


## Riesgos

| ID | Riesgo | Severidad | Mitigación | Paquete relacionado | Decisión |
| --- | --- | --- | --- | --- | --- |
| R002-001 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-002 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-003 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-004 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-005 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-006 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-007 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-008 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-009 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-010 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-011 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-012 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-013 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-014 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-015 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-016 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-017 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-018 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-019 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-020 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-021 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-022 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-023 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-024 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-025 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-026 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-027 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-028 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-029 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-030 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-031 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-032 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-033 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-034 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-035 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-036 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-037 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-038 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-039 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-040 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-041 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-042 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-043 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-044 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-045 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-046 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-047 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-048 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-049 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-050 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-051 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-052 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-053 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-054 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-055 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-056 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-057 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-058 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-059 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-060 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-061 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-062 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-063 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-064 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-065 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-066 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-067 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-068 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-069 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-070 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-071 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-072 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-073 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-074 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-075 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-076 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-077 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-078 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-079 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-080 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-081 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-082 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-083 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-084 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-085 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-086 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-087 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-088 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-089 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-090 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-091 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-092 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-093 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-094 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-095 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-096 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-097 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-098 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-099 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-100 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-101 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-102 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-103 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-104 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-105 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-106 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-107 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-108 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-109 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-110 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-111 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-112 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-113 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-114 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-115 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-116 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-117 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-118 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-119 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-120 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-121 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-122 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-123 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-124 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-125 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-126 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-127 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-128 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-129 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-130 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-131 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-132 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-133 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-134 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-135 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-136 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-137 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-138 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-139 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-140 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |
| R002-141 | Diagnóstico filtra secretos | crítico | allowlist + redacción + consentimiento | 04 | bloquear paquete si aparece |
| R003-142 | Mensajes parecen enviados | alto | blocked_no_server y copy claro | 05 | bloquear paquete si aparece |
| R004-143 | Tablet bloquea venta | crítico | volver a venta siempre visible | 03 | bloquear paquete si aparece |
| R005-144 | Plugin se ejecuta antes de 07 | crítico | plugins read-only | 03/07 | bloquear paquete si aparece |
| R006-145 | Update se aplica antes de 08 | crítico | updates read-only | 03/08 | bloquear paquete si aparece |
| R007-146 | Licencia parece secuestrar datos | alto | copy de no eliminación | 02/03 | bloquear paquete si aparece |
| R008-147 | Datos vivos caen en repo | alto | Runtime 01 customer root | 01/05 | bloquear paquete si aparece |
| R009-148 | Anuncio comercial interrumpe checkout | medio | regla no popup checkout | 03/06 | bloquear paquete si aparece |
| R010-149 | Soporte adjunta archivo libre | alto | refs controladas | 04/05 | bloquear paquete si aparece |
| R001-150 | Centro PRISMA promete acciones reales | alto | mantener mock/read-only visible | 03 | bloquear paquete si aparece |

## Política

Riesgo crítico no se documenta “para luego”. Se bloquea implementación. El papel aguanta todo, el cliente no.
