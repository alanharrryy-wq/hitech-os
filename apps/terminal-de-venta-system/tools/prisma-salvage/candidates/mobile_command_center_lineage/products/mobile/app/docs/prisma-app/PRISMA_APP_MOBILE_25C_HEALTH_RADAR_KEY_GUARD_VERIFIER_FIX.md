# PRISMA App Mobile 25C - Health Radar Key Guard Verifier Fix

## Objetivo
Corregir el hotfix 25B que falló porque su verificador Node traía una cadena mal escapada.

## Causa
El paquete 25B sí corregía el componente del Radar, pero el verificador incluía una cadena con comillas internas sin escape. Node detenía el apply con `SyntaxError: Unexpected identifier 'guardrail'` y el instalador hacía rollback automático.

## Corrección
- Mantiene la corrección real de React keys duplicadas.
- Cambia el verificador a sintaxis ESM válida.
- Valida que no regrese `key={item}`.
- Valida escenarios con evidencia duplicada como `tablet: OK`.
- Actualiza la versión móvil a `0.25.2`.

## Alcance
Solo App móvil. No toca Tablet, PC ni `shared-kernel`.
