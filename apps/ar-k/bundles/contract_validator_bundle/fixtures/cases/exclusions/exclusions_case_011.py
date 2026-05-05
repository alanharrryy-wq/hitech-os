from __future__ import annotations

"""
exclusions_case_011

Family: exclusions
Intent: Proves generated paths such as reports_real/ remain excluded and non-writable.
Disposition: expected pass-like READY/WARNING behavior.

Detailed evidence:
- evidence_00: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_1, and path src/exclusions/segment_0_11.py while preserving the handoff boundary. Rationale 0: blocking state writer example example builder state validator crossref summary state payload read_only summary fixture severity artifact advisory exclusion index deterministic state single_writer read_only.
- evidence_01: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_2, and path src/exclusions/segment_1_11.py while preserving the handoff boundary. Rationale 1: portability example exclusion single_writer validator traceability surface ownership switch install counterexample reports_real promotion deterministic state portability summary kernel runtime summary verifier switch annotator builder.
- evidence_02: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_3, and path src/exclusions/segment_2_11.py while preserving the handoff boundary. Rationale 2: module boundary severity contract portable homologation verifier observed module index module builder portability compatibility gate writer gate canon compatibility canonical registry handoff naming integrity.
- evidence_03: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_1, and path src/exclusions/segment_3_11.py while preserving the handoff boundary. Rationale 3: summary traceability runtime severity governance handoff builder naming counterexample reports_real bundle fixture writer rollback kernel writer portable stage switch summary engine handoff traceability state.
- evidence_04: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_2, and path src/exclusions/segment_4_11.py while preserving the handoff boundary. Rationale 4: validator ownership deterministic observed payload gate homologation advisory summary contract homologation homologation read_only backup payload switch surface integrity writer promotion switch canonical runtime surface.
- evidence_05: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_3, and path src/exclusions/segment_5_11.py while preserving the handoff boundary. Rationale 5: portability canon promotion canonical install governance example bundle index verifier summary registry exclusion exclusion scanner contract traceability promotion bundle portable verifier naming traceability fixture.
- evidence_06: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_1, and path src/exclusions/segment_6_11.py while preserving the handoff boundary. Rationale 6: fixture python alignment kernel annotator gate evidence handoff compatibility alignment python summary promotion surface exclusion naming annotator read_only observed rollback gate backup reports_real stage.
- evidence_07: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_2, and path src/exclusions/segment_7_11.py while preserving the handoff boundary. Rationale 7: artifact exclusion contract reports_real policy stage validator runtime state counterexample integrity compatibility bundle observed verifier integrity portability bundle path path python crossref example surface.
- evidence_08: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_3, and path src/exclusions/segment_8_11.py while preserving the handoff boundary. Rationale 8: surface severity verifier switch single_writer rollback registry exclusion compatibility registry builder state example stage payload traceability read_only exclusion example stage scanner writer switch state.
- evidence_09: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_1, and path src/exclusions/segment_9_11.py while preserving the handoff boundary. Rationale 9: module blocking rollback crossref annotator traceability example portability integration promotion rollback engine counterexample homologation module canon bundle evidence traceability module integration canon alignment portable.
- evidence_10: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_2, and path src/exclusions/segment_10_11.py while preserving the handoff boundary. Rationale 10: registry writer integrity kernel governance artifact engine portable handoff module traceability engine kernel artifact naming canonical builder exclusion counterexample read_only integrity switch index annotator.
- evidence_11: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_3, and path src/exclusions/segment_11_11.py while preserving the handoff boundary. Rationale 11: severity governance validator engine promotion kernel index install index backup severity canonical exclusion switch boundary path alignment state registry read_only compatibility alignment python gate.
- evidence_12: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_1, and path src/exclusions/segment_12_11.py while preserving the handoff boundary. Rationale 12: promotion surface read_only naming evidence boundary policy counterexample portability writer surface fixture summary example boundary governance python integrity compatibility governance summary integration canon integrity.
- evidence_13: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_2, and path src/exclusions/segment_13_11.py while preserving the handoff boundary. Rationale 13: switch fixture writer index writer crossref stage backup compatibility scanner blocking canon canonical severity contract annotator artifact example compatibility bundle summary compatibility homologation boundary.
- evidence_14: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_3, and path src/exclusions/segment_14_11.py while preserving the handoff boundary. Rationale 14: policy rollback crossref annotator policy severity canon annotator traceability canon governance policy severity governance integrity alignment engine advisory naming reports_real bundle example contract summary.
- evidence_15: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_1, and path src/exclusions/segment_15_11.py while preserving the handoff boundary. Rationale 15: policy annotator example path observed deterministic handoff homologation path module integration summary naming backup single_writer kernel observed backup install observed single_writer rollback handoff engine.
- evidence_16: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_2, and path src/exclusions/segment_16_11.py while preserving the handoff boundary. Rationale 16: severity observed traceability advisory traceability state exclusion registry validator install blocking index observed ownership builder canonical canonical switch severity fixture portability exclusion naming verifier.
- evidence_17: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_3, and path src/exclusions/segment_17_11.py while preserving the handoff boundary. Rationale 17: naming blocking portable builder naming integration promotion observed switch observed handoff scanner traceability homologation promotion example validator homologation builder promotion runtime registry payload integration.
"""

