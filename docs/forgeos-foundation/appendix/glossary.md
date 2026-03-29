# glossary.md

| Término | Definición |
| --- | --- |
| ForgeOS | Plataforma gobernada para hospedar múltiples productos sobre kernel y commons. |
| Forge Kernel | Núcleo domain-agnostic que gobierna bootstrap, lifecycle, contracts, host shell y packaging gates. |
| Forge Commons | Capa de capacidades compartidas reutilizables y neutrales al dominio. |
| Forge Products | Productos aislados con su propio dominio, estado, contracts y packaging. |
| Host shell | Superficie domain-agnostic que presenta slots y chrome, sin lógica de negocio de productos. |
| Contribution | Declaración formal de una integración del producto con un extension point del host. |
| Capability | Servicio reusable de Forge Commons con contracts, owner, lifecycle y packaging propios. |
| Published context | Proyección mínima y aprobada de estado que un producto publica al host. |
| State authority | Responsable único de escritura de un state slice. |
| Source of truth | Store o runtime que posee autoridad de escritura sobre un dato. |
| Lifecycle authority | Entidad que decide las transiciones oficiales de prepare/activate/suspend/dispose. |
| Contract runtime | Infraestructura que valida, enruta y observa contratos versionados. |
| Command contract | Contrato de intención de acción con handler y outcome explícitos. |
| Event contract | Contrato de hecho ocurrido, inmutable y observable. |
| State contract | Contrato que define snapshot, restore, publish o migrate de un state slice. |
| Service contract | Contrato para consumir una capability sin exponer internals. |
| Packaging gate | Validación que decide si un paquete puede instalarse, activarse, actualizarse o revertirse. |
| BOM | Bill of Materials. Lista verificable de componentes y assets de un paquete. |
| Teardown | Secuencia explícita de cierre y liberación de recursos. |
| Kernel contamination | Entrada de lógica o semántica de producto dentro del kernel/host. |
| Shared capability abuse | Promoción de algo a Commons sin neutralidad, contratos o reuso real. |
| Product leakage | Dependencia del host o de otros productos hacia internals de un producto, o viceversa. |
| Legacy shim | Compatibilidad temporal para deuda anterior. En ForgeOS solo existe si se declara explícitamente. |
| Failure isolation | Política por la cual una falla de producto o capability no debe tumbar el host. |
| Strong default | Decisión firme adoptada por falta de información completa y registrada en el decision log. |
