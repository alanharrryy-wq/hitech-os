# Keystone Luxury Kernel

## Purpose

The Luxury Visual Kernel is the single source of truth for premium UI styling in Keystone surfaces. It is token-driven, governed, and additive.

Flow:

1. Tokens (`luxury/tokens/*`) define style ramps, budgets, and policy ceilings.
2. Materials (`luxury/materials/*`) derive canonical recipes from token packs.
3. Semantics (`luxury/semantics/semanticMap.ts`) maps intent to accents with hard limits.
4. Surface application (`applyLuxuryStyle`, `applyLuxuryMaterial`) applies safe vars and attributes.

## Type Contracts

- `StyleId`: `LIQUID_GLASS | GOLD_NOIR_TERMINAL | GRAPHITE_PRISM_ISO`
- `SurfaceId`: `controlRoomHud | pitchCard | pitchPanel | kpiWidget | tableDense | drawer | rail | popover`
- `SemanticIntent`: `deal | cash | evidence | outcome | governance | risk | neutral`
- `PerfProfile`: `default | perf`
- `MotionLevel`: `micro | standard | hero | off`
- `MaterialId`: `glass/card | glass/inset | glass/drawer | glass/hero | ink/card | ink/drawer | graphite/card | graphite/inset`

## Governance Rules

1. Derive, do not invent.
- New materials must derive from an existing base recipe (`Card/Table/Badge/Chart` family).
- No one-off CSS fragments for premium surfaces.

2. Semantics over decoration.
- Accent/glow is only valid when tied to `deal`, `cash`, `evidence`, `outcome`, `governance`, or `risk`.
- Neutral state must remain available.

3. Motion hierarchy.
- One hero motion max per screen.
- Micro motion for all other interactions.
- Reduced motion and `motion=off` render final state with zero animation.

4. Budget enforcement.
- Glow budget and gold budget are first-class tokens and must be consumed via helpers.
- `perf` profile reduces or disables expensive effects while preserving hierarchy.

## Canonical Material Stack

- Liquid Glass: `glass/card`, `glass/inset`, `glass/drawer`, `glass/hero`
- Gold Noir Terminal: `ink/card`, `ink/drawer`
- Graphite Prism ISO: `graphite/card`, `graphite/inset`

Each recipe includes:

- Surface background vars
- Hairline border vars
- Inner-stroke vars
- Optional blur vars (gated by perf + blur support)
- Specular overlay vars (subtle only)
- Optional bounded texture vars (`grain` or `grid`)

## Budgets

Global semantic policy:

- Max accents per screen: `3`
- Max accents per chart: `4`
- Graphite Prism gradient scope: chart data only

Style budget source:

- `luxury/tokens/liquidGlass.ts`
- `luxury/tokens/goldNoirTerminal.ts`
- `luxury/tokens/graphitePrismIso.ts`

## Safe Fallback Behavior

- If `backdrop-filter` is unavailable, blur falls back to opaque/tinted surfaces.
- If `perfProfile=perf`, blur and texture are minimized/disabled and specular is constrained.
- Helpers return data attributes for deterministic CSS branching (`data-lux-blur`, `data-lux-perf`, etc.).

## Anti-Flicker Rule

- Do not rewrite URL query params on initial mount.
- Query normalization must be idempotent and triggered only by explicit user action (e.g., share link click).
- Layer/style query handling must preserve first paint determinism.

## Derive vs Invent Examples

Allowed derivation:

- `glass/inset` derives from `glass/card` and only narrows blur/specular/elevation.
- `ink/drawer` derives from `ink/card` and adjusts panel shell behavior.

Forbidden invention:

- Creating `gold-neon-kpi.css` with bespoke shadows outside token budgets.
- Applying ad-hoc gradient text for Graphite Prism headings.
- Adding a new premium preset not mapped through `MaterialId` and token policy.

## Usage Pattern

```ts
import { applyLuxuryStyle } from "@hitech/ui-kit/src/luxury/index.js";

const style = applyLuxuryStyle({
  styleId: "LIQUID_GLASS",
  surfaceId: "pitchCard",
  perfProfile: "default",
  motionLevel: "micro"
});
```

Apply `style.cssVars` to the subtree and mirror `style.dataAttributes` on the same root element.