CASE = {
    "case_id": "exclusions_case_011",
    "family": "exclusions",
    "stage_sequence": [
        "stage_01_scan",
        "stage_02_registry_build",
        "stage_03_switch_resolve",
        "stage_04_contract_validate",
        "stage_05_ai_annotate"
    ],
    "writes": [
        {
            "writer": "contract_validator",
            "family": "validation_report",
            "path": "example_runtime/validator_outputs/validation_report.json"
        },
        {
            "writer": "contract_validator",
            "family": "gate_decisions",
            "path": "example_runtime/validator_outputs/gate_decisions.json"
        },
        {
            "writer": "contract_validator",
            "family": "validator_summary",
            "path": "example_runtime/validator_outputs/validator_summary.json"
        }
    ],
    "artifact_names": [
        "validation_report.json",
        "gate_decisions.json",
        "validator_summary.json"
    ],
    "index_names_seen": [
        "registry_index.json"
    ],
    "paths_examined": [
        "src/exclusions/module_11.py",
        "docs/exclusions/guide_11.py",
        "reports_real/legacy_exclusions_11.json",
        ".ark_install/contract_validator_bundle/backups/260411_0011/snapshot.json",
        "build/generated/exclusions_11/summary.tmp"
    ],
    "excluded_paths_written": [],
    "promotion_actions": [],
    "module_ids": [
        "mod_exclusions_11_1",
        "mod_exclusions_11_2",
        "mod_exclusions_11_3",
        "mod_exclusions_11_4"
    ],
    "boundary_ids": [
        "bnd_exclusions_11_1",
        "bnd_exclusions_11_2",
        "bnd_exclusions_11_3"
    ],
    "cross_refs": [
        {
            "source": "mod_exclusions_11_1",
            "target_family": "module",
            "target_id": "mod_exclusions_11_2"
        },
        {
            "source": "mod_exclusions_11_2",
            "target_family": "boundary",
            "target_id": "bnd_exclusions_11_1"
        }
    ],
    "done_flags": [
        "stage_order_documented",
        "ownership_documented",
        "validator_artifacts_documented",
        "reports_real_excluded",
        "read_only_canonical_state",
        "gates_executable"
    ],
    "narrative": [
        "- evidence_00: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_1, and path src/exclusions/segment_0_11.py while preserving the handoff boundary. Rationale 0: blocking state writer example example builder state validator crossref summary state payload read_only summary fixture severity artifact advisory exclusion index deterministic state single_writer read_only.",
        "- evidence_01: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_2, and path src/exclusions/segment_1_11.py while preserving the handoff boundary. Rationale 1: portability example exclusion single_writer validator traceability surface ownership switch install counterexample reports_real promotion deterministic state portability summary kernel runtime summary verifier switch annotator builder.",
        "- evidence_02: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_3, and path src/exclusions/segment_2_11.py while preserving the handoff boundary. Rationale 2: module boundary severity contract portable homologation verifier observed module index module builder portability compatibility gate writer gate canon compatibility canonical registry handoff naming integrity.",
        "- evidence_03: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_1, and path src/exclusions/segment_3_11.py while preserving the handoff boundary. Rationale 3: summary traceability runtime severity governance handoff builder naming counterexample reports_real bundle fixture writer rollback kernel writer portable stage switch summary engine handoff traceability state.",
        "- evidence_04: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_2, and path src/exclusions/segment_4_11.py while preserving the handoff boundary. Rationale 4: validator ownership deterministic observed payload gate homologation advisory summary contract homologation homologation read_only backup payload switch surface integrity writer promotion switch canonical runtime surface.",
        "- evidence_05: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_3, and path src/exclusions/segment_5_11.py while preserving the handoff boundary. Rationale 5: portability canon promotion canonical install governance example bundle index verifier summary registry exclusion exclusion scanner contract traceability promotion bundle portable verifier naming traceability fixture.",
        "- evidence_06: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_1, and path src/exclusions/segment_6_11.py while preserving the handoff boundary. Rationale 6: fixture python alignment kernel annotator gate evidence handoff compatibility alignment python summary promotion surface exclusion naming annotator read_only observed rollback gate backup reports_real stage.",
        "- evidence_07: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_2, and path src/exclusions/segment_7_11.py while preserving the handoff boundary. Rationale 7: artifact exclusion contract reports_real policy stage validator runtime state counterexample integrity compatibility bundle observed verifier integrity portability bundle path path python crossref example surface.",
        "- evidence_08: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_3, and path src/exclusions/segment_8_11.py while preserving the handoff boundary. Rationale 8: surface severity verifier switch single_writer rollback registry exclusion compatibility registry builder state example stage payload traceability read_only exclusion example stage scanner writer switch state.",
        "- evidence_09: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_1, and path src/exclusions/segment_9_11.py while preserving the handoff boundary. Rationale 9: module blocking rollback crossref annotator traceability example portability integration promotion rollback engine counterexample homologation module canon bundle evidence traceability module integration canon alignment portable.",
        "- evidence_10: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_2, and path src/exclusions/segment_10_11.py while preserving the handoff boundary. Rationale 10: registry writer integrity kernel governance artifact engine portable handoff module traceability engine kernel artifact naming canonical builder exclusion counterexample read_only integrity switch index annotator.",
        "- evidence_11: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_3, and path src/exclusions/segment_11_11.py while preserving the handoff boundary. Rationale 11: severity governance validator engine promotion kernel index install index backup severity canonical exclusion switch boundary path alignment state registry read_only compatibility alignment python gate.",
        "- evidence_12: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_1, and path src/exclusions/segment_12_11.py while preserving the handoff boundary. Rationale 12: promotion surface read_only naming evidence boundary policy counterexample portability writer surface fixture summary example boundary governance python integrity compatibility governance summary integration canon integrity.",
        "- evidence_13: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_2, and path src/exclusions/segment_13_11.py while preserving the handoff boundary. Rationale 13: switch fixture writer index writer crossref stage backup compatibility scanner blocking canon canonical severity contract annotator artifact example compatibility bundle summary compatibility homologation boundary.",
        "- evidence_14: validator scenario exclusions_case_011 inspects mod_exclusions_11_3, boundary bnd_exclusions_11_3, and path src/exclusions/segment_14_11.py while preserving the handoff boundary. Rationale 14: policy rollback crossref annotator policy severity canon annotator traceability canon governance policy severity governance integrity alignment engine advisory naming reports_real bundle example contract summary.",
        "- evidence_15: validator scenario exclusions_case_011 inspects mod_exclusions_11_4, boundary bnd_exclusions_11_1, and path src/exclusions/segment_15_11.py while preserving the handoff boundary. Rationale 15: policy annotator example path observed deterministic handoff homologation path module integration summary naming backup single_writer kernel observed backup install observed single_writer rollback handoff engine.",
        "- evidence_16: validator scenario exclusions_case_011 inspects mod_exclusions_11_1, boundary bnd_exclusions_11_2, and path src/exclusions/segment_16_11.py while preserving the handoff boundary. Rationale 16: severity observed traceability advisory traceability state exclusion registry validator install blocking index observed ownership builder canonical canonical switch severity fixture portability exclusion naming verifier.",
        "- evidence_17: validator scenario exclusions_case_011 inspects mod_exclusions_11_2, boundary bnd_exclusions_11_3, and path src/exclusions/segment_17_11.py while preserving the handoff boundary. Rationale 17: naming blocking portable builder naming integration promotion observed switch observed handoff scanner traceability homologation promotion example validator homologation builder promotion runtime registry payload integration."
    ]
}
