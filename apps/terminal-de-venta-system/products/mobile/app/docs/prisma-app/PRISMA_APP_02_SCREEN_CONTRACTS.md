# PRISMA App 02 - Screen contracts

## Contrato de pantalla: Hoy

### Pregunta

¿Cómo va mi negocio hoy?

### Datos necesarios

- venta total del día
- número de tickets
- ticket promedio
- estado de caja
- alertas principales
- tareas sugeridas
- última actualización

### Fuente futura

```text
GET /api/mobile/summary
```

### Permisos sugeridos

```text
mobile.summary.view
mobile.sales.view
mobile.alerts.view
```

## Contrato de pantalla: Ventas

### Pregunta

¿Estoy vendiendo como debería a esta hora?

### Datos necesarios

- venta acumulada
- comparación contra ayer
- venta por hora
- tickets
- ticket promedio
- categoría top
- producto top

### Fuente futura

```text
GET /api/mobile/sales/today
```

### Permisos sugeridos

```text
mobile.sales.view
```

## Contrato de pantalla: Caja

### Pregunta

¿La caja está sana o requiere revisión?

### Datos necesarios

- caja esperada
- caja contada
- diferencias
- movimientos de efectivo
- retiros
- gastos
- último corte

### Fuente futura

```text
GET /api/mobile/cash/current
```

### Permisos sugeridos

```text
mobile.cash.view
```

## Contrato de pantalla: Inventario

### Pregunta

¿Qué se me está acabando o quedando atorado?

### Datos necesarios

- productos críticos
- productos a reponer
- productos estrella
- productos con sobrestock
- venta semanal
- stock actual
- prioridad

### Fuente futura

```text
GET /api/mobile/inventory/watchlist
```

### Permisos sugeridos

```text
mobile.inventory.watchlist.view
```

## Contrato de pantalla: Alertas

### Pregunta

¿Qué necesita atención primero?

### Datos necesarios

- severidad
- área
- título
- detalle
- hora
- acción sugerida
- origen del evento

### Fuente futura

```text
GET /api/mobile/alerts
```

### Permisos sugeridos

```text
mobile.alerts.view
```

## Contrato de pantalla: Reportes

### Pregunta

¿Qué pasó hoy y qué debo decidir?

### Datos necesarios

- resumen diario
- ventas
- caja
- inventario
- alertas
- productos top
- categorías top

### Fuente futura

```text
GET /api/mobile/reports/daily
```

### Permisos sugeridos

```text
mobile.reports.view
```

## Contrato de pantalla: MultiSucursal

### Pregunta

¿Qué sucursal merece atención hoy?

### Datos necesarios

- sucursal
- estado operativo
- venta
- tickets
- caja
- alertas
- sync
- ranking

### Fuente futura

```text
GET /api/mobile/branches
```

### Permisos sugeridos

```text
mobile.branches.view
```

## Reglas transversales

Todo dato sensible debe poder rastrearse a evento o consolidación. Si afecta dinero, inventario o caja, no debe aparecer como número mágico. La app móvil debe presentar resumen, no inventar verdad.
