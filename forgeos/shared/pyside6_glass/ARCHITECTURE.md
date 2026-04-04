# Arquitectura

## Tesis

`ui_baseline` es una capa de adaptación. No es una fuente de autoridad visual.
Su trabajo consiste en traducir intención declarativa de pantalla hacia el
runtime oficial del core.

## Flujo obligatorio

1. `VisualScreenTemplate` levanta intención desde atributos semánticos.
2. Se materializa `UIBaselineIntent`.
3. Se normaliza con defaults seguros y alias de compatibilidad.
4. Se traduce a `VisualIntelligenceContext`.
5. Se invoca `create_visual_runtime(...)`.
6. El core coordina apariencia, tokens y surfaces.
7. El runtime oficial gobierna la superficie final.

## Separación de capas

- `intent.py`: contrato semántico inmutable.
- `defaults.py`: normalización y sanitización.
- `context_adapter.py`: traducción robusta a contexto visual.
- `runtime.py`: adapter/factory del runtime oficial.
- `screen_template.py`: shell estructural con zonas.
- `builder/*`: recipe, catálogo, preview y generator.
- `tools/*`: CLI, builder UI y validación heurística.

## Límites explícitos

`ui_baseline` sí hace:

- declarar intención semántica,
- normalizar vocabulario,
- traducir a contexto visual,
- invocar el runtime oficial,
- montar contenido en zonas.

`ui_baseline` no hace:

- decidir tokens finales,
- renderizar charts como autoridad visual,
- sustituir al `AppearanceCoordinator`,
- resolver apariencia final por su cuenta,
- mezclar builder, validator y runtime.

## Consecuencia práctica

Si cambia la estrategia del core, el punto de ajuste debe estar en el runtime
oficial y, a lo mucho, en el adapter. Las screens no deben convertirse en un
jardín de excepciones con luces de neón por cuenta propia.
