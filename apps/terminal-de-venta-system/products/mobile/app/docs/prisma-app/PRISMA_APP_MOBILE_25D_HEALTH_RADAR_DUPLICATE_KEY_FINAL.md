# PRISMA App Mobile 25D - Health Radar duplicate key final

## Objetivo
Cerrar el warning de React/Next:

`Encountered two children with the same key, tablet: OK`

## Causa real
El Radar de Salud imprimía evidencias provenientes de fuentes móviles. Cuando dos probes regresaban el mismo texto visible, por ejemplo `tablet: OK`, React podía recibir la misma llave para hermanos del mismo `<ul>`.

Eso no rompe TypeScript, pero sí rompe identidad visual de React. Es como ponerle la misma placa a tres motonetas del mercado: todas existen, pero el tránsito ya no sabe cuál multar.

## Corrección
- `PrismaMobileHealthRadar.tsx` conserva llaves estables con `scope + index + valor normalizado`.
- El caso duplicado `tablet: OK` ya genera llaves distintas.
- El verificador 25D ya no depende del corpus faltante de 25C.
- Se agrega corpus nuevo de regresión con más de 6000 vectores de evidencia duplicada.
- El instalador limpia `.next` después de aplicar para evitar que Turbopack sirva una versión vieja.

## Alcance
Solo App móvil.

No toca:
- Tablet POS
- PC Backoffice
- `shared-kernel`
- contratos compartidos

## Validación esperada
Desde `F:epos\hitech-ospps	erminal-de-venta-system\products\mobilepp`:

```powershell
pnpm run verify:health-radar
pnpm run typecheck
```

Luego reiniciar el dev server móvil.
