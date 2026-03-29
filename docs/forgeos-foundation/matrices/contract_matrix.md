# contract_matrix.md

Matriz maestra del sistema contractual.

| Familia | Propósito | Owner target | Interacción típica | Observabilidad mínima |
| --- | --- | --- | --- | --- |
| Lifecycle | Activación, suspensión, reanudación y dispose de kernel/capability/product | Forge Kernel | Kernel y el paquete afectado | Request/ack versionado | Correlación, duración, resultado, owner |
| State | Lectura, publicación, snapshot, restore y migración de estado | Dueño del state slice | Dueño y consumidores declarados | Read/write con authority explícita | Schema version, source of truth, restore status |
| Command | Pedidos de acción con intención y respuesta | Quien define la acción | Host, commons o producto | Request/response | Command id, initiator, timeout, outcome |
| Event | Notificaciones inmutables de hechos ocurridos | Actor que posee el hecho | Consumidores suscritos | One-way publish | Event id, producer, correlation, severity |
| Contribution | Declaración de superficies, acciones y extensiones de host | Producto | Host/Kernal | Registration + validation | Contribution id, slot, policy result |
| Capability Service | Consumo de capabilities de Forge Commons | Capability owner | Producto o kernel | Request/response o streaming | Capability id, SLA, timeout, degrade mode |
| Persistence | Serialización, schema, migraciones y ownership de datos | Dueño del store | Dueño + migradores | Read/write/migrate | Store id, schema version, migration path |
| Packaging | Manifest, BOM, firma, assets, instalación y rollback | Package owner | Kernel packaging/runtime | Validation + lifecycle | Package id, version, hashes, compatibility |
| Compatibility | Declaración de rangos soportados entre kernel, commons y producto | Package owner | Kernel install/release gates | Declaration + validation | Version ranges, channel, migration requirement |
