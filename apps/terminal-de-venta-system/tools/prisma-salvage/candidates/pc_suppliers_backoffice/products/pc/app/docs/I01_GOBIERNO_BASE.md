# I01 Gobierno base de PC

## Propósito
Congelar una línea de trabajo ordenada para **PC** como frente activo, manteniendo a **Tablet** como gemela contractual de referencia.

## Decisiones que quedan fijas desde I01
- PC es el frente activo de evolución.
- Cada iteración se registra como cambio trazable dentro del repo.
- Cada entrega incremental suma y no reemplaza de forma destructiva.
- Cuando haya que tocar superficies compartidas, el cambio se marca como gemelo.
- Cuando el cambio sea local de inventario/backoffice, se queda solo en PC.

## Qué entra en gobierno base
- naming de iteraciones
- definición de base canon
- glosario visible es-MX
- checklist de integración
- mapa de superficies twin vs locales
- evidencia de módulos, rutas y labels actuales

## Base canon observada
- fuente canónica actual: `products/pc/app`
- contrato gemelo compartido: `shared/twin-kernel`
- gemela operativa de punto de venta: `products/tablet/app`

## Política de iteraciones
- una intención de cambio por ronda
- cambio versionado por iteración
- no sobreescritura destructiva por defecto
- consolidación cuando una futura ola lo amerite

## Resultado de I01
Esta iteración no intenta reescribir la base. La deja gobernada, indexada y lista para que las siguientes adiciones entren sin sopa de cables.
