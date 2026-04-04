# Reemplazo modular de `template.py`

Este paquete divide el archivo original en módulos pequeños y mantiene `template.py`
como fachada compatible para no romper imports existentes.

## Archivos incluidos

- `template.py` -> fachada compatible
- `_template_helpers.py`
- `_template_specs.py`
- `_template_tabs.py`
- `_template_panels.py`
- `_template_layout.py`
- `_template_shell.py`
- `_template_shell_build.py`
- `_template_shell_appearance.py`
- `_template_shell_workspace.py`
- `_template_shell_state.py`

## Cómo usarlo

1. Abre la carpeta donde hoy vive tu `template.py` original.
2. Descomprime **todo** el contenido de este `.zip` en esa misma carpeta.
3. Reemplaza archivos cuando te lo pida.
4. No cambies nombres de archivo.

## Mapa rápido

- Helpers y normalizaciones -> `_template_helpers.py`
- Specs/dataclasses -> `_template_specs.py`
- Tabs -> `_template_tabs.py`
- Panel frame -> `_template_panels.py`
- Layout + slot hosts + DTOs -> `_template_layout.py`
- Shell principal y constructor -> `_template_shell.py`
- Construcción visual base -> `_template_shell_build.py`
- Apariencia / theming / bindings -> `_template_shell_appearance.py`
- Tabs / panels / movimientos -> `_template_shell_workspace.py`
- Layout state / snapshot / restore -> `_template_shell_state.py`
- API pública compatible -> `template.py`
