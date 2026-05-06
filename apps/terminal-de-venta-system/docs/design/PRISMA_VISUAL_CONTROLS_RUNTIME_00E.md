# PRISMA Visual OS 00E - Visual Controls Runtime

El runtime usa un JSON activo y un generador determinista. La edición visual deja de ser tanteo de CSS a mano y pasa a ser control por perillas.

## Archivo activo

```text
config/prisma-visual-os/prisma-visual-controls.active.json
```

## CSS generado

```text
styles/prisma-visual-os/prisma-visual-controls.generated.css
```

## Validaciones

- preset permitido;
- superficie permitida;
- controles numéricos entre 0 y 100;
- diez layers presentes;
- combinaciones peligrosas bloqueadas.

## Uso

```powershell
cd F:epos\hitech-ospps	erminal-de-venta-system
node tools/prisma-visual-os/generate_prisma_visual_os_controls_00e.mjs
node tools/prisma-visual-os/verify_prisma_visual_os_core_00d_00e.mjs
```
