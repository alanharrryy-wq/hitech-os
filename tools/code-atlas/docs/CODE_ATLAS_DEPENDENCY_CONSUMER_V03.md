# Code Atlas Dependency Consumer V03.1

Consumes Capatch dependency-map JSON and emits Code Atlas-friendly reports.

## V03.1 changes

- Keeps the same CLI path: `apps/code-atlas/tools/code_atlas_dependency_consumer_v03.py`.
- Reports `version = 3.1.0`.
- Reclassifies unresolved-free Python imports like `json`, `pathlib`, `__future__`, `sqlite3`, etc. as external dependencies instead of file nodes.
- Resolves local Python imports only when a same-dir or indexed project Python file can be matched.
- Suppresses malformed import-like literals such as escaped regex strings that previously created an empty `external:` graph node.
- Keeps unresolved imports unchanged so the existing `max-unresolved` gate still works.

## Main commands

Generate reports from an existing dependency-map JSON:

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_consumer_v03.py" report --report-json "F:\descargasf\dependency_map_raw_terminal-de-venta-system_260504_2146.json" --output-dir "F:\descargasf" --format all
```

Verify the clean Terminal report:

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_consumer_v03.py" verify --report-json "F:\descargasf\dependency_map_raw_terminal-de-venta-system_260504_2146.json" --max-unresolved 3 --forbid-source-prefix tools/prisma-salvage
```

Run analyzer and consumer together:

```powershell
python "F:\repos\hitech-os\apps\code-atlas\tools\code_atlas_dependency_consumer_v03.py" analyze --project-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --output-dir "F:\descargasf" --exclude-dir prisma-salvage --format all
```
