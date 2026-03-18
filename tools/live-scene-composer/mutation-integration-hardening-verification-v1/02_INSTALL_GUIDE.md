# Install Guide

## Camino recomendado

```powershell
powershell -ExecutionPolicy Bypass -File "F:\OneDrive\Descargasun_live_scene_composer_mutation_integration_hardening_verification_v1_from_zip.ps1" -AllowInferredPaths
```

## Alternativa

```powershell
powershell -ExecutionPolicy Bypass -File "F:\OneDrive\Descargas\install_live_scene_composer_mutation_integration_hardening_verification_v1.ps1" -AllowInferredPaths
```

## Flags útiles

- `-RepoRoot "F:epos\hitech-os"`
- `-DownloadsRoot "F:\OneDrive\Descargas"`
- `-AllowInferredPaths`
- `-InstallIntoComposerSrc`
- `-SkipGuard`
- `-SkipSmoke`
- `-SkipVerification`

## Outputs

Cada corrida crea una carpeta con timestamp dentro de `F:\OneDrive\Descargas` con:

- `install_summary.txt`
- `install_summary.json`
- `verification_report.txt`
- `verification_report.json`
- `smoke_report.txt`
- `smoke_report.json`
- stdout/stderr auxiliares cuando aplica
