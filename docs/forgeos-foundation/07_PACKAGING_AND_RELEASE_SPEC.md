# 07_PACKAGING_AND_RELEASE_SPEC.md

## Propósito

Definir cómo se empaqueta, versiona, instala, actualiza, revierte y valida ForgeOS.

## Principios

- todo lo instalable tiene manifest;
- todo paquete declara compatibilidad;
- todo paquete tiene owner;
- todo paquete tiene BOM;
- todo paquete tiene rollback plan;
- toda migración de estado está declarada;
- ningún paquete escribe fuera de su ownership sin contrato.

## Taxonomía de paquetes

| Package type | Naming rule | Contenido | Scope | Owner típico |
| --- | --- | --- | --- | --- |
| Kernel package | `forge-kernel` | bootstrap, lifecycle, contracts, host shell, packaging runtime | plataforma base | kernel owner |
| Commons capability package | `forge-commons-<capability-id>` | capability runtime, contratos, stores, migrations | reusable, instalable selectivamente | capability owner |
| Product package | `forge-product-<product-id>` | domain, application, adapters, views, contracts, docs, assets | producto aislado | product owner |
| Platform release bundle | `forge-platform-<channel>` | kernel + commons baseline + manifests de release | despliegue de plataforma | release owner |

## Qué se empaqueta a nivel plataforma vs producto

### Plataforma
Se empaqueta en el bundle de plataforma:

- Forge Kernel;
- commons baseline requeridos por el host;
- compatibility matrix del release;
- release manifest;
- release notes;
- rollback plan global;
- integrity metadata.

### Producto
Se empaqueta por producto:

- manifest de producto;
- contracts del producto;
- views y adapters del producto;
- assets propios;
- state migrations del producto;
- BOM del producto;
- compatibility del producto;
- rollback plan del producto.

### Regla
El bundle de plataforma no absorbe lógica de dominio de productos.  
Solo referencia paquetes de producto compatibles.

## Manifests requeridos para empaquetado

### Obligatorios para plataforma
- `PLATFORM_PACKAGE_MANIFEST.json`
- `BOM.md`
- `RELEASE_NOTES.md`
- `ROLLBACK_PLAN.md`

### Obligatorios para producto
- `PRODUCT_PACKAGE_MANIFEST.json`
- `BOM.md`
- `COMPATIBILITY.md`
- `ROLLBACK_PLAN.md`
- `PRODUCT_MANIFEST.json`

## Estrategia de versionado

- SemVer por paquete.
- `forge-kernel` versiona independiente de cada commons capability.
- Cada producto versiona independiente.
- El platform release bundle fija una combinación exacta de versiones.
- La doctrina arquitectónica tiene versión aparte y no reemplaza el versionado de runtime.

### Reglas
- major: rompe compatibilidad contractual o de schema;
- minor: agrega capabilities/contratos backward-compatible;
- patch: corrige sin romper contratos públicos.

## Reglas de matriz de compatibilidad

- Todo producto declara rango soportado de `forge-kernel`.
- Todo producto declara las capabilities de commons que requiere y sus ranges.
- Toda capability declara rango soportado de `forge-kernel`.
- El bundle de plataforma solo puede incluir combinaciones compatibles.
- La instalación debe fallar si una dependencia resuelta cae fuera de rango.

## Reglas de declaración de dependencias

- Sin dependencias implícitas.
- Sin dependencias laterales entre productos.
- Las dependencias opcionales deben marcarse como opcionales.
- Las dependencies de runtime externo deben declararse separadas de kernel/commons/products.
- Las dependencias se validan en install time y en activate time si son dinámicas.

## Reglas de migración

- Toda migración tiene `from_version` y `to_version`.
- Toda migración declara si es reversible, no reversible o compensable.
- Toda migración declara el owner que la ejecuta.
- Ningún rollback puede ignorar el estado.
- Toda upgrade path debe indicar qué stores toca.

## Reglas de runtime assets

- Los assets de un paquete viven bajo el paquete.
- Ningún producto mete assets en carpetas del kernel.
- Ningún commons mete assets product-specific.
- Todo asset versionado debe aparecer en el BOM.
- Assets generados en runtime no se consideran parte del paquete salvo que una export capability los emita como artefacto formal.

