# PRISMA 06/07 Screen Copy Catalog

**Paquete:** `PRISMA_ANNOUNCEMENTS_PLUGIN_LOCAL_06_07_FULL_DOCS`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Copys seguros para UI futura.


## Guardrails no negociables

- No se reemplazan runtime, pantallas reales, rutas Next, handlers API ni motores de negocio en este paquete.
- No se toca base de datos de cliente ni `tablet-pos.db`.
- No se modifica `.env`, `.next`, `node_modules`, caches, logs existentes ni archivos binarios.
- No se abren puertos entrantes ni se introduce servidor remoto local.
- No se ejecuta codigo arbitrario desde manifiestos, anuncios, mensajes, comandos remotos ni contexto de IA.
- No se procesan pagos bancarios, tarjetas, transferencias, custodia de dinero ni validacion bancaria.
- Tablet conserva autonomia de venta local; PC gobierna cuando existe, pero no autoriza la venta basica.
- Todo contrato debe declarar superficie: `pc`, `tablet`, `remote_ops`, `support`, `shared` o combinacion explicita.
- Todo flujo sensible debe tener stop condition, evento auditable futuro y criterio de rollback documental.

Dicho sin perfume: esto es contrato, no magia. Primero se dibuja la barda; luego ya vemos si metemos el perro guardian.


## Superficies PRISMA respetadas

| Superficie | Rol | Regla |
|---|---|---|
| PC | Centro de mando, administracion, auditoria, configuracion y resolucion | Puede mostrar mayor detalle y controles de gobierno. |
| Tablet | Operacion ligera de piso, venta, estado y acciones de soporte minimo | No debe saturarse ni bloquear checkout con ruido comercial. |
| Remote Ops | Canal saliente/polling seguro y controlado | No abre puertos entrantes ni ejecuta comandos libres. |
| Support | Diagnostico, evidencia y comunicacion asistida | Nunca debe filtrar secretos ni datos sensibles sin redaccion. |
| Shared contracts | Nombres, schemas, eventos y compatibilidad | No debe convertirse en basurero de utilidades. |


# Copys PC

