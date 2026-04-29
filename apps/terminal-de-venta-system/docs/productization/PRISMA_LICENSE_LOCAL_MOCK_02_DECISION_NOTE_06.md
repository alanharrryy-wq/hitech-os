# PRISMA License Local Mock 02 - Decision Note 06: No payment boundary

**Paquete:** PRISMA_LICENSE_LOCAL_MOCK_02  
**Estado:** nota de decisión corregida  
**Uso:** reemplaza la nota repetida previa `06`.

---

## Decisión

La licencia de PRISMA no es procesamiento de pagos. Este paquete no valida transferencias, no toma tarjetas, no custodia dinero y no integra banca. Los métodos de pago de ticket son registro operativo, no procesamiento financiero.

---

## Regla práctica

- No meter esta decisión como string suelto en UI.
- No mezclar licencia con pagos bancarios.
- No bloquear datos del cliente por estado comercial.
- Registrar evento cuando exista infraestructura de auditoría.

---

## Resultado esperado

La implementación futura debe poder probar esta decisión con fixture, test case o verificación documental. Si no se puede probar, es puro humo con gafete.
