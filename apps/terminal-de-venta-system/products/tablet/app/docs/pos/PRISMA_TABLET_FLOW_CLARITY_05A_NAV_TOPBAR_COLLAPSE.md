# PRISMA Tablet Flow Clarity 05A - Navigation, Topbar and Collapse

## Objetivo

Corregir la descubrilidad de pantallas de Tablet sin convertir la app en mini PC.

La navegacion anterior era contextual y escondia rutas. Eso reducia ruido, pero hacia dificil encontrar pantallas durante operacion y QA visual. La nueva regla mantiene foco POS, pero deja visibles las puertas principales.

## Decision de producto

- `Vender` queda como accion primaria permanente.
- El sidebar muestra rutas agrupadas: Operacion, Consulta rapida y Soporte.
- El logo de PRISMA contrae o expande la navegacion lateral.
- La barra superior se vuelve una sola barra compacta con estado operativo integrado.
- `Inicio` funciona como mapa de trabajo, no como escondite de rutas.

## Navegacion esperada

### Operacion

- Vender
- Inicio
- Turno y caja
- Ventas de hoy

### Consulta rapida

- Catalogo
- Existencias

### Soporte

- Pendientes
- Offline / Export
- Estado del sistema
- Licencia

## Topbar esperado

La parte superior debe tener una sola barra compacta que incluya titulo, subtitulo corto, estado de tienda/terminal, chips de turno/conexion/pendientes/catalogo, selector de apariencia, accesos rapidos y status pill cuando aplique.

La barra de status grande ya no debe renderizarse debajo del header.

## Sidebar colapsable

- Expandido: muestra logo, textos, grupos y labels completos.
- Colapsado: queda como rail con iconos, badges y tooltips.
- El toggle es el bloque de marca PRISMA.
- La accion de Inicio vive en el item `Inicio`, no en el logo.

## Preservacion de skins

### Light

- Usa blanco/frosted premium.
- El primario usa azul operacional.
- Badges y estados activos de Light no deben regresar a oro/tan.

### Dark

- Conserva dark glass.
- Conserva oro para accion primaria y estados activos.
- No deben filtrarse superficies blancas de Light.

## No toca

- backend;
- DB;
- Prisma schema;
- sync contracts;
- ventas/carrito/cobro;
- shared-kernel;
- PC;
- Mobile;
- packshots o image resolver.

## Validacion esperada

- Desde cualquier pantalla se ven las rutas principales.
- El logo contrae y expande el sidebar.
- El topbar ocupa una sola franja compacta.
- Inicio muestra flujo de trabajo y herramientas disponibles.
- Todo elemento clicable tiene affordance clara.
