# DEPENDENCIES

## Dependencias duras declaradas

| Dependency kind | Identificador | Rango | Requerida | Justificación | Owner aprobador |
| --- | --- | --- | --- | --- | --- |
| Forge Kernel API | `forge-kernel` | `^1.0.0` | sí | lifecycle, contracts, host integration | `<owner>` |
| Forge Commons capability | `forge-commons-<capability-id>` | `^1.0.0` | sí/no | `<para-que>` | `<owner>` |
| Runtime externo | `<python-package-o-binario>` | `<range>` | sí/no | `<para-que>` | `<owner>` |

## Dependencias blandas u opcionales

| Dependency | Cómo se degrada si falta | Quién detecta la ausencia | Qué evidencia se emite |
| --- | --- | --- | --- |
| `<capability-opcional>` | `<modo degradado>` | `<runtime owner>` | `<evento/diagnóstico>` |

## Dependencias prohibidas

- otros productos;
- internals del host;
- widgets/controladores del host;
- service locator global;
- stores del kernel;
- paquetes legacy solo por conveniencia;
- heurísticas por nombre de producto.

## Reglas

- Toda dependencia debe existir en `PRODUCT_MANIFEST`.
- Toda dependencia externa debe estar en BOM.
- Toda dependencia opcional debe declarar modo degradado.
- Si una dependencia dura no existe, el producto no se activa.
- Ningún adapter lateral entre productos es aceptable.
