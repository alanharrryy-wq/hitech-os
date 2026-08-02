# Contrato de autoridad

- `instruction_only=true`
- `direct_target_mutation=false`
- compatibilidad, binding, cobertura y readiness son estados independientes
- fingerprint sólo produce `CANDIDATE`
- los adaptadores nunca inventan owner, route, slot, component o layer
- importación y migración son read-only
- no se escribe producto, `dist`, RIFAT ni `.governance/current`
