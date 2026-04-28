# PRISMA - Ventajas competitivas frente a plataformas POS similares

**Documento interno**
**Version:** 1.0
**Fecha:** 2026-04-26
**Uso:** estrategia, producto, marketing, ventas, roadmap y battlecards internas.
**No publicar tal cual:** este documento menciona marcas y compara con franqueza. Sirve para entender donde PRISMA puede competir, donde todavia debe madurar y como hablar sin vender humo con moño.

---

## 0. Resumen breve para humanos con conocimiento medio

PRISMA no debe competir como "otro punto de venta". Ese es el callejon donde todos se pelean por quien imprime el ticket mas bonito, como si el negocio moderno se resolviera con papel termico y buenas intenciones.

La ventaja estrategica de PRISMA esta en posicionarse como:

> **Una plataforma POS modular que convierte la operacion comercial en un sistema gobernado, extensible y preparado para crecer por giro, sucursal y dispositivo.**

La mayoria de plataformas similares ya resuelven bien varias cosas:

- cobrar
- imprimir tickets
- controlar inventario
- hacer cortes de caja
- emitir facturas
- manejar clientes
- soportar varias cajas
- trabajar con hardware POS
- en algunos casos operar offline
- en algunos casos manejar sucursales o nube

Eso significa que PRISMA no debe venderse como "tenemos inventario". Eso ya lo dicen todos. Vender eso como gran diferenciador seria como presumir que una taqueria tiene tortillas.

La ventaja competitiva real debe estar en otro nivel:

1. **Arquitectura modular real**
   - Core comun.
   - Modulos reutilizables.
   - Plugins verticales.
   - Contratos para extender sin romper.

2. **PC y Tablet con roles distintos**
   - PC gobierna, configura, audita y resuelve.
   - Tablet opera, vende, cobra, recibe, consulta y ejecuta en piso.
   - No son dos pantallas sueltas: son dos superficies coordinadas.

3. **Verticalizacion sin deformar el core**
   - Farmacia, restaurante, gym, taller, retail tecnico, rutas, B2B, reservas, produccion ligera.
   - Cada giro entra como plugin/capacidad, no como parche metido a machetazos.

4. **Offline con reglas**
   - No basta decir "funciona sin internet".
   - PRISMA debe declarar que se permite offline, que se bloquea, que se encola, que se audita y como se sincroniza despues.

5. **Sync observable**
   - No solo "se sincroniza".
   - Debe haber outbox, eventos, conflictos, checkpoints, auditoria y resolucion desde PC.

6. **Gobierno operativo**
   - Permisos.
   - Eventos.
   - Auditoria.
   - Politicas de pantalla.
   - Contratos de plugins.
   - Trazabilidad.

7. **Hardware y fiscal desacoplados**
   - Impresoras, basculas, cajones, lectores, KDS, biometria, torniquetes, CFDI y timbrado no deben contaminar el core.
   - Entran por adaptadores/capas.

8. **Dos experiencias visuales**
   - **PRISMA Black:** impacto premium, demo ejecutiva, percepcion tecnologica.
   - **PRISMA Light:** claridad operativa, velocidad, lectura facil, piso de venta.
   - Mismo core, distinta experiencia visual.

La idea madre:

> **Muchos POS cobran. Algunos administran. PRISMA debe diferenciarse por gobernar, extender y coordinar la operacion.**

---

## 1. Tesis competitiva central

### 1.1 Lo que NO debe ser la pelea

PRISMA no debe entrar a competir diciendo:

- "tambien tenemos inventario"
- "tambien hacemos tickets"
- "tambien tenemos clientes"
- "tambien podemos facturar"
- "tambien tenemos reportes"
- "tambien tenemos caja"

Eso ya es piso minimo. Si PRISMA presume eso como si fuera descubrimiento cientifico, el mercado le va a contestar con un bostezo del tamaño de una bodega.

### 1.2 Lo que SI debe ser la pelea

PRISMA debe competir en esta idea:

> **El problema ya no es cobrar. El problema es crecer sin que la operacion se vuelva un tamal de modulos pegados, sucursales desordenadas, reglas de giro improvisadas y sincronizacion misteriosa.**

Entonces PRISMA debe defender esta tesis:

> **PRISMA no es una caja registradora digital. Es una plataforma de operacion comercial modular, gobernada por contratos, preparada para PC + Tablet, offline con reglas, sync observable y verticalizacion por plugins.**

### 1.3 Traduccion de barrio ejecutivo

Un POS tradicional es como una tiendita bien acomodada con anaqueles, caja y libreta.

PRISMA debe aspirar a ser como una central de operacion:

- quien vendio
- que vendio
- donde se movio el inventario
- que permiso se uso
- que paso offline
- que evento se genero
- que plugin intervino
- que se debe auditar
- que conflicto debe resolver PC
- que debe poder operar Tablet sin romper nada

La diferencia no es "boton bonito".
La diferencia es **gobierno operativo**.

---

## 2. Mapa del mercado competitivo

Este documento agrupa competidores por tipo, porque meter a todos en una sola bolsa seria como comparar una taqueria, una refineria y una app de yoga nomas porque todas tienen "clientes".

### 2.1 POS tradicionales mexicanos

Ejemplos:

- SICAR
- eleventa
- CONTPAQi Comercial Start/Pro
- algunos distribuidores locales de punto de venta

Suelen ganar por:

- reconocimiento local
- enfoque fiscal mexicano
- familiaridad con negocios pequeños
- hardware POS tradicional
- soporte via distribuidores
- costo entendible
- flujo de caja ya conocido por el mercado

PRISMA puede competir si no intenta ser "lo mismo pero mas oscuro", sino:

- mas modular
- mas moderno
- mas extensible
- mas preparado para multiples giros
- mas claro en PC + Tablet
- mas serio en contratos, auditoria y sync

### 2.2 POS globales / SaaS

Ejemplos:

- Shopify POS
- Square
- Loyverse
- Poster POS
- Lightspeed
- Odoo POS

Suelen ganar por:

- UI cuidada
- onboarding rapido
- nube
- ecosistemas de apps
- omnicanalidad
- pagos integrados
- escalabilidad SaaS
- operacion en tablet/movil

PRISMA puede competir si aterriza mejor el contexto local y vertical:

- fiscal mexicano desacoplado
- hardware comun del mercado local
- necesidades reales de abarrotes, refaccionaria, farmacia, talleres, rutas, credito, pedidos y caja local
- operacion offline pensada para negocios con red inestable
- PC como centro de mando y Tablet como operacion de piso

### 2.3 ERP / administracion comercial

Ejemplos:

- CONTPAQi Comercial Pro
- Bind ERP
- Odoo
- Zoho Inventory / Books con POS externo
- ERPs verticales

Suelen ganar por:

- compras
- ventas
- inventario
- reportes
- contabilidad/fiscal
- procesos administrativos mas amplios

PRISMA puede competir en el borde donde el ERP se vuelve pesado y el POS simple se queda corto:

