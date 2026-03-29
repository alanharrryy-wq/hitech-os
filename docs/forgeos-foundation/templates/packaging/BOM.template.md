# BOM

## Identidad del paquete

- `package_id`: `<package-id>`
- `version`: `<version>`
- `channel`: `<channel>`

## Componentes incluidos

| Ruta | Tipo | Owner | Hash | Obligatorio | Motivo de inclusión |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<code|asset|doc|schema|migration>` | `<owner>` | `<sha256>` | sí/no | `<motivo>` |

## Dependencias externas

| Dependencia | Tipo | Versión/rango | Obligatoria | Uso |
| --- | --- | --- | --- | --- |
| `<dependency>` | `<library|binary|service>` | `<range>` | sí/no | `<uso>` |

## Validaciones de integridad

- hashes verificados: `<sí/no>`
- firma verificada: `<sí/no>`
- archivos faltantes: `<lista o ninguno>`
- archivos extra no declarados: `<lista o ninguno>`

## Notas

- Ningún asset runtime relevante queda fuera de este BOM.
- Si el paquete emite artefactos instalables, estos también deben aparecer aquí o en un BOM derivado.
