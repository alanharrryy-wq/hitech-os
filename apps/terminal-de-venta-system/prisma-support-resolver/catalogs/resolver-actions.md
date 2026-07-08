# Resolver Actions

Fuente canonica: `resolver-actions.json`.

El flujo real es:

Diagnosticar -> Simular resolucion -> Confirmar -> Resolver problema real ->
Validar -> Exportar evidencia.

`Resolver problema` no debe aparecer si la accion requiere deploy, D1 migration,
secreto, reescritura manual de licencia firmada, presencial o no tiene rollback.

## choose_authority

Acción no mutante para seleccionar ruta de autoridad: Setup Code/Refresh, DB POS local seed o paquete firmado externo. No habilita apply por sí sola.


## recon4: Setup Code / License Refresh guiado

- `setup_claim_or_refresh_guided`: guía al operador por Setup Code / License Refresh sin editar `license.json` firmado.
- `apply` permanece bloqueado hasta que exista setup code/refresh source, verificación de licencia firmada, backup, rollback y validación posterior.
