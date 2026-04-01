# DeltaForge · Import Rules

## Reglas por capa

| Capa | Puede importar | Prohibido |
|---|---|---|
| `domain/*` | stdlib, `typing`, `dataclasses`, `enum`, `hashlib`, `datetime`, `deltaforge.domain.*` | `deltaforge.application.*`, `deltaforge.infrastructure.*`, `deltaforge.ui.*`, `PySide6.*` |
| `application/contracts/*` | stdlib, `typing.Protocol`, `deltaforge.domain.*` | `deltaforge.ui.*`, `PySide6.*`, infraestructura concreta |
| `application/*` core | stdlib, `deltaforge.domain.*`, `deltaforge.application.contracts.*` | `deltaforge.ui.*`, `deltaforge.infrastructure.*`, `PySide6.*` |
| `application/controllers/*` | `deltaforge.application.*`, `deltaforge.domain.*` | `PySide6.*`, adapters concretos, watchers concretos |
| `infrastructure/*` | stdlib, `deltaforge.application.contracts.*`, `deltaforge.domain.*` | `deltaforge.ui.*` |
| `ui/theme/*` | stdlib, `deltaforge.ui.theme.*` | `application/*`, `infrastructure/*`, `domain/*` de negocio |
| `ui/primitives/*` | `PySide6.*`, `deltaforge.ui.theme.*` | `infrastructure/*` |
| `ui/panes/*` | `PySide6.*`, `deltaforge.application.workspace_facade`, controladores, `deltaforge.domain.*` solo lectura, primitives/widgets | `infrastructure/*` directo |
| `ui/widgets/*` | `PySide6.*`, panes/primitives, facade readonly | reglas de negocio, engine directo |
| `bootstrap/*` | todas las capas solo para wiring | negocio, decisiones de estado |

## Reglas adicionales
- `main_window.py` integra, no decide negocio
- la UI no muta `SessionWorkspace` directo
- watcher no muta estado directo; emite eventos
- bus no guarda feed visible
- theme es la única fuente de color/variant
- legacy solo puede re-exportar o shimear, no añadir comportamiento nuevo

## Comandos de verificación sugeridos
```powershell
rg "from deltaforge\.ui" F:\repos\hitech-os\apps\deltaforge\deltaforge\domain
rg "from deltaforge\.infrastructure" F:\repos\hitech-os\apps\deltaforge\deltaforge\application
rg "from deltaforge\.ui" F:\repos\hitech-os\apps\deltaforge\deltaforge\infrastructure
```
