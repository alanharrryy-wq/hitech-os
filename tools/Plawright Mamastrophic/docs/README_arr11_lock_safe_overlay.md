# arr11 lock-safe overlay installer

Este paquete cambia el instalador y rollback para no mover ni renombrar la carpeta completa `Plawright Mamastrophic`.

## Causa corregida

Windows puede bloquear el directorio target cuando una consola, editor, watcher o proceso tiene handle abierto sobre la carpeta. El paquete anterior intentaba mover toda la carpeta a `F:\Trash-old`, lo cual puede fallar con WinError 32 aunque los archivos editables no esten bloqueados.

## Nueva regla

- No se mueve la carpeta target completa.
- Se hace backup completo a `F:\descargasf`.
- Se copian archivos del payload encima del target, archivo por archivo.
- Los extras se mueven archivo por archivo a `F:\Trash-old`.
- El rollback restaura in-place desde backup.
- No mata procesos, no libera puertos, no levanta servidores, no toca DB.

## Relacion con opcion 7

Mantiene el paralelismo por superficie y el fix del agregador `children` de arr10.