> **PRISMA debe vivir entre la caja rapida y el ERP completo: lo bastante operativo para vender rapido, lo bastante arquitectonico para crecer.**

### 2.4 Verticales especializadas

Ejemplos:

- Soft Restaurant
- Poster POS
- sistemas de farmacia
- sistemas de gimnasios
- sistemas de talleres
- sistemas de reservas

Suelen ganar por:

- profundidad especifica del giro
- lenguaje operativo del sector
- flujos especializados ya probados
- reputacion en un nicho

PRISMA no debe fingir que ya les gana por profundidad vertical desde el dia uno. Eso seria ponerse capa antes de aprender a volar.

PRISMA debe competir por:

- permitir multiples verticales sobre un core comun
- evitar que una vertical contamine todo
- abrir plugins especializados con contratos
- escalar horizontalmente a muchos giros
- ofrecer una base comun para negocios hibridos

---

## 3. Comparativa ejecutiva por competidor

> Nota interna: las columnas "donde ganan ellos" no son derrota. Son realidad. Y la realidad, aunque cae mal, cobra menos intereses que la fantasia.

| Competidor | Donde suele ganar | Donde PRISMA puede diferenciarse | Riesgo para PRISMA |
|---|---|---|---|
| SICAR | Mercado mexicano, funciones maduras, inventario, caja, CFDI, nube, app, offline local, refaccionarias/farmacia | Plataforma modular, plugins por giro, PC/Tablet por contrato, sync observable, UI moderna, hardware/fiscal desacoplado | SICAR ya tiene confianza, base instalada y muchas funciones que PRISMA debe igualar gradualmente |
| eleventa | Simplicidad, adopcion rapida, abarrotes, bajo costo, "sin saber computacion", inventario y facturacion facil | PRISMA puede vender crecimiento, control, multi-vertical y arquitectura mas seria | Si PRISMA se siente complejo, eleventa gana por facilidad |
| CONTPAQi Comercial | Fiscal mexicano, ciclo comercial, inventario, CFDI, cuentas por cobrar, reputacion administrativa | PRISMA puede ganar en experiencia POS moderna, Tablet, plugins, operacion de piso y extensibilidad visual | CONTPAQi tiene marca fiscal fuerte; PRISMA debe evitar verse debil ante SAT/CFDI |
| Odoo POS | ERP modular global, web, PC/tablet, inventario, contabilidad, franquicias, offline | PRISMA puede ser mas enfocado a operacion mexicana, menos generico, mas controlado en PC/Tablet y verticales locales | Odoo ya es modular y ecosistema; PRISMA debe explicar por que no es "otro Odoo chiquito" |
| Shopify POS | Omnicanal fuerte, e-commerce, retail moderno, pagos, admin central | PRISMA puede ganar en offline local realista, fiscal/hardware local, giros no e-commerce y operacion mas mexicana | Shopify gana si el cliente ya vive de ecommerce |
| Loyverse | Gratis/freemium, tablet/movil, inventario, lealtad, multi-store, simple y global | PRISMA puede diferenciarse por contratos, verticalizacion, gobernanza, PC mando + Tablet piso | Loyverse gana por precio y velocidad de adopcion |
| Soft Restaurant | Restaurante profundo, marca del sector, comandas, mesas, inventario, reportes, pagos/facturacion | PRISMA puede ganar si ofrece restaurante como plugin dentro de plataforma multi-giro | Soft Restaurant gana por especializacion restaurantera probada |
| Poster POS | Restaurante/retail cloud, tablet, reportes, inventario, offline funcional, cocina | PRISMA puede ganar con fiscal/localizacion, PC governance, plugins y estrategia multi-vertical | Poster tiene SaaS simple y vertical listo |
| Square POS | Facilidad extrema, pagos integrados, hardware, analitica simple, small business | PRISMA puede ganar en Mexico, fiscal, inventario serio, verticales y operacion hibrida | Square gana donde pagos y setup inmediato sean prioridad |
| Bind ERP | ERP mexicano en nube, ventas, inventario, pedidos, reportes, comercializadoras | PRISMA puede ganar como POS operativo modular mas agil, con Tablet y plugins de piso | Bind gana si el cliente busca ERP administrativo mas que POS operativo |

---

## 4. Ventajas competitivas de PRISMA por eje

### 4.1 Arquitectura modular real

#### Que hacen muchos competidores

Muchos competidores dicen "modulos", pero en la practica pueden funcionar como:

- secciones del mismo sistema
- paquetes comerciales
- pantallas extra
- funciones prendidas/apagadas
- integraciones laterales
- verticales tratadas como variantes del producto

Eso no esta mal. Sirve. Pero no siempre significa arquitectura extensible limpia.

#### Que debe hacer PRISMA

PRISMA debe tratar cada capacidad como parte de un sistema gobernado:

- core comun
- modulos funcionales
- plugins verticales
- contratos compartidos
- slots de extension
- permisos
- eventos
- auditoria
- politicas offline
- politicas sync

#### Ventaja competitiva

PRISMA puede decir internamente:

> "No queremos acumular funciones. Queremos ordenar capacidades."

Esto es mas potente que "tenemos mas botones".

#### Como venderlo

Mensaje interno:

> PRISMA compite contra el software que crece como cuarto añadido en azotea: util, pero peligroso si sigues construyendo. PRISMA debe crecer como edificio con planos.

Mensaje comercial publicable:

> **PRISMA esta diseñado para crecer por modulos y plugins, sin romper la base operativa del negocio.**

---

### 4.2 Core comun + plugins verticales

#### Que hacen muchos competidores

Algunos sistemas son muy buenos en un giro:

- restaurante
- farmacia
- abarrotes
- retail
- ERP comercial

Pero cuando el negocio cruza fronteras, aparecen problemas:

- restaurante que tambien vende productos empacados
- farmacia con pedidos y rutas
- refaccionaria con servicio/taller
- gym con tienda y membresias
- franquicia pequeña con multi-sucursal
- distribuidor que tambien tiene mostrador
- taller que vende piezas, servicio y citas

Ahi muchos sistemas empiezan a estirarse como liga vieja.

#### Que debe hacer PRISMA

PRISMA debe diseñarse para que la vertical no sea una version paralela, sino una extension:

```text
Core comercial comun
  - ventas
  - inventario
  - caja
  - clientes
  - pagos
  - permisos
  - eventos
  - sync

Plugins verticales
  - farmacia: lotes, caducidades, restricciones
  - restaurante: mesas, comandas, KDS, modifiers
  - gym: membresias, accesos, renovaciones
  - taller: ordenes de servicio, piezas, mano de obra
  - rutas: reparto, cobranza, liquidacion
  - B2B: pedidos, listas, credito, cartera
  - renta/reservas: disponibilidad, agenda, garantias
```

#### Ventaja competitiva

PRISMA puede atacar una franja muy interesante:

