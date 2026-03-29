# CONTRACT_REVIEW_CHECKLIST

Usa esta lista antes de aprobar cualquier contrato nuevo o cambio de versión.

## Identidad y ownership

- [ ] `contract_id` sigue la convención oficial.
- [ ] La familia contractual es correcta.
- [ ] Hay owner nominal y backup.
- [ ] Producer y consumer están claramente definidos.

## Semántica

- [ ] El propósito es claro y no ambiguo.
- [ ] El payload usa vocabulario correcto y no contrabandea dominio al kernel.
- [ ] Los campos tienen restricciones explícitas.
- [ ] La dirección del flujo está clara.

## Lifecycle y timing

- [ ] Se declara el momento válido de emisión/uso.
- [ ] Hay timeout si el contrato lo requiere.
- [ ] La transición o acción es legal según el lifecycle.

## Error model

- [ ] Hay categorías de error compatibles con el catálogo oficial.
- [ ] El comportamiento en falla está documentado.
- [ ] El contrato no requiere excepciones sin envelope.

## Versioning y compatibilidad

- [ ] La estrategia de versionado está documentada.
- [ ] El cambio propuesto indica si rompe compatibilidad.
- [ ] Existe plan de deprecación o coexistencia si aplica.

## Validación y observabilidad

- [ ] Existe schema o validación equivalente.
- [ ] El contrato emite correlación y métricas mínimas.
- [ ] Los owners podrán investigar fallas con la evidencia producida.

## Límites arquitectónicos

- [ ] El contrato no requiere acceso a internals del host.
- [ ] El contrato no crea dependencia lateral entre productos.
- [ ] El contrato no convierte una capability en service locator.
- [ ] El contrato no duplica authority de estado.

## Decisión final

- [ ] Aprobado
- [ ] Rechazado
- [ ] Requiere rediseño
