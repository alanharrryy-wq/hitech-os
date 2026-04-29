# PRISMA License Local Mock 02 - Decision Note 05: UI policy

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `05`.

---

## Decisión

La UI debe mostrar estado de licencia sin asustar al usuario ni bloquear datos. Tablet prioriza mensajes operativos cortos. PC puede mostrar detalle administrativo. Ninguna pantalla debe ocultar exportación o respaldo por suspensión.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
