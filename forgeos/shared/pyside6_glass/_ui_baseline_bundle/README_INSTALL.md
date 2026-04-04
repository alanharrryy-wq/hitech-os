# Instalación y uso

## 1. Desempaquetar

```bash
unzip ui_baseline_governed_pyside6_bundle_rematado.zip -d ./destino
```

## 2. Copiar a tu repo

Copia estas rutas en tu árbol del proyecto:

- `forgeos/shared/pyside6_glass/`
- `README_INSTALL.md`
- `MANIFEST.txt`

## 3. Dependencias mínimas

- Python 3.10 o superior
- PySide6
- Runtime oficial del core con `create_visual_runtime(...)` cuando se use integración real

Instalación rápida:

```bash
pip install PySide6
```

## 4. Cómo correr

### Builder UI

```bash
python -m forgeos.shared.pyside6_glass.tools.ui_baseline.ui_baseline_builder
```

### Generator CLI

```bash
python -m forgeos.shared.pyside6_glass.tools.ui_baseline.new_ui_screen customers_dashboard \
  --output-dir ./screens \
  --role dashboard \
  --variant data-heavy \
  --emphasis high \
  --fx subtle \
  --visual-level premium \
  --ingredient hero_header \
  --ingredient summary_cards \
  --ingredient table_panel
```

### Validator

```bash
python -m forgeos.shared.pyside6_glass.tools.ui_baseline.validate_ui_baseline ./screens
```

### Ejemplo runnable

```bash
python -m forgeos.shared.pyside6_glass.examples.ui_baseline_customers_dashboard
```

## 5. Vocabulario canónico

- `visual_level`: `performance`, `standard`, `premium`, `showcase`
- `visual_fx_level`: `off`, `subtle`, `standard`, `rich`
- `visual_emphasis`: `low`, `medium`, `high`

Alias heredados aceptados solo durante normalización para compatibilidad.

## 6. Notas operativas

- El fallback de runtime no reemplaza al core.
- El generator crea scaffold editable sin estilo final incrustado.
- El validador es heurístico; no sustituye revisión humana.
