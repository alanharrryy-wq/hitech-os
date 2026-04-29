# PRISMA License Local Mock 02 - Decision Note 07: Audit events

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `07`.

---

## Decisión

Cambios de licencia, refresh, suspensión, grace, denegación de feature y activación de plugin deben generar evento cuando exista event log. El evento debe incluir actor, deviceId, businessId, featureKey y razón de decisión.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
