from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
README = ROOT / "tools/code-atlas/README.md"
WOW_MD = ROOT / "tools/code-atlas/docs/CODE_ATLAS_CUSTOMER_WOW_V1.md"
WOW_JSON = ROOT / "tools/code-atlas/docs/CODE_ATLAS_CUSTOMER_WOW_V1.contract.json"
LEDGER = ROOT / "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json"
EVIDENCE = ROOT / "PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json"
MANUAL = ROOT / "apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md"

MERGE = "caf918694c1c397d19a61bff217800d027a384e3"
FIX_MESH_RUN = 31866829102
FIX_MESH_ARTIFACT = 9242284746
TARGETED_ARTIFACT = 9242394010
FULL_RUN = 31867491454
FULL_ARTIFACT = 9242450935
CLOSURE_MESH_RUN = 31867706125
CLOSURE_MESH_ARTIFACT = 9242519545
CLOSURE_MESH_DIGEST = "sha256:1f73190bd9213fdac786001d0d5a8c89050e1d73c9f029ea514244ea8721d9ae"
UPDATED = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unique(values):
    return list(dict.fromkeys(values))


# README: replace only the evidence-status section.
readme = README.read_text(encoding="utf-8")
readme_replacement = f'''## Current evidence status

Current governed state: **`LOCAL_VERIFIED`**.

The Universal Intelligence + Customer Wow binding remains the canonical implementation and the Factory Ledger continues to preserve it as `doNotRebuild=true`. PR #275 hardened that implementation after a real external falsification gate and merged the source fix into `main` as `{MERGE}`.

External evidence is now **limited but real**: the neutral/default profile was replayed read-only against pinned unrelated repositories **Click (Python), Vite (TypeScript/Node monorepo), and ripgrep (Rust)**. The post-fix full replay completed **30/30 declared scenarios**, **3/3 repeatability**, read-only compliance, and zero critical behavior failures after manual adjudication of legacy harness reporting. The hardened source also passed **140 Code Atlas tests** and **6/6 PR CI workflows**.

The evidence specifically supports fail-closed undeclared dirty-worktree detection, evidence-bearing Rust source targets with bounded repository-provable Rust dependencies, and normalized JS/TS parent-relative dependency resolution. It does **not** establish correctness for arbitrary repositories or stacks.

The next evidence gate is **broader repository/stack diversity, independent second-machine repeatability, and hosted/security boundary evidence**. Current evidence does **not** certify hosted multi-tenant execution, enterprise IAM/security, legal/privacy compliance, paid-pilot readiness by itself, absolute repository universality, or production certification.

`certifiable=false` and `productionCertified=false` remain invariant until separate evidence-backed gates prove otherwise.

## Architecture'''
readme_pattern = re.compile(r"## Current evidence status\n.*?\n## Architecture", re.S)
if len(readme_pattern.findall(readme)) != 1:
    raise SystemExit("README_EVIDENCE_SECTION_ANCHOR_MISMATCH")
write_text(README, readme_pattern.sub(readme_replacement, readme, count=1))


# Customer Wow narrative: remove pending claim, add limited external evidence block.
wow = WOW_MD.read_text(encoding="utf-8")
old_status = "Status: `UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED_EXTERNAL_REPO_EVIDENCE_PENDING`"
if wow.count(old_status) != 1:
    raise SystemExit("WOW_STATUS_ANCHOR_MISMATCH")
wow = wow.replace(
    old_status,
    "Status: `UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED`\n\nExternal evidence status: `LIMITED_EXTERNAL_FALSIFICATION_PASS_3_REPOS`",
    1,
)
marker = "## External falsification evidence after PR #275"
if marker not in wow:
    anchor = "- Universal Intelligence PR #270 merge commit `83a83bf50691e866d31465993d7145e033fb2cc0`\n"
    if wow.count(anchor) != 1:
        raise SystemExit("WOW_AUTHORITY_ANCHOR_MISMATCH")
    block = f'''

{marker}

Source hardening was driven by external evidence rather than a rebuild:

- repair Authority Mesh: run `{FIX_MESH_RUN}` on the pre-fix governed baseline;
- source repair: PR #275, merged to `main` as `{MERGE}`;
- targeted post-fix external evidence artifact: `{TARGETED_ARTIFACT}`;
- full post-fix external replay: workflow run `{FULL_RUN}`, artifact `{FULL_ARTIFACT}`;
- external corpus: pinned Click, Vite and ripgrep repositories under the neutral/default profile;
- result: `30/30` declared full-gate scenarios behaved as expected after fix, `3/3` repeatability, read-only compliance;
- source regression suite: `140` Code Atlas tests PASS;
- PR #275 repository CI: `6/6` workflows PASS;
- closure Authority Mesh: run `{CLOSURE_MESH_RUN}`, artifact `{CLOSURE_MESH_ARTIFACT}`, digest `{CLOSURE_MESH_DIGEST}`.

Proven hardening includes independent Git-worktree reconciliation in Verify, Rust source evidence plus bounded repository-provable Rust dependency edges, normalized JS/TS parent-relative imports, and more explicit architecture coverage/provenance.

Legacy harness outputs required manual adjudication: case-insensitive `NDC` matched inside source-derived `tailwindcss`, and the legacy matrix read Change Impact size from the DISCOVER graph rather than the prepared change model. Those instrumentation defects are not promoted to Code Atlas product failures.

This is **limited external falsification evidence**, not an arbitrary-repository, enterprise, hosted, legal/privacy/IAM, or production certification.
'''
    wow = wow.replace(anchor, anchor + block, 1)
