# arr10 parallel manifest guard

## Context

The all-surfaces orchestrator can finish every surface worker correctly and still fail during final aggregation if a Windows PowerShell `OrderedDictionary` key is overwritten through dot notation with an array/list.

Observed runtime error:

```txt
SURFACE-PARALLEL 100% [####################] remaining 000% :: termino control-center
Los tipos de argumentos no coinciden
RUN.ps1:216
$parallelManifest.children = @($records)
FAIL fase=discovery surface=all exit=1
```

## Fix

`RUN.ps1` now builds the final manifest as a fresh ordered dictionary named `$parallelManifestFinal` and assigns `children` during construction:

```powershell
$children = @($records.ToArray())
$parallelManifestFinal = [ordered]@{
  status = $finalStatus
  # ...
  children = $children
}
```

This avoids mutating `$parallelManifest.children` through property assignment after the initial manifest has already been serialized.

## Rule

For this tool, final aggregation must avoid shared mutable manifest objects. Build final JSON artifacts from explicit immutable snapshots after workers finish.
