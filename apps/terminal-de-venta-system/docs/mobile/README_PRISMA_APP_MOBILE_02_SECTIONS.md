# PRISMA_APP_MOBILE_02_SECTIONS

## Estado de esta entrega

Esta iteración convierte `/prisma-app` en una app móvil conceptual organizada por secciones. La entrega anterior instaló la base visual y cambió la narrativa desde `Pulso` hacia `PRISMA App`. Esta segunda entrega ya separa la experiencia en módulos entendibles para cualquier cliente:

- Hoy
- Ventas
- Caja
- Inventario
- Alertas
- Reportes
- MultiSucursal

La decisión importante es que **MultiSucursal no es la identidad completa de la app**. MultiSucursal queda como función avanzada. La app base debe servir para un solo negocio, una sola caja, un local con empleados o una operación chica que solo quiere saber cómo va el día sin abrir la PC.

## Regla de producto

```text
PRISMA Tablet vende.
PC administra cuando existe.
PRISMA App resume, alerta y reporta desde el celular.
```

Esto evita confundir las superficies del sistema. La app móvil no reemplaza el POS de Tablet ni el backoffice de PC. La app existe para darle visibilidad rápida al dueño, encargado o supervisor.

## Ruta instalada

```text
/prisma-app
```

## Archivos principales

```text
products/pc/app/app/prisma-app/page.tsx
products/pc/app/app/prisma-app/prisma-app.module.css
products/pc/app/src/lib/prisma-app/prisma-app-demo-data.ts
products/pc/app/src/lib/prisma-app/prisma-app-section-contracts.ts
products/pc/app/docs/README_PRISMA_APP_MOBILE_02_SECTIONS.md
products/pc/app/docs/prisma-app/PRISMA_APP_02_SCREEN_CONTRACTS.md
products/pc/app/docs/prisma-app/PRISMA_APP_02_INFORMATION_ARCHITECTURE.md
products/pc/app/docs/prisma-app/PRISMA_APP_02_COMMERCIAL_PLAYBOOK.md
products/pc/app/docs/prisma-app/PRISMA_APP_02_ROADMAP.md
products/pc/app/docs/prisma-app/fixtures/prisma-app-02-synthetic-business-fixtures.json
products/pc/app/tools/verify_prisma_app_mobile_02_sections.mjs
```

## Qué cambia frente a la iteración 01

La iteración 01 mostraba una maqueta visual compacta. La 02 ya define una estructura navegable y comercialmente vendible. Antes la app era una vitrina. Ahora tiene anaqueles, pasillos y letreros; ya no es el local bonito donde nadie sabe dónde está el arroz.

### Cambios concretos

1. Se agrega navegación interna por secciones.
2. Se define `PrismaAppSectionId` para evitar nombres improvisados.
3. Se agrega un contrato de sección móvil.
4. Se documenta la arquitectura de información.
5. Se agrega fixture grande de datos sintéticos para futuras pruebas.
6. Se separa MultiSucursal como módulo avanzado.
7. Se mantiene la ruta `/prisma-app`.
8. Se mantiene intacto el rol de Tablet y PC.

## Pantallas de la app

### 1. Hoy

Pantalla principal. Debe responder:

```text
¿Cómo va mi negocio hoy?
```

Muestra venta del día, tickets, caja, alertas y tareas rápidas. Esta pantalla debe ser entendible para cualquier dueño sin saber de módulos, sync ni arquitectura. Si no se entiende esta pantalla, la app falló. Así de simple, como puesto de tacos sin salsa.

### 2. Ventas

Pantalla para ver ritmo comercial. Debe mostrar:

- venta acumulada
- comparación contra ayer
- tickets
- ticket promedio
- ventas por horario
- categoría fuerte
- lectura de tendencia

No debe convertirse en tablero financiero pesado. Para eso está PC. En celular la lectura debe ser rápida.

### 3. Caja

Pantalla para ver estado de caja y cortes. Debe mostrar:

- caja esperada
- caja contada
- último corte
- movimientos de efectivo
- retiros
- gastos
- diferencias

No debe venderse como vigilancia agresiva. El enfoque correcto es control sano: menos sospecha, más evidencia.

### 4. Inventario

Pantalla de inventario útil. No debe mostrar todo el catálogo como si fuera una bodega tirada en la banqueta. Debe priorizar:

- productos críticos
- productos a reponer
- productos normales
- sobrestock
- productos estrella
- posibles faltantes

El cliente no necesita leer 8,000 SKUs en el celular. Necesita saber qué se le acaba, qué le sobra y qué le puede costar venta.

### 5. Alertas

Pantalla de excepciones. Debe ordenar alertas por severidad:

- crítica
- alta
- media
- info

