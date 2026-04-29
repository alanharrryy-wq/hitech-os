# PRISMA Customer Operations Foundation 00 - Installer Plan corregido

**Paquete:** `PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00`  
**Tipo:** documentación, contratos, schemas, fixtures, checklist y manifest  
**Raíz objetivo:** `F:\repos\hitech-os\apps\terminal-de-venta-system`  
**Estado:** contrato instalable documental. No modifica runtime, DB, rutas Next ni lógica de venta.

---

## 1. Objetivo

Instalar la base documental y contractual de Customer Operations dentro de:

```text
F:\repos\hitech-os\apps\terminal-de-venta-system
```

Este paquete crea o reemplaza documentos y archivos JSON bajo:

```text
docs\productization\
tooling\productization\schemas\
tooling\productization\fixtures\
tooling\productization\manifests\
tooling\productization\installer-plan\
tooling\productization\checklists\
```

No ejecuta Remote Ops, no conecta servidores, no toca SQLite, no activa licencias reales y no instala plugins.

---

## 2. Modos obligatorios del instalador

El instalador asociado debe soportar:

```text
--dry-run
--apply
--verify
--rollback
--repo-root F:\repos\hitech-os
```

Debe resolver el product root como:

```text
<repo-root>\apps\terminal-de-venta-system
```

El instalador no debe depender del directorio actual. El `cwd` no manda aquí; ese compa siempre llega tarde a la obra.

---

## 3. `--dry-run`

Debe informar, sin modificar archivos:

- raíz de repo recibida;
- product root resuelto;
- carpetas que crearía;
- archivos que copiaría;
- archivos existentes que respaldaría;
- conflictos detectados;
- ubicación del log;
- si falta `F:\descargasf`;
- si falta `apps\terminal-de-venta-system`.

---

## 4. `--apply`

Debe ejecutar:

1. validar `--repo-root`;
2. validar product root;
3. crear log único en `F:\descargasf`;
4. generar backup previo de cualquier archivo existente que vaya a reemplazar;
5. crear carpetas faltantes;
6. copiar el payload completo;
7. escribir registro de instalación;
8. ejecutar `--verify`;
9. hacer rollback automático si verify falla.

---

## 5. `--verify`

Debe confirmar existencia mínima de:

```text
docs\productization\PRISMA_CUSTOMER_OPERATIONS_LAYER.md
docs\productization\PRISMA_LICENSE_ENTITLEMENTS_CONTRACT.md
docs\productization\PRISMA_CUSTOMER_MESSAGING_CONTRACT.md
docs\productization\PRISMA_PLUGIN_CATALOG_CONTRACT.md
docs\productization\PRISMA_NO_PAYMENT_PROCESSING_BOUNDARY.md
docs\productization\PRISMA_SUPPORT_DIAGNOSTICS_CONTRACT.md
docs\productization\PRISMA_REMOTE_OPS_IMPLEMENTATION_BLUEPRINT.md
tooling\productization\schemas\license.schema.json
tooling\productization\schemas\plugin-manifest.schema.json
tooling\productization\manifests\PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00.manifest.json
```

También debe validar que todos los `.json` del payload parseen correctamente.

Si se valida hash, el manifest no debe validarse contra un hash declarado dentro de sí mismo. Esa trampa es una víbora mordiéndose la cola, pero con JSON.

---

## 6. `--rollback`

Debe restaurar únicamente archivos respaldados por esta instalación.

Ruta sugerida:

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\.prisma_integration_backups\PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00_YYMMDD_HHMM\
```

Rollback no debe borrar archivos ajenos ni limpiar carpetas completas a lo bruto.

---

## 7. Log

Debe crear un solo log por ejecución en:

```text
F:\descargasf\PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00_int_YYMMDD_HHMM.log
```

El log debe incluir:

- modo ejecutado;
- root recibido;
- product root resuelto;
- archivos copiados;
- archivos respaldados;
- errores;
- resultado de verify;
- rollback automático, si ocurrió.

---

## 8. Stop conditions

El instalador debe detenerse si:

- no existe `apps\terminal-de-venta-system`;
- `--repo-root` no es absoluto;
- el payload intenta escribir fuera del product root;
- falta el manifest;
- un JSON no parsea;
- un archivo requerido no existe después de aplicar;
- el backup no puede crearse antes de reemplazar;
- verify falla.

---

## 9. Criterio de aceptación

El paquete pasa cuando:

- se puede inspeccionar con `--dry-run`;
- se puede aplicar sin tocar runtime;
- genera backup si reemplaza archivos;
- genera un único log en `F:\descargasf`;
- verifica archivos requeridos;
- valida JSON;
- puede revertirse;
- no depende de `cwd`;
- no introduce DB, `.next`, `node_modules`, `.env`, logs ni binarios.
