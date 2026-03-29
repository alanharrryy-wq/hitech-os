# 00_PLATFORM_CONSTITUTION.md

## Propósito constitucional

Este documento fija la ley arquitectónica de ForgeOS.  
Si una futura decisión de implementación, refactor o packaging contradice este texto, la implementación está mal y este texto manda.

## Misión de la plataforma

ForgeOS existe para **construir, hospedar, operar y evolucionar múltiples productos** sobre una base común gobernada, con fronteras explícitas y sin contaminar el host con lógica de dominio.

## Qué es ForgeOS

ForgeOS es una plataforma compuesta por tres capas mayores:

1. **Forge Kernel**  
   Núcleo domain-agnostic que gobierna bootstrap, lifecycle, contratos, estado de sesión, extensiones, observabilidad, aislamiento de fallas y host shell.

2. **Forge Commons**  
   Capa de capacidades compartidas, neutrales al dominio, con owner, contratos, lifecycle y packaging propios.

3. **Forge Products**  
   Productos aislados que contienen su dominio, estado, adapters, vistas, contratos locales y packaging propio.

## Qué no es ForgeOS

- No es un solo producto disfrazado de plataforma.
- No es un host con plugins libres sin gobierno.
- No es un “monolito con carpetas”.
- No es una colección de widgets que se enchufan directo al main window.
- No es un service locator gigante con nombres string como contrato principal.
- No es una estrategia de “limpiar poquito a poquito” el repo legado.

## Hard Architectural Laws

1. **El host es domain-agnostic.**
2. **Los productos son dueños de su lógica de dominio.**
3. **Forge Commons no puede contrabandear semántica de producto hacia Forge Kernel.**
4. **Toda interacción cross-layer pasa por un contrato declarado, versionado y validable.**
5. **Todo slice de estado tiene dueño nombrado.**
6. **Todo recurso con lifecycle tiene teardown explícito.**
7. **Ningún producto puede leer o mutar internals del host fuera de las extension points aprobadas.**
8. **Ningún capability compartido puede depender de un producto concreto.**
9. **La compatibilidad se declara; no se asume.**
10. **La deuda legacy se aísla o se elimina; no se normaliza dentro del target limpio.**

## Leyes de plataforma

### Ley 1. Separación por capa
Cada módulo pertenece exactamente a una capa: Kernel, Commons o Product.  
Las capas no son etiquetas decorativas; definen ownership, dependencias, lifecycle y packaging.

### Ley 2. Ownership explícito
Toda decisión relevante debe responder cuatro preguntas:
- quién posee el cambio;
- quién posee el contrato;
- quién posee el estado;
- quién posee el teardown.

Si una de las cuatro no tiene dueño, el diseño está incompleto.

### Ley 3. Source of truth única
Un mismo dato no puede tener dos autoridades de escritura activas.  
Puede haber caches, proyecciones o snapshots, pero la autoridad es única y nombrada.

### Ley 4. Productos aislados
Los productos se integran al host por contribuciones y contratos.  
No por reach-through, no por `getattr`, no por `main_window`, no por service lookups ambiguos.

### Ley 5. Commons mínimos y justificados
Una capacidad solo sube a Forge Commons si:
- es neutral al dominio;
- tiene más de un consumidor real o necesidad transversal de plataforma;
- tiene contrato explícito;
- tiene lifecycle y teardown independientes.

### Ley 6. Host limpio
Forge Kernel puede saber:
- identidad, versión y compatibilidad de un producto;
- contratos que expone;
- contributions que solicita;
- permisos declarados.

Forge Kernel no puede saber:
- reglas de negocio del producto;
- strings de producto usados como branching;
- detalles internos de su UI;
- stores internos del producto.

### Ley 7. Lifecycle gobernado
La activación, suspensión, reanudación y disposal no se dejan a constructores ni a side effects casuales.  
El lifecycle es una autoridad explícita del kernel.

### Ley 8. Teardown verificable
Todo cierre debe poder demostrar:
- procesos detenidos;
- subscriptions removidas;
- handles liberados;
- stores flushed si aplica;
- surfaces descartadas;
- recursos temporales limpiados.

### Ley 9. Packaging con evidencia
Nada se considera instalable si no trae:
- manifest;
- declaración de compatibilidad;
- BOM;
- plan de rollback;
- ownership claro;
- migraciones declaradas cuando aplique.

### Ley 10. Compatibilidad sin romanticismo
La plataforma no promete compatibilidad backward por nostalgia.  
Solo se soporta lo que se declare en manifests y gates.

## Anti-leyes / comportamientos prohibidos

