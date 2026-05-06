# PRISMA Light Canonical Status

Status: DRAFT_FOR_REVIEW

As of this document set, PRISMA Light POS is defined as a white / light operational visual skin for the PRISMA terminal experience.

---

## 1. Canonical intent

PRISMA Light POS exists to describe a premium clear interface that preserves the same operational skeleton as PRISMA Dark POS:

- left sidebar,
- central catalog,
- right cart,
- large product cards,
- visible totals,
- dominant `COBRAR` button,
- Spanish Mexican copy.

The skin changes surface language, not product responsibility. In barrio terms: misma taqueria, nueva iluminacion, no nuevo menu inventado por un primo.

---

## 2. Relationship to the shared visual system

The shared visual layer should govern:

- brand tokens,
- semantic states,
- typography family,
- radius philosophy,
- motion limits,
- component names,
- accessibility rules,
- es-MX copy conventions,
- visual OS surface profiles.

The local product surface should govern:

- density,
- layout emphasis,
- exact module hierarchy,
- POS vs backoffice behavior,
- card-first vs table-first presentation,
- desktop, tablet or mobile ergonomics.

---

## 3. Canonical skin interpretation

| Skin | Core identity | Best surface |
|---|---|---|
| PRISMA Dark POS | dark, glass, gold, cinematic | POS showcase / premium dark |
| PRISMA Light POS | white, frosted, blue, operational | POS daily operation |
| PRISMA PC Slate | clear, technical, table-first | PC Backoffice |
| PRISMA Mobile Pulse | compact, alert-first, supervisor | Mobile App |

---

## 4. Guardrails

PRISMA Light POS must not:

- become generic fintech,
- replace product grid with tables,
- use green as checkout primary,
- remove product images,
- hide stock,
- lose the cart panel,
- use English labels,
- break the three-zone POS composition.

---

## 5. Promotion criteria

Promote PRISMA Light POS from `DRAFT_FOR_REVIEW` to `PROMOTED` only when:

1. The docs are installed under the canonical docs folder.
2. The white reference screenshot is available as visual source.
3. The design system tokens are mapped to implementation tokens.
4. The UI kit component names match code or planned component wrappers.
5. A screenshot comparison confirms the three-zone composition.
6. PC, Tablet and Mobile ownership boundaries are not broken.

---

## 6. Current recommendation

Use PRISMA Light POS as the reference for the clear operational POS skin. Do not force PC Backoffice to become the same screen. PC should consume the shared skin language only where it makes sense, then interpret it through a backoffice surface profile.
