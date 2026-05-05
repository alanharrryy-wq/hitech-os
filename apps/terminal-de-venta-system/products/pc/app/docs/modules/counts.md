# PC I03 - Conteos físicos

## Objetivo

Convertir `/counts` en una vista operativa de conteos, diferencias y exactitud.

## Alcance

- Lee `AuditCount`.
- Muestra ubicación, actor de conteo, variación, estado y fecha.
- Calcula exactitud simple: conteos sin variación / conteos totales.
- Marca variaciones altas como hallazgos.

## Límite honesto

El modelo actual no trae líneas de conteo por SKU. Esta fase expone conteos agregados disponibles y deja documentada la necesidad de líneas de conteo para exactitud por SKU.
