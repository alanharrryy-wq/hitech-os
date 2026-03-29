# Rollout pipeline

## Flujo nominal
1. crear workspace shadow desde una fuente
2. aplicar overlay candidate
3. generar diff manifest
4. evaluar gate de promoción
5. emitir review bundle
6. calcular readiness de cutover
7. construir execution bundle
8. ejecutar solo con confirm token explícito

## Modo plan-only
El helper `run_rollout_pipeline_plan_only()` corre la historia completa sin tocar el target.
