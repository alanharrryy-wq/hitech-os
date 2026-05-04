# PRISMA Visual OS — 00R/00S Studio Pro + QA

## Propósito

Este paquete convierte el Live Studio en una consola pro separada, flotante y pop-out, con recetas, preset mixer, layer inspector, snapshots, score visual y publish gate.

## Superficies

- Tablet POS
- PC Backoffice
- Mobile Pulse

## Rutas instaladas

```text
/visual-os
/visual-os/detached
/visual-os/pro
/visual-os/realtime
```

## Filosofía

Preview vivo primero. Publicación después. QA siempre visible.

La consola puede verse de lujo, pero Tablet POS sigue siendo operación: contraste, touch target y claridad de cobro mandan sobre el ego visual.

## Modo realtime

Arrancar servidor local:

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system
node tools\prisma-visual-os\live-preview-server-00q.mjs --port 4177
```

Luego abrir:

```text
http://127.0.0.1:3120/visual-os
http://127.0.0.1:3120/visual-os/realtime
```

## Publish gate

El gate bloquea publicación si:

- contraste y blur vuelven ilegible la UI;
- densidad Tablet queda debajo de umbral táctil;
- score de seguridad cae demasiado;
- operación POS queda comprometida.

## Archivos dueños

Este paquete puede reemplazar sus rutas propias con `--force-reset-owned`, siempre con backup previo y rollback automático si falla verificación.
