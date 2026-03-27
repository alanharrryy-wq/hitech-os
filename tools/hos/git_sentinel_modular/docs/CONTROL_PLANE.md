# Control plane

`operations/` ahora concentra:

- `runtime.py`: rutas y runtime status
- `supervision.py`: estado de heartbeat, stale locks y scheduler summary
- `observability.py`: eventos, métricas y failure snapshots
- `status.py`: health summary combinado

Las demás capas quedan como implementaciones o utilidades que la fachada puede consumir.
