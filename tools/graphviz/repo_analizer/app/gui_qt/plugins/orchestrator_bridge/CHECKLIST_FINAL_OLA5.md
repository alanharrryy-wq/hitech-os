# Checklist final ola 5

- [x] Compatibilidad con host plugin manager
- [x] Package contiene `__init__.py`, `plugin.py`, `plugin.json`, `README.md`
- [x] `plugin.json` declara `module = "plugin"` y `class_name = "PluginImplementation"`
- [x] Registro seguro del host con `register_safe_dock`, `register_safe_toolbar_action`, `register_safe_menu_action`
- [x] Runner puente solamente, sin logica de motor
- [x] UI no bloqueante usando `QProcess`
- [x] Sin dependencias nuevas
- [x] Configurable paths y runtime root bajo `tools\_local`
- [x] Persistencia minima de ultimos N runs
- [x] Guardrails de input y path/config
- [x] Tests unitarios y de integracion ligera incluidos
- [x] Fixtures stdout/stderr incluidos
- [x] Guia Operator/Codex incluida
