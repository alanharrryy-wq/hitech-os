# PRISMA Twin Runtime Kernel Package

Entrega maciza para pasar de propuesta de paridad a contrato técnico compartido entre PC y Tablet.

## Qué instala

- Tipos TypeScript para `TwinCapabilityManifest`.
- Validador puro y sin side effects.
- Registry runtime para buscar por id, dominio, surface y módulo.
- Manifest canónico con 14 capabilities PC/Tablet.
- Catálogo de eventos runtime conectado a `SHARED_SYNC_EVENTS`.
- Bridges de composición para PC y Tablet.
- Validador Python semántico ligero.
- Documentación de contrato, smoke e integración.

## Modos del instalador

```powershell
py install_prisma_twin_runtime_kernel.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --smoke
py install_prisma_twin_runtime_kernel.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --dry-run
py install_prisma_twin_runtime_kernel.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --apply
py install_prisma_twin_runtime_kernel.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --verify
py install_prisma_twin_runtime_kernel.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --rollback
```

## Nota operativa

La entrega no modifica `package.json`, no instala dependencias y no toca pantallas existentes. Esto es deliberado: primero se instala columna vertebral, después se enchufan pantallas. Andar al revés es construir segundo piso sobre puesto de lámina.
