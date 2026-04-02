# DeltaForge | Core Session Integrity Pack v1

Este paquete aterriza la siguiente jugada aprobada:

**Core Session Integrity Pass**

## Incluye
- matriz de ownership de integridad
- checklist de gaps críticos
- secuencia corta de implementación
- guardrails de diseño
- script PowerShell para extraer el paquete

## Uso sugerido
1. Abrir `01_CORE_SESSION_INTEGRITY_OWNERSHIP_MATRIX.md`
2. Abrir `02_CORE_SESSION_INTEGRITY_GAP_CHECKLIST.md`
3. Ejecutar el pase siguiendo `03_CORE_SESSION_INTEGRITY_IMPLEMENTATION_SEQUENCE.md`
4. Usar `04_DESIGN_GUARDRAILS.md` como freno para no meter acoplamiento nuevo

## Prioridad real
No reorganizar el repo completo.
Primero cerrar:
- events por sesión
- dirty/stale también por edición de ops
- refresh sin degradación indebida
- scope tipado
- infrastructure desacoplado de PySide
