# PRISMA 03-04-05 — Cross Package Contract


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


## Dependencias

| Paquete | Depende de | Produce para |
| --- | --- | --- |
| 03 Centro UI Shell | 00, 01, 02 | navegación visible para 04/05/06/07/08 |
| 04 Support Bundle Local | 00, 01, 03 | diagnóstico seguro |
| 05 Messaging Mock | 00, 01, 03, opcional 04 | threads y mensajes locales mock |

## Flujo integrado

```text
Centro PRISMA
  -> Soporte
    -> Crear solicitud local mock
    -> Referenciar diagnóstico futuro bajo contrato 04
  -> Mensajes
    -> Mostrar thread mock
    -> Referenciar paquete/ruta/contexto
  -> Diagnóstico
    -> Mostrar allowlist
    -> Pedir consentimiento
```

## Contradicciones prohibidas

| Contradicción | Decisión correcta |
| --- | --- |
| Mensajes adjuntan bundle completo sin consentimiento | mensajes solo referencian diagnosticBundleId autorizado |
| Soporte genera diagnóstico sin redacción | 04 exige redacción antes de persistir |
| Centro muestra Enviar mensaje real | mostrar mock local |
| Tablet muestra panel completo de plugins | Tablet muestra estado ligero |
| Licencia bloquea soporte básico | licencia no secuestra datos |
| Update aparece accionable | read-only hasta 08 |
