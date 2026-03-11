# 35_THEME_AND_STYLE_SYSTEM

## Document Status

- Status: Canonical
- Audience: Product, Design, Engineering
- Scope: Styling model, theming concepts, visual consistency, and style application rules

---

## Purpose

This document defines the Theme and Style System for Live Scene Composer. It exists to ensure that visual styling is powerful, structured, and consistent rather than becoming an uncontrolled set of per-widget overrides with no design logic.

Styling should create quality, not visual entropy.

---

## Style System Summary

The style system should support multiple layers of visual control:

- scene-level visual context
- layout or container-level treatment
- widget-level style
- prefab defaults
- future themes and variants
- local overrides where appropriate

The system must preserve the distinction between:

- content
- structural layout
- style and treatment

---

## Why a Style System Matters

Without a structured style system, users end up with:

- inconsistent typography
- random color usage
- uneven spacing
- duplicated visual decisions
- hard-to-maintain scenes
- no clear path for theme reuse or variation

The style system exists to make visual editing scalable.

---

## Style Layers

### Scene-level style

This includes broad visual context such as:

- scene background
- overall theme context
- high-level visual treatment
- global presentation tone

### Layout/container style

This includes:

- region treatment
- spacing behavior
- panel or card chrome
- grouping treatment

### Widget-level style

This includes:

- typography
- color
- background
- spacing
- border treatment
- local effects

### Prefab defaults

Prefabs should carry opinionated style defaults that can then be refined at instance level.

---

## Typography System

Typography should be a first-class part of the style system.

Expected controls may include:

- font family
- size
- weight
- line height
- letter spacing
- alignment
- emphasis
- truncation or clamp behavior where relevant
- color and opacity

Typography is too central to be treated as an afterthought.

---

## Color and Background System

The style system should support:

- background color
- background treatment
- card or surface color
- contrast-conscious text and accent usage
- hierarchy through color, not just decoration

Users should be able to improve clarity and hierarchy through style, not merely change colors at random.

---

## Effects System

The style system may include bounded effects such as:

- shadow
- glow
- opacity
- blur where appropriate
- border emphasis
- depth treatment

Effects should enhance hierarchy and presentation, not degrade readability.

---

## Chart Appearance Styling

Charts often need style beyond data display.

Chart style capabilities may include:

- palette
- label treatment
- padding
- card or panel chrome
- title/subtitle styling
- contrast treatment

Chart appearance should be treated as a legitimate styling domain, not a special-case hack.

---

## Themes

Themes are higher-level style configurations that influence multiple parts of the scene consistently.

A theme may affect:

- palette
- typography family or rhythm
- card treatment
- default spacing feel
- visual tone

Themes should be layered in a way that does not destroy local editability.
They should guide appearance, not eliminate useful control.

---

## Variants

Variants are controlled visual alternatives within an approved pattern.

Examples:

- light vs dark treatment
- executive vs dense view
- emphasis variants for a prefab family

Variants are useful because they provide consistency with controlled difference.

---

## Style Inheritance and Override

The system should support a clear mental model for how style is applied.

A healthy model may include:

- scene-level defaults
- prefab defaults
- widget or container-level overrides
- local targeted changes

Overrides should remain understandable.
Users should not have to reverse-engineer why a color or font is coming from somewhere.

---

## Reset and Recovery

The style system should support bounded recovery actions such as:

- reset selected widget style
- reset local treatment
- discard draft style changes
- compare against baseline

If style control is powerful, recovery must also be strong.

---

## Style Anti-Patterns

The system must reject:

- uncontrolled override stacking with no clear precedence
- styling behavior hidden in unrelated modules
- treating content props and style props as the same thing
- theme systems that silently override everything without visibility
- style controls that create chaos faster than they create quality

---

## Summary

The Theme and Style System exists to give Live Scene Composer powerful visual control without visual entropy. It should support scene-level styling, typography, color, effects, chart appearance, prefab defaults, themes, and variants, while keeping precedence and local overrides understandable.
