# PRISMA Full E2E Certification 18

Paquete de certificación, no de feature. Instala verificadores y documentación para decidir si PRISMA FULL está listo como flujo real: Tablet vende, PC gobierna, Mobile supervisa.

## Qué instala

- `tools/e2e-certification/prisma_full_e2e_certification_18.mjs`
- `tools/e2e-certification/run_prisma_full_e2e_certification_18.ps1`
- matriz QA y guion humano E2E
- corpus JSONL de escenarios de certificación

## Comando recomendado

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "F:epos\hitech-ospps	erminal-de-venta-system	ools\e2e-certificationun_prisma_full_e2e_certification_18.ps1" -RepoRoot "F:epos\hitech-os" -Out "F:\descargasf"
```

## Modo full

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "F:epos\hitech-ospps	erminal-de-venta-system	ools\e2e-certificationun_prisma_full_e2e_certification_18.ps1" -RepoRoot "F:epos\hitech-os" -Out "F:\descargasf" -Full
```

## Dictamen

- `READY`: typecheck y smoke base sin bloqueos, sin caveats pendientes.
- `READY_WITH_CAVEATS`: apps responden o compilan, pero faltan evidencias manuales o rutas opcionales.
- `BLOCKED`: falta path crítico o falla comando requerido.