> negocios que ya no caben en un POS simple, pero tampoco quieren casarse con un ERP pesado o una vertical cerrada.

#### Como venderlo

> **Un solo core. Multiples giros. Sin convertir tu sistema en Frankenstein.**

---

### 4.3 PC como centro de mando y Tablet como consola de operacion

#### Que hacen muchos competidores

Muchos POS funcionan en PC, tablet o movil. Eso ya no es exotico. Hasta la lonchera del futuro va a tener dashboard, porque la humanidad decidio que todo necesita login.

Pero una cosa es "corre en varios dispositivos" y otra es **asignar responsabilidades distintas por superficie**.

#### Que debe hacer PRISMA

PRISMA debe tener dos superficies promovidas y diseñadas con intencion:

#### PC

PC debe ser:

- configuracion
- gobierno
- administracion
- auditoria
- resolucion de conflictos
- permisos
- reportes
- fiscal
- hardware
- sync
- plugins
- analisis

#### Tablet

Tablet debe ser:

- venta
- cobro
- caja
- pedidos
- recepcion rapida
- inventario rapido
- clientes
- cobranza
- operacion offline
- ejecucion de plugins en piso

#### Ventaja competitiva

La ventaja no es "tenemos PC y Tablet".

La ventaja es:

> **PC configura y audita lo que Tablet ejecuta. Tablet reporta lo que PC gobierna.**

Eso permite vender una operacion coordinada, no pantallas duplicadas.

#### Como venderlo

> **PRISMA separa mando y operacion: PC para controlar, Tablet para ejecutar.**

---

### 4.4 Offline con reglas, no offline magico

#### Que hacen muchos competidores

Muchos competidores dicen "funciona offline". Pero en realidad offline puede significar muchas cosas:

- solo ventas simples
- solo efectivo
- no clientes nuevos
- no inventario completo
- no devoluciones
- no pagos integrados
- sincronizacion posterior limitada
- riesgo si se cierra sesion o se apaga dispositivo
- datos marcados como pendientes

Eso no es malo. Es normal. Offline siempre tiene limites. El problema es cuando se vende como si fuera magia negra confiable.

#### Que debe hacer PRISMA

PRISMA debe declarar:

- que acciones se permiten offline
- que acciones se bloquean
- que se encola
- que genera evento
- que requiere revision posterior
- que conflictos pueden aparecer
- quien resuelve conflictos
- como se audita
- como se sincroniza

#### Ventaja competitiva

PRISMA puede competir no prometiendo "offline total", sino:

> **offline gobernado, auditable y sincronizable.**

#### Como venderlo

Mensaje interno:

> Offline sin reglas es vender con los ojos vendados y rezarle al router.

Mensaje comercial:

> **PRISMA esta pensado para operar con tolerancia a fallas: lo permitido sigue, lo sensible se protege y todo queda trazado para sincronizarse.**

---

### 4.5 Sync observable

#### Que hacen muchos competidores

Los sistemas suelen hablar de sincronizacion como beneficio:

- sincroniza sucursales
- sincroniza inventario
- sincroniza nube
- sincroniza admin
- sincroniza back office

Pero muchas veces para el usuario final sync es una caja negra:

> "A ver si ya paso."

Eso en operacion real es veneno lento. Cuando hay ventas, caja, stock, rutas y sucursales, no basta con "ya sincroniza".

#### Que debe hacer PRISMA

PRISMA debe tener una narrativa de sync observable:

- outbox
- cola de eventos
- estado de sync
- checkpoints
- conflictos
- reintentos
- resolucion desde PC
- auditoria del evento
- origen por dispositivo
- impacto por entidad

#### Ventaja competitiva

No vender sync como nube bonita. Vender sync como control.

#### Como venderlo

> **PRISMA no solo sincroniza: muestra que paso, que falta, que fallo y quien debe resolverlo.**

---

### 4.6 Contratos vivos

#### Que hacen muchos competidores

En muchos sistemas, las reglas estan implicitas:

- "este boton hace esto"
- "esta pantalla toca esta tabla"
- "este modulo afecta inventario"
- "esta funcion requiere permiso"
- "esta vertical mete estos campos"

Funciona mientras el sistema esta chico. Despues se vuelve mercado sobre ruedas.

#### Que debe hacer PRISMA

PRISMA debe exigir contratos:

- contrato de plugin
- contrato de pantalla
- contrato de evento
- contrato de permiso
- contrato de offline
- contrato de sync
- contrato de auditoria
- contrato de modulo

#### Ventaja competitiva

La ventaja es que PRISMA puede crecer con disciplina.

> **El contrato evita que un plugin de farmacia termine rompiendo caja, inventario o venta como niño con martillo nuevo.**

#### Como venderlo internamente

> Toda extension debe declarar que lee, que escribe, que evento genera, que permiso exige, que pasa offline y como se audita.

#### Como venderlo externamente

> **PRISMA esta diseñado para extenderse con reglas claras, manteniendo estable el nucleo del negocio.**

---

### 4.7 Auditoria como producto, no como reporte olvidado

#### Que hacen muchos competidores

Muchos sistemas tienen reportes, roles, permisos o historial. Eso es basico en POS serio.

Pero PRISMA puede llevarlo como parte de su ADN:

- evento por accion sensible
- permiso por impacto
- origen por usuario/dispositivo
- trazabilidad PC/Tablet
- auditoria en sync
- resolucion de conflictos
- bitacora de plugin

#### Ventaja competitiva

En negocios reales, el problema no es solo que algo pase. Es saber:

- quien lo hizo
- cuando
- desde donde
- con que permiso
- si estaba offline
- que cambio
- que afecto
- si el cambio sincronizo
- si genero conflicto

#### Como venderlo

> **PRISMA no solo registra operacion: deja rastro operativo para controlar dinero, stock, caja y decisiones sensibles.**

---

### 4.8 Hardware desacoplado

#### Que hacen muchos competidores

Muchos POS trabajan con:

- impresoras
- cajones
- lectores
- basculas
- terminales
- pantallas cliente
- KDS
- tablets

Eso es normal.

#### Riesgo comun

Cuando el hardware queda pegado al flujo central, cada integracion se vuelve dependencia peligrosa:

- "esta impresora define el ticket"
- "esta bascula modifica venta"
- "este cajon requiere hack"
- "este KDS se mete directo al pedido"
- "esta terminal manda a rezar a soporte"

#### Que debe hacer PRISMA

PRISMA debe meter hardware por adaptadores:

```text
Core de venta
  - Hardware layer
      - printer adapter
      - scale adapter
      - scanner adapter
      - cash drawer adapter
      - customer display adapter
      - biometric adapter
      - kitchen display adapter
```

#### Ventaja competitiva

La promesa no es "soporta todo". Eso seria invitar al infierno.

La promesa es:

> **PRISMA debe integrar hardware sin dejar que el hardware gobierne el sistema.**

---

### 4.9 Fiscal desacoplado

#### Que hacen muchos competidores

