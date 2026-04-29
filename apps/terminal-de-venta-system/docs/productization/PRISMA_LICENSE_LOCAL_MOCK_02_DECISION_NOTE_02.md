# PRISMA License Local Mock 02 - Decision Note 02: Feature resolution

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `02`.

---

## Decisión

Toda feature se decide por `featureKey`, plan, estado de licencia, entitlements explícitos y política offline. La UI no debe esconder reglas hardcodeadas. Si una feature no existe en el catálogo, se niega por defecto y queda evento auditable.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
