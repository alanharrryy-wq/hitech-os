from __future__ import annotations

import re
from pathlib import Path

path = Path("tools/code-atlas/docs/CODE_ATLAS_CUSTOMER_WOW_V1.md")
text = path.read_text(encoding="utf-8")

section9 = '''## 9. What this status proves

`UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED` with `LIMITED_EXTERNAL_FALSIFICATION_PASS_3_REPOS` proves:

- the neutral Customer Wow composition layer remains bound to the canonical Universal Intelligence Core rather than duplicating it;
- fail-closed preparation and verification still work against the neutral synthetic Git fixture;
- the repaired source passed 140 Code Atlas tests and 6/6 PR #275 repository CI workflows;
- the same neutral/default core was exercised read-only against pinned Click, Vite and ripgrep repositories;
- the full post-fix external replay produced 30/30 declared scenario behavior and 3/3 repeatability;
- undeclared dirty-worktree mutation is independently detected instead of trusting an incomplete caller manifest;
- explicit Rust source targets now receive physical/semantic evidence and bounded repository-provable Rust dependency relationships;
- normalized JS/TS parent-relative imports recover direct static dependencies such as Vite's `define.spec.ts` -> `../../plugins/define` relationship;
- missing ownership or source-vs-document reconciliation evidence remains `UNKNOWN` rather than being invented.

This evidence is deliberately limited to the pinned repositories, commits, runner and declared scenarios recorded by the external falsification package.

## 10. What this status does NOT prove'''
pat9 = re.compile(r"## 9\. What this status proves\n.*?\n## 10\. What this status does NOT prove", re.S)
if len(pat9.findall(text)) != 1:
    raise SystemExit("WOW_SECTION9_ANCHOR_MISMATCH")
text = pat9.sub(section9, text, count=1)

section11 = '''## 11. Next gate

The next allowed gate is **broader external diversity and independent repeatability**, not another source rebuild.

Expand the same read-only falsification protocol to additional unrelated repository and stack families, including technologies not represented by Click, Vite and ripgrep. Repeat the governed evidence collection on an independent second machine/environment, preserve snapshot/provenance locking, and continue to adjudicate harness instrumentation separately from product behavior.

Hosted multi-tenant, security/IAM, data-egress, legal/privacy and production-readiness claims remain separate gates and must be proved independently if those product boundaries are pursued.

Universal Intelligence and Customer Wow remain `doNotRebuild=true`: future source work is allowed only when new evidence localizes a concrete defect.
'''
pat11 = re.compile(r"## 11\. Next gate\n.*\Z", re.S)
if len(pat11.findall(text)) != 1:
    raise SystemExit("WOW_SECTION11_ANCHOR_MISMATCH")
text = pat11.sub(section11, text, count=1)

text = text.replace("The operational suite on the final fix ran **106 tests** and passed.", "The current hardened regression suite runs **140 tests** and passes; the original pre-external integration evidence ran 106 tests.")
text = text.replace("- Ubuntu operational suite: 106 tests, `OK`;", "- original Ubuntu integration suite: 106 tests, `OK`;\n- post-external-hardening Code Atlas suite: 140 tests, `PASS`;")

if "EXTERNAL_REPO_EVIDENCE_PENDING" in text:
    raise SystemExit("WOW_PREPATCH_STALE_PENDING_REMAINS")
path.write_text(text.rstrip() + "\n", encoding="utf-8")
print("PASS_CAEXT_WOW_SECTIONS_PREPATCHED")
