# DeltaForge · Import and Packaging Dependency Map 1:1

## Objetivo

Blindar la parte menos glamorosa pero más traicionera del shell swap: imports, `sys.path`, entrypoints y contrato de empaquetado entre DeltaForge y `pyside6_glass`, para que la migración no termine en un “sí compila, pero no arranca”.

## Base observada

Rutas inspeccionadas:

- `deltaforge/deltaforge_app.py`
- `deltaforge/bootstrap/app_bootstrap.py`
- `deltaforge/ui/window/main_window.py`
- `deltaforge/ui/adapters/glass_framework_adapter.py`
- `deltaforge/ui/widgets/command_bar.py`
- `deltaforge/ui/widgets/session_tabs.py`
- `deltaforge/ui/widgets/session_workspace.py`
- `deltaforge/ui/widgets/bottom_results_tabs.py`
- `deltaforge/ui/theme/stylesheet.py`
- `deltaforge/ui/primitives/confirm_dialog.py`
- `deltaforge/ui/primitives/busy_dialog.py`
- `deltaforge/ui/dialogs/rollback_dialog.py`
- `shared/pyside6_glass/__init__.py`

---

## 1. Topología observada en el zip

## 1.1 DeltaForge

```text
deltaforge/
  deltaforge_app.py
  application/
  bootstrap/
  domain/
  infrastructure/
  ui/
```

## 1.2 Shared

```text
shared/
  pyside6_glass/
    __init__.py
    template.py
    runtime.py
    scene.py
    controls.py
    icons.py
    integration/
```

## 1.3 Import namespace esperado por DeltaForge

Aunque el zip de shared cae como `shared/pyside6_glass`, los imports observados dentro de DeltaForge esperan:

```python
from forgeos.shared.pyside6_glass ...
```

Eso significa que hoy existe una dependencia de namespace hacia una raíz de repo tipo `forgeos/...` que no viene “lista” solo por descomprimir ambos zips lado a lado.

---

## 2. Entry points actuales

## 2.1 `deltaforge_app.py`

### Comportamiento observado

- calcula `APP_ROOT = Path(__file__).resolve().parent`
- inserta `APP_ROOT` en `sys.path`
- importa `from bootstrap import run`

### Qué resuelve

Permite que módulos locales como:

- `application`
- `bootstrap`
- `domain`
- `infrastructure`
- `ui`

sean importables desde cualquier cwd.

### Qué NO resuelve

No garantiza que exista el namespace externo:

```python
forgeos.shared.pyside6_glass
```

---

## 2.2 `ui/window/main_window.py`

### Comportamiento observado

`main_window.py` hace un segundo truco de ruta:

- calcula `Path(__file__).resolve().parents[4]`
- inserta ese repo root en `sys.path`

Y luego importa:

```python
from forgeos.shared.pyside6_glass.scene import build_glass_dialog_scene
```

### Implicación

El arranque actual depende de que `parents[4]` apunte a un root donde exista:

```text
forgeos/shared/pyside6_glass/
```

Si esa topología no existe, truena con `ModuleNotFoundError: No module named 'forgeos'`.

---

## 3. Mapa actual de imports hacia shared

## 3.1 Imports directos observados en DeltaForge

| Archivo DeltaForge | Import externo observado | Propósito |
| --- | --- | --- |
| `ui/window/main_window.py` | `forgeos.shared.pyside6_glass.scene` | backdrop / dialog scene |
| `ui/adapters/glass_framework_adapter.py` | `forgeos.shared.pyside6_glass` | config, icon packs, template config |
| `ui/widgets/command_bar.py` | `forgeos.shared.pyside6_glass.controls` | `create_button` |
| `ui/widgets/session_tabs.py` | `forgeos.shared.pyside6_glass.icons` | `apply_icon` |
| `ui/widgets/session_workspace.py` | `forgeos.shared.pyside6_glass.template` | `GlassWorkspaceTabs`, `GlassWorkspaceTabSpec` |
| `ui/widgets/bottom_results_tabs.py` | `forgeos.shared.pyside6_glass.template` | tabs de resultados |
| `ui/theme/stylesheet.py` | `forgeos.shared.pyside6_glass.theme` | theme integration |
| `ui/primitives/confirm_dialog.py` | `forgeos.shared.pyside6_glass.scene` | scene wrapper |
| `ui/primitives/busy_dialog.py` | `forgeos.shared.pyside6_glass.scene` | scene wrapper |
| `ui/dialogs/rollback_dialog.py` | `forgeos.shared.pyside6_glass.scene` | dialog scene |

