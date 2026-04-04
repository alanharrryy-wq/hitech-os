# CLEANUP MIGRATION FINAL

## Qué queda vivo

- `theme.py`
- `appearance/`
- `template.py`
- `runtime.py`
- `visual_runtime.py`
- `effects.py`
- `rendering/`
- `backdrop.py`
- `visual_contracts.py`
- `legacy_cleanup.py`

## Qué sobrevive solo como shim

- `atlas_styles.py`
- `atlas_theme_bridge.py`

## Qué debe desaparecer del repo aplicado

- caches de pytest
- `__pycache__`
- respaldos `*.bak_silver_case`

## Regla operativa para cambios futuros

1. Si el cambio es de color o paleta, tocar `theme.py`.
2. Si el cambio es de escala, blur, glow, opacidad o densidad, tocar `appearance/`.
3. Si el cambio es de wiring, tocar `runtime.py`, `visual_runtime.py` o `template.py`.
4. Si el cambio es de superficie premium, tocar `rendering/` o `effects.py`.
5. Si el cambio es de semántica visual de widgets, tocar `visual_contracts.py`.
6. No agregar nuevos bridges visuales legacy.
