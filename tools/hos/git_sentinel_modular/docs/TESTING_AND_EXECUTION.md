# Testing and execution

## Smoke recomendado
```powershell
python -m tools.hos.git_sentinel_modular --help
python -m pytest tools/hos/git_sentinel_modular/tests/sentinel_shadow `
  tools/hos/git_sentinel_modular/tests/sentinel_shadow_apply `
  tools/hos/git_sentinel_modular/tests/sentinel_supervisor `
  tools/hos/git_sentinel_modular/tests/sentinel_observability `
  tools/hos/git_sentinel_modular/tests/integration/test_rollout_pipeline_plan_only.py -q
```

## Validación de pipeline
```powershell
python -m tools.hos.git_sentinel_modular pipeline-plan-only --run-id demo --source-root <src> --target-root <target>
```

## Ejecución real
Solo usar `execute-run` con `--confirm-token EXECUTE_MANUAL_PROMOTION`.
