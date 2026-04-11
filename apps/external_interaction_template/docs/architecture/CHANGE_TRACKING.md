# Change Tracking Strategy
**Project:** `apps/external_interaction_template`  
**Goal:** let you touch frontend or backend with a clear rollback point instead of cowboy-editing the repo into the void.

## 1. Is this viable?

Yes. Very viable.

This project is already modular enough to track safely because:

- frontend changes can be isolated to docs + README managed section
- backend rules live in clear modules
- the app already has strong boundaries between routes, services, store, adapters, and schema rules
- the uploaded visual artifacts also suggest a **sidecar / forensics mindset**, which is perfect for change tracking

---

## 2. What this bundle tracks

### Managed docs
- `docs/architecture/FRONTEND_VISUAL_MAP.md`
- `docs/architecture/BACKEND_FLOW_MAP.md`
- `docs/architecture/CHANGE_TRACKING.md`

### Managed README section
- `README.md` only inside a marked block

### Tracking artifacts
- `docs/architecture/_tracking/manifests/*.json`
- `docs/architecture/_tracking/snapshots/*_before.json`
- `docs/architecture/_tracking/snapshots/*_after.json`
- `docs/architecture/_tracking/backups/<run_id>/...`
- `docs/architecture/_tracking/baselines/<baseline_id>/...`
- `docs/architecture/_tracking/LAST_KNOWN_GOOD.json`
- `docs/architecture/_tracking/CHANGELOG_TRACKING.md`

---

## 3. The safety model

## A. Managed section, not full README replacement
The injector only owns a bounded block:

```md
<!-- EXTERNAL_INTERACTION_TEMPLATE:ARCHITECTURE_MAPS:START -->
...managed content...
<!-- EXTERNAL_INTERACTION_TEMPLATE:ARCHITECTURE_MAPS:END -->
```

That means:
- your manual README content stays intact
- reruns are idempotent
- updates are predictable

---

## B. Before / after snapshots
Each run writes:
- a `before` snapshot
- an `after` snapshot
- hashes
- file sizes
- timestamps

That gives you a forensic breadcrumb trail instead of vibes.

---

## C. Run manifest
Each run writes one manifest with:
- `run_id`
- `generated_at_utc`
- `app_root`
- `changed_files`
- `before`
- `after`
- `backups_dir`
- `git_head` if available
- `git_branch` if available

---

## D. Backups
Before the injector overwrites a managed file, it copies the previous version into:

`docs/architecture/_tracking/backups/<run_id>/<relative-path>.bak`

That lets you roll back the latest run even if you did not set a baseline.

---

## E. Baseline / clear point
When you run with `--set-baseline`, the injector creates a known-good checkpoint:

- copies current managed files into `baselines/<baseline_id>/...`
- updates `LAST_KNOWN_GOOD.json`

That becomes your **clear point**.

---

## 4. Recommended workflow

## Normal safe run
1. run `--dry-run`
2. inspect output
3. run real write
4. if happy, run `--set-baseline`

## When experimenting hard
1. set a baseline first
2. make your changes
3. if things go sideways, use `--rollback-baseline`

## When you just want to undo the last injector pass
1. run `--rollback-latest`

---

## 5. Rollback modes

## A. Latest rollback
Use this when:
- the last injector run was bad
- you want to restore the previous state of managed files

Command:
```powershell
$root = 'F:\repos\hitech-os\apps\external_interaction_template'
python "$root\inject_external_interaction_template_maps.py" --app-root "$root" --rollback-latest
```

---

## B. Baseline rollback
Use this when:
- the repo drifted after several edits
- you want to go back to your last known-good checkpoint

Command:
```powershell
$root = 'F:\repos\hitech-os\apps\external_interaction_template'
python "$root\inject_external_interaction_template_maps.py" --app-root "$root" --rollback-baseline
```

---

## 6. What should count as tracked later

Once you want to go beyond docs, the next logical tracked targets are:

### Frontend
- `components/layout/app-shell.tsx`
- `components/layout/ambient-backdrop.tsx`
- `components/flow/flow-runner.tsx`
- `components/records/record-inbox.tsx`
- `components/records/record-detail.tsx`
- `components/sync/sync-center.tsx`
- `src/lib/ui/runtime.ts`

### Backend
- `src/lib/services/records.ts`
- `src/lib/services/actions.ts`
- `src/lib/core/schema-registry.ts`
- `src/lib/core/state.ts`
- `src/lib/core/validation.ts`
- `src/lib/store/prisma-store.ts`
- `app/api/*`

I would not make the injector auto-edit those yet unless you deliberately want a broader managed footprint.

---

## 7. Safe vs dangerous changes

## Safe-ish
- changing docs
- changing README managed section
- changing copy
- changing visual primitives with local validation

## Medium risk
- changing runtime UI presets
- changing inbox/record/sync layout
- changing schema view sections

## High risk
- changing state transitions
- changing validation logic
- changing adapter dispatch logic
- changing Prisma persistence
- changing request-context role normalization

---

## 8. Clear-point rule

A baseline is only valid if:

- docs generated cleanly
- README managed block updated cleanly
- tracked file hashes look sane
- no unexpected files changed
- the app still boots
- at least smoke tests pass

If those conditions are not true, do **not** bless the baseline.

---

## 9. Suggested practical routine

For this repo, the clean routine is:

1. `--dry-run`
2. real apply
3. inspect git diff
4. run tests / smoke check
5. `--set-baseline`

That gives you a crisp, human-readable, machine-restorable clear point.
