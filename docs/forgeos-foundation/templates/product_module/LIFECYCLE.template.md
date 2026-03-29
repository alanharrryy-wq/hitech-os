# LIFECYCLE

## Estados oficiales

```text
discovered -> registered -> prepared -> active -> suspended -> faulted -> disposing -> disposed
```

## Tabla de estados

| Estado | Significado | Entrada permitida desde | Salida permitida hacia | Entry actions | Exit actions | Timeout máximo |
| --- | --- | --- | --- | --- | --- | --- |
| `discovered` | paquete encontrado por el kernel | N/A | `registered` | validar manifest | ninguna | inmediato |
| `registered` | identidad y compatibilidad aprobadas | `discovered` | `prepared`, `disposing` | registrar contratos y contributions | ninguna | 5 s |
| `prepared` | dependencias y estado listos, sin surfaces activas | `registered`, `suspended` | `active`, `disposing`, `faulted` | restore, preload, alloc de recursos controlados | emitir ready | 30 s |
| `active` | surfaces y handlers activos | `prepared` | `suspended`, `faulted`, `disposing` | bind a slots, subscribe, iniciar trabajos permitidos | flush incremental si aplica | continuo |
| `suspended` | producto inactivo pero reinstalable sin reinstall | `active` | `prepared`, `disposing` | unbind visual, pausar workers, conservar solo lo declarado | ninguna | 10 s |
| `faulted` | falla no absorbible dentro del estado actual | `prepared`, `active`, `suspended` | `disposing`, `prepared` si recovery documentado | emitir diagnostics y degradación | ninguna | inmediato |
| `disposing` | teardown en curso | cualquier estado gestionable | `disposed` | stop workers, unsubscribe, close stores, release handles | none | 30 s |
| `disposed` | producto fuera de runtime | `disposing` | N/A | evidence log final | N/A | terminal |

## Eventos lifecycle mínimos

- `prepare_requested`
- `prepare_completed`
- `activate_requested`
- `activate_completed`
- `suspend_requested`
- `suspend_completed`
- `faulted`
- `dispose_requested`
- `dispose_completed`

## Reglas duras

- El constructor no activa runtime.
- Ninguna suscripción de bus ocurre antes de `prepare`.
- Ningún subprocess arranca fuera de `activate` o de un command explícito.
- Todo background worker se detiene en `suspend` o `dispose`, según policy.
- `faulted` no puede quedarse callado. Debe emitir evidencia.

## Recursos sujetos a teardown

- subscriptions
- timers
- background tasks
- subprocesses
- sockets
- file handles
- caches temporales
- surfaces/UI bindings
- exported contexts

## Checklist de salida de `dispose`

- cero subscriptions activas;
- cero timers vivos;
- cero subprocesses huérfanos;
- stores flushed y cerrados;
- contextos publicados retirados;
- contributions retiradas del host;
- evidence log emitido.
