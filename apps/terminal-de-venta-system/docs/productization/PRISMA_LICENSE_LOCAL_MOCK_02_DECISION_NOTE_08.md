# PRISMA License Local Mock 02 - Decision Note 08: Runtime handoff

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `08`.

---

## Decisión

La licencia local debe vivir fuera del repo en runtime cliente. La ruta sugerida es `C:\ProgramData\PRISMA\config\license.json`. Dev puede usar fixture, cliente no. Runtime Config Boundary 01 manda sobre rutas.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
