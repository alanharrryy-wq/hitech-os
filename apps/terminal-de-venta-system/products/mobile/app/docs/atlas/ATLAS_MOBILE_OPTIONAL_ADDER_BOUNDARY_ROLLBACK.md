# ATLAS_MOBILE_OPTIONAL_ADDER_BOUNDARY_ROLLBACK

**Phase:** MOBILE_OPTIONAL_ADDER_BOUNDARY_PHASE_1
**Scope:** `products/mobile/app/**`

El aplicador crea backup antes de escribir. Si falla escritura o verificacion obligatoria, restaura modificados y borra nuevos creados por el aplicador.

No restaurar ni borrar nada fuera de `products/mobile/app/**`.
