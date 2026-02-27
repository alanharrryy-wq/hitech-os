# GIT_ARGS_DROPPED

## Symptom

`git` runs with empty arguments (for example, usage text appears instead of `git --version` output).

## Root Cause

In PowerShell, `$Args` is an automatic variable. Using `$Args` as a function/script parameter name can break argument binding and cause dropped external arguments.

## Fix

Use `Invoke-ExternalCommand` from `tools/scripts/lib/Invoke-External.ps1` and pass arguments through `-ArgList` (never via a parameter named `$Args`).

## Quick Verify

```powershell
. tools/scripts/lib/Invoke-External.ps1
Invoke-ExternalCommand -ExePath git -ArgList @('--version') -WorkDir 'F:\repos\hitech-os' -Debug
```