En Mexico, fiscal importa mucho. CONTPAQi, SICAR, eleventa y otros tienen discurso fuerte alrededor de CFDI, SAT, facturacion, notas y cumplimiento.

PRISMA no debe minimizar eso. Si lo hace, pierde confianza rapido.

#### Que debe hacer PRISMA

PRISMA debe tratar fiscal como capa critica, pero desacoplada:

- CFDI
- catalogos fiscales
- timbrado
- notas de credito
- cancelaciones
- intentos fallidos
- reintentos
- auditoria fiscal
- relacion ticket/factura
- politica offline fiscal

#### Ventaja competitiva

> **Fiscal debe ser serio, pero no debe envenenar el core.**

#### Como venderlo

> **PRISMA separa operacion comercial y capa fiscal para mantener el sistema ordenado, auditable y preparado para cambios regulatorios.**

---

### 4.10 Experiencia visual dual: PRISMA Black y PRISMA Light

#### Que hacen muchos competidores

Muchos POS ofrecen una interfaz unica. Algunos tienen modo oscuro o claro. Pero eso suele ser tema visual, no posicionamiento de producto.

#### Que debe hacer PRISMA

PRISMA puede convertir sus dos interfaces en ventaja comercial:

- **PRISMA Black**
  - premium
  - alto impacto
  - demos ejecutivas
  - retail moderno
  - restaurantes premium
  - cadenas
  - pitch visual fuerte

- **PRISMA Light**
  - claridad
  - operacion diaria
  - mostrador
  - caja rapida
  - recepcion
  - inventario
  - lectura prolongada
  - adopcion rapida

#### Ventaja competitiva

No son "version cara" y "version media".
Son dos experiencias de la misma plataforma:

> **La misma potencia modular. Dos formas de verla trabajar.**

#### Como usarlo contra competidores

- Contra POS viejos: PRISMA se ve moderno y aspiracional.
- Contra SaaS globales: PRISMA se ve premium, pero aterrizado al mercado local.
- Contra software operativo sencillo: PRISMA Light conserva claridad.
- Contra herramientas oscuras/confusas: PRISMA Black tiene intencion, no solo fondo negro.

---

## 5. Lectura competitiva por marca

## 5.1 SICAR

### Lectura interna

SICAR es fuerte porque entiende el mercado mexicano de POS tradicional. Tiene funciones amplias: inventario, ventas, administracion, roles, permisos, CFDI, nube, app movil, lotes, caducidades, ventas en espera, multiples monedas, cortes, reportes, ordenes de servicio y mas.

No hay que subestimarlo. SICAR no es "el viejito facil de tumbar". Es mas como el vecino que ya conoce a todo el barrio, tiene herramienta para todo y ademas sabe a quien llamar cuando se va la luz.

### Donde gana SICAR

- Reconocimiento en Mexico.
- Pago unico/licenciamiento entendible.
- Funciones maduras de POS.
- Funciones de inventario robustas.
- CFDI 4.0.
- Nube SICAR para sucursales.
- App movil operativa.
- Lotes, caducidades, compatibilidades.
- Refaccionarias y farmacia tienen terreno.
- Offline local por instalacion en computadora.

### Donde PRISMA puede competir

PRISMA no debe competir diciendo "tambien tengo inventario". SICAR ya trae inventario pesado.

PRISMA debe competir en:

- arquitectura modular desde origen
- core + plugins verticales
- PC/Tablet por contrato
- sync observable
- permisos/eventos/auditoria como columna vertebral
- fiscal y hardware desacoplados
- UI Black/Light moderna
- narrativa de plataforma, no POS tradicional

### Frase interna

> SICAR es fuerte por funcion y mercado. PRISMA debe ser fuerte por arquitectura, experiencia y capacidad de evolucion.

### Frase publica segura

> PRISMA esta diseñado para negocios que buscan una base modular moderna, preparada para crecer por sucursal, giro y dispositivo.

### No decir

- "SICAR ya esta viejo"
- "SICAR no sirve"
- "PRISMA tiene todo lo de SICAR"
- "ya les ganamos"

Eso suena a pleito de cantina y ademas obliga a demostrar demasiado pronto.

---

## 5.2 eleventa

### Lectura interna

eleventa gana por sencillez. Su promesa es casi emocional: "no necesitas saber computacion". Para abarrotes, papelerias, tiendas pequeñas y negocios que vienen de papel/calculadora/Excel, eso pesa muchisimo.

### Donde gana eleventa

- Facil de usar.
- Instalacion rapida.
- Ideal para negocios pequeños.
- Retail sencillo.
- Inventario.
- Facturacion.
- Credito/fiado.
- Reportes.
- Hardware basico.
- Varias cajas.
- Curva de aprendizaje baja.

### Donde PRISMA puede competir

PRISMA puede ganar cuando el negocio ya siente que "lo simple" empieza a quedarse corto:

- multiples giros
- operacion PC + Tablet
- auditoria mas seria
- plugins
- sync con reglas
- control multisucursal
- roles avanzados
- verticales especializadas
- vision de crecimiento

### Riesgo

Si PRISMA parece complicado, eleventa gana sin despeinarse.

### Regla para PRISMA Light

PRISMA Light debe existir para esta batalla:

> claridad, rapidez, lectura facil, cero intimidacion.

### Frase interna

> Contra eleventa, PRISMA no debe presumir complejidad. Debe demostrar que puede crecer sin volverse dificil.

### Frase publica segura

> PRISMA combina una operacion clara con una arquitectura preparada para crecer cuando el negocio ya necesita mas control.

---

## 5.3 CONTPAQi Comercial Start/Pro

### Lectura interna

CONTPAQi tiene un capital de confianza muy fuerte en Mexico por administracion, contabilidad y fiscal. Cuando un cliente escucha CONTPAQi, piensa SAT, CFDI, control, procesos administrativos. Eso no se derriba con una interfaz bonita.

### Donde gana CONTPAQi

- Confianza fiscal mexicana.
- CFDI.
- Inventarios.
- Ciclo compra-venta.
- Cuentas por cobrar.
- Reportes.
- Integracion administrativa.
- Marca conocida.
- Multialmacen/lotes/series en productos mas robustos.
- Ecosistema contable/comercial.

### Donde PRISMA puede competir

PRISMA puede ganar en:

- punto de venta mas moderno
- operacion Tablet
- experiencia visual superior
- modularidad por plugins
- verticalizacion mas flexible
- PC como centro de mando
- piso de venta mas agil
- contratos vivos para extensiones
- mejor narrativa de operacion comercial, no solo administracion

### Riesgo

Si PRISMA no tiene una historia fiscal clara, CONTPAQi se ve mas confiable.

### Frase interna

> CONTPAQi vende confianza administrativa. PRISMA debe vender operacion modular moderna sin parecer debil en fiscal.

### Frase publica segura

> PRISMA separa operacion comercial, hardware y fiscal en capas claras para mantener control y capacidad de evolucion.

---

## 5.4 Odoo POS

