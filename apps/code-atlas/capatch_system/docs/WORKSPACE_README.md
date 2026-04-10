# Capatch workspace

Este workspace centraliza el sistema de capatch fuera de Descargas para trabajar ya desde code-atlas.

## Estructura
- `capatch.py`: runtime principal
- `capatch_plugins/active`: plugins activos que carga capatch
- `capatch_plugins/templates`: plantillas base
- `capatch_plugins/disabled`: reserva manual
- `capatch_plugins/quarantine`: cuarentena manual
- `capatch_plugins/archive`: historicos/manual
- `capatch_plugins/_logs`: logs por plugin
- `tooling/capatch_plugin_factory.py`: fabrica local de plugins
- `reports/`: reportes y logs del workspace
- `backups/`: respaldos previos a migraciones o cambios grandes

## Comandos utiles
```powershell
py -3 "apps/code-atlas/capatch_system/capatch.py" --plugin-health
py -3 "apps/code-atlas/capatch_system/capatch.py" --plugin-list
py -3 "apps/code-atlas/capatch_system/tooling/capatch_plugin_factory.py" --interactive --run-health-check
```
