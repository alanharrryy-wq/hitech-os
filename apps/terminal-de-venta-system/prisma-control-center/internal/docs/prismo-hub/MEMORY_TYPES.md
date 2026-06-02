# PRISMO Memory Types

PRISMO must use memory as operational intelligence, not as decorative copy.

## semantic_memory
Concepts, definitions, system vocabulary, known surfaces, render block meanings.

## episodic_memory
What happened before: installs, failures, fixes, PASS/FAIL episodes, result ZIPs, user-approved decisions.

## procedural_memory
How to solve: diagnostic recipes, fix protocols, validation paths, rollback rules, UI repair procedures.

## working_memory
Current active query context: user text, inferred intent, selected area, selected lens, temporary response state.

## operational_memory
Current runtime state: evidence count, pattern count, protocol count, store status, endpoint availability.

## visual_memory
Visual rules: Cloudglass/Refrigerant, opacity budgets, z-index, layer stack, forbidden visual downgrades.

## governance_memory
Safety and policy: no DB writes, no .env reads, no deploy, no git push, no unsafe raw HTML, no fake green.

## Required behavior
Free text queries must work without dropdowns.
Dropdowns are guidance, not required input.
If dropdowns are empty, infer intent, area, and lens from the query.
Feedback must strengthen episodic and procedural memory over time.
