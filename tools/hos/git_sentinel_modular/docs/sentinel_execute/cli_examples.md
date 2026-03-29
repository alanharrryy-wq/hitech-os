# CLI Examples

## Plan only

```powershell
python -m sentinel_execute plan `
  --workspace-root C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime\shadow_mode\shadow_20260317_000000_demo `
  --target-root F:\repos\hitech-os\tools\hos\git_sentinel_modular
```

## Execute explicitly

```powershell
python -m sentinel_execute execute `
  --workspace-root C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime\shadow_mode\shadow_20260317_000000_demo `
  --target-root F:\repos\hitech-os\tools\hos\git_sentinel_modular `
  --do-execute `
  --confirm-token EXECUTE_MANUAL_PROMOTION
```

## Policy override

```powershell
python -m sentinel_execute plan `
  --workspace-root C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime\shadow_mode\shadow_20260317_000000_demo `
  --target-root F:\repos\hitech-os\tools\hos\git_sentinel_modular `
  --policy F:\repos\hitech-os\tools\hos\git_sentinel_modular\configs\sentinel_execute\execution_policy.safe_override.example.json
```