- `001`: Novedad disponible
- `002`: Este aviso no interrumpe ventas
- `003`: Plugin no compatible con tu versión
- `004`: Plugin requiere plan superior
- `005`: Manifiesto rechazado por seguridad
- `006`: No se pudo validar la firma
- `007`: Aviso leído
- `008`: Recordarme después
- `009`: Ver detalle
- `010`: Descartar
- `011`: Novedad disponible
- `012`: Este aviso no interrumpe ventas
- `013`: Plugin no compatible con tu versión
- `014`: Plugin requiere plan superior
- `015`: Manifiesto rechazado por seguridad
- `016`: No se pudo validar la firma
- `017`: Aviso leído
- `018`: Recordarme después
- `019`: Ver detalle
- `020`: Descartar
- `021`: Novedad disponible
- `022`: Este aviso no interrumpe ventas
- `023`: Plugin no compatible con tu versión
- `024`: Plugin requiere plan superior
- `025`: Manifiesto rechazado por seguridad
- `026`: No se pudo validar la firma
- `027`: Aviso leído
- `028`: Recordarme después
- `029`: Ver detalle
- `030`: Descartar
- `031`: Novedad disponible
- `032`: Este aviso no interrumpe ventas
- `033`: Plugin no compatible con tu versión
- `034`: Plugin requiere plan superior
- `035`: Manifiesto rechazado por seguridad
- `036`: No se pudo validar la firma
- `037`: Aviso leído
- `038`: Recordarme después
- `039`: Ver detalle
- `040`: Descartar
- `041`: Novedad disponible
- `042`: Este aviso no interrumpe ventas
- `043`: Plugin no compatible con tu versión
- `044`: Plugin requiere plan superior
- `045`: Manifiesto rechazado por seguridad
- `046`: No se pudo validar la firma
- `047`: Aviso leído
- `048`: Recordarme después
- `049`: Ver detalle
- `050`: Descartar
- `051`: Novedad disponible
- `052`: Este aviso no interrumpe ventas
- `053`: Plugin no compatible con tu versión
- `054`: Plugin requiere plan superior
- `055`: Manifiesto rechazado por seguridad
- `056`: No se pudo validar la firma
- `057`: Aviso leído
- `058`: Recordarme después
- `059`: Ver detalle
- `060`: Descartar
- `061`: Novedad disponible
- `062`: Este aviso no interrumpe ventas
- `063`: Plugin no compatible con tu versión
- `064`: Plugin requiere plan superior
- `065`: Manifiesto rechazado por seguridad
- `066`: No se pudo validar la firma
- `067`: Aviso leído
- `068`: Recordarme después
- `069`: Ver detalle
- `070`: Descartar
- `071`: Novedad disponible
- `072`: Este aviso no interrumpe ventas
- `073`: Plugin no compatible con tu versión
- `074`: Plugin requiere plan superior
- `075`: Manifiesto rechazado por seguridad
- `076`: No se pudo validar la firma
- `077`: Aviso leído
- `078`: Recordarme después
- `079`: Ver detalle
- `080`: Descartar
- `081`: Novedad disponible
- `082`: Este aviso no interrumpe ventas
- `083`: Plugin no compatible con tu versión
- `084`: Plugin requiere plan superior
- `085`: Manifiesto rechazado por seguridad
- `086`: No se pudo validar la firma
- `087`: Aviso leído
- `088`: Recordarme después
- `089`: Ver detalle
- `090`: Descartar
- `091`: Novedad disponible
- `092`: Este aviso no interrumpe ventas
- `093`: Plugin no compatible con tu versión
- `094`: Plugin requiere plan superior
- `095`: Manifiesto rechazado por seguridad
- `096`: No se pudo validar la firma
- `097`: Aviso leído
- `098`: Recordarme después
- `099`: Ver detalle
- `100`: Descartar
- `101`: Novedad disponible
- `102`: Este aviso no interrumpe ventas
- `103`: Plugin no compatible con tu versión
- `104`: Plugin requiere plan superior
- `105`: Manifiesto rechazado por seguridad
- `106`: No se pudo validar la firma
- `107`: Aviso leído
- `108`: Recordarme después
- `109`: Ver detalle
- `110`: Descartar
- `111`: Novedad disponible
- `112`: Este aviso no interrumpe ventas
- `113`: Plugin no compatible con tu versión
- `114`: Plugin requiere plan superior
- `115`: Manifiesto rechazado por seguridad
- `116`: No se pudo validar la firma
- `117`: Aviso leído
- `118`: Recordarme después
- `119`: Ver detalle
- `120`: Descartar
- `121`: Novedad disponible
- `122`: Este aviso no interrumpe ventas
- `123`: Plugin no compatible con tu versión
- `124`: Plugin requiere plan superior
- `125`: Manifiesto rechazado por seguridad
- `126`: No se pudo validar la firma
- `127`: Aviso leído
- `128`: Recordarme después
- `129`: Ver detalle
- `130`: Descartar
- `131`: Novedad disponible
- `132`: Este aviso no interrumpe ventas
- `133`: Plugin no compatible con tu versión
- `134`: Plugin requiere plan superior
- `135`: Manifiesto rechazado por seguridad
- `136`: No se pudo validar la firma
- `137`: Aviso leído
- `138`: Recordarme después
- `139`: Ver detalle
- `140`: Descartar
- `141`: Novedad disponible
- `142`: Este aviso no interrumpe ventas
- `143`: Plugin no compatible con tu versión
- `144`: Plugin requiere plan superior
- `145`: Manifiesto rechazado por seguridad
- `146`: No se pudo validar la firma
- `147`: Aviso leído
- `148`: Recordarme después
- `149`: Ver detalle
- `150`: Descartar
- `151`: Novedad disponible
- `152`: Este aviso no interrumpe ventas
- `153`: Plugin no compatible con tu versión
- `154`: Plugin requiere plan superior
- `155`: Manifiesto rechazado por seguridad
- `156`: No se pudo validar la firma
- `157`: Aviso leído
- `158`: Recordarme después
- `159`: Ver detalle
- `160`: Descartar
- `161`: Novedad disponible
- `162`: Este aviso no interrumpe ventas
- `163`: Plugin no compatible con tu versión
- `164`: Plugin requiere plan superior
- `165`: Manifiesto rechazado por seguridad
- `166`: No se pudo validar la firma
- `167`: Aviso leído
- `168`: Recordarme después
- `169`: Ver detalle
- `170`: Descartar
- `171`: Novedad disponible
- `172`: Este aviso no interrumpe ventas
- `173`: Plugin no compatible con tu versión
- `174`: Plugin requiere plan superior
- `175`: Manifiesto rechazado por seguridad
- `176`: No se pudo validar la firma
- `177`: Aviso leído
- `178`: Recordarme después
- `179`: Ver detalle
- `180`: Descartar
- `181`: Novedad disponible
- `182`: Este aviso no interrumpe ventas
- `183`: Plugin no compatible con tu versión
- `184`: Plugin requiere plan superior
- `185`: Manifiesto rechazado por seguridad
- `186`: No se pudo validar la firma
- `187`: Aviso leído
- `188`: Recordarme después
- `189`: Ver detalle
- `190`: Descartar
- `191`: Novedad disponible
- `192`: Este aviso no interrumpe ventas
- `193`: Plugin no compatible con tu versión
- `194`: Plugin requiere plan superior
- `195`: Manifiesto rechazado por seguridad
- `196`: No se pudo validar la firma
- `197`: Aviso leído
- `198`: Recordarme después
- `199`: Ver detalle
- `200`: Descartar