- Meter lógica de dominio dentro del host.
- Inferir grupos, categorías o rutas con heurísticas basadas en nombres de producto.
- Permitir que un producto lea controllers, widgets o stores del host por conveniencia.
- Reusar una capability compartida como cajón de utilidades de un solo producto.
- Guardar estado de producto en stores del kernel.
- Guardar estado de kernel en stores del producto.
- Saltarse contratos porque “es más rápido”.
- Dejar teardown “implícito” en el garbage collector o en el cierre de la app.
- Portar shims legacy al target limpio sin fecha de muerte.
- Tratar errores como “pass” silencioso en fronteras críticas.

## Principios de arquitectura

1. **Contract-first**  
   Primero se define la interacción. Después se implementa.

2. **Boundary-first**  
   Primero se fijan los límites. Después se mueven features.

3. **Owner-first**  
   Primero se nombra al dueño. Después se comparte el acceso.

4. **Lifecycle-aware**  
   Nada entra al runtime sin saber cómo se activa, suspende, degrada y destruye.

5. **Packaging-aware**  
   Todo lo que se construye debe poder empaquetarse, versionarse, instalarse y revertirse.

6. **Failure-contained**  
   Las fallas de un producto o capability no deben convertirse en fallas sistémicas del host.

7. **Observability-required**  
   Toda interacción crítica deja huella suficiente para diagnóstico.

8. **Promotion-by-proof**  
   Lo shared se gana con evidencia. No se declara por antojo.

## Principios de dependencias

- Kernel no depende de productos.
- Commons no depende de productos.
- Productos pueden depender del Kernel público y de Commons contratados.
- Domain no depende de UI, host, OS ni red.
- Adapters encapsulan side effects.
- Cross-layer import directo sin contrato es inválido.
- Los internals privados de una capa no son API pública para otra.
- Las dependencias blandas deben declararse como opcionales y validarse en runtime.

## Principios de ownership de estado

- Todo state slice tiene nombre, owner, storage, schema y policy de restore.
- Un reader no se vuelve owner por leer mucho.
- Un widget nunca es source of truth.
- Un cache nunca es autoridad.
- El host solo posee estado del host.
- Un producto solo posee estado de su dominio y de sus vistas internas.
- Un capability posee únicamente su runtime y su persistencia declarada.

## Principios de aislamiento de productos

- Cada producto tiene package, manifest y contract index propios.
- Cada producto declara permissions.
- Cada producto declara error boundaries.
- Cada producto declara teardown.
- Ningún producto toca el layout global fuera de contributions aprobadas.
- Ningún producto puede invocar a otro producto de forma lateral.
- Todo contexto publicado por un producto al host es deliberado y mínimo.

## Principios de lifecycle

- Discover no significa activate.
- Register no significa render.
- Render no significa own.
- Suspend no significa destroy.
- Dispose no significa uninstall.
- Fault no significa crash global.
- Rehydrate no significa escribir sobre la autoridad de otro.

## Principios de teardown / disposal

- Todo subscription tiene unsubscribe nominativo.
- Todo proceso tiene timeout, kill policy y evidence log.
- Todo store conoce flush/close/migrate.
- Toda surface conoce bind/unbind/dispose.
- Todo capability declara qué deja persistido y qué purga.
- Toda uninstall elimina solo lo que posee.

## Principios de extensibilidad

- Extender no equivale a contaminar.
- Una extension point existe porque el kernel la declara, no porque un producto la “descubre”.
- Contributions se validan antes de activarse.
- Un producto no puede crear extension points nuevas de facto desde su lado.
- Capabilities y productos deben poder no estar instalados sin romper el kernel.
- La ausencia de un producto no debe dejar branches muertos dentro del host.

## Principios de versionado

- SemVer por paquete.
- Major cuando rompe contratos o compatibilidad.
- Minor para capacidades o contratos nuevos backward-compatible.
- Patch para correcciones internas sin cambio contractual.
- La versión doctrinal de arquitectura es independiente de la versión de cada paquete.

## Principios de compatibilidad

- Toda compatibilidad se declara por rango.
- La instalación valida rangos antes de activar.
- Las migraciones de estado también tienen compatibilidad y orden.
- El rollback debe considerar schema y data, no solo binarios.
- No existe “compatibilidad implícita por parecido”.

## Lenguaje de gobierno para futuros productos

Usar estas fórmulas y no otras:

- **“El producto X es dueño de…”**
- **“El contrato Y autoriza…”**
- **“La capability Z expone…”**
- **“El kernel no sabe…”**
- **“La autoridad de estado de A es…”**
- **“El teardown de B requiere…”**
- **“La compatibilidad declarada de C es…”**
- **“Está prohibido…”**

Todo documento futuro que hable de ForgeOS debe escribir en ese marco.  
Si un documento no puede decir quién manda, quién posee y cómo se destruye algo, ese documento todavía no sirve.
