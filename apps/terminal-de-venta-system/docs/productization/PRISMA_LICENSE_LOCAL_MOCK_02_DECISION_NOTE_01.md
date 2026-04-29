# PRISMA License Local Mock 02 - Decision Note 01: State machine

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `01`.

---

## Decisión

Define los estados `active`, `offline_grace`, `suspended`, `expired` y `revoked`. La implementación debe resolver estado antes de resolver features. Estados duros como `revoked` no ejecutan capacidades operativas. `suspended` conserva exportación, backup y soporte básico para proteger datos del cliente.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
