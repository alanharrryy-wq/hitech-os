# PRISMA PC Proveedores - Copy Hygiene 09.1

## Objetivo

Limpiar residuos de copy tecnico en los componentes visibles de Proveedores sin tocar motor, Tablet ni shared-kernel.

## Alcance

- `smart-purchase-workbench.tsx`
- `supplier-action-cockpit.tsx`
- verificador local de higiene de copy

## Resultado esperado

Los componentes de UI no contienen de forma literal tokens visibles como `blocked`, `safe`, `backoffice` o `ingest`.

Los valores tecnicos que vienen del dominio se siguen traduciendo en tiempo de ejecucion a lenguaje es-MX:

- Revisar antes
- Caja comoda
- Panel administrativo
- Recepcion de eventos

## Validacion

Ejecutar:

```powershell
node products\pc\app\tools\verify_pc_suppliers_copy_hygiene_09_1.mjs products\pc\app
```

Este paquete es correctivo y deliberadamente pequeno. No agrega persistencia ni cambia contratos.
