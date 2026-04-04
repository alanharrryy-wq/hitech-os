# 🎨 Contributing Visuals
### How to extend PySide6 Glass without turning it into a stylish disaster

---

## Before you touch anything

PySide6 Glass is not a loose styling playground.

It is a governed visual system with:

- orchestration
- tokens
- contracts
- runtime structure
- rendering discipline
- validation
- release-gated quality

That means contribution is welcome, but freelancing is not.

If you want to add or refine visuals, your job is to **extend the system**, not work around it.

---

## 🎯 Contributor goals

When contributing visuals, aim for:

- stronger coherence
- clearer hierarchy
- better tactility
- more truthful data surfaces
- cleaner architecture
- better observability
- zero regressions in governance

---

## 🧾 Non-negotiable rules

### 1. Respect the contract vocabulary
All first-class surfaces should align with:

- `visualRole`
- `visualVariant`
- `visualEmphasis`
- `visualFxLevel`

Do not invent a side dialect because a widget felt special.

### 2. Consume tokens, do not bypass them
If your change needs final values, they should come from the governed appearance system whenever possible.

### 3. Do not bypass orchestration
Avoid local visual logic that skips the coordinator and invents final identity on its own.

### 4. Truth beats decoration
Dashboards, metrics, and charts must remain honest about state, freshness, and failure.

### 5. Accessibility outranks spectacle
`reduced_motion`, contrast constraints, and readability are governors, not suggestions.

---

## 🧩 If you add a component

A new component should:

- have a clear purpose
- fit the homologated language
- support a stable contract identity
- use tokens instead of local style finals
- expose sensible states
- feel like part of the product, not a visitor from a different design galaxy

### Ask yourself
- What is this component’s role?
- What variant family does it belong to?
- How much emphasis should it carry?
- How much FX envelope is actually appropriate?
- Does it still look correct when motion is off and atmosphere is reduced?

---

## 🌫 If you add an effect

A new effect should:

- flow through the governed effects system
- be disable-able
- obey visual level envelopes
- obey accessibility constraints
- remain subordinate to task clarity

Good effects feel like craft.  
Bad effects feel like the UI discovered an energy drink.

---

## 🎞 If you refine motion

Motion should:

- preserve continuity
- guide attention
- confirm interaction
- feel premium
- remain calm under long sessions

Motion should not:

- exist just because animation is possible
- keep moving while hidden
- override reduced motion
- make operational interfaces harder to parse

---

## 📊 If you touch charts or dashboards

Always remember:

- charts are truth surfaces
- dashboards are trust surfaces

That means your change should preserve or improve:

- registry discipline
- state clarity
- freshness visibility
- empty/error quality
- readability under density
- semantic consistency

A gorgeous chart that hides stale data is still a failure wearing expensive shoes.

---

## 🧠 If you touch orchestration or runtime

Be careful.

Changes to:

- `AppearanceCoordinator`
- `AppearanceProfile`
- `EffectsProfile`
- `visual_runtime.py`
- `runtime.py`
- `template.py`
- `rendering/surface_renderer.py`

can affect the entire package.

When working here:

- prefer minimal, clear changes
- avoid parallel control paths
- keep state flow legible
- improve observability where possible
- protect the token boundary

---

## 🛡 If you touch validation or the release gate

Your goal is not to make the gate louder.
Your goal is to make it more trustworthy.

Good improvements include:

- clearer categories
- better blocker vs warning splits
- explicit issue reporting
- easier audit output
- stronger mapping between violations and evidence

Bad improvements include:

- ceremonial complexity
- vague pass/fail theater
- duplicated logic everywhere
- second gates pretending to help

---

## ✅ Definition of a good visual contribution

A contribution is probably healthy if it makes the system feel:

- more coherent
- more intentional
- more premium
- more truthful
- more governable
- easier to audit

A contribution is probably unhealthy if it makes the system feel:

- more fragmented
- more ad hoc
- more theatrical
- less predictable
- harder to validate
- more dependent on local exceptions

---

## 🔍 Review checklist

Before calling a visual change done, ask:

### Contracts
- Does it respect contract vocabulary?

### Tokens
- Does it consume tokens instead of bypassing them?

### Runtime
- Does it preserve the expected orchestration path?

### Motion
- Does it obey motion policy and accessibility?

### Data truth
- Does it preserve or improve state/freshness clarity?

### Cohesion
- Does it feel like PySide6 Glass, not like an imported mood?

### Governance
- Would validation and release discipline still make sense after this change?

---

## 🪙 Final principle

> **Contributing to PySide6 Glass means improving a system language, not decorating a screen in isolation.**
