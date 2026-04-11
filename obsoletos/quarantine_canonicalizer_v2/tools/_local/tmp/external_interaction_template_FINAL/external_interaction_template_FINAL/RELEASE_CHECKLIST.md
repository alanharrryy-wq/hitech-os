# RELEASE_CHECKLIST

Use this checklist before creating any distributable zip for `external_interaction_template`.

## 1. Pre-release hygiene

- [ ] Start from a clean working tree or a dedicated release branch/tag.
- [ ] Confirm the deliverable scope: source-only zip, demo zip, or installable package with sample data.
- [ ] Confirm Node and pnpm versions match the project contract in `package.json`.
- [ ] Confirm `.env.example` is current and does not expose local-only assumptions beyond intentional defaults.

## 2. Remove contaminated artifacts

The release zip must **not** be built from a dirty working directory.

- [ ] Remove `.next/`
- [ ] Remove `node_modules/`
- [ ] Remove nested dependency trees under `.next/` if present
- [ ] Remove `*.tsbuildinfo`
- [ ] Remove temp files, logs, caches, and editor junk
- [ ] Remove generated test output if any exists
- [ ] Remove local storage/output folders that are not part of source delivery

## 3. Decide database policy explicitly

- [ ] Decide whether `prisma/external-interaction.db` belongs in the release
- [ ] If the DB is only demo/seed state, move it to a separate demo artifact or regenerate it during setup
- [ ] If the DB is intentionally included, document why and what state it contains
- [ ] Confirm `.gitignore` and release scripts do not accidentally re-include local DB artifacts

## 4. Validate source portability

- [ ] Review `tsconfig.json` for workspace-relative assumptions such as `../../tsconfig.base.json`
- [ ] Review `README.md` for monorepo-specific commands such as `pnpm --filter ...`
- [ ] Review imports and aliases for assumptions that only work inside the original workspace
- [ ] Confirm the package can be understood and bootstrapped by someone receiving only the zip

## 5. Build the release from staging

- [ ] Create a clean staging directory
- [ ] Copy only intended source files into staging
- [ ] Re-check staging for banned artifacts before zipping
- [ ] Generate the zip from staging, not from the live repo root
- [ ] Name the zip with version/date/build metadata that can be traced later

## 6. Install-flow validation

- [ ] Run `installer.py` against the staged zip
- [ ] Validate project-root detection even if the zip has an outer wrapper directory
- [ ] Validate backup behavior by reinstalling over an existing target
- [ ] Confirm `install-report.json` is generated
- [ ] Confirm the report has no contamination warnings for the clean release zip

## 7. Runtime smoke validation

Run these from the installed copy, not from the original working repo.

- [ ] Install dependencies
- [ ] Generate Prisma client if required
- [ ] Apply DB setup/bootstrap path
- [ ] Run tests
- [ ] Run typecheck
- [ ] Run a production build
- [ ] Start the app and confirm the main surfaces load

## 8. Product smoke test

- [ ] Launcher renders
- [ ] At least one schema-driven flow can be started
- [ ] Draft save works
- [ ] Final submit path works
- [ ] Review/inbox surface loads
- [ ] Record detail surface loads
- [ ] Sync center loads
- [ ] Example schemas still switch without breaking architecture assumptions

## 9. Release contents review

- [ ] `package.json` present
- [ ] `app/` present
- [ ] `components/` present
- [ ] `src/` present
- [ ] `public/` present if required assets exist
- [ ] `prisma/` present only with intended contents
- [ ] `README.md` present and accurate
- [ ] release docs included if this is a premium handoff build

## 10. Final sign-off

- [ ] Zip size is reasonable for source delivery
- [ ] No local machine paths leaked into docs or scripts
- [ ] No credentials, tokens, or real data are present
- [ ] Version/tag/build identity is recorded
- [ ] The artifact was tested from the zip, not just from the repo
- [ ] Any remaining caveats are documented in release notes rather than left implicit