# Copys Tablet

- `001`: Estado actualizado
- `002`: Hay novedades
- `003`: Soporte disponible
- `004`: No se muestra durante cobro
- `005`: Aviso crítico
- `006`: Ver después
- `007`: Estado actualizado
- `008`: Hay novedades
- `009`: Soporte disponible
- `010`: No se muestra durante cobro
- `011`: Aviso crítico
- `012`: Ver después
- `013`: Estado actualizado
- `014`: Hay novedades
- `015`: Soporte disponible
- `016`: No se muestra durante cobro
- `017`: Aviso crítico
- `018`: Ver después
- `019`: Estado actualizado
- `020`: Hay novedades
- `021`: Soporte disponible
- `022`: No se muestra durante cobro
- `023`: Aviso crítico
- `024`: Ver después
- `025`: Estado actualizado
- `026`: Hay novedades
- `027`: Soporte disponible
- `028`: No se muestra durante cobro
- `029`: Aviso crítico
- `030`: Ver después
- `031`: Estado actualizado
- `032`: Hay novedades
- `033`: Soporte disponible
- `034`: No se muestra durante cobro
- `035`: Aviso crítico
- `036`: Ver después
- `037`: Estado actualizado
- `038`: Hay novedades
- `039`: Soporte disponible
- `040`: No se muestra durante cobro
- `041`: Aviso crítico
- `042`: Ver después
- `043`: Estado actualizado
- `044`: Hay novedades
- `045`: Soporte disponible
- `046`: No se muestra durante cobro
- `047`: Aviso crítico
- `048`: Ver después
- `049`: Estado actualizado
- `050`: Hay novedades
- `051`: Soporte disponible
- `052`: No se muestra durante cobro
- `053`: Aviso crítico
- `054`: Ver después
- `055`: Estado actualizado
- `056`: Hay novedades
- `057`: Soporte disponible
- `058`: No se muestra durante cobro
- `059`: Aviso crítico
- `060`: Ver después
- `061`: Estado actualizado
- `062`: Hay novedades
- `063`: Soporte disponible
- `064`: No se muestra durante cobro
- `065`: Aviso crítico
- `066`: Ver después
- `067`: Estado actualizado
- `068`: Hay novedades
- `069`: Soporte disponible
- `070`: No se muestra durante cobro
- `071`: Aviso crítico
- `072`: Ver después
- `073`: Estado actualizado
- `074`: Hay novedades
- `075`: Soporte disponible
- `076`: No se muestra durante cobro
- `077`: Aviso crítico
- `078`: Ver después
- `079`: Estado actualizado
- `080`: Hay novedades
- `081`: Soporte disponible
- `082`: No se muestra durante cobro
- `083`: Aviso crítico
- `084`: Ver después
- `085`: Estado actualizado
- `086`: Hay novedades
- `087`: Soporte disponible
- `088`: No se muestra durante cobro
- `089`: Aviso crítico
- `090`: Ver después
- `091`: Estado actualizado
- `092`: Hay novedades
- `093`: Soporte disponible
- `094`: No se muestra durante cobro
- `095`: Aviso crítico
- `096`: Ver después
- `097`: Estado actualizado
- `098`: Hay novedades
- `099`: Soporte disponible
- `100`: No se muestra durante cobro
- `101`: Aviso crítico
- `102`: Ver después
- `103`: Estado actualizado
- `104`: Hay novedades
- `105`: Soporte disponible
- `106`: No se muestra durante cobro
- `107`: Aviso crítico
- `108`: Ver después


# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
