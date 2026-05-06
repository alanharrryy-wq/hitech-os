# Rollback Rules

Cada instalador debe soportar `--dry-run`, `--apply`, `--verify`, `--rollback`, `--target-root`, `--zip-path`.

Debe crear backup antes de sobrescribir, rollback automatico si falla apply/verify, rollback manual, y log unico en `F:\descargasf`.

Pausar si intenta escribir fuera del scope, falta manifest, falta checksum o target root no parece `terminal-de-venta-system`.
