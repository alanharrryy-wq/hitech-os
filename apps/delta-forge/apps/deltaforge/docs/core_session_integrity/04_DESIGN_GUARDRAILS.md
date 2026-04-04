# Core Session Integrity | Design Guardrails

## Reglas duras
- `SessionWorkspace` es la verdad operativa de una sesión
- `SessionManager` administra colección y selección, no semántica fina
- el event bus mueve eventos, no conserva el historial visible
- el watcher emite señales, no decide `dirty` / `stale`
- la UI solicita acciones, no muta verdad del core
- `main_window` integra, no decide negocio
- `scope` vive tipado en dominio
- infrastructure implementa contratos, no define producto

## Anti-patrones
- buffer global como truth source del bottom pane
- widgets marcando `dirty` directo
- refresh como side effect invisible
- helpers visuales mutando sesión
- response raw del engine persistida como verdad del core
- PySide filtrado en infraestructura base

## Señales de que vas bien
- switching de sesión limpio
- event feed consistente por sesión
- transiciones de estado observables y trazables
- policies centralizadas
- ownership sin duplicados
