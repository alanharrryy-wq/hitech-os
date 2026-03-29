# forge_commons

Shared capability runtime for ForgeOS phase 3.

Capabilities:

- `config_policy`
- `diagnostics`
- `process_execution`
- `history_runs`
- `export_artifacts`

Validation command:

```powershell
$env:PYTHONPATH='src;..\\forge_kernel\\src'; python -m unittest discover -s tests -p "test_*.py"
```
