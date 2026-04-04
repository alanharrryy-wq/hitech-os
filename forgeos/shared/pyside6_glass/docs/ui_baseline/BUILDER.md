# Builder

El builder de `ui_baseline` sirve para definir una receta de pantalla y generar
un scaffold gobernado. No diseña la apariencia final.

## Piezas

- `ScreenRecipe`: contrato de entrada.
- `catalog.py`: ingredientes disponibles.
- `generator.py`: emite el archivo `.py`.
- `preview.py`: resume receta y resultado esperado.
- `ui_baseline_builder.py`: interfaz PySide6 para operar el flujo.

## Valores canónicos en la UI

- `visual_level`: `performance`, `standard`, `premium`, `showcase`
- `visual_variant`: `default`, `data-heavy`, `analysis`, `focused`, `compact`
- `visual_emphasis`: `low`, `medium`, `high`
- `visual_fx_level`: `off`, `subtle`, `standard`, `rich`

## Flujo

1. Define nombre de screen y clase.
2. Selecciona preset e intención visual.
3. Marca zonas activas.
4. Elige ingredientes.
5. Ejecuta preview.
6. Genera.
7. Valida.

## Resultado

Se genera una clase derivada de `VisualScreenTemplate` con métodos `build_*`,
flags `enable_*` y placeholders limpios por zona activa.
