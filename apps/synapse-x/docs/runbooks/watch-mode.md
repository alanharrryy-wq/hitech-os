# Runbook Watch Mode

## Goal
Continuously monitor configured sources.

## Start
```powershell
cd F:\repos\hitech-os\apps\synapse-x
.\scripts\ops\watch-on.ps1 -Interval 30 -Path F:\repos\hitech-os\apps\synapse-x\sample_inputs
```

## Stop
```powershell
cd F:\repos\hitech-os\apps\synapse-x
.\scripts\ops\watch-off.ps1
```

## Notes
- watch loop runs incremental ingest repeatedly
- duplicate processing is prevented by file fingerprint checks
- stop signal is file-based (`tools\_local\tmp\synapse-x-watch.stop`)
