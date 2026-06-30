# PRISMA Original Customer Sync E2E Verifier

Runs a guarded local certification for the first customer context.

- Backs up PC, Tablet, and Shell Lab SQLite files under `F:/Trash-old/prisma-original-customer-sync-e2e/<timestamp>/`.
- Seeds/repairs only first-customer identity rows and fixed synthetic test rows.
- Creates Tablet sale `PRISMA-SYNC-E2E-TEST` with product `PRISMA Test Product`.
- Dispatches the event through the PC ingest service.
- Confirms Tablet persistence, PC persistence, Shell Lab registration, and Mobile snapshot/read-model evidence.

Rollback is whole-file restore from the manifest printed by the verifier.
