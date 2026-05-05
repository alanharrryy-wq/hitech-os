# PC Twin Runtime Kernel

La app PC consume `pcTwinCapabilityRegistry`, `pcTwinCapabilities`, `pcTwinCapabilityScorecard` y `pcModuleTwinReadiness` desde `src/composition/twin-capabilities.ts`.

La regla es simple: PC no necesita parecer tablet. PC necesita saber qué ejecuta tablet, qué observa PC y dónde vive la verdad canónica.

## Uso esperado

- Dashboards: usar `pcTwinCapabilityScorecard` para mostrar paridad de dominios.
- Módulos: usar `pcModuleTwinReadiness` para detectar capabilities por módulo.
- Auditoría: resolver capability por `id` antes de aceptar eventos nuevos.

## Gate mínimo

Una pantalla PC nueva que refleje operación tablet debe declarar capability o enlazarse a una existente. Sin eso, se rechaza el cambio.