old_next = "The next gate is execution against **unrelated external repositories**."
if old_next in wow:
    wow = wow.replace(
        old_next,
        "The next gate is broader repository/stack diversity, independent second-machine repeatability, and hosted/security boundary evidence.",
        1,
    )
if "EXTERNAL_REPO_EVIDENCE_PENDING" in wow:
    raise SystemExit("WOW_STALE_EXTERNAL_PENDING_REMAINS")
write_text(WOW_MD, wow)


# Machine-readable Customer Wow contract.
contract = json.loads(WOW_JSON.read_text(encoding="utf-8"))
if contract.get("certifiable") is not False or contract.get("productionCertified") is not False:
    raise SystemExit("WOW_CERTIFICATION_INVARIANT_BROKEN_PRE")
contract["status"] = "UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED"
contract["externalEvidence"] = {
    "status": "LIMITED_EXTERNAL_FALSIFICATION_PASS_3_REPOS",
    "sourceRepairPr": 275,
    "sourceRepairMergeCommit": MERGE,
    "repairAuthorityMeshRunId": FIX_MESH_RUN,
    "repairAuthorityMeshArtifactId": FIX_MESH_ARTIFACT,
    "targetedExternalArtifactId": TARGETED_ARTIFACT,
    "fullReplayRunId": FULL_RUN,
    "fullReplayArtifactId": FULL_ARTIFACT,
    "closureAuthorityMeshRunId": CLOSURE_MESH_RUN,
    "closureAuthorityMeshArtifactId": CLOSURE_MESH_ARTIFACT,
    "closureAuthorityMeshDigest": CLOSURE_MESH_DIGEST,
    "repositories": [
        {"name": "pallets/click", "stack": "Python library/CLI"},
        {"name": "vitejs/vite", "stack": "TypeScript/Node monorepo"},
        {"name": "BurntSushi/ripgrep", "stack": "Rust workspace/CLI"},
    ],
    "declaredScenarioResult": "30/30",
    "repeatability": "3/3",
    "readOnlyCompliance": True,
    "prCiResult": "6/6",
    "regressionTestCount": 140,
    "regressionTestResult": "PASS",
    "provenHardening": [
        "undeclared dirty worktree mutation blocks Verify independently of caller manifest",
        "legitimate explicitly declared in-scope dirty target remains verifiable",
        "recognized Rust source receives physical and semantic evidence",
        "Rust dependency graph resolves only repository-provable bounded module relationships",
        "JS/TS parent-relative imports normalize before graph matching",
        "architecture coverage and provenance are reported without granting authorization",
    ],
    "manualAdjudications": [
        "legacy case-insensitive NDC leak scan false-positive inside source-derived tailwindcss names",
        "legacy matrix changeImpactSize read from DISCOVER graph instead of prepared change model",
    ],
    "certifiesArbitraryRepositories": False,
}
negative = list(contract.get("negativeTestsCovered") or [])
for item in [
    "undeclared staged unstaged or untracked worktree mutation",
    "dirty baseline cannot issue a fresh authority pack",
]:
    if item not in negative:
        negative.append(item)
contract["negativeTestsCovered"] = negative
verification = contract.setdefault("verification", {})
verification["operationalTestCount"] = 140
verification["operationalTestResult"] = "PASS"
verification["externalRepositoryFalsification"] = "LIMITED_PASS_3_PINNED_REPOS"
verification["externalDeclaredScenarios"] = "30/30"
verification["externalRepeatability"] = "3/3"
verification["externalReadOnlyCompliance"] = "PASS"
contract["doesNotProve"] = [
    "correctness beyond the three tested pinned repositories or across arbitrary real external repositories or stacks",
    "production runtime readiness",
    "hosted multi-tenant isolation",
    "enterprise IAM or security certification",
    "customer data-egress certification beyond the runner contract",
    "paid-pilot readiness by itself",
    "legal or privacy compliance",
    "production certification",
]
contract["nextGate"] = (
    "Expand read-only falsification to broader repository and stack diversity, repeat on an independent "
    "second machine/environment, and separately prove hosted/security boundaries as required. Do not rebuild "
    "the Universal Core or Customer Wow unless new evidence identifies a concrete defect."
)
if contract.get("certifiable") is not False or contract.get("productionCertified") is not False:
    raise SystemExit("WOW_CERTIFICATION_INVARIANT_BROKEN_POST")
