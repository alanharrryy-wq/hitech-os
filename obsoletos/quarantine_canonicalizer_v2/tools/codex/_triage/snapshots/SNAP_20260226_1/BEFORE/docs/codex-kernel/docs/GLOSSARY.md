# GLOSSARY — Terms Used by the Codex Kernel

STATUS: ACTIVE

## Built‑in Improvements (10)

1. Short definitions (no essays)
2. Disambiguation for overloaded words (scope, contract, determinism)
3. “If you mean X, say Y” guidance
4. Canonical file naming conventions
5. What counts as “contract” in different project types
6. What “additive-only” really forbids
7. What “integrator repair” allows
8. What “smoke test” means here
9. A mini FAQ
10. A “don’t fight over words” section

---

## Core Terms

**Contract**  
A publicly consumed interface: schema/API/type/test-id/CLI flag. If you break it, you must declare it and migrate it.

**Scope**  
The exact set of folders/files a builder is allowed to touch.

**Additive-only**  
No deletion/move/rename by default; changes should extend behavior without breaking existing usage.

**Deterministic-by-default**  
Runs behave the same given the same inputs; avoid timer-driven control as the primary mechanism.

**Builder (A/B/C/D)**  
A scoped agent producing changes + evidence artifacts.

**Integrator (Z)**  
The merge/repair/validate/report agent. Integration-only, no feature invention.

**Bundle**  
A folder containing machine+human artifacts: status, diffs, logs, summaries.

**Smoke Test**  
A minimal deterministic test that proves the system still boots and performs one critical path.

---

## Mini FAQ

Q: Can Z change code?  
A: Yes, but only to repair integration breakage, not to invent new features.

Q: Can we delete files?  
A: Only if explicitly allowed; otherwise file goes into DELETION_REQUESTS.

Q: Do we have to use Playwright?  
A: No. If UI exists, e2e smoke is recommended, and Python can invoke Playwright. Otherwise, use stack-appropriate smoke signals.
