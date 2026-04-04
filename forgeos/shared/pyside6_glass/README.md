# pyside6_glass

`pyside6_glass` reúne contratos, adapters y tooling para construir pantallas
PySide6 sin abrir una autoridad visual paralela dentro del repositorio.

La regla central es simple:

**la pantalla declara intención; el core decide la apariencia final.**

## Cadena obligatoria

```text
VisualScreenTemplate
-> UIBaselineIntent
-> VisualIntelligenceContext
-> create_visual_runtime(...)
-> AppearanceCoordinator
-> resolve_appearance_tokens(...)
-> GlassWorkspaceRuntime
-> renderers/surfaces
```

## Qué incluye

- `ui_baseline/`: adapter semántico y shell gobernado.
- `tools/ui_baseline/`: generator CLI, builder UI y validador.
- `examples/`: ejemplo runnable.
- `docs/`: documentación canónica para adopción.

## Qué no hace

- No define tokens finales.
- No sustituye al `AppearanceCoordinator`.
- No decide la estética final con `setStyleSheet(...)`.
- No convierte `runtime.py` en mini framework visual.

## Vocabulario canónico

- `visual_level`: `performance`, `standard`, `premium`, `showcase`
- `visual_fx_level`: `off`, `subtle`, `standard`, `rich`
- `visual_emphasis`: `low`, `medium`, `high`

Los alias viejos se aceptan solo durante normalización para no romper adopción.
