# state_authority_matrix.md

Matriz de authority por slice de estado.

| State slice | Owner target | Storage | Writer authority | Readers | Nota |
| --- | --- | --- | --- | --- | --- |
| Sesión de plataforma | Forge Kernel | Store de sesión del kernel | Kernel | Host shell, observabilidad | Se crea al boot y se destruye al shutdown. |
| Layout y chrome del host | Forge Kernel Host Shell | Store de layout del kernel | Host shell | Kernel | No contiene estado de dominio. |
| Política runtime / preferencias transversales | Forge Commons Config & Policy | Capability config store | Capability owner | Kernel y productos vía contrato | Puede restaurarse por perfil/canal. |
| Índice y búsqueda de repositorio | Forge Product `repo_analyzer` | Store local del producto | Producto | Producto; host solo consume published context | No subir al kernel. |
| Preview/navegación de repositorio | Forge Product `repo_analyzer` | Store local del producto | Producto | Producto | Se publica solo resumen si el host lo necesita. |
| Contexto diagnóstico Cloudflare | Forge Product `cloudflare_guardian` | Store local del producto | Producto | Producto | Nunca en contexto kernel. |
| Run request y session state del orchestrator | Forge Product `orchestrator_bridge` | Store local del producto | Producto | Producto | Process runtime genérico va a Commons. |
| Telemetría de proceso | Forge Commons Process Execution | Capability runtime store | Capability owner | Producto solicitante y observabilidad | Se destruye al cierre de ejecución. |
| Historial de runs | Forge Commons History & Runs | Ledger store | Capability owner | Productos autorizados | Retención y purge explícitos. |
| Registro de paquetes instalados | Forge Kernel Packaging | Store de instalación | Kernel | Kernel/installer | Fuente de verdad para compatibilidad instalada. |
