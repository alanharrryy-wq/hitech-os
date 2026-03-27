# Arquitectura vigente

## Dueño canónico
`operations/` es la fachada interna canónica del paquete. No reemplaza la lógica de dominio ya existente, pero sí concentra las preguntas de runtime, supervisión, observabilidad y estado combinado.

## Contratos nuevos
- `shared/runtime_paths.py`: única verdad de rutas, runtime y salidas
- `shared/status_payloads.py`: payloads canónicos para estado, supervisor, scheduler y health summary
- `plugins/`: seam mínima para integraciones externas futuras

## Pipeline canónico
1. `sentinel_shadow.prepare_shadow_run`
2. `sentinel_shadow_apply.run_shadow_apply_engine`
3. `sentinel_promotion.build_promotion_bundle`
4. `sentinel_cutover.build_cutover_readiness_bundle`
5. `sentinel_execute.build_execution_bundle`
6. `sentinel_execute.execute_manual_promotion`

## Frontera explícita
`engine_guardian` queda fuera del paquete. Aquí solo existe el seam de plugins y la superficie limpia para conectarlo después.