## 3.2 Lectura de riesgo

DeltaForge ya está acoplado a shared en:

- escena
- botones
- iconos
- tabs
- theme

La migración de shell no introduce esa dependencia desde cero. Lo que sí hace es **volverla estructuralmente más visible**.

---

## 4. Dependency graph mínimo del arranque

```text
deltaforge_app.py
  -> bootstrap.run()
    -> bootstrap.app_bootstrap
      -> ui.window.main_window.DeltaForgeMainWindow
        -> ui.adapters.glass_framework_adapter
          -> forgeos.shared.pyside6_glass
        -> ui.widgets.command_bar
          -> forgeos.shared.pyside6_glass.controls
        -> ui.widgets.session_tabs
          -> forgeos.shared.pyside6_glass.icons
        -> ui.widgets.session_workspace
          -> forgeos.shared.pyside6_glass.template
```

## Regla crítica

Si la nueva shell vive en `ui/window/glass_main_window.py`, **no debe empeorar** este grafo metiendo imports cruzados al core. La dependencia nueva tiene que ser:

```text
ui.window.glass_main_window
  -> ui.adapters.glass_projection_adapter
  -> ui.window.interop
  -> forgeos.shared.pyside6_glass.template/runtime
  -> widgets DeltaForge reutilizados
```

Y no:

```text
forgeos.shared.pyside6_glass.*
  -> application.*
  -> domain.*
```

---

## 5. Contrato de packaging recomendado

## 5.1 Contrato final deseado

Debe existir un root importable donde estas rutas sean válidas simultáneamente:

```text
<repo_root>/deltaforge/
<repo_root>/forgeos/shared/pyside6_glass/
```

O bien, en forma de paquete instalable equivalente, de modo que Python pueda resolver:

- `bootstrap`, `application`, `domain`, `infrastructure`, `ui` desde DeltaForge
- `forgeos.shared.pyside6_glass` desde shared

## 5.2 Recomendación operativa

Para una migración segura, elegir **una sola** estrategia y no mezclar:

### Estrategia canónica recomendada

- mantener `deltaforge_app.py` como entry point local del app
- mantener `APP_ROOT` en `sys.path` para paquetes locales de DeltaForge
- garantizar además que el repo root que contiene `forgeos/` esté en `sys.path` antes de levantar la UI
- mover el truco de path a un sitio más explícito y único durante la limpieza final **INFERRED**

> Lo de “sitio más explícito y único” es **INFERRED** porque hoy el sistema usa dos inyecciones de path: una en `deltaforge_app.py` y otra en `main_window.py`.

---

## 6. Mapa 1:1 de responsabilidades de import

| Capa | Qué importa hoy | Qué debe importar tras shell swap | Qué no debe importar |
| --- | --- | --- | --- |
| `deltaforge_app.py` | `bootstrap.run` | igual | `forgeos.shared.*` directo |
| `bootstrap/app_bootstrap.py` | controller, facade, theme, `ui.window.main_window` | controller, facade, theme, `ui.window.glass_main_window` o shim | `forgeos.shared.integration.*` |
| `ui/window/main_window.py` o shim | widgets + adapter + shared scene | shell nueva + adapter + runtime/template shared | `application.session_actions` directo |
| `ui/adapters/glass_projection_adapter.py` | `ui.window.interop` **y/o** shapes del facade | igual | `SessionManager` o `SessionActions` directos |
| `forgeos.shared.pyside6_glass.*` | internals shared | internals shared | imports a DeltaForge core |

