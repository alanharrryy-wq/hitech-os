# PRISMA PC - Matriz QA Proveedores + Compra Inteligente 01

Esta matriz baja el canon de producto a casos de aceptación verificables. Sirve para revisar entregas sin caer en el deporte humano favorito: declarar listo algo que sólo tiene botones bonitos.

## Gates globales

- PC gobierna proveedores, compras, recepciones, cuentas por pagar y Compra Inteligente.
- Tablet vende local y no queda bloqueada por PC.
- Cada recomendación explica razón, riesgo, monto, cobertura, fechas y acción.
- Cada acción sensible pide confirmación, motivo y auditoría.
- No hay data demo disfrazada de realidad productiva.
- No hay texto técnico visible para usuario final.


## Caso QA SP-001 · Proveedor sin calendario

**Clave:** `sin_calendario_001`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-002 · Stock crítico

**Clave:** `stock_critico_002`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-003 · Sobreinventario

**Clave:** `sobreinventario_003`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-004 · Caja apretada

**Clave:** `caja_apretada_004`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-005 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_005`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-006 · Recepción con diferencia

**Clave:** `recepcion_diferencia_006`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-007 · Pedido sugerido

**Clave:** `pedido_sugerido_007`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-008 · Simulador

**Clave:** `simulador_008`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-009 · Señal ligera Tablet

**Clave:** `tablet_signal_009`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-010 · Sin proveedores

**Clave:** `sin_proveedores_010`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-011 · Proveedor sin calendario

**Clave:** `sin_calendario_011`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-012 · Stock crítico

**Clave:** `stock_critico_012`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-013 · Sobreinventario

**Clave:** `sobreinventario_013`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-014 · Caja apretada

**Clave:** `caja_apretada_014`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-015 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_015`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-016 · Recepción con diferencia

**Clave:** `recepcion_diferencia_016`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-017 · Pedido sugerido

**Clave:** `pedido_sugerido_017`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-018 · Simulador

**Clave:** `simulador_018`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-019 · Señal ligera Tablet

**Clave:** `tablet_signal_019`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-020 · Sin proveedores

**Clave:** `sin_proveedores_020`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-021 · Proveedor sin calendario

**Clave:** `sin_calendario_021`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-022 · Stock crítico

**Clave:** `stock_critico_022`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-023 · Sobreinventario

**Clave:** `sobreinventario_023`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-024 · Caja apretada

**Clave:** `caja_apretada_024`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-025 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_025`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-026 · Recepción con diferencia

**Clave:** `recepcion_diferencia_026`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-027 · Pedido sugerido

**Clave:** `pedido_sugerido_027`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-028 · Simulador

**Clave:** `simulador_028`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-029 · Señal ligera Tablet

**Clave:** `tablet_signal_029`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-030 · Sin proveedores

**Clave:** `sin_proveedores_030`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-031 · Proveedor sin calendario

**Clave:** `sin_calendario_031`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-032 · Stock crítico

**Clave:** `stock_critico_032`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-033 · Sobreinventario

**Clave:** `sobreinventario_033`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-034 · Caja apretada

**Clave:** `caja_apretada_034`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-035 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_035`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-036 · Recepción con diferencia

**Clave:** `recepcion_diferencia_036`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-037 · Pedido sugerido

**Clave:** `pedido_sugerido_037`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-038 · Simulador

**Clave:** `simulador_038`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-039 · Señal ligera Tablet

**Clave:** `tablet_signal_039`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-040 · Sin proveedores

**Clave:** `sin_proveedores_040`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-041 · Proveedor sin calendario

**Clave:** `sin_calendario_041`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-042 · Stock crítico

**Clave:** `stock_critico_042`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-043 · Sobreinventario

**Clave:** `sobreinventario_043`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-044 · Caja apretada

