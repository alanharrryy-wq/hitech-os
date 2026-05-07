# PRISMA Tablet VisionOS Glass Pass 02

## Objetivo
Elevar el shell visual de Tablet a un estilo glass tipo Apple / VisionOS, sin tocar navegación lógica, POS, rutas, APIs, DB ni sincronización.

## Cambios
- Sidebar más transparente con blur fuerte, highlights y profundidad óptica.
- Logo PRISMA flotante, sin tarjeta rectangular ni tinte amarillo.
- Grupos de navegación como etiquetas limpias, sin contadores visibles.
- Estados de grupo azul apagado cuando no están activos y glow neón suave cuando están activos.
- CTA **Vender** como glass azul líquido con motion sutil.
- Header superior con vidrio esmerilado y sin clipping del selector.
- Selector de apariencia sin doble óvalo.

## Archivos tocados
- `components/tablet-shell/prisma-tablet-shell.module.css`
- `components/ui/prisma-skin-selector.module.css`

## No toca
- POS / checkout / venta
- APIs / DB / sync
- PC
- shared-kernel
- rutas

## Validación visual esperada
- `http://127.0.0.1:3120/` debe mostrar sidebar más translúcido.
- El cuadro de venta guiada no debe verse.
- `Operación`, `Consulta rápida` y `Soporte` no deben mostrar números.
- El selector de apariencia debe verse como un control compacto, no como óvalo sobre óvalo.
- El logo debe verse integrado al fondo.
