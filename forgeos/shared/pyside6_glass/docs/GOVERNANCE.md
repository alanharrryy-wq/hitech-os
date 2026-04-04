# 🛡 Governance
### How code-atlas protects quality, coherence, and product identity

---

## Why governance exists

Without governance, visual systems decay in a very predictable way:

- local fixes multiply
- components fork their own style logic
- charts stop speaking the same language
- motion becomes inconsistent
- legacy modules creep back into authority
- the product starts feeling like three apps in a trench coat

Governance exists to prevent that collapse.

code-atlas does not treat quality as a matter of taste.
It treats quality as a **release discipline**.

---

## 🎯 Governance goals

The governance layer exists to ensure that:

- the package remains contract-driven
- components remain homologated
- token resolution stays authoritative
- motion remains policy-bound
- charts remain registry-driven
- dashboards remain truthful
- legacy escape hatches do not reclaim control
- release quality remains auditable

---

## 🧾 Foundational rules

### Rule 1. The coordinator owns visual truth
Final visual authority must flow through the governed appearance system, not through local component hacks.

### Rule 2. Tokens own concrete values
Spacing, blur, opacity, border strength, radius, and similar finals should be derived from tokens, not handcrafted per screen.

### Rule 3. Contracts are not optional
All first-class surfaces must participate in the shared contract vocabulary:

- `visualRole`
- `visualVariant`
- `visualEmphasis`
- `visualFxLevel`

### Rule 4. Data surfaces must tell the truth
A premium dashboard that hides freshness or error is still a failure.

### Rule 5. Legacy modules may survive, but not rule
`atlas_*` compatibility paths may exist, but they must not become final visual authority.

---

## 🚫 What governance forbids

### Styling anti-patterns
- hardcoded `setStyleSheet(...)` with final values
- local blur/shadow/glow rules outside coordinator/tokens
- random inline hex-based styling decisions

### Component anti-patterns
- default Qt widgets used as final identity
- screen-local variants with no catalog or contract
- ungoverned tables, tabs, and shells

### Motion anti-patterns
- motion that ignores `reduced_motion`
- hidden animation loops
- ornamental motion with no product purpose
- conflicting motion languages in the same workspace

### Data anti-patterns
- private chart palettes and hidden chart rules
- stale data presented as fresh
- empty states with no path forward
- giant KPIs with no timeframe, freshness, or interpretive context

### Architecture anti-patterns
- bypassing `AppearanceCoordinator`
- bypassing token resolution
- introducing parallel styling systems
- restoring legacy modules as visual headquarters

---

## 🧠 Governance mechanisms

Governance is enforced through multiple layers, not a single magic checkbox.

### 1. Contract vocabulary
Contracts constrain how surfaces are identified and rendered.

### 2. Validation
`validation.py` acts as a structured guardrail for visual governance checks.

### 3. Release gate
`release_gate.py` acts as the final checkpoint before trust is granted.

### 4. Capability contracts
Sacred and premium capability contracts define what the system must retain.

### 5. Tests
Targeted tests validate critical behaviors such as:

- chart registry integrity
- visual runtime wiring
- component governance
- template surface roles
- visual intelligence behavior

### 6. Evidence artifacts
Release evidence is emitted as structured JSON so checks can be inspected later.

---

## 🪓 Severity model

A healthy governance model distinguishes between things that are ugly and things that are disqualifying.

### Warning
Something looks risky or unclear, but not necessarily release-blocking.

Examples:
- observability could be stronger
- a module is under-documented
- a compatibility path needs cleanup

### Error
A rule is violated in a way that threatens quality or coherence.

Examples:
- hardcoded stylesheet finals
- missing contract participation
- chart logic outside the registry
- missing data-state distinction

### Release blocker
An error severe enough that the package should not pass gate.

Examples:
- coordinator bypass in a critical runtime path
- broken contract invariants
- visual regression in core proof flows
- false freshness or silent state ambiguity in operational surfaces

---

## 🔍 What the gate should make visible

A good release gate should not merely say “passed” or “failed”.

It should make visible:

- what categories were checked
- how many issues were found
- which ones are blockers vs warnings
- whether contracts are solid
- whether validation passed cleanly
- whether proof/capability deltas introduced blockers

Governance without observability is just a stern face in a dark hallway.

---

## 📊 Governance categories that matter

A mature governance layer should reason in categories such as:

- `hardcoded_styles`
- `visual_contracts`
- `motion_policy`
- `chart_registry`
- `data_states`
- `atlas_authority`
- `capability_contracts`
- `proof_integrity`

These categories help audits stay fast, precise, and trustworthy.

---

## 🧪 Validation philosophy

Validation should be:

- deterministic
- explainable
- category-aware
- stable under CI
- rich enough to support debugging
- strict enough to stop rot before release

Validation should not be:
- purely decorative
- too vague to trust
- dependent on guesswork
- impossible to interpret after the fact

---

## 🧱 Governance and design quality

Governance is not the enemy of beauty.
It is what keeps beauty from collapsing into inconsistency.

A visually premium system without governance usually lasts about as long as a paper umbrella in a thunderstorm.

A visually premium system with governance can scale.

That is the point.

---

## 🧭 Decision rule for contributors

When deciding whether something belongs, ask:

1. Does it strengthen the existing language?
2. Does it obey contracts?
3. Does it consume tokens instead of bypassing them?
4. Does it preserve truth and usability?
5. Does it keep the system more governable, not less?

If the answer is “no” to any of those, the change is not ready.

---

## 🪙 Governance principle in one sentence

> **code-atlas treats visual quality as a protected system invariant, not as a fragile accident of good taste.**
