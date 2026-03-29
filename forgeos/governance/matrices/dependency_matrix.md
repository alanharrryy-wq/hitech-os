# dependency_matrix.md

Matriz de dependencias permitidas y prohibidas.

| Capa | Dependencias permitidas | Dependencias prohibidas | Racional |
| --- | --- | --- | --- |
| Kernel | Solo módulos kernel, abstracciones del runtime/UI, manifiestos de paquete, observabilidad base | Productos, nombres de producto, contratos privados de commons, stores de dominio | Kernel debe compilar/vivir sin ningún producto instalado. |
| Commons | Kernel public APIs, propios módulos, otros commons aprobados | Productos, host internals, widgets o semántica de producto | Commons solo expone capabilities neutrales. |
| Products | Kernel public APIs, commons contratados, propios módulos | Otros productos, host internals, stores de kernel | Todo acceso cross-layer es contractual. |
| Adapters | OS, red, FS, subprocess, serialización, APIs externas | Domain/application de otra capa | Los side effects viven aquí. |
| Domain | Solo domain y contratos locales | UI, host, OS, network, kernel internals | Domain debe seguir seco y portable. |
| Views | Application presenters, contratos de host_contribution | Service container global, estado de otro producto | La view no es service locator. |