**Clave:** `caja_apretada_044`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-045 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_045`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-046 · Recepción con diferencia

**Clave:** `recepcion_diferencia_046`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-047 · Pedido sugerido

**Clave:** `pedido_sugerido_047`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-048 · Simulador

**Clave:** `simulador_048`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-049 · Señal ligera Tablet

**Clave:** `tablet_signal_049`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-050 · Sin proveedores

**Clave:** `sin_proveedores_050`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-051 · Proveedor sin calendario

**Clave:** `sin_calendario_051`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-052 · Stock crítico

**Clave:** `stock_critico_052`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-053 · Sobreinventario

**Clave:** `sobreinventario_053`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-054 · Caja apretada

**Clave:** `caja_apretada_054`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-055 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_055`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-056 · Recepción con diferencia

**Clave:** `recepcion_diferencia_056`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-057 · Pedido sugerido

**Clave:** `pedido_sugerido_057`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-058 · Simulador

**Clave:** `simulador_058`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-059 · Señal ligera Tablet

**Clave:** `tablet_signal_059`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-060 · Sin proveedores

**Clave:** `sin_proveedores_060`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-061 · Proveedor sin calendario

**Clave:** `sin_calendario_061`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-062 · Stock crítico

**Clave:** `stock_critico_062`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-063 · Sobreinventario

**Clave:** `sobreinventario_063`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-064 · Caja apretada

**Clave:** `caja_apretada_064`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-065 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_065`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-066 · Recepción con diferencia

**Clave:** `recepcion_diferencia_066`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-067 · Pedido sugerido

**Clave:** `pedido_sugerido_067`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-068 · Simulador

**Clave:** `simulador_068`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-069 · Señal ligera Tablet

**Clave:** `tablet_signal_069`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-070 · Sin proveedores

**Clave:** `sin_proveedores_070`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-071 · Proveedor sin calendario

**Clave:** `sin_calendario_071`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-072 · Stock crítico

**Clave:** `stock_critico_072`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-073 · Sobreinventario

**Clave:** `sobreinventario_073`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-074 · Caja apretada

**Clave:** `caja_apretada_074`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-075 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_075`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-076 · Recepción con diferencia

**Clave:** `recepcion_diferencia_076`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-077 · Pedido sugerido

**Clave:** `pedido_sugerido_077`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-078 · Simulador

**Clave:** `simulador_078`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-079 · Señal ligera Tablet

**Clave:** `tablet_signal_079`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-080 · Sin proveedores

**Clave:** `sin_proveedores_080`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-081 · Proveedor sin calendario

**Clave:** `sin_calendario_081`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-082 · Stock crítico

**Clave:** `stock_critico_082`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-083 · Sobreinventario

**Clave:** `sobreinventario_083`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-084 · Caja apretada

**Clave:** `caja_apretada_084`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-085 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_085`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-086 · Recepción con diferencia

**Clave:** `recepcion_diferencia_086`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-087 · Pedido sugerido

**Clave:** `pedido_sugerido_087`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-088 · Simulador

**Clave:** `simulador_088`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-089 · Señal ligera Tablet

**Clave:** `tablet_signal_089`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-090 · Sin proveedores

**Clave:** `sin_proveedores_090`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-091 · Proveedor sin calendario

**Clave:** `sin_calendario_091`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-092 · Stock crítico

**Clave:** `stock_critico_092`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-093 · Sobreinventario

**Clave:** `sobreinventario_093`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-094 · Caja apretada

**Clave:** `caja_apretada_094`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-095 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_095`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-096 · Recepción con diferencia

**Clave:** `recepcion_diferencia_096`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-097 · Pedido sugerido

**Clave:** `pedido_sugerido_097`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-098 · Simulador

**Clave:** `simulador_098`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-099 · Señal ligera Tablet

**Clave:** `tablet_signal_099`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-100 · Sin proveedores

**Clave:** `sin_proveedores_100`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-101 · Proveedor sin calendario

**Clave:** `sin_calendario_101`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-102 · Stock crítico

**Clave:** `stock_critico_102`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-103 · Sobreinventario

**Clave:** `sobreinventario_103`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-104 · Caja apretada

