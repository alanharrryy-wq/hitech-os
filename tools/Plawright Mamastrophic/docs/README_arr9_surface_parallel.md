# arr9: Surface parallel para opcion 7

## Cambio

Cuando `RUN.ps1` recibe `-Surface all` con `-SurfaceParallel auto` u `on`, expande la ejecucion a workers aislados por superficie:

- chart-lab
- web
- tablet
- pc
- mobile
- control-center

Cada worker ejecuta `core/run-surf8-capture.ps1` con una superficie concreta y escribe sus propios artifacts/result ZIPs. El orquestador no comparte carpetas de screenshots entre workers; solo agrega stdout/stderr, comandos y resumen final.

## Valores seguros

- `-SurfaceParallelMax 4`: maximo 4 superficies simultaneas.
- `-SurfaceChildWorkers 1`: un worker Playwright por superficie para evitar licuadora de RAM/GPU.
- `-SurfaceParallel off`: conserva el comportamiento viejo de `Surface=all` en un solo run.

## Politica preservada

No mata procesos, no libera puertos, no levanta servicios, no toca base de datos y no cambia configuracion de dev servers.

## Output

El orquestador genera un folder como:

```txt
F:\descargasf\surf8 all-parallel quick 1006 102233\
```

con:

```txt
logs/<surface>.stdout.log
logs/<surface>.stderr.log
logs/<surface>.command.txt
reports/all-surfaces-parallel-manifest.json
reports/ALL_SURFACES_SUMMARY.md
```

y un ZIP final `result.zip` o `fail.zip` segun los exit codes reales de los workers.


## arr10 direct option-7 guard

- `RUN.ps1 -Surface 7`, `-Surface all`, `-Surface todo` and menu option 7 all resolve to the same parallel-by-surface orchestrator.
- Installer validation uses AST parsing and package scans, not `py_compile`, so no `__pycache__`/`.pyc` are written into the target.
