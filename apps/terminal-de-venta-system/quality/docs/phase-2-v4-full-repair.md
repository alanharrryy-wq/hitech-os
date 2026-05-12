# Phase 2 V4 Full Repair

This repair consolidates the Phase 2 fixes:

- CLI entrypoint awaits `runCli()`.
- Runtime manifest uses PRISMA real local ports.
- Q11 probes real PRISMA ports.
- Generic Next.js ports 3000/3001/3002/3003 are forbidden.
- Incomplete or bad-port PQOS runs are moved to quarantine instead of being deleted.
- Chart Lab remains disabled until its port is discovered from project evidence.

The repair does not start services, mutate databases, change Cloudflare, or delete project files.