Las alertas deben conectar con acción. Una alerta sin acción es chisme caro.

Ejemplo bueno:

```text
Producto estrella por agotarse. Reponer hoy o transferir desde bodega.
```

Ejemplo malo:

```text
Stock bajo.
```

Eso es como gritar “aguas” y no decir si viene un carro o la suegra.

### 6. Reportes

Pantalla de corte ejecutivo móvil. Debe incluir:

- resumen diario
- producto más vendido
- categoría fuerte
- stock crítico
- alertas importantes
- cierre de caja
- lectura semanal

El reporte móvil debe ser digerible. Si el dueño necesita filtros avanzados, se manda a PC.

### 7. MultiSucursal

Pantalla avanzada para negocios con más de una tienda. Debe incluir:

- sucursales
- estado operativo
- venta por tienda
- tickets
- alertas por tienda
- caja
- sync
- ranking

MultiSucursal se queda separado para no espantar al cliente de una sola tienda. No todos quieren sentirse franquicia cuando apenas están sobreviviendo al proveedor que llega tarde.

## Funcionamiento futuro esperado

En esta iteración los datos siguen siendo demo data local de frontend. El objetivo es consolidar UX, narrativa y estructura. En futuras iteraciones se conectará a APIs reales o endpoints agregadores.

### Fuentes futuras

```text
Tablet POS
  -> ventas locales
  -> caja local
  -> stock local
  -> eventos/outbox

PC Backoffice
  -> consolidación
  -> reportes
  -> auditoría
  -> sync
  -> permisos
  -> multisucursal

PRISMA App
  -> consulta resumen
  -> muestra alertas
  -> reporta indicadores
  -> no ejecuta venta
```

## Endpoints sugeridos para fases futuras

```text
GET /api/mobile/summary
GET /api/mobile/sales/today
GET /api/mobile/cash/current
GET /api/mobile/inventory/watchlist
GET /api/mobile/alerts
GET /api/mobile/reports/daily
GET /api/mobile/branches
GET /api/mobile/branches/:branchId/summary
```

## Permisos sugeridos

```text
mobile.summary.view
mobile.sales.view
mobile.cash.view
mobile.inventory.watchlist.view
mobile.alerts.view
mobile.reports.view
mobile.branches.view
```

Para acciones futuras:

```text
mobile.alert.acknowledge
mobile.report.share
mobile.branch.switch
```

La app móvil debe ser principalmente lectura. Si algún día permite acciones, deben ser acciones controladas y auditables.

## Beneficio para el cliente

PRISMA App sirve para que el dueño no dependa de llamadas, WhatsApps, capturas borrosas ni promesas del encargado que siempre responde “todo bien” mientras la caja está bailando jarabe tapatío.

Beneficios claros:

- saber cuánto vendió
- saber si la caja va bien
- saber qué producto urge
- saber si hay alertas importantes
- recibir reporte diario
- revisar varias sucursales si existen
- tomar decisiones sin estar pegado al mostrador

## Beneficio comercial para vender PRISMA

La app móvil aumenta valor percibido porque convierte PRISMA en algo que acompaña al dueño fuera del local. No vendemos solo caja. Vendemos tranquilidad operativa.

Frase recomendada:

```text
PRISMA App: tu negocio al día, desde tu celular.
```

Frase corta para WhatsApp:

```text
Consulta ventas, caja, inventario y alertas desde tu celular, sin estar en el local.
```

Frase para demo:

```text
Tablet vende sola, PC administra cuando existe y PRISMA App te mantiene enterado desde el celular.
```

## Criterios de aceptación de esta iteración

La iteración 02 se considera correcta si:

- `/prisma-app` existe.
- La pantalla usa el nombre PRISMA App.
- La UI muestra secciones claras.
- MultiSucursal aparece separado como avanzado.
- Tablet y PC no cambian de rol.
- El demo data está en `src/lib/prisma-app`.
- Existen contratos de sección.
- Existe documentación completa.
- Existe fixture amplio para futuras pruebas.
- Existe verificador `.mjs`.

## Comando de verificación directa

```powershell
node "F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\tools\verify_prisma_app_mobile_02_sections.mjs" "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Próxima iteración recomendada

La siguiente entrega debe ser:

```text
PRISMA_APP_MOBILE_03_DEMO_DATA
```

Objetivo: robustecer datos demo con más variedad, estados, series temporales, escenarios comerciales y preparación para reportes reales. Aunque esta entrega ya incluye fixture grande, la 03 debe convertirlo en datos consumibles por componentes y mocks más realistas.

## Nota de validación

MultiSucursal separado: esta frase queda explícita para validar que el módulo avanzado no se confunde con la identidad base de PRISMA App.
