# PRISMA Support Error Code Catalog

La fuente machine-readable es:

`prisma-support-resolver/catalogs/support-error-codes.json`

Cada codigo define:

- `category`
- `severity`
- `label`
- `customerExplanation`
- `technicalExplanation`
- `detectionCriteria`
- `requiredEvidence`
- `suggestedResolution`
- `remoteResolvable`
- `autoResolvable`
- `requiresDryRun`
- `requiresAdminToken`
- `requiresSetupCode`
- `requiresCodex`
- `requiresOnsite`
- `safeActions`
- `blockedActions`
- `validationAfterAction`

No se deben agregar codigos en UI o APIs sin incorporarlos al catalogo JSON.