### Lectura interna

Odoo es peligroso porque si tiene modularidad real y ecosistema. No se le puede decir "tu no eres modular". Seria falso y medio ridiculo, como acusar al mar de estar mojado.

### Donde gana Odoo

- Ecosistema ERP modular.
- Web-based.
- PC/tablet compatible.
- Inventario integrado.
- Contabilidad integrada.
- CRM, compras, ventas, ecommerce, fabricacion y mas.
- Franquicias.
- Multidispositivo.
- Offline POS.
- Comunidad y ecosistema global.

### Donde PRISMA puede competir

PRISMA puede competir si se vuelve mas:

- localizado para Mexico
- enfocado al mostrador real
- menos pesado para implementacion
- mas claro en PC/Tablet
- mas directo para giros locales
- fiscalmente aterrizado
- visualmente mas premium/adaptado
- gobernado por contratos pensados para POS modular especifico

### Riesgo

Odoo puede absorber muchos argumentos de PRISMA porque ya es plataforma modular.

### Diferenciador clave

PRISMA no debe intentar ser "ERP universal". Debe ser:

> plataforma POS modular especializada en operacion comercial de piso, con capacidad de crecer por vertical.

### Frase publica segura

> PRISMA se enfoca en convertir el punto de venta y la operacion diaria en una plataforma modular clara, con extensiones por giro y operacion PC/Tablet.

---

## 5.5 Shopify POS

### Lectura interna

Shopify POS gana cuando el cliente ya vive o quiere vivir en ecommerce. Su fuerza esta en omnicanalidad, inventario conectado con tienda online, pagos, catalogo y venta fisica/digital.

### Donde gana Shopify POS

- Ecommerce + POS.
- Omnicanal.
- Admin central.
- Inventario conectado.
- Retail moderno.
- App iOS/Android.
- Hardware.
- Ecosistema Shopify.
- Pagos y canales digitales.

### Donde PRISMA puede competir

PRISMA puede ganar en negocios que no son primordialmente ecommerce:

- abarrotes
- farmacia
- restaurante
- taller
- refaccionaria
- rutas
- B2B local
- produccion ligera
- caja/corte/offline local
- fiscal mexicano mas especifico
- hardware local
- operacion de piso

### Riesgo

Si el cliente ya esta vendido a Shopify por ecommerce, PRISMA debe integrarse o convivir, no pelear como si Shopify fuera una caja vieja.

### Frase interna

> Shopify gana en venta omnicanal. PRISMA debe ganar en operacion comercial local, modular y multi-giro.

### Frase publica segura

> PRISMA esta pensado para negocios cuya operacion diaria requiere caja, inventario, piso, sucursal, plugins por giro y control operativo mas alla del ecommerce.

---

## 5.6 Loyverse

### Lectura interna

Loyverse es fuerte porque es facil, global, movil y con entrada gratis/freemium. Tiene POS, inventario, empleados, analitica, lealtad, restaurantes, hardware y multi-store. Es el tipo de competidor que parece tranquilo y luego te roba leads por precio.

### Donde gana Loyverse

- Entrada gratuita.
- Tablet/movil.
- Facil adopcion.
- Inventario.
- Lealtad.
- Multi-store.
- Restaurante/bar.
- Reportes.
- Hardware basico.
- Idiomas y presencia global.
- Offline para ventas principales.

### Donde PRISMA puede competir

PRISMA puede ganar si comunica:

- mas gobierno operativo
- contratos
- verticalizacion seria
- fiscal/localizacion Mexico
- PC centro de mando
- Tablet piso
- sync observable
- auditoria avanzada
- plugins para giros complejos

### Riesgo

Precio y simplicidad.

### Frase interna

> Contra Loyverse, PRISMA debe justificar por que vale mas que una app rapida y gratis.

### Frase publica segura

> PRISMA esta diseñado para negocios que necesitan mas que vender desde una tablet: necesitan control, trazabilidad, permisos, sync y extensiones por giro.

---

## 5.7 Soft Restaurant

### Lectura interna

Soft Restaurant es especialista. En restaurante, tiene credibilidad. Habla el idioma del giro: mesas, comandas, servicio rapido, comedor, domicilio, inventarios, reportes, pagos, facturacion.

### Donde gana Soft Restaurant

- Especializacion restaurantera.
- Marca fuerte en Mexico/LatAm.
- Mesas.
- Comandas.
- Tipos de servicio.
- Inventario.
- Reportes.
- Facturacion.
- Distribuidores y capacitacion.
- Historial del sector.

### Donde PRISMA puede competir

PRISMA no debe decir "somos mejor restaurante" al principio.

Debe decir:

> restaurante puede ser una vertical dentro de una plataforma modular que tambien controla tienda, inventario, pedidos, membresias, rutas o produccion ligera si el negocio crece.

Eso sirve para:

- negocios hibridos
- cafeteria + tienda
- restaurante + delivery propio + inventario
- franquicia pequeña
- dark kitchen con produccion
- negocios que mezclan alimentos, retail y operacion comercial

### Riesgo

Soft Restaurant gana en profundidad restaurantera inmediata.

### Frase interna

> Contra Soft Restaurant, PRISMA debe vender plataforma multi-giro, no presumir profundidad restaurantera que todavia debe probar.

### Frase publica segura

> PRISMA puede extenderse por verticales, permitiendo que restaurante sea una capacidad especializada dentro de una operacion comercial mas amplia.

---

## 5.8 Poster POS

### Lectura interna

Poster POS tiene una narrativa SaaS fuerte: tablet, telefono, browser, restaurante/retail, reportes, inventario, offline y cocina. Es un competidor moderno.

### Donde gana Poster

- Cloud POS.
- Tablet/phone/browser.
- Restaurante y retail.
- Inventario.
- Reportes en tiempo real.
- Offline funcional.
- Kitchen tickets.
- Setup rapido.
- SaaS claro.

### Donde PRISMA puede competir

PRISMA puede competir por:

- localizacion Mexico
- fiscal mexicano
- PC governance mas fuerte
- contratos de plugin
- verticales mas amplias
- operacion offline con auditoria
- UI Black/Light como herramienta comercial
- hardware local/adaptadores

### Riesgo

Poster se vende simple y moderno. Si PRISMA se explica como tesis doctoral, pierde.

### Frase publica segura

> PRISMA combina operacion moderna en piso con una estructura de gobierno pensada para crecer por modulos, permisos, eventos y verticales.

---

## 5.9 Square POS

### Lectura interna

Square es brutal en facilidad y pagos. Su valor historico fue simplificar el acceso a POS y cobro con tarjeta. Para pequeños negocios, esa friccion baja vale muchisimo.

### Donde gana Square

- Setup rapido.
- Pagos integrados.
- Hardware propio.
- App facil.
- Inventario basico/intermedio.
- Reportes.
- Ecosistema small business.
- Costo inicial bajo en algunos mercados.

### Donde PRISMA puede competir

