# Runbook Full Ingest

## Goal
Rebuild state from configured sources.

## Steps
1. pause watch mode if active
2. rescan all sources
3. reprocess all files
4. rebuild indexes
5. regenerate metrics
6. capture diagnostics

## Command
```powershell
cd F:\repos\hitech-os\apps\synapse-x
.\scripts\ops\full-ingest.ps1 -Path F:\repos\hitech-os\apps\synapse-x\sample_inputs
```
