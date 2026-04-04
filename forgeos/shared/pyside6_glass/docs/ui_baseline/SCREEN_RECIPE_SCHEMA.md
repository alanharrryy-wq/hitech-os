# ScreenRecipe schema

## Campos

- `screen_name`: nombre lógico del screen.
- `class_name`: nombre opcional de clase.
- `output_dir`: directorio de salida.
- `preset`: preset base.
- `visual_level`: nivel visual solicitado.
- `visual_role`: rol de pantalla.
- `visual_variant`: variante semántica.
- `visual_emphasis`: nivel de énfasis.
- `visual_fx_level`: nivel de FX.
- `data_state`: estado de data.
- `include_hero`
- `include_main`
- `include_side`
- `include_footer`
- `include_status`
- `ingredients: list[str]`

## Reglas prácticas

- Si `class_name` viene vacío, se deriva desde `screen_name`.
- Si una zona está desactivada, el generator la marca con `enable_* = False`.
- Si una zona activa no tiene ingredientes, el generator deja un placeholder limpio para revisión humana.
- Los ingredientes se agrupan por `suggested_zone`.
- El generator nunca debe inyectar estilo final.

## Ejemplo

```python
ScreenRecipe(
    screen_name="customers_dashboard",
    output_dir="./screens",
    preset="glass-default",
    visual_level="premium",
    visual_role="dashboard",
    visual_variant="data-heavy",
    visual_emphasis="high",
    visual_fx_level="subtle",
    data_state="ready",
    ingredients=["hero_header", "summary_cards", "table_panel", "inspector_panel"],
)
```