PRISMA puede competir si se enfoca en:

- Mexico/LATAM
- fiscal
- inventario mas operativo
- caja/cortes reales
- modulos verticales
- offline de piso
- hardware comun
- PC/Tablet coordinados
- no depender tanto del procesador de pagos como centro del producto

### Riesgo

Si pagos integrados son el punto #1 del cliente, Square puede ser mas atractivo.

### Frase interna

> Square vende cobrar facil. PRISMA debe vender operar completo.

---

## 5.10 Bind ERP

### Lectura interna

Bind es ERP mexicano en la nube, con enfoque en ventas, inventario, pedidos, reportes y comercializadoras. Puede ser mas administrativo que POS de mostrador.

### Donde gana Bind

- ERP en nube.
- Ventas.
- Inventario.
- Pedidos.
- Reportes.
- Comercializadoras.
- Listas de precios.
- Control administrativo.
- Operacion B2B.

### Donde PRISMA puede competir

PRISMA puede ganar cuando se requiere:

- mostrador rapido
- caja de piso
- Tablet operativa
- PC mando
- hardware POS
- verticales en punto de operacion
- offline
- plugin por giro
- venta presencial + control

### Riesgo

Si el cliente busca ERP administrativo puro, PRISMA debe integrarse o diferenciarse, no fingir ser contabilidad completa.

### Frase publica segura

> PRISMA se ubica en el punto donde el POS debe dejar de ser simple caja y convertirse en operacion comercial modular.

---

## 6. Matriz de ventajas competitivas defendibles

| Eje | Competidores suelen decir | PRISMA debe decir | Ventaja real |
|---|---|---|---|
| POS | "Cobra rapido" | "Cobra rapido dentro de una operacion gobernada" | No se queda en transaccion |
| Inventario | "Controla existencias" | "Inventario ligado a eventos, permisos, offline y sync" | Mayor trazabilidad |
| Multi-dispositivo | "Corre en tablet/PC" | "Tablet vende sola; PC gobierna cuando existe" | Roles claros por superficie |
| Offline | "Funciona sin internet" | "Offline con reglas, cola, evento y auditoria" | Menos riesgo operativo |
| Sync | "Sincroniza con nube" | "Sync observable con estados, conflictos y resolucion" | Mayor confianza |
| Verticales | "Tenemos modulo para giro" | "Plugins verticales sin romper core" | Escalabilidad limpia |
| Fiscal | "Factura CFDI" | "Fiscal desacoplado y auditable" | Menos contaminacion del core |
| Hardware | "Compatible con dispositivos" | "Hardware por adaptadores" | Menos dependencia fragil |
| UX | "Interfaz facil" | "Black para impacto, Light para claridad" | Dos frentes comerciales |
| Reportes | "Reportes de venta" | "Auditoria + eventos + reportes" | Mas control |
| Expansion | "Mas sucursales" | "Crecimiento por contratos y politicas" | Menos caos al escalar |

---

## 7. Ventajas competitivas por tipo de cliente

### 7.1 Dueño de negocio pequeño que ya crecio

#### Dolor

- ya no puede manejar todo en libreta/Excel
- el inventario ya le falla
- caja no siempre cuadra
- clientes piden fiado/credito
- necesita mas control

#### Competidor probable

- eleventa
- SICAR
- Loyverse
- CONTPAQi Start

#### Ventaja PRISMA

> PRISMA puede venderle una base que no solo ordena hoy, sino que no se vuelve carcel mañana.

#### Mensaje

> "Empieza con operacion clara y deja preparada la base para crecer por caja, sucursal, giro o dispositivo."

---

### 7.2 Negocio mediano con varias areas

#### Dolor

- ventas por un lado
- inventario por otro
- caja por otro
- pedidos por otro
- administracion por otro
- reportes tarde o incompletos

#### Competidor probable

- SICAR
- CONTPAQi Pro
- Bind ERP
- Odoo

#### Ventaja PRISMA

> Plataforma modular enfocada en operacion comercial, sin volverse ERP pesado desde el primer dia.

#### Mensaje

> "Controla venta, caja, inventario, pedidos y operacion con una arquitectura preparada para extenderse."

---

### 7.3 Negocio multi-giro

#### Dolor

- tienda + taller
- restaurante + retail
- gym + tienda
- distribuidor + mostrador
- farmacia + pedidos/rutas
- maquila + venta

#### Competidor probable

- vertical especializado + Excel
- ERP + POS
- sistema custom

#### Ventaja PRISMA

> Core comun + plugins verticales.

#### Mensaje

> "No fuerces tu negocio a caber en un solo giro. PRISMA esta pensado para especializar sin romper el core."

---

### 7.4 Franquicia pequeña o multi-sucursal

#### Dolor

- sucursales operan distinto
- cada encargado resuelve como puede
- inventario no se sincroniza claro
- caja requiere revision
- permisos y auditoria son debiles

#### Competidor probable

- SICAR Nube
- Odoo
- Shopify POS
- Poster POS
- CONTPAQi

#### Ventaja PRISMA

> PC governance + Tablet operation + sync observable + contratos.

#### Mensaje

> "Estandariza operacion sin apagar la flexibilidad de cada sucursal."

---

### 7.5 Negocio premium / demo ejecutiva

#### Dolor

- quiere percepcion moderna
- quiere sistema que se vea serio
- quiere diferenciarse
- quiere vender confianza a socios/franquiciatarios

#### Competidor probable

- Shopify POS
- Odoo
- Lightspeed
- Poster POS
- soluciones custom

#### Ventaja PRISMA

> PRISMA Black como interfaz premium, sin perder control modular.

#### Mensaje

> "La experiencia premium de un POS modular preparado para operar como centro de mando."

---

## 8. Como NO comparar

Para evitar que marketing se convierta en pelea de tianguis con Canva, estas frases quedan prohibidas internamente para material publico:

- "Somos mejores que SICAR."
- "SICAR ya esta obsoleto."
- "eleventa es basico."
- "CONTPAQi es viejo."
- "Odoo es complicado."
- "Shopify no sirve para Mexico."
- "Soft Restaurant solo sirve para restaurantes."
- "Loyverse es gratis pero malo."
- "PRISMA hace todo lo que ellos hacen."

No porque no haya cosas criticables, sino porque esas frases obligan a defender demasiado y suenan ardidas.

### Mejor enfoque

Usar comparativa conceptual:

- POS tradicional vs plataforma modular
- funcion aislada vs contrato vivo
- sincronizacion opaca vs sync observable
- modulo pegado vs plugin gobernado
- interfaz unica vs Black/Light
- dispositivo duplicado vs PC mando + Tablet operacion
- crecimiento por parche vs crecimiento por arquitectura

---

## 9. Claims internos y externos

### 9.1 Claims internos fuertes

Estos son para estrategia, no necesariamente para publicar tal cual:

