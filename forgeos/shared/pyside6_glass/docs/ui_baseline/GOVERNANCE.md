# Gobernanza

## Prohibido

- Resolver tokens finales dentro de `ui_baseline`.
- Hacer bypass del runtime oficial.
- Convertir `runtime.py` en framework visual.
- Mezclar generator, validador y runtime.
- Generar screens sin intención visual mínima.

## Aceptación

Una screen o herramienta nueva debe:

- respetar la cadena oficial,
- declarar intención explícita,
- evitar `setStyleSheet(...)` como autoridad final,
- pasar revisión humana,
- producir código mantenible.

## Validación recomendada

```bash
python -m forgeos.shared.pyside6_glass.tools.ui_baseline.validate_ui_baseline ./ruta
```

## Pregunta de control

Si una persona quita el core visual y la screen “se sigue viendo bien” gracias
a estilos locales, ya te fuiste por el carril incorrecto.
