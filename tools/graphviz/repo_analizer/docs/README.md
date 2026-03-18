# Repo Analyzer Qt Connected

Esta versión ya **conecta el shell Qt al backend real** de indexado, búsqueda, preview, imports, dependents, quick filters, dropdown dinámico de extensiones y exportación.

## Estructura

- `app/backend/analyzer_backend.py`: lógica real reutilizable de indexado/búsqueda/preview/export.
- `app/gui_qt/main_window.py`: GUI GitKraken-ish conectada al backend.
- `app/gui_qt/skins.py`: skins enchufables.
- `app/gui_qt/widgets.py`: cards, botones y detalles visuales.
- `app/gui_qt/effects.py`: sombras/fade.
- `app/gui_qt/workers.py`: workers en QThread.

## Run

```powershell
pip install -r requirements.txt
python main.py
```

## Overlay sobre tu repo

Copia el contenido respetando rutas dentro de:

```text
F:epos\hitech-os	ools\graphvizepo_analizer
```

## Qué ya quedó conectado

- indexado real
- quick filters dinámicos
- filtro completo de carpetas
- filtro de extensiones dinámico
- búsqueda real con regex / case / whole word / names only
- preview real con line numbers
- imports/dependents reales
- export a csv/json/txt
- bookmarks por repo
- persistencia de layout por Qt + settings del analyzer
