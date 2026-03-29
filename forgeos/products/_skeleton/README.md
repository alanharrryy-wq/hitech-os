# Product Module Template for Forge Products

Este directorio contiene el paquete documental mínimo para crear un **Forge Product** sin contaminar el host.

## Cómo usar este template

1. Copia este directorio a `products/<product_id>/`.
2. Renombra `PRODUCT_MANIFEST.template.json` a `PRODUCT_MANIFEST.json`.
3. Rellena todos los documentos obligatorios antes de escribir runtime.
4. Define primero contratos y ownership.
5. Pide revisión de kernel antes de registrar contributions de host.
6. No copies adapters legacy que dependan de `main_window`, `service_container` o strings implícitos.

## Orden recomendado dentro del template

1. `PRODUCT_MANIFEST.template.json`
2. `OWNERSHIP.template.md`
3. `STATE_AUTHORITY.template.md`
4. `LIFECYCLE.template.md`
5. `DEPENDENCIES.template.md`
6. `CONTRACT_INDEX.template.md`
7. `HOST_CONTRIBUTIONS.template.md`
8. `ERROR_BOUNDARIES.template.md`
9. `COMPATIBILITY.template.md`
10. `PACKAGING.template.md`
11. `TEARDOWN.template.md`

## Regla de oro

> Ningún producto puede leer o mutar internals del host. Toda integración pasa por contratos y extension points declarados.

## Qué no debes copiar del legado

- adapters que raspan widgets o atributos del host;
- acceso lateral a otros productos;
- stores mezclados con configuración global;
- lifecycle escondido en constructores;
- heurísticas por nombre de producto para activar UI.

## Checklist mínimo antes de pedir implementación

- `product_id` estable y único.
- owner nominal definido.
- state slices con autoridad declarada.
- contracts versionados.
- contributions del host acotadas.
- dependencies justificadas.
- teardown explícito.
- package y compatibility listos.

Generado: 2026-03-29T02:10:37Z
