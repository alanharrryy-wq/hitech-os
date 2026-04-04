# DeltaForge · Import Rules

## Reglas por capa

| Capa | Puede importar | Prohibido |
|---|---|---|
| `domain/*` | stdlib, `typing`, `dataclasses`, `enum`, `hashlib`, `datetime`, `domain.*` | `application.*`, `infrastructure.*`, `ui.*`, `PySide6.*` |
| `application/contracts/*` | stdlib, `typing.Protocol`, `domain.*` | `ui.*`, `PySide6.*`, infraestructura concreta |
| `application/*` core | stdlib, `domain.*`, `application.contracts.*` | `ui.*`, `infrastructure.*`, `PySide6.*` |
| `application/controllers/*` | `application.*`, `domain.*` | `PySide6.*`, adapters concretos, watchers concretos |
| `infrastructure/*` | stdlib, `application.contracts.*`, `domain.*` | `ui.*` |
| `ui/theme/*` | stdlib, `ui.theme.*` | `application/*`, `infrastructure/*`, `domain/*` de negocio |
| `ui/primitives/*` | `PySide6.*`, `ui.theme.*` | `infrastructure/*` |
| `ui/panes/*` | `PySide6.*`, `application.workspace_facade`, controladores, `domain.*` solo lectura, primitives/widgets | `infrastructure/*` directo |
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
rg "from ui" F:\repos\hitech-os\apps\deltaforge\domain
rg "from infrastructure" F:\repos\hitech-os\apps\deltaforge\application
rg "from ui" F:\repos\hitech-os\apps\deltaforge\infrastructure
```
