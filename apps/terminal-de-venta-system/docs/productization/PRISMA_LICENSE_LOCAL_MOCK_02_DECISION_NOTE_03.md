# PRISMA License Local Mock 02 - Decision Note 03: Plan catalog

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `03`.

---

## Decisión

Los planes iniciales son `TABLET_SOLO`, `TABLET_PRO`, `PC_BACKOFFICE` y `TABLET_PC_MANAGED`. El catálogo de planes es fuente de lectura para demos y mocks, pero la decisión final debe pasar por resolver entitlements.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
