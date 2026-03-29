# lifecycle_matrix.md

Matriz de lifecycle por entidad relevante.

| Entidad | Estados target | Autoridad | Triggers | Teardown | Failure policy |
| --- | --- | --- | --- | --- | --- |
| Proceso ForgeOS | booting -> running -> shutting_down -> stopped | Forge Kernel | Boot, health gate, shutdown command | Todos los subsistemas | Un fallo de producto no tira el proceso. |
| Capability de Forge Commons | declared -> validated -> ready -> serving -> degraded -> disposing -> disposed | Owner del capability + kernel | Install, activate, failure, remove | Runtime y stores del capability | Degrade antes de abortar plataforma. |
| Producto Forge | discovered -> registered -> prepared -> active -> suspended -> faulted -> disposing -> disposed | Forge Kernel Lifecycle | Install, activate, suspend, fault, uninstall | Views, application, state local, resources | Fault aislado al producto. |
| Superficie de host | unbound -> bound -> visible -> hidden -> disposing -> disposed | Host shell | Contribution registration y lifecycle del producto | Widget/render tree del slot | El host no posee lógica de dominio. |
| Task background | queued -> running -> completed|failed|cancelled -> disposed | Kernel supervisor o capability | Dispatch, timeout, cancel | Task handle, logs, temp resources | Timeout obligatorio. |
| Proceso externo | requested -> spawned -> streaming -> finished|timed_out|killed -> reaped | Forge Commons Process Execution | Process contract | Subprocess, pipes, temp dirs | Siempre con kill policy y evidence log. |
| Store persistente | cold -> mounted -> serving -> migrating -> disposing -> disposed | Dueño del store | Boot, migration, shutdown | Archivos/tablas/manifest | Nadie escribe fuera de su owner. |
