# PRISMA Support Diagnostics Contract

**Paquete:** PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00  
**Estado:** contrato documental  
**Superficies:** PC, Tablet y Local Agent futuro  
**Regla madre:** diagnóstico con consentimiento, sin secretos y sin exfiltrar datos sensibles.

---

## 1. Propósito

Este contrato define qué puede incluir un paquete de diagnóstico de soporte para PRISMA y qué queda prohibido. La meta es ayudar a soporte sin convertir la terminal del cliente en piñata de datos.

---

## 2. Ruta cliente sugerida

Los bundles de soporte deben vivir fuera del repo, en runtime cliente:

```text
C:\ProgramData\PRISMA\businesses\<businessId>\support\bundles\
```

En desarrollo puede usarse una ruta temporal, pero nunca debe confundirse con ruta de cliente final.

---

## 3. Contenido permitido

Un support bundle puede incluir:

- versión instalada;
- plan/licencia en estado resumido;
- runtime mode;
- businessId y deviceId;
- estado de sync/outbox;
- conteo de eventos pendientes;
- últimos errores técnicos sanitizados;
- estado general de DB;
- lista de plugins instalados;
- checksums de archivos de configuración no secretos;
- reporte de rutas resueltas;
- health report local.

---

## 4. Contenido prohibido

Un support bundle no debe incluir:

- tokens;
- contraseñas;
- secretos;
- `.env` completo;
- datos bancarios;
- llaves privadas;
- dumps completos de DB;
- datos personales innecesarios;
- información de tarjetas;
- credenciales de proveedores;
- archivos arbitrarios del cliente.

Si algo parece secreto, se trata como secreto. Nada de hacerse el sorprendido como mapache en bote de basura.

---

## 5. Consentimiento

La generación de diagnóstico debe declarar:

- qué se recolecta;
- para qué se usa;
- dónde se guarda;
- si se enviará a soporte;
- quién lo solicitó;
- fecha y hora.

La carga remota de diagnóstico requiere autorización explícita cuando exista Remote Ops.

---

## 6. Formato mínimo

Cada bundle debe incluir un manifest:

```json
{
  "bundleId": "diag_demo_001",
  "businessId": "demo-store",
  "deviceId": "tablet-001",
  "createdAt": "2026-04-28T00:00:00Z",
  "createdBy": "local-user-or-support-flow",
  "consent": true,
  "files": [],
  "redactionsApplied": true
}
```

---

## 7. Validación

Un bundle válido debe cumplir:

- manifest JSON parseable;
- sin archivos prohibidos;
- sin rutas fuera del runtime root;
- sin secretos detectables por patrones básicos;
- sin DB completa;
- sin `.env`;
- tamaño razonable;
- redacciones aplicadas.

---

## 8. Relación con IA futura

La IA de soporte futura solo puede leer diagnósticos ya sanitizados y en modo read-only. No puede ejecutar correcciones, borrar datos, modificar licencias, tocar stock, cambiar precios ni alterar ventas sin confirmación humana y contrato posterior.