**Clave:** `caja_apretada_104`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-105 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_105`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-106 · Recepción con diferencia

**Clave:** `recepcion_diferencia_106`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-107 · Pedido sugerido

**Clave:** `pedido_sugerido_107`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-108 · Simulador

**Clave:** `simulador_108`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-109 · Señal ligera Tablet

**Clave:** `tablet_signal_109`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-110 · Sin proveedores

**Clave:** `sin_proveedores_110`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-111 · Proveedor sin calendario

**Clave:** `sin_calendario_111`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor activo sin regla de visita.

**Resultado esperado:** Mostrar Configurar calendario y bloquear Compra Inteligente por producto.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-112 · Stock crítico

**Clave:** `stock_critico_112`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura menor a 2 días.

**Resultado esperado:** Recomendación crítica con razón de cobertura y proveedor.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-113 · Sobreinventario

**Clave:** `sobreinventario_113`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto con cobertura mayor a 9 días.

**Resultado esperado:** No comprar ahora con protección de caja.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-114 · Caja apretada

**Clave:** `caja_apretada_114`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Compra útil pero pagos próximos reducen caja.

**Resultado esperado:** Estado Compra con cuidado o Caja apretada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-115 · Proveedor bloqueado

**Clave:** `proveedor_bloqueado_115`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Proveedor con estatus blocked.

**Resultado esperado:** Bloquear creación de pedido y pedir revisión.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-116 · Recepción con diferencia

**Clave:** `recepcion_diferencia_116`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Recibir menos de lo ordenado.

**Resultado esperado:** Exigir motivo y dejar trazabilidad.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-117 · Pedido sugerido

**Clave:** `pedido_sugerido_117`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Crear pedido desde recomendación.

**Resultado esperado:** Mantener razones originales en pedido.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-118 · Simulador

**Clave:** `simulador_118`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Quitar producto lento.

**Resultado esperado:** Recalcular total, cobertura y caja restante.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-119 · Señal ligera Tablet

**Clave:** `tablet_signal_119`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Producto crítico detectado en PC.

**Resultado esperado:** Tablet solo ve aviso, no administración pesada.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.


## Caso QA SP-120 · Sin proveedores

**Clave:** `sin_proveedores_120`

**Objetivo:** validar que Proveedores + Compra Inteligente conserva el ciclo detectar, investigar, decidir, actuar, verificar y auditar sin convertir PC en una tabla muda.

**Precondiciones operativas:**

- PC Backoffice está disponible en puerto 3130.
- Tablet conserva venta local independiente.
- El dataset puede venir de fixtures o repositorios reales, pero si es demo debe etiquetarse como tal.
- La pantalla visible usa español de México y evita jerga técnica como payload, runtime, schema o sync job.

**Acción de prueba:** Abrir Proveedores sin registros.

**Resultado esperado:** Mostrar empty state con CTA Agregar proveedor y no recomendaciones falsas.

**Evidencia mínima:**

1. Captura de la card o tabla involucrada.
2. Texto visible con qué pasó, por qué importa y qué puede hacer el usuario.
3. Registro de acción o señal, si aplica.
4. Verificación de que la acción no exige PC para que Tablet pueda seguir vendiendo.
5. Revisión de que la recomendación explica razón, monto, fechas y riesgo.

**Bloquea release si:**

- Se crea compra sin proveedor activo.
- Se oculta caja apretada.
- Se recomienda comprar producto con cobertura alta sin justificación.
- Se permite recepción con diferencia sin motivo.
- Se muestra lenguaje técnico en UI final.
- La recomendación no se puede convertir en pedido o marcar para revisión.

**Notas de implementación:**

- Este caso debe poder revisarse desde `/proveedores` y desde la API `/api/proveedores/compra-inteligente`.
- Si se conecta a Prisma real, conservar compatibilidad con el motor determinístico para pruebas.
- La evidencia debe guardarse como parte del log o reporte de QA de la integración.
