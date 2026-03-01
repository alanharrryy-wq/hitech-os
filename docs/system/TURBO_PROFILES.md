# TURBO_PROFILES

Execution profiles are available but **OFF by default** until constitution enables policy.

| Profile | Concurrency | Intended For |
|---|---:|---|
| `aggressive` | `auto` | High-core local machines or dedicated CI runners. |
| `balanced` | `6` | Default developer profile for modern desktop CPUs. |
| `stable` | `4` | Lower noise and reproducible local execution. |

## Resolver

```powershell
python tools/hos/turbo/resolve_profile.py
python tools/hos/turbo/resolve_profile.py --profile stable --json
```

## Wrapper

```powershell
python tools/hos/turbo/turbo_wrap.py --profile stable -- run build
python tools/hos/turbo/turbo_wrap.py --ci --profile stable -- run test
```