- PRISMA debe dejar de competir por botones y competir por arquitectura.
- El enemigo no es SICAR; el enemigo es la operacion parchada.
- El POS simple cobra. PRISMA debe gobernar.
- Si una vertical rompe el core, perdimos.
- Offline sin auditoria es deuda operativa con internet apagado.
- Sync sin visibilidad es fe con loading spinner.
- PC y Tablet no son duplicados: son mando y campo.
- La diferencia no es dark mode. Es sistema.

### 9.2 Claims publicos seguros

- **El POS modular hecho para crecer.**
- **Una plataforma. Multiples giros. Un solo core.**
- **Vende, controla y escala sin parches.**
- **PC para gobernar. Tablet para operar.**
- **PRISMA Black para impacto. PRISMA Light para claridad.**
- **Mas que cobrar: controla tu operacion.**
- **Core comun, plugins por giro y operacion preparada para crecer.**
- **La misma potencia modular. Dos experiencias visuales.**
- **Del punto de venta al centro de mando.**

---

## 10. Argumentario competitivo para ventas

### Pregunta: "¿Por que no uso SICAR?"

Respuesta interna fuerte:

> Porque SICAR ya resuelve muchas funciones POS tradicionales, pero PRISMA quiere competir en arquitectura modular, experiencia moderna, PC/Tablet coordinados, sync observable y verticalizacion por plugins.

Respuesta comercial:

> SICAR es una solucion conocida. PRISMA esta pensado para negocios que quieren una base modular moderna, con core comun, plugins por giro y operacion PC/Tablet preparada para crecer.

---

### Pregunta: "¿Por que no eleventa si es mas facil?"

Respuesta interna fuerte:

> Porque eleventa es excelente para entrada rapida. PRISMA debe ganar cuando el negocio ya necesita mas gobierno, verticales, sync, auditoria y expansion.

Respuesta comercial:

> eleventa es muy practico para empezar. PRISMA esta pensado para negocios que ademas de vender rapido necesitan controlar mejor, operar por modulos y crecer por giro o sucursal.

---

### Pregunta: "¿Por que no CONTPAQi?"

Respuesta interna fuerte:

> CONTPAQi gana en confianza fiscal/administrativa. PRISMA debe ganar en operacion POS moderna, Tablet, experiencia visual, plugins y arquitectura de piso.

Respuesta comercial:

> CONTPAQi es fuerte en administracion. PRISMA se enfoca en convertir el punto de venta y la operacion diaria en una plataforma modular de control comercial.

---

### Pregunta: "¿Por que no Odoo?"

Respuesta interna fuerte:

> Odoo es modular y enorme. PRISMA debe ser mas especifico, mas claro para POS mexicano, mas dirigido a PC/Tablet y verticales locales.

Respuesta comercial:

> Odoo es una plataforma amplia. PRISMA se enfoca en la operacion comercial diaria: venta, caja, inventario, plugins por giro y control PC/Tablet.

---

### Pregunta: "¿Por que no Shopify POS?"

Respuesta interna fuerte:

> Shopify gana si ecommerce manda. PRISMA debe ganar si el negocio vive en mostrador, inventario local, caja, fiscal, offline y operacion multi-giro.

Respuesta comercial:

> Shopify es fuerte para comercio omnicanal. PRISMA esta pensado para operacion comercial de piso, con control modular, offline con reglas y extensiones por giro.

---

### Pregunta: "¿Por que no Loyverse?"

Respuesta interna fuerte:

> Loyverse gana por precio y facilidad. PRISMA debe ganar por control, contratos, auditoria y verticalizacion.

Respuesta comercial:

> Loyverse es una buena entrada movil. PRISMA esta pensado para negocios que necesitan mas gobierno operativo, trazabilidad, plugins y crecimiento estructurado.

---

### Pregunta: "¿Por que no Soft Restaurant?"

Respuesta interna fuerte:

> Soft Restaurant gana en restaurante puro. PRISMA debe ganar en negocios hibridos o multi-giro donde restaurante sea solo una vertical mas.

Respuesta comercial:

> Soft Restaurant es especializado en restaurantes. PRISMA busca una plataforma modular donde restaurante puede convivir con tienda, inventario, pedidos, clientes y otras verticales.

---

## 11. Riesgos competitivos reales

### 11.1 Riesgo de prometer demasiado

PRISMA tiene una vision grande. Eso es bueno. Pero si marketing habla como si todo ya estuviera producido, probado y vendido a 40 cadenas, el proyecto se pone una soga con moño.

#### Control

Usar lenguaje como:

- diseñado para
- pensado para
- preparado para
- arquitectura orientada a
- roadmap modular
- capacidad prevista
- enfoque de plataforma

Evitar:

- ya resuelve cualquier giro
- listo para todo
- supera a todos
- hace lo mismo que X y mas
- cualquier negocio puede entrar mañana

---

### 11.2 Riesgo de complejidad percibida

Si PRISMA habla demasiado de contratos, plugins, eventos y sync, puede sonar como software para astronautas fiscales.

#### Control

Tener dos capas de discurso:

- comercial simple: vender, controlar, crecer
- tecnico interno: contratos, sync, plugins, auditoria

---

### 11.3 Riesgo de debilidad fiscal percibida

En Mexico, CFDI y SAT pesan. Si PRISMA no muestra camino fiscal serio, competidores como CONTPAQi, SICAR y eleventa se ven mas confiables.

#### Control

Construir narrativa clara:

- fiscal layer
- CFDI
- notas
- cancelaciones
- timbrado
- auditoria fiscal
- relacion ticket/factura
- politica offline fiscal

---

### 11.4 Riesgo de falta de vertical profunda

Soft Restaurant en restaurante, sistemas de farmacia en farmacia o ERPs en distribucion pueden tener profundidad que PRISMA aun debe construir.

#### Control

No vender profundidad total inmediata. Vender plataforma y roadmap:

- core comun
- plugin vertical
- contrato
- fases
- matriz de capacidades
- validacion por giro

---

### 11.5 Riesgo de precio

Loyverse, eleventa y otros pueden ser mas baratos o tener entrada gratuita.

#### Control

No competir por barato. Competir por:

- control
- crecimiento
- extensibilidad
- trazabilidad
- reduccion de caos
- multi-giro
- imagen premium

---

## 12. Recomendacion de posicionamiento competitivo

### 12.1 Posicionamiento maestro

> **PRISMA es la plataforma POS modular para negocios que ya no quieren solo cobrar, sino controlar, sincronizar y crecer por giro, sucursal y dispositivo sin romper su operacion.**

### 12.2 Posicionamiento frente a POS tradicionales

> **Menos parche. Mas sistema.**

### 12.3 Posicionamiento frente a POS simples

> **Cuando vender ya no basta, necesitas una base que controle.**

### 12.4 Posicionamiento frente a ERPs

> **La operacion de piso con la disciplina de una plataforma.**

### 12.5 Posicionamiento frente a verticales

> **Especializacion por giro sin encerrar tu negocio en una sola vertical.**

