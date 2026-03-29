# Hydration Guard Bundle

A hardened documentation-and-tooling bundle for isolating noisy React hydration warnings on internal, form-heavy tooling routes.

## What is included

- `docs/architecture/hydration-isolation-standard.md`
  - Repository standard / ADR-style document
- `docs/architecture/hydration-isolation-adoption-guide.md`
  - Adoption criteria, validation workflow, and rollout notes
- `scripts/hydration_guard_audit.py`
  - Python CLI that scans a repo for hydration-related patterns, risky broad client-only workarounds, and likely internal-tooling subtrees
- `scripts/hydration_guard_scaffold.py`
  - Python CLI that scaffolds the standard docs and implementation templates into a target repo without editing existing application code
- `templates/*.tsx`
  - Reference React / Next.js templates for narrow client-only boundaries and diagnostics
- `examples/sample_audit_report.md`
  - Example report layout produced by the audit tool

## Design principles

- Narrow isolation only
- No broad no-SSR on public content
- External DOM mutation is treated as an environment issue, not an application guarantee
- Diagnostics are opt-in and off by default
- Python tooling is standard-library only

## Typical workflow

### 1) Audit a repo

```bash
python scripts/hydration_guard_audit.py --repo-root /path/to/repo --output-dir /path/to/output
```

### 2) Scaffold docs and templates into a repo

```bash
python scripts/hydration_guard_scaffold.py --repo-root /path/to/repo --output-dir /path/to/output --force
```

### 3) Review the generated report and selectively adopt the templates

The scaffold tool intentionally does **not** patch your app automatically. It writes docs and safe reference templates so adoption stays deliberate.

## Notes

- The audit script is conservative. It reports likely candidates and risky patterns, not proof of correctness.
- The reference templates are meant for internal tooling subtrees only.
