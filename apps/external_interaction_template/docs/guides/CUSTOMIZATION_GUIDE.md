# CUSTOMIZATION_GUIDE

## Goal

Customize branding, theme, visual polish, and layout behavior **without** breaking the schema-driven core.

The safest rule is simple:

- treat record schemas, state logic, validation, actions, services, and sync behavior as the product engine
- treat branding and presentation as a layer around that engine

## What to preserve

Do not change these concepts just to achieve a visual goal:

- schema IDs
- step IDs
- field IDs
- state names
- action IDs
- service contracts
- adapter boundaries
- token/resume behavior

If the change is visual, keep it visual.

## Safe customization zones

### 1. Branding assets

Safe changes:

- product name and description metadata
- logos, icons, favicons, and marketing assets under `public/`
- route copy, empty-state copy, helper text, and labels that do not affect schema contracts

Avoid:

- coupling brand terms to generic domain entities in the core model

### 2. Theme tokens without editing shared global token files

If `globals.css` or `tailwind.config.mjs` are frozen, prefer local layering:

- add route-level wrappers with brand-specific utility classes
- use CSS Modules or component-local styles for page-specific accents
- create wrapper components that inject consistent className patterns
- use composition around existing primitives instead of mutating the primitives themselves

Recommended pattern:

- create `components/brand/` or `components/theme/`
- keep brand-specific wrappers there
- let shared primitives remain the stable baseline

### 3. Visual primitives

Safe approach:

- compose from existing primitives such as buttons, badges, inputs, cards/surfaces
- add alternative wrappers like `BrandSurface`, `BrandSectionHeader`, `BrandHero`, `BrandSidebar`
- keep props/contracts compatible with the shared primitives where possible

Risky approach:

- editing the foundational primitive in a way that changes spacing, semantics, or behavior for every consumer at once

### 4. Layout customization

Safe approach:

- add route-local containers
- add optional brand panels, onboarding blocks, help rails, or dashboards around the existing schema-driven surfaces
- introduce higher-level wrappers that call into the same flow/review/detail/sync components

Risky approach:

- changing shared shell/frame behavior in a way that breaks other streams or assumes only one product skin will exist

## Recommended customization strategy

### Tier 1. Surface-only branding

Use when the goal is a new visual identity without runtime risk.

Examples:

- logo swap
- copy rewrite
- background/hero treatments
- status legend polish
- branded wrappers around existing content blocks

### Tier 2. Presentation composition

Use when the goal is a premium product skin.

Examples:

- custom dashboard page that links into the same flows
- specialized landing page for a chosen schema family
- branded review shell around the same record surfaces
- alternate section headers or information rails

### Tier 3. Controlled schema customization

Use when the goal is domain adaptation while preserving engine behavior.

Examples:

- add or rename example schemas
- change field labels, descriptions, or options
- change view sections and list field projections
- adjust conditional visibility within schema definitions

Keep this schema-driven. Do not fork the runtime just to support a new business vocabulary.

## Guardrails for schema-driven safety

When customizing, verify all of the following remain true:

- field IDs remain stable where data continuity matters
- flow steps still validate through the existing validation layer
- visibility still comes from schema/config rules instead of page-specific hacks
- actions still map to valid states/roles
- record rendering still works from schema metadata rather than one-off component branching

## Suggested file organization for custom work

```text
components/
  brand/
    brand-shell.tsx
    brand-header.tsx
    brand-surface.tsx
    brand-hero.tsx
  theme/
    brand-tokens.ts
    status-palette.ts
public/
  brand/
    logo.svg
    mark.svg
    illustrations/
```

This keeps custom presentation additive instead of invasive.

## What not to do

Avoid these anti-patterns:

- baking a specific business domain into core record/service names
- hardcoding schema-specific behavior into shared runtime components
- changing validation/state logic to achieve a cosmetic outcome
- modifying shared files owned by another stream just to move pixels around
- relying on a bundled local DB as the long-term customization mechanism

## Practical customization sequence

1. Brand assets and metadata
2. Wrapper components and route-local visual composition
3. Schema labels/views/examples
4. Only then consider shared visual primitive changes, and only with cross-stream coordination

That order keeps the engine reusable and sharply reduces merge pain with parallel work on shared shell/flow/review/sync files.