### 12.6 Posicionamiento frente a SaaS globales

> **Tecnologia modular con logica local de operacion, fiscal, hardware y piso de venta.**

---

## 13. Battlecard resumida para uso interno

| Tipo de competidor | Si el cliente dice | Responder con |
|---|---|---|
| POS tradicional | "Ese ya lo conozco" | "PRISMA no busca ser otro POS conocido; busca una base modular preparada para crecer." |
| POS simple | "Ese es mas facil" | "PRISMA Light conserva claridad, pero deja preparada la operacion para control y expansion." |
| ERP | "Ese administra todo" | "PRISMA se enfoca en operacion comercial diaria: caja, piso, Tablet, venta, plugins y control." |
| SaaS global | "Ese se ve moderno" | "PRISMA suma experiencia moderna con logica local, fiscal, hardware y operacion multi-giro." |
| Vertical especializado | "Ese es para mi giro" | "PRISMA permite que tu giro sea plugin, sin cerrar el negocio a otras capacidades." |
| Gratis/barato | "Ese cuesta menos" | "PRISMA no compite por ser el mas barato; compite por evitar que el crecimiento salga caro." |

---

## 14. Guia para IA: como desarrollar material competitivo usando este documento

### 14.1 Instruccion madre

Cuando una IA genere material competitivo de PRISMA, debe entender que:

> PRISMA no compite principalmente por tener mas funciones sueltas, sino por ofrecer una arquitectura modular, gobernada y extensible para operacion comercial.

### 14.2 Variables clave

Toda pieza competitiva debe considerar:

```yaml
producto: PRISMA
categoria: plataforma POS modular
mercado: Mexico / LATAM primero
posicionamiento:
  - plataforma de operacion comercial
  - core comun
  - modulos reutilizables
  - plugins verticales
  - PC gobierna
  - Tablet opera
  - offline con reglas
  - sync observable
  - fiscal desacoplado
  - hardware por adaptadores
  - Black y Light como experiencias visuales
no_decir:
  - somos mejores que todos
  - ya hacemos todo
  - version basica
  - version media
  - reemplaza cualquier ERP
  - listo para cualquier giro sin configuracion
tono:
  - claro
  - firme
  - competitivo
  - interno puede ser mas directo
  - externo debe ser elegante
```

### 14.3 Estructura recomendada para cualquier comparativa

Toda comparativa debe tener:

1. Quien es el competidor.
2. Que hace bien.
3. En que contexto gana.
4. Donde PRISMA puede diferenciarse.
5. Que no debe prometer PRISMA.
6. Mensaje interno.
7. Mensaje publico seguro.
8. Riesgo real.
9. Siguiente mejora de producto recomendada.

### 14.4 Regla de oro para IA

No convertir ventajas de roadmap en afirmaciones de producto terminado.

Correcto:

> PRISMA esta diseñado para soportar plugins verticales bajo contratos.

Incorrecto:

> PRISMA ya supera a cualquier POS vertical.

Correcto:

> PRISMA debe diferenciarse por sync observable.

Incorrecto:

> PRISMA sincroniza mejor que todos.

Correcto:

> PRISMA puede posicionarse como plataforma modular frente a POS tradicionales.

Incorrecto:

> Los POS tradicionales son obsoletos.

---

## 15. Recomendaciones de producto derivadas de la competencia

Para que las ventajas competitivas sean reales y no puro confeti de estrategia, PRISMA debe priorizar:

### Fase 1: Paridad minima POS

- venta rapida
- carrito
- cobro
- caja
- tickets
- clientes
- inventario basico
- productos/categorias
- cortes
- permisos basicos
- reportes basicos

Sin esto, la arquitectura sera muy bonita, pero el cliente preguntara "¿y donde cobro?" y se acabo la poesia.

### Fase 2: Diferenciadores visibles

- PC dashboard de gobierno
- Tablet operacion de piso
- PRISMA Black
- PRISMA Light
- eventos por accion sensible
- auditoria visible
- estado offline/sync
- slots de plugins
- matriz de permisos

Aqui empieza a oler a PRISMA.

### Fase 3: Ventaja modular real

- plugin contract ejecutable
- registry de modulos
- vertical target atlas
- farmacia minimo viable
- restaurante minimo viable
- taller/servicio minimo viable
- B2B/pedidos minimo viable
- offline policy por modulo
- sync conflict resolver en PC

Aqui ya no es discurso. Aqui ya hay sistema.

### Fase 4: Competencia fuerte

- fiscal layer
- hardware adapters
- multi-sucursal
- reportes ejecutivos
- cartera/cobranza
- rutas/distribucion
- membresias/gym
- produccion ligera
- marketplace interno de plugins
- documentacion viva por vertical

Aqui PRISMA empieza a defender "plataforma" con mas que palabras bonitas.

---

## 16. Mensaje final interno

PRISMA no debe obsesionarse con copiar a SICAR, eleventa, CONTPAQi, Odoo, Shopify, Loyverse o Soft Restaurant.

Debe entender que hacen bien y construir una propuesta distinta:

- mas modular que el POS tradicional
- mas local que el SaaS global
- mas operativo que el ERP
- mas flexible que la vertical cerrada
- mas gobernado que la app simple
- mas moderno visualmente que el software heredado
- mas serio arquitectonicamente que el sistema parchado

La frase final para guiar todo:

> **PRISMA gana si convierte el punto de venta en una plataforma de operacion comercial modular, gobernada y extensible. Pierde si se queda compitiendo por botones, pantallas bonitas o promesas gigantes antes de tener core solido.**

---

# Anexo A - Fuentes consultadas

Este documento usa como base la documentacion interna/estrategica de PRISMA y revision publica de capacidades declaradas por competidores.

## Fuentes internas PRISMA

- Dossier maestro de posicionamiento, marketing y ventas de PRISMA.
- Documento `00_START_HERE.md` de PRISMA UI, version 3.0.0.

## Fuentes publicas revisadas

- SICAR: caracteristicas del punto de venta, inventario, CFDI, nube, app, offline local y licencias.
- eleventa: punto de venta, inventario, facilidad de uso, facturacion, varias cajas y credito.
- CONTPAQi Comercial Start/Pro: POS, inventario, CFDI, cuentas por cobrar, ciclo comercial y hardware.
- Odoo POS: POS web, PC/tablet, offline, inventario, contabilidad, franquicias y modulos.
- Shopify POS: POS iOS/Android, admin Shopify, inventario, offline checkout y restricciones offline.
- Loyverse: POS movil/tablet, inventario, lealtad, multi-store, offline y limitaciones offline.
- Soft Restaurant: gestion restaurantera, ventas, inventario, reportes, facturacion, pagos y especializacion.
- Poster POS: cloud POS, tablet/phone/browser, restaurante/retail, inventario, reportes y offline.
- Square POS: facilidad de adopcion, pagos, inventario, reportes y small business.
- Bind ERP: ERP mexicano en nube, ventas, inventario, pedidos y reportes.
