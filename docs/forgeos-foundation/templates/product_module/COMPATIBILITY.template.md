# COMPATIBILITY

## Matriz declarada

| Dependencia | Rango soportado | Tipo | Obligatoria | Notas |
| --- | --- | --- | --- | --- |
| `forge-kernel` | `^1.0.0` | kernel | sí | runtime base |
| `forge-commons-<capability-id>` | `^1.0.0` | commons | sí/no | capability requerida |
| `<runtime-externo>` | `<range>` | external | sí/no | librería, binario o servicio |

## Canales soportados

- `<beta>`
- `<stable>`

## Combinaciones no soportadas

| Combinación | Motivo | Gate que debe fallar |
| --- | --- | --- |
| kernel fuera de rango | contrato o lifecycle incompatible | install/activate gate |
| capability ausente | dependencia no resuelta | install/prepare gate |
| canal no permitido | política de release | package gate |

## Reglas

- No asumir forward compatibility.
- Toda excepción debe documentarse aquí y en release notes.
- Si una capability cambia major, este documento debe actualizarse antes del release.
