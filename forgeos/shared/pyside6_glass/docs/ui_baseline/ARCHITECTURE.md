# Arquitectura de ui_baseline

## Idea base

La screen describe intención. El core decide cómo se ve y cómo se comporta la
superficie final.

## Pipeline

1. `VisualScreenTemplate` levanta intención desde atributos de clase.
2. `UIBaselineIntent` expresa el contrato mínimo.
3. `normalize_intent(...)` sanea valores y colapsa alias heredados.
4. `intent_to_visual_context(...)` construye `VisualIntelligenceContext`.
5. `create_visual_runtime(...)` se invoca desde `runtime.py`.
6. `AppearanceCoordinator`, `resolve_appearance_tokens(...)` y `GlassWorkspaceRuntime`
   gobiernan la capa final.

## Decisiones arquitectónicas

- El fallback existe solo para conservar contrato y habilitar bootstrapping.
- El fallback no resuelve estilo final.
- El builder genera código legible y editable.
- El validador protege límites de gobernanza.

## Riesgo que se evita

Sin esta separación, cada pantalla empieza a cargar reglas visuales locales.
Al principio parece práctico. Luego el repo termina sonando como cinco bandas
tocando en cuartos distintos con la puerta abierta.
