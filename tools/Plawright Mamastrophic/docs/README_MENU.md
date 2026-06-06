# PRISMA Mamastrophic MENU fix1

Corrige el selector de fases del menú interactivo.

## Fix

Antes el menú mostraba:

- `5) quick,full  combo comun`
- `6) all         todas las fases`

pero `Resolve-Phases` no aceptaba `5` ni `6` cuando venían dentro de listas como `1,5`.

Ahora acepta:

- `5`
- `6`
- `1,5`
- `discovery,5`
- `quick_full`
- `quick+full`
- `all`

## Política

- GPU default: `off`.
- No start.
- No kill.
- No DB.
- No deploy.
- Sólo instala `MENU.ps1` y esta documentación.
