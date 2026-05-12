# PRISMA DB Backup Ritual

Status: active
Scope: F:\repos\hitech-os\apps\terminal-de-venta-system

## Purpose

Before any schema or migration work, create a verified backup of local SQLite DBs, Prisma schemas and migrations. This ritual is read-only for source files and DBs.

## Commands

Dry run:

```powershell
pnpm backup:prisma:dry-run
```

Create backup:

```powershell
pnpm backup:prisma
```

Verify latest backup:

```powershell
pnpm backup:prisma:verify
```

## Output

Backups are written outside the source tree:

```text
F:\descargasf\prisma-backup-before-migration-<timestamp>\
F:\descargasf\prisma-backup-before-migration-<timestamp>.zip
```

Each backup includes:

- SQLite DB files found in approved PRISMA locations.
- Prisma schema.prisma files.
- Prisma migrations.
- backup-manifest.json with sha256, size and source path.
- BACKUP_SUMMARY.md.

## Rules

- Do not copy .env files.
- Do not copy node_modules, .next, out, dist, coverage or previous backups.
- Treat zero-byte DBs as WARN, never as operational proof.
- Fail if a detected non-empty DB cannot be read.
- Do not run migrations from the backup command.
