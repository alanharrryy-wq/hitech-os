# Implementation Notes

- El installer evita supuestos frágiles sobre `.Path` y normaliza rutas a string canónico.
- El hardening se enfoca en PowerShell 5.1 friendly syntax.
- La verificación post-install es estructural primero; toolchain/guard son opcionales y registrados como `passed`, `failed` o `skipped`.
- El pack se puede apilar sobre `selection`, `structure/canvas sync` y `mutation client v2 fixed` sin requerir que esos bundles sigan presentes en disco.