---

## 7. Riesgos concretos de packaging

## Riesgo A. Namespace fantasma `forgeos`

### Síntoma

```text
ModuleNotFoundError: No module named 'forgeos'
```

### Causa

El root efectivo de Python no contiene el árbol `forgeos/shared/pyside6_glass` esperado por los imports.

### Contención

Validar el contrato de repo root **antes** del shell swap funcional.

---

## Riesgo B. Doble inyección de `sys.path`

### Síntoma

La app arranca en un entorno, pero en otro toma una raíz distinta y los imports se vuelven caprichosos.

### Causa

- `deltaforge_app.py` inyecta `APP_ROOT`
- `main_window.py` inyecta `parents[4]`

### Contención

Consolidar la estrategia de path una vez que la shell nueva sea canónica.

---

## Riesgo C. Shell nueva introduce imports al core desde shared

### Síntoma

El framework visual empieza a conocer `SessionManager`, `SessionActions` o `domain/*`.

### Contención

Toda dependencia hacia el core pasa por:

- `WorkspaceFacadeBridge`
- `ControllerBridge`
- adapter DeltaForge

Nunca desde `pyside6_glass` puro.

---

## Riesgo D. Archivo shim mal resuelto

### Síntoma

`bootstrap/app_bootstrap.py` sigue importando `ui.window.main_window`, pero el shim nuevo no reexporta bien `DeltaForgeMainWindow` y `WindowBindings`.

### Contención

Mantener contrato 1:1 en el shim:

```python
from .glass_main_window import DeltaForgeGlassMainWindow as DeltaForgeMainWindow
from .glass_main_window import WindowBindings
```

---

## 8. Plan 1:1 de saneamiento de imports

## Fase 1. Antes de migrar shell

- inventariar todos los imports `forgeos.shared.pyside6_glass.*`
- confirmar topología real del repo de integración
- validar que el arranque actual es reproducible

## Fase 2. Durante shell swap

- crear `ui/window/glass_main_window.py`
- mantener `ui/window/main_window.py` como shim
- mover el wiring nuevo ahí sin alterar imports del core

## Fase 3. Después de paridad

- reducir hacks de path duplicados
- centralizar resolución del repo root **INFERRED**
- dejar un solo contrato de arranque limpio

---

## 9. Checklist de verificación de arranque

### Arranque local
- `deltaforge_app.py` encuentra `bootstrap.run`
- `bootstrap.run()` construye app y ventana
- la shell nueva importa `forgeos.shared.pyside6_glass.template/runtime`
- no aparece `ModuleNotFoundError` por `forgeos`

### Arranque de UI
- se registran icon packs de DeltaForge
- `build_deltaforge_template_config()` se resuelve
- se crea el `GlassPanelTemplate`
- se crea el `GlassWorkspaceRuntime`
- se pintan tabs y paneles sin fallas de import

### No-regresión de imports
- `application/*`, `domain/*`, `infrastructure/*` no importan shared
- `shared/pyside6_glass/*` no importa core DeltaForge
- `ui/adapters/*` es la frontera de acoplamiento

---

## 10. Criterios de aceptación

- existe una topología de imports reproducible para DeltaForge + shared
- `main_window.py` puede volverse shim sin romper `bootstrap/app_bootstrap.py`
- la shell nueva no añade dependencia invertida hacia el core
- el crash de namespace `forgeos` queda contenido como problema de packaging y no de lógica
- la estrategia final de `sys.path` queda unificada o al menos explícitamente documentada

---

## 11. Definition of done de este documento

Este mapa queda completo cuando el shell swap puede ejecutarse en un repo integrado real sin hacks ocultos, con contrato de imports verificable, con un único entrypoint canónico y sin dependencia circular entre framework visual y motor de DeltaForge.