write_json(WOW_JSON, contract)


# Factory Ledger: preserve official status vocabulary and doNotRebuild.
ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
capabilities = ledger.get("capabilities")
if not isinstance(capabilities, list):
    raise SystemExit("LEDGER_CAPABILITIES_MISSING")
matches = [c for c in capabilities if c.get("id") == "code_atlas.change_intelligence.customer_wow_v1"]
if len(matches) != 1:
    raise SystemExit("LEDGER_CAPABILITY_CARDINALITY")
cap = matches[0]
if cap.get("doNotRebuild") is not True:
    raise SystemExit("LEDGER_DONOTREBUILD_INVARIANT")
if cap.get("status") != "LOCAL_VERIFIED":
    raise SystemExit("LEDGER_STATUS_VOCABULARY_DRIFT:" + str(cap.get("status")))
cap["stateLabel"] = "PASS_EXTERNAL_FALSIFICATION_HARDENED_3_REPOS_LOCAL_VERIFIED"
cap["nextGate"] = (
    "Broaden external repository/stack diversity, repeat the same falsification gate on an independent "
    "second machine/environment, then pursue hosted/security evidence only where required. Do not rebuild "
    "Universal Intelligence or Customer Wow."
)
cap["evidence"] = unique(list(cap.get("evidence") or []) + [
    "PR #275 merge " + MERGE,
    "Authority Mesh run 31866829102",
    "targeted external artifact 9242394010",
    "post-fix full external run 31867491454 artifact 9242450935",
    "140 Code Atlas tests PASS",
    "PR #275 CI 6/6 PASS",
    "closure Authority Mesh run 31867706125 artifact 9242519545",
])
cap["doesNotProve"] = [
    "Correct behavior beyond the three tested pinned external repositories or across arbitrary stacks",
    "Production runtime readiness",
    "Hosted multi-tenant isolation",
    "Enterprise IAM or security certification",
    "Customer data-egress certification beyond the runner contract",
    "Paid-pilot readiness by itself",
    "Legal or privacy compliance",
    "Production certification",
]
if isinstance(cap.get("allowedActions"), list):
    cap["allowedActions"] = unique(cap["allowedActions"] + [
        "broader read-only external falsification",
        "independent second-machine repeatability verification",
    ])
if "updatedAt" in ledger:
    ledger["updatedAt"] = UPDATED
write_json(LEDGER, ledger)


# Evidence index: append an idempotent limited external evidence record.
evidence_index = json.loads(EVIDENCE.read_text(encoding="utf-8"))
artifacts = evidence_index.get("artifacts")
if not isinstance(artifacts, list):
    raise SystemExit("EVIDENCE_ARTIFACTS_MISSING")
artifact_name = "PR #275 Code Atlas external falsification hardening"
record = {
    "artifact": artifact_name,
    "type": "code_atlas_external_falsification_hardening",
    "scope": ["code_atlas", "change_intelligence", "external_evidence", "governance"],
    "status": "PASS_EXTERNAL_FALSIFICATION_LIMITED",
    "proves": [
        "Code Atlas source was hardened from concrete external falsification defects without rebuilding Universal Intelligence or Customer Wow",
        "PR #275 merged as " + MERGE + " with 6/6 repository CI workflows passing",
        "140 Code Atlas tests passed after the source repair",
        "Full post-fix read-only replay against pinned Click, Vite and ripgrep produced 30/30 declared scenario behavior and 3/3 repeatability",
        "Verify blocks undeclared dirty-worktree mutations while preserving declared in-scope changes",
        "Rust source evidence and bounded repository-provable dependency relationships are available",
        "Vite parent-relative JS/TS import evidence is recovered into static dependency/change-impact analysis",
    ],
    "doesNotProve": [
        "Correctness across arbitrary external repositories or every technology stack",
        "Production runtime readiness",
        "Hosted multi-tenant isolation",
        "Enterprise IAM/security certification",
        "Legal/privacy compliance",
        "Absolute repository universality",
    ],
    "evidence": [
        "repair Authority Mesh run 31866829102",
        "targeted artifact 9242394010",
        "full replay run 31867491454 artifact 9242450935",
        "closure Authority Mesh run 31867706125 artifact 9242519545",
    ],
}
for i, old in enumerate(artifacts):
    if isinstance(old, dict) and old.get("artifact") == artifact_name:
        artifacts[i] = record
        break
else:
    artifacts.append(record)
