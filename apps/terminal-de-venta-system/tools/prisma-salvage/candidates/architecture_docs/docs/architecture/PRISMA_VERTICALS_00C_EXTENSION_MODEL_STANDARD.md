# PRISMA_VERTICALS_00C_EXTENSION_MODEL_STANDARD

## Estandar de extension vertical

Toda extension debe declarar:

- `verticalId`
- `extensionId`
- `entityName`
- `extensionType`
- `ownerSurface`
- `storagePolicy`
- `tabletAccess`
- `pcAuthority`
- `syncPolicy`
- `auditImpact`
- `offlineImpact`
- `coreRelations`
- `requiredEvents`
- `fixtures`
- `acceptanceCriteria`

## Owner surface

- `tablet_local`: requerido para vender o capturar en mostrador.
- `pc_backoffice`: administracion profunda.
- `shared_contract`: contrato comun estable, no implementacion.

## Storage policy

- `local_required`: Tablet debe guardar localmente.
- `local_cache`: Tablet puede cachear.
- `pc_authoritative`: PC es fuente de gobierno.
- `event_only`: se reconstruye desde eventos.

## Regla de oro

La extension no puede obligar a todos los giros a cargar sus datos. Si lo hace, no es extension: es secuestro del modelo.
