# Next Steps

## Próximo upgrade recomendado

Crear motores Python en:

```txt
engines/python
```

Orden sugerido:

1. `governor_inventory_engine.py`
2. `route_budget_audit_engine.py`
3. `public_leak_sanitizer_engine.py`
4. `visual_regression_engine.py`
5. `recipe_compiler_engine.py`
6. `runtime_adapter_validator.py`

## Reglas

- Cada motor debe generar `receipt.json`.
- Cada motor debe generar ZIP de evidencia en `<OUTPUT_DIR>`.
- Cada motor debe ser idempotente.
- Cada motor debe correr desde cualquier directorio.
- Nada de fake green.
