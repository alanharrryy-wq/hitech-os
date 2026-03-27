# Engine Guardian v3

`engine_guardian` es la superficie operativa nueva y oficial para el engine público.

## Rol
- orquestador externo
- adapter consumer
- wrapper-based
- sin invadir `git_sentinel_modular`
- sin reescribir internals de `repo_analizer`

## Superficie oficial nueva
1. `F:\repos\hitech-os\engine_guardian\cli.py`
2. `F:\repos\hitech-os\igniters\*.cmd`
3. scheduled tasks:
   - `HITECH-EngineGuardian-Boot`
   - `HITECH-EngineGuardian-Pulse`

## Truth model
El engine público solo está sano cuando `https://engine.hitechrts.com` responde 2xx o 3xx.

## Runtime root canónico
`F:\OneDrive\Descargas\engine_guardian\`

Subrutas:
- `state`
- `locks`
- `logs`
- `reports`
- `snapshots`
- `backups`
- `install`
