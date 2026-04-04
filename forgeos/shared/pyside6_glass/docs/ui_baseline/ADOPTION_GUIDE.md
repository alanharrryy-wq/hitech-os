# Adoption guide

## Objetivo

Adoptar `ui_baseline` en un repo existente sin crear una segunda constitución visual.

## Plan sugerido

### Fase 1
- Identifica screens candidatas.
- Clasifícalas por rol y densidad de datos.
- Detecta `setStyleSheet(...)` locales.

### Fase 2
- Sustituye screens nuevas por `VisualScreenTemplate`.
- Declara intención mínima.
- Deja el runtime oficial como punto de entrada.

### Fase 3
- Migra screens existentes por lotes.
- Usa el generator solo como scaffold inicial.
- Corre el validador en CI o pre-merge.

### Fase 4
- Endurece gobernanza.
- Rechaza bypass de `AppearanceCoordinator`.
- Documenta patrones aprobados.

## Consejo operativo

No intentes migrar todo de golpe con un “gran refactor heroico”.
Mejor una fila disciplinada de cambios pequeños que una estampida con humo y confeti.
