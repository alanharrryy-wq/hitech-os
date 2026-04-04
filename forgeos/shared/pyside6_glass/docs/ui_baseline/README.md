# ui_baseline

## Qué es

`ui_baseline` es una capa de adaptación para pantallas PySide6 gobernadas por
contrato. Su misión es declarar intención semántica, traducirla a
`VisualIntelligenceContext` e invocar el runtime oficial.

## Qué no es

- No es un sistema de temas.
- No es un reemplazo del `AppearanceCoordinator`.
- No es un builder con autoridad visual final.
- No es un mini framework de render.

## Flujo obligatorio

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

## Vocabulario canónico

- `visual_level`: `performance`, `standard`, `premium`, `showcase`
- `visual_fx_level`: `off`, `subtle`, `standard`, `rich`
- `visual_emphasis`: `low`, `medium`, `high`

Alias heredados aceptados solo en normalización:

- `balanced -> medium`
- `minimal -> performance`
- `rich -> premium` cuando venga como `visual_level`
- `none -> off`
- `enhanced -> rich`
- `standard -> default` cuando venga como `visual_variant`

## Uso rápido

1. Hereda de `VisualScreenTemplate`.
2. Declara `visual_role`, `visual_variant`, `visual_emphasis` y `visual_fx_level`.
3. Construye contenido en `build_hero`, `build_main`, `build_side`, `build_footer` y `build_status`.
4. Deja que `runtime.py` traduzca e invoque el runtime oficial.
5. Usa el validador antes de mergear.
