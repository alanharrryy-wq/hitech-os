# Migration map

## Cerrado en este bundle
- bootstrap de paquete y pytest namespace-aware
- contrato central de paths
- payloads homogéneos de estado
- plugin seam mínima
- control plane canónico en `operations`
- flujo plan-only `shadow -> promotion -> cutover -> execute`
- cobertura base para `sentinel_shadow`, `sentinel_shadow_apply`, `sentinel_supervisor` y `sentinel_observability`

## Deliberadamente fuera
- integración real con `engine_guardian`
- migraciones de Cloudflare o Keystone
- scheduled tasks
- runtime roots de otros sistemas
