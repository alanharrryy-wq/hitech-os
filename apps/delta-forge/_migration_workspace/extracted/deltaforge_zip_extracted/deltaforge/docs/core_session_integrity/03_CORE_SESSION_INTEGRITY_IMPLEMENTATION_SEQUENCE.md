# Core Session Integrity | Implementation Sequence

## Secuencia corta

### 1. Congelar ownership
- fijar qué vive en `SessionWorkspace`
- fijar qué vive en `SessionManager`
- marcar qué es solo proyección de UI

### 2. Cerrar transición de estado
- unificar `dirty`
- unificar `stale`
- unificar `busy`
- formalizar `refresh_requested` y `refresh_completed`

### 3. Rehacer event surface
- hacer que el feed visible sea session-scoped
- sacar buffers globales del camino
- dejar al bus como transporte, no storage

### 4. Tipar `scope`
- introducir tipo explícito de scope
- mover branching de archivo/carpeta al modelo o policies del core

### 5. Limpiar infrastructure
- sacar dependencias GUI de donde no tocan
- dejar watcher y servicios con contratos puros

### 6. Validar invariantes
- cambio de sesión no mezcla eventos
- edición de ops dispara transición correcta
- refresh reconcilia sin degradar de más
- watchers solo notifican

## Qué no hacer durante el pase
- no meter engine real
- no reorganizar todo el repo
- no mover panes/widgets por estética
- no dejar a la UI decidir verdad del core