entries = evidence_index.get("entries")
if isinstance(entries, list):
    run_id = "PR275_CODE_ATLAS_EXTERNAL_FALSIFICATION_HARDENING"
    new_entry = {
        "capabilityId": "code_atlas.change_intelligence.customer_wow_v1",
        "status": "LOCAL_VERIFIED",
        "runId": run_id,
        "evidence": ["PR #275", MERGE, "31867491454/9242450935", "31867706125/9242519545"],
    }
    for i, old in enumerate(entries):
        if isinstance(old, dict) and old.get("runId") == run_id:
            entries[i] = new_entry
            break
    else:
        entries.append(new_entry)
if "updatedAt" in evidence_index:
    evidence_index["updatedAt"] = UPDATED
write_json(EVIDENCE, evidence_index)


# Field Manual: append one idempotent learning entry.
manual = MANUAL.read_text(encoding="utf-8")
heading = "### 2026-08-14/15 - Code Atlas: falsificación externa real antes de ampliar claims"
if heading not in manual:
    manual += f'''

---

{heading}

**Tipo:** EVIDENCE_LEARNING / GOVERNANCE_LEARNING / GOTCHA
**Superficie:** Tooling / Code Atlas / Governance
**Contexto:** Se ejecutó el primer gate externo serio de Code Atlas contra repositorios ajenos a PRISMA: `pallets/click`, `vitejs/vite` y `BurntSushi/ripgrep`, siempre con perfil neutral/default y originales read-only.
**Resultado observado:** FAIL útil inicial → FIX gobernado → PASS externo limitado.
**Evidencia:** Authority Mesh de reparación `31866829102`; PR #275; merge `{MERGE}`; artifact focal `9242394010`; replay completo `31867491454` / `9242450935`; 140 tests Code Atlas PASS; CI PR 6/6; Authority Mesh de cierre `31867706125` / `9242519545`.
**Defectos de source demostrados:** Verify podía aceptar un worktree dirty oculto si el caller lo omitía del manifest; `.rs` se reconocía como Rust pero no recibía evidencia textual coherente; imports JS/TS con `..` podían perder dependencias directas; Rust no tenía relaciones de dependencia repository-provable; Architecture Layer Graph tenía cobertura externa débil.
**Corrección:** reconciliar Git real contra manifest antes de Verify; alinear source suffixes reconocidos con evidencia segura; normalizar rutas relativas JS/TS; resolver Rust sólo con relaciones acotadas demostrables (`mod`, `#[path]`, `crate/self/super`); reportar arquitectura/cobertura con provenance y sin convertir impacto en autorización.
**Harness / tooling que NO debe confundirse con fallo del producto:** el scan legacy de leakage encontró `NDC` dentro de `tailwindcss`; la matriz legacy leyó `changeImpactSize` desde el grafo DISCOVER en lugar del change model PREPARE; un workflow temporal usó un scope guard contra HEAD transitorio; el gateway Remote AutoMesh exige Base64 URL-safe sin padding.
**Comando de regresión confirmado:**

```bash
PYTHONPATH=tools/code-atlas/src python -m unittest discover -s tools/code-atlas/tests -p 'test_*.py' -v
```

**Rollback probado:** N/A sobre producto. El FIX se trabajó en rama gobernada y no se mergeó hasta 140 tests, replay externo y CI; los repos externos originales permanecieron read-only.
**Regla nueva:** Un verde externo no se promociona sólo porque el proceso terminó en cero. Separar `PRODUCT FAILURE` de `HARNESS FAILURE`, adjudicar manualmente métricas/leak scans sospechosos contra provenance física, y después de cualquier FIX repetir exactamente el mismo gate adversarial antes de ampliar claims.
**Límite:** Este aprendizaje prueba sólo el corpus externo y condiciones declaradas. No prueba universalidad absoluta, producción, enterprise, hosted multi-tenant ni cumplimiento legal/privacidad/IAM.
'''
write_text(MANUAL, manual)


# Cross-file fail-closed checks.
final_contract = json.loads(WOW_JSON.read_text(encoding="utf-8"))
final_ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
final_evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
final_cap = next(c for c in final_ledger["capabilities"] if c.get("id") == "code_atlas.change_intelligence.customer_wow_v1")
assert final_contract["certifiable"] is False
assert final_contract["productionCertified"] is False
assert final_contract["status"] == "UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED"
assert final_cap["status"] == "LOCAL_VERIFIED"
assert final_cap["doNotRebuild"] is True
assert any(a.get("artifact") == artifact_name for a in final_evidence["artifacts"])
assert "EXTERNAL_REPO_EVIDENCE_PENDING" not in WOW_MD.read_text(encoding="utf-8")
assert "The next evidence gate is execution against **unrelated external repositories**" not in README.read_text(encoding="utf-8")
print("PASS_CAEXT_EVIDENCE_CLOSURE_APPLIED")
