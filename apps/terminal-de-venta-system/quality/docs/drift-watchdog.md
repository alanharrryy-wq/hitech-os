# Operational Drift Watchdog

`C6` fingerprints critical customer-readiness files and compares them with the latest previous `PRISMA_QUALITY_OS_*` run that contains a customer snapshot.

Drift is usually a warning, not a blocker. Hard failures are left to hard gates such as Tablet sovereignty, secret scanning, schema safety, and no-fake-green.
