# PRISMA License Local Mock 02 - Decision Note 04: Offline grace

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `04`.

---

## Decisión

Offline grace protege continuidad operativa local, no desbloquea todo el producto. Permite venta local y datos mínimos según plan. No permite activar plugins remotos, cambiar permisos críticos ni hacer operaciones administrativas sensibles.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
