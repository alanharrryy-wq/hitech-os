# PRISMA Support Bundle Local 04 — Master Spec


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Versión documental: `1.1.0`  
> Fecha: `2026-04-28`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: docs, schemas, examples, test-cases, manifest y checksums.  
> Restricción: no instala runtime, no crea rutas Next, no toca DB, no toca `.env`, no ejecuta sync remoto y no procesa pagos.

## Base que no se contradice

Este paquete asume que ya existen y quedan como piso:

- `PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00`: contratos base de customer operations, remote ops, updates, soporte, plugins, licencias y frontera de no procesamiento bancario.
- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01`: separación repo / release / runtime cliente, reglas de `ProgramData`, logs, backups, config y prohibición de depender de `cwd`.
- `PRISMA_LICENSE_LOCAL_MOCK_02`: planes, feature flags mock, entitlements, offline grace y contrato local de licencia.

Nada de este paquete invalida lo anterior. Esto no viene a patear la mesa, viene a poner mantel, cubiertos y letrero de “no meter los dedos al enchufe”.


## Objetivo

Definir el soporte diagnóstico local que una implementación posterior podrá generar. Este documento no genera bundles; define qué puede entrar, qué no, con qué consentimiento y cómo se manifiesta.

## Qué es un support bundle

Un support bundle es un paquete local, controlado y redactado con información útil para soporte: versión, runtime, logs filtrados, estado superficial de DB, conteos de outbox, plugins declarativos y errores clasificados.

No es copia del disco. No es dump de DB. No es `.env`. No es “mándame toda la carpeta y vemos”. Esa técnica pertenece al museo del soporte irresponsable.

## Flujo conceptual

```text
Centro PRISMA > Soporte/Diagnóstico
  -> explicar datos permitidos
  -> pedir consentimiento
  -> leer allowlist
  -> redactar
  -> generar snapshot
  -> generar manifest
  -> calcular checksums
  -> guardar local
  -> mostrar resumen
```

## Estados de consentimiento

| Estado | Significado | Acción permitida |
| --- | --- | --- |
| not_requested | no se ha pedido diagnóstico | mostrar explicación |
| requested | usuario abrió flujo | mostrar allowlist |
| granted | usuario autorizó | generar bundle futuro |
| denied | usuario rechazó | no generar |
| expired | autorización vieja | pedir de nuevo |

## Secciones permitidas

| Sección | Permitido | Prohibido |
| --- | --- | --- |
| version | versión, package ids, canal | secretos o tokens |
| runtime | modo, roots normalizados | rutas sensibles sin mascarar |
| license | plan, estado, features | claves o firma cruda |
| database | existe, tamaño, integridad superficial | dump o contenido |
| logs | líneas recientes filtradas | logs crudos con secretos |
| outbox | conteos por estado | payload completo por defecto |
| plugins | id, versión, status, hash | config secreta |
| messages | conteos por categoría | cuerpos completos por defecto |

## Regla de oro

Si el dato no ayuda a diagnosticar o no puede redactarse, no entra. El soporte bueno encuentra el problema sin abrirle la mochila completa al cliente.
