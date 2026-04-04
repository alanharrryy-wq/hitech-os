# Gobernanza visual

## Regla madre

La autoridad visual final vive en el core. `ui_baseline` no compite con eso.

## Prohibiciones

- Crear tokens finales dentro de `ui_baseline`.
- Aplicar `setStyleSheet(...)` como decisión visual principal.
- Resolver apariencia final en `runtime.py`.
- Invocar `AppearanceCoordinator` o `resolve_appearance_tokens(...)` desde screens.
- Introducir un stack visual paralelo mediante tooling o ejemplos.

## Criterio de aceptación

Una contribución se acepta cuando:

1. declara intención semántica explícita,
2. conserva separación de capas,
3. usa el runtime oficial o fallback explícito sin autoridad visual,
4. no agrega un sistema local de temas,
5. pasa validación heurística y revisión humana.

## Release gate recomendado

- Ejecutar el validador heurístico.
- Confirmar que las screens heredan de `VisualScreenTemplate` o `GlassPanelTemplate`.
- Confirmar presencia de `visual_role`, `visual_variant`, `visual_emphasis` y `visual_fx_level`.
- Confirmar ausencia de bypass de `AppearanceCoordinator` y token resolution.
- Confirmar que dashboards y charts operan como truth surfaces del dominio, no como motores de estilo.

## Señales de alarma

- “Solo metí un stylesheet rápido”.
- “La screen llama el runtime directamente porque era más fácil”.
- “El builder ya sabe qué theme final debe aplicar”.
- “El fallback se ve suficientemente bien como para dejarlo así”.

Ese camino parece práctico un rato y luego cobra intereses como tarjeta mal pagada.
