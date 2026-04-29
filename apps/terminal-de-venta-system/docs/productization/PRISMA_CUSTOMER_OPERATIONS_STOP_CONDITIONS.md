# PRISMA Customer Operations - Stop Conditions

**Paquete:** PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00  
**Estado:** matriz canónica corregida  
**Uso:** instalación, revisión, handoff y paquetes posteriores.

---

## Regla madre

Si una condición de alto riesgo aparece, el instalador, agente o reviewer debe detenerse. No se improvisa con producción como si fuera olla de frijoles a ojo.

---

## Matriz canónica

| Área | Stop condition | Acción obligatoria |
|---|---|---|
| Root | `--repo-root` no es absoluto | detener |
| Root | no existe `apps\terminal-de-venta-system` | detener |
| Payload | un archivo intenta escribir fuera del product root | detener |
| Payload | path con `..` o ruta absoluta dentro del ZIP | detener |
| JSON | cualquier `.json` no parsea | detener |
| Manifest | falta manifest del paquete | detener |
| Manifest | manifest declara archivo inexistente | detener |
| Hash | hash declarado no coincide | detener o regenerar manifest |
| Backup | no se puede crear backup antes de reemplazar | detener |
| Apply | falla copia de archivo | rollback automático |
| Verify | falta archivo requerido | rollback automático |
| Runtime | paquete documental intenta tocar DB | detener |
| Runtime | paquete documental intenta tocar `.next`, `node_modules` o rutas Next | detener |
| Seguridad | comando remoto fuera de allowlist | detener |
| Pagos | aparece integración bancaria, tarjetas, transferencia o custodia de dinero | detener |
| Licencias | una licencia intenta borrar/secuestrar datos cliente | detener |
| Plugins | plugin sin manifest o sin permisos declarados | detener |
| Diagnóstico | bundle incluye secretos, `.env` o DB completa | detener |
| Updates | update sin checksum, backup, verify y rollback | detener |
| IA | IA futura intenta ejecutar cambios sin humano | detener |

---

## Regla de revisión

Cada stop condition debe terminar en una de estas decisiones:

```text
PASS
BLOCKED
FIX_REQUIRED
OUT_OF_SCOPE
```

No usar “más o menos”. Eso es frase de taquero midiendo salsa, no criterio de instalación.

---

## Relación con paquetes siguientes

Estas condiciones aplican como base para:

- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01`;
- `PRISMA_LICENSE_LOCAL_MOCK_02`;
- paquetes de UI de Centro PRISMA;
- soporte local;
- messaging;
- announcements;
- plugin loader;
- Remote Ops bridge;
- IA read-only futura.
