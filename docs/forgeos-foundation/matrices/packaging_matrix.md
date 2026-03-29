# packaging_matrix.md

Matriz de packaging y release.

| Package type | Naming rule | Contenido | Manifests obligatorios | Scope | Rollback | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| Platform release bundle | `forge-platform-<channel>` | Kernel + commons baseline + release manifest | PLATFORM_PACKAGE_MANIFEST, BOM, RELEASE_NOTES, ROLLBACK_PLAN | Despliegue completo | Sí | No incluye lógica de producto. |
| Kernel package | `forge-kernel` | Bootstrap, lifecycle, contracts, host shell, packaging runtime | PLATFORM_PACKAGE_MANIFEST | Base del runtime | Sí | Versionado semver propio. |
| Commons capability package | `forge-commons-<capability-id>` | Capability runtime, contratos, stores y migraciones | PRODUCT_PACKAGE_MANIFEST o capability-equivalent | Instalación selectiva | Sí | Nunca contiene productos. |
| Product package | `forge-product-<product-id>` | Dominio, app, adapters, views, contratos, docs, packaging | PRODUCT_PACKAGE_MANIFEST, BOM, COMPATIBILITY, ROLLBACK_PLAN | Instalación por producto | Sí | Debe declarar permissions y compatibility. |
