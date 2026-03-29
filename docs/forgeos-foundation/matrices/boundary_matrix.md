# boundary_matrix.md

Matriz de fronteras permitidas/prohibidas entre capas.

| Desde | Hacia | Permitido | Mecanismo | Comentario |
| --- | --- | --- | --- | --- |
| Forge Kernel | Forge Kernel | Sí | APIs internas del kernel | La implementación interna puede acoplarse solo al kernel. |
| Forge Kernel | Forge Commons | Sí, pero solo vía interfaces/contratos de capability | Service contracts declarados | Sin importar módulos product-specific ni semántica de capability. |
| Forge Kernel | Forge Products | No directo | Solo discovery, manifests y lifecycle contracts | El kernel no importa lógica de dominio del producto. |
| Forge Commons | Forge Kernel | Sí | Kernel contracts y abstracciones públicas | Nunca por internals privados. |
| Forge Commons | Forge Commons | Sí, con declaración explícita | Service contracts versionados | Evitar cadenas de dependencias largas. |
| Forge Commons | Forge Products | No | N/A | Un capability no conoce productos concretos. |
| Forge Products | Forge Kernel | Sí | Lifecycle, contribution, state, command, event, capability broker | Siempre mediante contratos declarados. |
| Forge Products | Forge Commons | Sí | Capability service contracts | Nunca por imports a internals privados del capability. |
| Forge Products | Forge Products | No | N/A | Cero llamadas laterales; solo intercambio mediado por kernel/commons si se aprueba. |
| Cualquier capa | Runtime externo / OS / red / FS | Sí, solo desde adapters declarados | Adapters y permissions | Nada de side effects escondidos en domain/application. |
