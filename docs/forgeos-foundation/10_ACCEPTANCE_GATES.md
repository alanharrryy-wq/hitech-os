# 10_ACCEPTANCE_GATES.md

Estos gates definen cuándo una implementación de ForgeOS se considera aceptable.

No son sugerencias. Son condiciones de entrada y salida de fase.

## Architecture acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| ARCH-01 | El host debe seguir siendo domain-agnostic. | Es la ley principal de ForgeOS. | No hay nombres, branches ni state de producto en kernel/host. | Existe cualquier lógica de dominio de producto en kernel/host. | import graph limpio, search de símbolos, review de `00`/`02`. |
| ARCH-02 | Todo subsistema debe estar asignado a una sola capa. | Sin asignación, no hay ownership real. | Cada módulo/package aparece en la matriz de ownership con una sola capa. | Hay módulos híbridos o sin owner. | ownership matrix actualizada. |

## Boundary acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| BOUND-01 | No debe existir dependencia prohibida entre capas. | Las fronteras son el cimiento del rebuild. | Import graph y manifests no muestran product->product, commons->product ni kernel->product. | Existe al menos una dependencia prohibida. | dependency matrix + reporte de imports. |
| BOUND-02 | No se permiten service locators globales como surface oficial. | El legacy se rompió por reach-through. | No existe acceso directo a `main_window` ni controllers del host. | Aparece un lookup o import directo a internals del host. | escaneo de símbolos prohibidos. |

## Contract acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| CON-01 | Toda interacción cross-layer tiene contrato declarado. | Sin contrato no hay control ni versionado. | El contract index cubre todas las interacciones cross-layer. | Existe una llamada directa no documentada. | contract index + review de wiring. |
| CON-02 | Todo contrato tiene owner, version y validation. | Los strings libres no bastan. | Cada contrato documenta schema, error model y observability. | Falta cualquiera de esos campos. | catálogo contractual y plantillas llenas. |

## Lifecycle acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| LIFE-01 | Todo package con runtime tiene lifecycle explícito. | Los constructores no deben gobernar el sistema. | Existe `LIFECYCLE.md` y transitions verificables. | El runtime depende de side effects implícitos. | lifecycle matrix + docs del package. |
| LIFE-02 | Todo resource vivo tiene teardown explícito. | Shutdown incompleto fue una falla legacy crítica. | Existe `TEARDOWN.md` y evidence log de dispose. | Quedan subscriptions, tasks o procesos huérfanos. | teardown docs + pruebas/logs. |

## Packaging acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| PACK-01 | Todo package instalable trae manifest, BOM y rollback plan. | Sin eso no hay release confiable. | Los archivos requeridos existen y son consistentes. | Falta alguno o se contradicen. | packaging docs y manifests. |
| PACK-02 | Toda instalación valida compatibilidad e integridad. | La compatibilidad declarada evita runtime roulette. | Los ranges y hashes se validan antes de activar. | Un package entra sin validation previa. | compatibility report + integrity report. |

## Product isolation acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| PROD-01 | Cada producto posee su dominio, estado y views. | El producto no debe vivir repartido por el host. | El producto puede desinstalarse sin romper el host. | El host requiere internals del producto para vivir. | ownership/state docs + uninstall check. |
| PROD-02 | Ningún producto toca internals del host. | Es la prohibición central de contaminación. | Toda integración va por contributions o service contracts. | Aparece scraping del host o mutation directa. | host integration review + symbol scan. |

## Teardown acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| DOWN-01 | El cierre del runtime es verificable y ordenado. | No más `shutdown_all()` olvidado. | Kernel, commons y productos reportan dispose exitoso. | El cierre depende del proceso del OS o del GC. | shutdown evidence log. |

## State ownership acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| STATE-01 | Todo state slice tiene owner nombrado y source of truth. | Sin authority clara el sistema vuelve a fragmentarse. | La state authority matrix cubre todos los slices. | Hay duplicidad de writers o slices huérfanos. | state authority matrix. |
| STATE-02 | El host no contiene state de dominio de productos. | La contaminación del contexto global fue crítica en el legado. | El contexto del host es mínimo y neutral. | Aparecen campos de dominio de producto en kernel/host. | review de schemas de host/session. |

## Compatibility acceptance

| Gate | Rule | Rationale | Pass condition | Failure condition | Evidence required |
| --- | --- | --- | --- | --- | --- |
| COMP-01 | Todo package declara rangos soportados. | La compatibilidad no se asume. | Existe `COMPATIBILITY.md` y manifest consistente. | La compatibilidad es implícita o ambigua. | compatibility docs + manifest. |


## Regla de uso

- Un gate se considera **pass** solo con evidencia.
- Un gate se considera **fail** ante la duda.
- Un gate fallado bloquea avance de fase si toca:
  - boundaries;
  - contratos;
  - state authority;
  - teardown;
  - compatibilidad.

## Regla final

ForgeOS no acepta implementaciones “casi limpias”.  
O la frontera existe y se demuestra, o no existe.
