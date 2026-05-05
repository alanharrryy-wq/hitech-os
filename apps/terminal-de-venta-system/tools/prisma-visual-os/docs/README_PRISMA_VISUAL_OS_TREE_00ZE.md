# PRISMA Visual OS Tree 00ZE

Esta carpeta documenta el cierre de la migración del árbol `tools/prisma-visual-os`.

La decisión operativa queda así:

- La raíz mantiene shims por compatibilidad.
- `doctors/` contiene implementación Python real de doctores.
- `verifiers/` contiene implementación real de verificadores Node.
- `realtime/`, `scoring/`, `generators/`, `gates/`, `qa/` y `tree/` son carpetas activas.
- `launchers/` queda reservada para una migración futura de `.cmd`, sin romper comandos existentes.
- `_plans/` conserva planes de reorg y notas de cierre.

No se debe borrar un shim raíz hasta que no exista reemplazo documentado y probado en Windows.
