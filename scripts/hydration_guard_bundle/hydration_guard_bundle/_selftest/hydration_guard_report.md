# Hydration Guard Audit Report

- Repo root: `/mnt/data/hydation_guard_bundle`
- Files scanned: **7**
- Files skipped: **0**
- Total findings: **140**
- Tool version: **1.0.0**

## Findings by category

- `client_boundary_hint`: 18
- `diagnostic_hint`: 11
- `dom_mutation_signature`: 4
- `dynamic_ssr_false`: 3
- `hydration_keyword`: 43
- `suppress_hydration_warning`: 1
- `tooling_route_hint`: 57
- `use_client`: 3

## Recommendations

- Investigate affected internal routes for narrow client-only isolation. The warning signature resembles external DOM mutation before hydration.
- Review all dynamic(..., { ssr: false }) usages and confirm they are scoped narrowly to internal tooling subtrees rather than full route trees.
- Audit suppressHydrationWarning usages and replace broad suppression with route-local root cause analysis where possible.

## Likely internal tooling paths

- `docs/architecture/hydration-isolation-standard.md`
- `examples/sample_audit_report.md`
- `docs/architecture/hydration-isolation-adoption-guide.md`
- `templates/internal-tool-client-only-boundary.tsx`
- `README.md`
- `templates/use-internal-tool-hydration-diagnostics.ts`
- `templates/scene-studio-page-client-only.tsx`

## Risky broad workaround paths

- None detected from the configured heuristics.

## Sample findings

