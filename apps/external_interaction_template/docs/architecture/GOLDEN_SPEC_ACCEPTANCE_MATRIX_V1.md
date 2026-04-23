# GOLDEN SPEC ACCEPTANCE MATRIX V1
Project: `apps/external_interaction_template`  
Version: `v1.0`  
Status: `APPROVED`  
Effective date: `2026-04-13`

This matrix operationalizes `GOLDEN_SPEC_UI_SHELL_V1.md` into route-by-route and theme-by-theme acceptance checks.

---

## 1) Route families under control

1. `/` (launcher)
2. `/inbox`
3. `/flow/[schemaId]`
4. `/record/[recordId]`
5. `/sync`

---

## 2) Canonical themes under control

1. `aurora` (Nebula Midnight)
2. `solstice` (Pearl Mist)
3. `neon` (Nova Rose)

---

## 3) Global pass/fail checklist (every route, every theme)

Use this checklist as binary gate:

1. Sidebar persistent on desktop.
2. Sidebar collapse/expand works and keeps active route clear.
3. Chrome bar height remains `44-48px`.
4. Chrome bar is single-row and utility-only.
5. No hero block dominates route first read.
6. Main task surface is primary.
7. Context stack is secondary and sticky on desktop.
8. Focus states are visible and keyboard traversal works.
9. Loading/empty/error states are coherent with shell grammar.
10. Background motion is visible, subtle, and non-distracting.
11. `prefers-reduced-motion` behavior is respected.
12. Theme persona is correct without changing layout grammar.

If any item fails, mark route/theme slice as failed.

---

## 4) Theme persona gates

### 4.1 Aurora gate

1. Cool deep-blue atmosphere.
2. Glow restrained and crisp.
3. No pink-dominant or washed look.

### 4.2 Solstice gate

1. Blue-mist identity maintained.
2. Never plain white flat backdrop.
3. Text contrast remains clear and stable.

### 4.3 Neon gate

1. Rose-magenta premium tone.
2. Bloom controlled, not oversaturated.
3. Action controls remain legible.

---

## 5) Route-specific functional gates

### 5.1 `/flow/[schemaId]`

1. Route summary is compact strip, not hero.
2. Flow engine is inside one primary work card.
3. Resume/progress/meta cards are in contextual stack.
4. Progress and record metadata stay visible.

### 5.2 `/inbox`

1. Queue controls remain compact and operational.
2. Record list/cards align with shell spacing rhythm.
3. Action buttons preserve clear visual hierarchy.

### 5.3 `/record/[recordId]`

1. Record detail reads as task workspace.
2. Timeline and controls stay within shell grammar.
3. Context information remains secondary.

### 5.4 `/sync`

1. Diagnostics sections are operational and compact.
2. Dispatch/event blocks follow same surface hierarchy.
3. No one-off visual language.

---

## 6) Execution matrix template

Use this table for every review cycle:

| Route | Theme | Shell | Sidebar | Chrome | Main Surface | Context Stack | Motion | Accessibility | Persona | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| `/inbox` | `aurora` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/inbox` | `solstice` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/inbox` | `neon` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/flow/[schemaId]` | `aurora` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/flow/[schemaId]` | `solstice` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/flow/[schemaId]` | `neon` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/record/[recordId]` | `aurora` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/record/[recordId]` | `solstice` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/record/[recordId]` | `neon` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/sync` | `aurora` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/sync` | `solstice` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| `/sync` | `neon` | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |

Final acceptance rule:

1. All matrix rows must be PASS.
2. Any FAIL blocks release of visual changes.

---

## 7) Minimum evidence for approval cycles

Every acceptance cycle must capture:

1. Completed matrix with reviewer name/date.
2. Screenshots per route/theme where needed.
3. Notes for each failed item and remediation owner.
4. Confirmation of no scope drift beyond UI shell/theme contracts.