## Reglas de config

- Config global de plataforma: propiedad del kernel/config commons.
- Config de capability: propiedad del capability owner.
- Config de producto: propiedad del producto.
- Los scopes no se mezclan.
- Toda config tiene schema/version cuando cruza packaging o restore.

## Release channels

Canales oficiales:

- `experimental`
- `beta`
- `stable`
- `lts`

### Reglas
- el package manifiesta su canal;
- el platform bundle decide qué canales admite;
- un package `experimental` no entra a un release `stable` salvo aprobación explícita.

## Rollback rules

- Todo rollback tiene unidad clara: package o platform bundle.
- Todo rollback verifica compatibilidad de datos antes de revertir binarios.
- Si el rollback no es seguro, debe bloquearse y exigir forward-fix o migración correctiva.
- Todo rollback deja evidencia: versión origen, versión destino, stores tocados, outcome.

## Expectativas de install/uninstall

### Install
- validar manifest;
- validar integrity;
- validar compatibility;
- registrar package;
- montar stores;
- ejecutar migraciones;
- preparar package;
- activar solo si corresponde.

### Uninstall
- suspender o dispose package;
- purgar solo los stores que el package posee;
- dejar historial de uninstall;
- no tocar state de otros packages;
- no dejar contributions huérfanas registradas.

## Integrity y validation gates

Todo paquete debe poder pasar:

- schema validation de manifest;
- compatibility validation;
- dependency resolution;
- integrity check;
- BOM completeness check;
- rollback plan presence check;
- ownership completeness check.

## Canonical package manifest schema en JSON

```json
{
  "schema_version": "forge.package.manifest.v1",
  "package_id": "forge-product-__PRODUCT_ID__",
  "package_type": "product",
  "name": "__PACKAGE_NAME__",
  "version": "0.1.0",
  "channel": "experimental",
  "owner": "__OWNER__",
  "layer": "product",
  "entrypoints": {
    "activation_contract": "forge.kernel.lifecycle.product.activate.v1",
    "dispose_contract": "forge.kernel.lifecycle.product.dispose.v1",
    "contract_index_ref": "CONTRACT_INDEX.md",
    "host_contributions_ref": "HOST_CONTRIBUTIONS.md"
  },
  "dependencies": {
    "kernel": ">=1.0.0 <2.0.0",
    "commons": [
      {
        "capability_id": "process_execution",
        "version_range": ">=1.0.0 <2.0.0",
        "required": true
      }
    ],
    "external_runtime": []
  },
  "compatibility": {
    "host_api": ">=1.0.0 <2.0.0",
    "supported_channels": ["experimental", "beta"]
  },
  "permissions": [
    "process.execute",
    "filesystem.read"
  ],
  "artifacts": [
    {
      "path": "packaging/bom/BOM.md",
      "kind": "bom"
    }
  ],
  "migrations": [
    {
      "from_version": "0.0.0",
      "to_version": "0.1.0",
      "reversible": false
    }
  ],
  "integrity": {
    "hashes": [],
    "signature_ref": ""
  }
}
```

## Product package bill of materials

Un BOM de producto debe incluir como mínimo:

- package id y versión;
- lista de archivos entregados;
- contracts incluidos;
- assets incluidos;
- stores declarados;
- migrations incluidas;
- dependencies declaradas;
- permissions solicitados.

## Platform package bill of materials

Un BOM de plataforma debe incluir como mínimo:

- versión de `forge-kernel`;
- commons baseline incluidos;
- products admitidos o anclados por release;
- manifests de release;
- integrity data;
- compatibility matrix del bundle.

## Package naming rules

- `forge-kernel`
- `forge-commons-<capability-id>`
- `forge-product-<product-id>`
- `forge-platform-<channel>`

### Reglas
- lower-case ASCII;
- `-` como separador;
- ids estables;
- sin nombres internos o apodos locales;
- sin versión incrustada en el nombre del package.

## Regla final

Packaging en ForgeOS no es un zip casual con buena vibra.  
Es una declaración gobernada de identidad, compatibilidad, integridad y reversibilidad.