- **MEDIUM** `hydration_keyword` in `README.md:1` -> `# Hydration Guard Bundle` (pattern match)
- **MEDIUM** `hydration_keyword` in `README.md:3` -> `A hardened documentation-and-tooling bundle for isolating noisy React hydration warnings on internal, form-heavy tooling routes.` (pattern match)
- **LOW** `tooling_route_hint` in `README.md:3` -> `A hardened documentation-and-tooling bundle for isolating noisy React hydration warnings on internal, form-heavy tooling routes.` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `README.md:7` -> `- `docs/architecture/hydration-isolation-standard.md`` (pattern match)
- **MEDIUM** `hydration_keyword` in `README.md:9` -> `- `docs/architecture/hydration-isolation-adoption-guide.md`` (pattern match)
- **MEDIUM** `hydration_keyword` in `README.md:11` -> `- `scripts/hydration_guard_audit.py`` (pattern match)
- **MEDIUM** `hydration_keyword` in `README.md:12` -> `- Python CLI that scans a repo for hydration-related patterns, risky broad client-only workarounds, and likely internal-tooling subtrees` (pattern match)
- **LOW** `tooling_route_hint` in `README.md:12` -> `- Python CLI that scans a repo for hydration-related patterns, risky broad client-only workarounds, and likely internal-tooling subtrees` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `README.md:13` -> `- `scripts/hydration_guard_scaffold.py`` (pattern match)
- **LOW** `tooling_route_hint` in `README.md:26` -> `- Python tooling is standard-library only` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `README.md:33` -> `python scripts/hydration_guard_audit.py --repo-root /path/to/repo --output-dir /path/to/output` (pattern match)
- **MEDIUM** `hydration_keyword` in `README.md:39` -> `python scripts/hydration_guard_scaffold.py --repo-root /path/to/repo --output-dir /path/to/output --force` (pattern match)
- **LOW** `tooling_route_hint` in `README.md:49` -> `- The reference templates are meant for internal tooling subtrees only.` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:1` -> `# Hydration Isolation Standard for Internal Tooling` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:1` -> `# Hydration Isolation Standard for Internal Tooling` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:8` -> `Reduce noisy or misleading React hydration warnings in internal, form-heavy tooling subtrees that are prone to third-party DOM mutation before hydration.` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:8` -> `Reduce noisy or misleading React hydration warnings in internal, form-heavy tooling subtrees that are prone to third-party DOM mutation before hydration.` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:12` -> `Some internal tooling routes emit hydration warnings where React reports unexpected attributes on form controls, including examples such as:` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:12` -> `Some internal tooling routes emit hydration warnings where React reports unexpected attributes on form controls, including examples such as:` (likely internal tooling subtree)
- **HIGH** `dom_mutation_signature` in `docs/architecture/hydration-isolation-standard.md:14` -> `- `field_signature`` (signature often associated with external DOM mutation)
- **HIGH** `dom_mutation_signature` in `docs/architecture/hydration-isolation-standard.md:15` -> `- `form_signature`` (signature often associated with external DOM mutation)
- **HIGH** `dom_mutation_signature` in `docs/architecture/hydration-isolation-standard.md:16` -> `- `alternative_form_signature`` (signature often associated with external DOM mutation)
- **HIGH** `dom_mutation_signature` in `docs/architecture/hydration-isolation-standard.md:17` -> `- `visibility_annotation`` (signature often associated with external DOM mutation)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:19` -> `This signature strongly suggests the DOM was mutated before or during hydration, commonly by agents outside application control such as browser extensions, password managers, or browser autofill tooling.` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:19` -> `This signature strongly suggests the DOM was mutated before or during hydration, commonly by agents outside application control such as browser extensions, password managers, or browser autofill tooling.` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:24` -> `- Whether internal tooling subtrees are isolated behind a client-only boundary` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:31` -> `- Browser autofill engines mutating fields before hydration` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:33` -> `Because those mutation sources are external, the correct mitigation is **defensive isolation** of the affected internal subtree, not a claim of full prevention.` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:39` -> `- guarantee prevention of all hydration warnings` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:41` -> `- replace debugging of genuine app-side render divergence` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:42` -> `- treat all hydration warnings as extension-induced` (pattern match)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:46` -> `For internal-only, form-heavy debug or tooling subtrees with recurring hydration warnings consistent with pre-hydration DOM mutation, render the affected subtree behind `InternalToolClientOnlyBoundary`.` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:46` -> `For internal-only, form-heavy debug or tooling subtrees with recurring hydration warnings consistent with pre-hydration DOM mutation, render the affected subtree behind `InternalToolClientOnlyBoundary`.` (likely internal tooling subtree)
- **LOW** `client_boundary_hint` in `docs/architecture/hydration-isolation-standard.md:46` -> `For internal-only, form-heavy debug or tooling subtrees with recurring hydration warnings consistent with pre-hydration DOM mutation, render the affected subtree behind `InternalToolClientOnlyBoundary`.` (existing boundary pattern or related naming)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:50` -> `Apply `InternalToolClientOnlyBoundary` only when the subtree satisfies most of the following:` (likely internal tooling subtree)
- **LOW** `client_boundary_hint` in `docs/architecture/hydration-isolation-standard.md:50` -> `Apply `InternalToolClientOnlyBoundary` only when the subtree satisfies most of the following:` (existing boundary pattern or related naming)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:52` -> `- internal-only route or internal-only overlay/panel` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:65` -> `- tooling subtree only` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:66` -> `- debug HUD only` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:68` -> `- internal workspace panel only` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:79` -> `The application can decide whether a subtree is hydrated from SSR output. It cannot prevent extensions or browser autofill systems from mutating form nodes before hydration starts.` (pattern match)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:81` -> `That makes narrow client-only isolation the appropriate architectural mitigation for internal tooling routes that repeatedly produce environment-driven hydration noise.` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:81` -> `That makes narrow client-only isolation the appropriate architectural mitigation for internal tooling routes that repeatedly produce environment-driven hydration noise.` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:87` -> `- lowers false-positive hydration noise on internal tooling routes` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:87` -> `- lowers false-positive hydration noise on internal tooling routes` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:88` -> `- reduces wasted debugging time on environment-driven warnings` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `docs/architecture/hydration-isolation-standard.md:96` -> `- careless overuse can mask legitimate hydration defects` (pattern match)
- **LOW** `tooling_route_hint` in `docs/architecture/hydration-isolation-standard.md:103` -> `- `InternalToolClientOnlyBoundary`` (likely internal tooling subtree)
- **LOW** `client_boundary_hint` in `docs/architecture/hydration-isolation-standard.md:103` -> `- `InternalToolClientOnlyBoundary`` (existing boundary pattern or related naming)
- **LOW** `client_boundary_hint` in `docs/architecture/hydration-isolation-standard.md:107` -> `- `SceneStudioPageClientOnly`` (existing boundary pattern or related naming)
