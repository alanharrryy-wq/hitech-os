# TEARDOWN

## Objetivo

Cerrar el producto de manera explícita, verificable y sin dejar basura viva en el runtime.

## Inventario de recursos a cerrar

| Recurso | Owner | Cuándo se crea | Cuándo se cierra | Evidencia requerida |
| --- | --- | --- | --- | --- |
| subscriptions | `<owner>` | prepare/activate | suspend/dispose | count before/after |
| timers/workers | `<owner>` | activate | suspend/dispose | health + stop ack |
| subprocesses | `<owner>` | command/activate | suspend/dispose | pid reap/killed |
| stores/snapshots | `<owner>` | prepare | dispose | flush/close result |
| surfaces host | `<owner>` | activate | suspend/dispose | slot unbound |
| published context | `<owner>` | activate | suspend/dispose | context withdrawn |

## Secuencia oficial

1. bloquear nuevas activaciones y commands entrantes;
2. retirar contributions del host;
3. cancelar timers y background tasks;
4. cerrar/reap subprocesses;
5. flush y cerrar stores;
6. retirar contextos publicados;
7. remover subscriptions;
8. emitir evidence log final.

## Criterio de éxito

- cero recursos vivos fuera de policy;
- cero referencias a slots del host;
- cero procesos huérfanos;
- cero subscriptions colgando;
- evidencia de cierre registrada.

## Falla de teardown

Si un recurso no cierra:
- marcar `faulted teardown`;
- aplicar kill/cleanup policy;
- dejar evidencia con owner;
- impedir reactivación si el recurso deja el runtime en estado inseguro.
