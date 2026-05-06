# PRISMA Remote Ops Implementation Blueprint

**Paquete:** PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00  
**Estado:** blueprint compacto corregido  
**Alcance:** guía de implementación futura, sin runtime activo.

---

## 1. Objetivo

Definir cómo debe evolucionar PRISMA hacia operación remota segura sin romper la regla principal:

> Tablet vende sola. Remote Ops observa, asiste y coordina. No gobierna la venta local básica.

---

## 2. Componentes futuros

| Componente | Rol |
|---|---|
| PRISMA Local Agent | proceso local controlado para health, licencia, diagnóstico y updates aprobados |
| Remote Ops API | superficie remota para comandos permitidos |
| Device Registry | registro de negocios, sucursales, dispositivos y versiones |
| License Service | fuente remota de estado de licencia y entitlements |
| Support Console | vista de soporte con consentimiento y diagnósticos sanitizados |
| Release Channel | stable, pilot y hotfix con checksum y rollback |

---

## 3. Allowlist mínima

Solo se permiten comandos declarados:

```text
CHECK_HEALTH
GENERATE_DIAGNOSTIC_BUNDLE
REFRESH_LICENSE
CHECK_FOR_UPDATES
STAGE_UPDATE
APPLY_APPROVED_UPDATE
DISABLE_PLUGIN
ENABLE_PLUGIN
RETRY_SYNC
```

Quedan prohibidos:

```text
RUN_ARBITRARY_COMMAND
EXECUTE_POWERSHELL
DELETE_DATABASE
EDIT_FILE_RAW
```

---

## 4. Secuencia recomendada

1. Resolver runtime root y config boundary.
2. Instalar licencia local mock.
3. Crear Centro PRISMA UI shell.
4. Agregar soporte local y diagnostic bundle.
5. Agregar messaging local/mock.
6. Agregar announcements controlados.
7. Agregar plugin manifest loader.
8. Agregar Remote Ops polling seguro.
9. Agregar IA read-only sobre diagnósticos sanitizados.

---

## 5. Reglas de seguridad

- No abrir puertos entrantes raros por defecto.
- Preferir polling autenticado desde Local Agent.
- No aceptar comandos arbitrarios.
- No ejecutar shell remoto.
- No borrar DB.
- No editar archivos crudos.
- Todo comando sensible debe generar evento/auditoría.
- Updates requieren checksum, backup, verify y rollback.
- Diagnóstico requiere sanitización.

---

## 6. Fronteras comerciales y regulatorias

Remote Ops no procesa pagos bancarios, no valida transferencias, no custodia dinero y no integra tarjetas. Si el producto registra métodos de pago internos, son datos operativos del ticket, no procesamiento financiero.

---

## 7. Definición de listo para implementación

Remote Ops puede empezar a implementarse cuando existan:

- runtime config boundary instalado;
- local license mock instalado;
- ruta de ProgramData definida;
- event/audit contract mínimo;
- diagnostic bundle local;
- manifest de plugin;
- update contract;
- allowlist validada.

Antes de eso, meter Remote Ops real sería ponerle turbo a una bicicleta con frenos de plastilina.
