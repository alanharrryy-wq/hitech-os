# PRISMA App 02 - Arquitectura de información

## Propósito

Este documento define cómo debe quedar organizada la app móvil de PRISMA para que funcione como producto general y no como una maqueta amarrada únicamente a clientes multisucursal.

## Idea central

PRISMA App debe abrir con una pregunta sencilla:

```text
¿Cómo va mi negocio hoy?
```

Desde ahí se ramifica por necesidad:

```text
Hoy
Ventas
Caja
Inventario
Alertas
Reportes
MultiSucursal
```

## Jerarquía recomendada

### Nivel 1: Inicio

La pantalla `Hoy` es la entrada. Debe mezclar los datos más importantes sin saturar.

### Nivel 2: Lectura por tema

Ventas, Caja, Inventario, Alertas y Reportes son temas que cualquier negocio puede entender.

### Nivel 3: Avanzado

MultiSucursal se muestra cuando aplica. No debe dominar el producto base.

## Por qué esta separación importa

Si la app inicia como multisucursal, el cliente pequeño piensa que no es para él. Si inicia como “tu negocio desde el celular”, todos entran. Luego el que tiene varias sucursales encuentra su sección avanzada.

## Navegación conceptual

```text
/prisma-app
  #hoy
  #ventas
  #caja
  #inventario
  #alertas
  #reportes
  #multisucursal
```

## Reglas UX

1. Cada sección debe responder una pregunta de negocio.
2. Cada sección debe tener una acción sugerida o una lectura clara.
3. El celular no debe mostrar todo lo que PC muestra.
4. La app móvil debe priorizar decisiones rápidas.
5. MultiSucursal no debe aparecer como requisito para entender el producto.

## Relación con Tablet y PC

Tablet produce eventos operativos.
PC consolida, gobierna, audita y resuelve.
App consulta y resume.

## Ejemplo de mapa de datos

```text
Venta cerrada en Tablet
  -> evento sale.completed
  -> PC consolida
  -> App muestra venta del día
```

```text
Stock bajo detectado
  -> evento inventory.low_stock_detected
  -> PC clasifica prioridad
  -> App muestra alerta e inventario útil
```

```text
Caja con diferencia
  -> evento cash.difference.detected
  -> PC audita
  -> App muestra alerta de caja
```
