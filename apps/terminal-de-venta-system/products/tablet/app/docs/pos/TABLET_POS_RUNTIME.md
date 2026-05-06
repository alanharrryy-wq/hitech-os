# Tablet POS Runtime

Estado: canon listo para codigo.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Guia ready-for-code para ejecutar Tablet como POS standalone sin PC.


## Runtime

Ver `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\architecture\RUNTIME_MODES_CONTRACT.md`.

## DB

- Canonical: `products/tablet/app/data/tablet-pos.db`
- Fallback: `file:./data/tablet-pos.db`
- Variables: `TABLET_DATABASE_URL`, `TABLET_RUNTIME_MODE`

## Reglas

- Tablet must never block basic sale because PC is absent.
- If sync fails, allowed local sale continues.
- Sensitive operations are marked.
- Events go to outbox.
- PC resolves conflicts later.
- Tablet commands must not validate PC existence for Tablet tasks.
- Do not depend on tools/_local/data/terminal-de-venta-system/canonical.db for selling.
- Do not use cwd as trusted root.
- Do not invent magic DB paths.

## Comandos esperados por siguiente etapa

- `F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd tablet-db-init`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd tablet-dev`
