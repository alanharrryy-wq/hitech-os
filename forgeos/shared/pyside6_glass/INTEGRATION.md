# INTEGRATION

## Inicialización recomendada

```python
from pyside6_glass.visual_runtime import create_visual_runtime

runtime = create_visual_runtime(template_config)
template = runtime.template
root = template.build()
```

## Binding explícito

```python
from pyside6_glass.appearance import AppearanceCoordinator

coordinator = AppearanceCoordinator.from_template_config(template_config)
template.bind_appearance_coordinator(coordinator)
```

## Declarar roles visuales en widgets custom

```python
from pyside6_glass.visual_contracts import set_visual_properties

set_visual_properties(
    card,
    role="metrics",
    variant="panel",
    emphasis="high",
    fx_level="rich",
)
```

## Backdrop

`FrostedGlassBackdrop` ya no necesita bridge Atlas externo para resolver su paleta. La API correcta es:

```python
backdrop.apply_appearance(snapshot)
```

o bien:

```python
backdrop.apply_appearance(profile=profile, effects=effects)
```

## Compatibilidad

- `theme.build_stylesheet_exact_atlas(...)` todavía funciona como shim delgado.
- `atlas_styles.build_app_stylesheet(...)` todavía existe.
- `atlas_theme_bridge.resolve_atlas_glass_palette(...)` todavía existe.

Pero esos caminos ya son frontera de compatibilidad, no centro del sistema.
La ruta productiva oficial de piel/materialización es `skin/*` vía `theme.build_stylesheet(...)`.
