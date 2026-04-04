# Generator and validation

## Generator

El generator transforma una `ScreenRecipe` en un archivo Python editable con:

- clase derivada de `VisualScreenTemplate`,
- intención visual declarada,
- flags `enable_*`,
- métodos `build_*`,
- placeholders por ingrediente.

## Validator

El validador revisa de forma heurística:

- `setStyleSheet(...)` fuera de foundation permitida,
- uso crudo de `QMainWindow`, `QDialog` o `QWidget` como identidad final,
- pantallas `_screen.py` sin herencia compatible,
- ausencia de intención visual mínima,
- señales de bypass de coordinación visual.

## Flujo recomendado

```bash
python -m forgeos.shared.pyside6_glass.tools.ui_baseline.new_ui_screen customers_dashboard       --output-dir ./screens       --role dashboard       --variant data-heavy       --emphasis high       --fx subtle       --ingredient hero_header       --ingredient summary_cards       --ingredient table_panel

python -m forgeos.shared.pyside6_glass.tools.ui_baseline.validate_ui_baseline ./screens
```

## Resultado esperado

Scaffold útil, validación entendible y cero sistemas de estilo escondidos bajo la alfombra.
