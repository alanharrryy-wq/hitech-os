# ROLLBACK_PLAN

## Identidad

- `package_id`: `<package-id>`
- `from_version`: `<version-nueva>`
- `to_version`: `<version-previa>`
- `owner`: `<owner>`

## Preconditions

- backup verificado;
- compatibilidad de datos evaluada;
- dependencias de destino disponibles;
- ventana operativa aprobada.

## Secuencia de rollback

1. bloquear nuevas activaciones;
2. suspender runtime afectado;
3. exportar evidencia y estado si aplica;
4. revertir paquete binario;
5. ejecutar migración inversa o compensación documentada;
6. validar integridad;
7. reactivar si los gates pasan.

## Riesgos

| Riesgo | Impacto | Mitigación | Evidence owner |
| --- | --- | --- | --- |
| `<riesgo>` | `<impacto>` | `<mitigación>` | `<owner>` |

## No permitido

- rollback ciego sin revisar schema;
- rollback que deje stores mezclados;
- rollback que ignore procesos vivos;
- rollback que oculte incompatibilidades.
