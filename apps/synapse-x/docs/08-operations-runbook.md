# Operations Runbook

## Main Operations
- ingest now
- full ingest
- repair
- watch on
- watch off

## Expected Safety
All operations should be idempotent where possible.

## Repair Includes
- DB integrity checks
- index rebuild
- cache/DB reconciliation
- retry failed files
- raw reference validation

## Logging
Every operational action should produce clear logs and diagnostics.

## Commands
```powershell
cd F:\repos\hitech-os\apps\synapse-x

.\scripts\ops\ingest-now.ps1 -Path F:\input\a -Path F:\input\b
.\scripts\ops\full-ingest.ps1 -Path F:\input\a
.\scripts\ops\repair.ps1
.\scripts\ops\watch-on.ps1 -Interval 30
.\scripts\ops\watch-off.ps1
```

## Watch Artifacts
- PID: `F:\repos\hitech-os\tools\_local\tmp\synapse-x-watch.pid`
- Stop signal: `F:\repos\hitech-os\tools\_local\tmp\synapse-x-watch.stop`
- STDOUT log: `F:\repos\hitech-os\tools\_local\logs\synapse-x-watch.out.log`
- STDERR log: `F:\repos\hitech-os\tools\_local\logs\synapse-x-watch.err.log`
