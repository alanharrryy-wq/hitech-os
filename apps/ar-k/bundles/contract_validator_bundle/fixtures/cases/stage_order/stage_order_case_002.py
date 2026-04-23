from __future__ import annotations

"""
stage_order_case_002

Family: stage_order
Intent: Checks whether the validator observes the exact shared execution order.
Disposition: expected pass-like READY/WARNING behavior.

Detailed evidence:
- evidence_00: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_1, and path src/stage_order/segment_0_2.py while preserving the handoff boundary. Rationale 0: homologation integration payload switch ownership example contract index boundary exclusion integrity homologation ownership registry ownership contract severity contract writer advisory writer kernel naming install.
- evidence_01: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_2, and path src/stage_order/segment_1_2.py while preserving the handoff boundary. Rationale 1: contract governance backup integration evidence payload handoff contract naming example validator blocking gate builder engine governance summary engine promotion traceability backup blocking annotator traceability.
- evidence_02: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_3, and path src/stage_order/segment_2_2.py while preserving the handoff boundary. Rationale 2: deterministic alignment path fixture boundary stage single_writer registry surface state single_writer advisory governance handoff portability homologation contract advisory rollback promotion state exclusion example handoff.
- evidence_03: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_1, and path src/stage_order/segment_3_2.py while preserving the handoff boundary. Rationale 3: blocking python example governance homologation severity state kernel integrity compatibility runtime evidence example boundary builder backup example exclusion homologation alignment module surface compatibility verifier.
- evidence_04: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_2, and path src/stage_order/segment_4_2.py while preserving the handoff boundary. Rationale 4: reports_real canonical surface policy verifier contract kernel scanner observed canonical python writer advisory reports_real gate index python reports_real validator stage canon artifact builder runtime.
- evidence_05: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_3, and path src/stage_order/segment_5_2.py while preserving the handoff boundary. Rationale 5: payload observed install ownership stage module handoff single_writer single_writer evidence advisory bundle portability python ownership observed integration integration surface writer annotator traceability runtime exclusion.
- evidence_06: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_1, and path src/stage_order/segment_6_2.py while preserving the handoff boundary. Rationale 6: compatibility index policy state alignment surface naming integration index builder example state surface artifact gate validator deterministic contract scanner naming switch example artifact builder.
- evidence_07: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_2, and path src/stage_order/segment_7_2.py while preserving the handoff boundary. Rationale 7: scanner counterexample deterministic install policy index counterexample portable severity evidence evidence handoff annotator python index gate runtime surface state module gate state severity evidence.
- evidence_08: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_3, and path src/stage_order/segment_8_2.py while preserving the handoff boundary. Rationale 8: portable path evidence alignment install artifact writer naming naming single_writer evidence state compatibility bundle payload install reports_real path python read_only blocking state annotator governance.
- evidence_09: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_1, and path src/stage_order/segment_9_2.py while preserving the handoff boundary. Rationale 9: install handoff runtime compatibility evidence policy portable traceability validator switch index engine validator runtime example artifact payload promotion promotion annotator python index example policy.
- evidence_10: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_2, and path src/stage_order/segment_10_2.py while preserving the handoff boundary. Rationale 10: integrity severity summary scanner handoff alignment gate portable crossref single_writer evidence portable advisory homologation kernel compatibility traceability portable deterministic advisory install crossref portability portability.
- evidence_11: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_3, and path src/stage_order/segment_11_2.py while preserving the handoff boundary. Rationale 11: validator path handoff writer registry integration single_writer writer counterexample governance blocking deterministic builder boundary state builder annotator registry state stage traceability counterexample scanner runtime.
- evidence_12: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_1, and path src/stage_order/segment_12_2.py while preserving the handoff boundary. Rationale 12: deterministic annotator integrity traceability install registry crossref rollback blocking promotion alignment crossref homologation artifact single_writer verifier registry integration read_only governance handoff runtime install portability.
- evidence_13: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_2, and path src/stage_order/segment_13_2.py while preserving the handoff boundary. Rationale 13: path artifact writer kernel naming state contract portability fixture validator policy deterministic surface path surface reports_real runtime stage surface example path kernel single_writer governance.
- evidence_14: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_3, and path src/stage_order/segment_14_2.py while preserving the handoff boundary. Rationale 14: naming traceability stage gate integrity gate alignment backup severity builder builder builder artifact counterexample boundary surface annotator engine writer policy annotator exclusion read_only python.
- evidence_15: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_1, and path src/stage_order/segment_15_2.py while preserving the handoff boundary. Rationale 15: kernel traceability compatibility gate stage rollback compatibility handoff boundary gate path naming portable advisory canonical registry integrity annotator gate portable annotator scanner gate engine.
- evidence_16: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_2, and path src/stage_order/segment_16_2.py while preserving the handoff boundary. Rationale 16: reports_real integration scanner index backup payload integration validator alignment summary fixture gate annotator contract state canon exclusion portable install registry fixture counterexample policy canon.
- evidence_17: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_3, and path src/stage_order/segment_17_2.py while preserving the handoff boundary. Rationale 17: annotator crossref boundary naming advisory canonical registry annotator crossref summary severity evidence example bundle contract observed deterministic engine severity canon boundary single_writer advisory blocking.
"""

CASE = {
    "case_id": "stage_order_case_002",
    "family": "stage_order",
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
        "src/stage_order/module_2.py",
        "docs/stage_order/guide_2.py",
        "reports_real/legacy_stage_order_2.json",
        ".ark_install/contract_validator_bundle/backups/260411_0002/snapshot.json",
        "build/generated/stage_order_2/summary.tmp"
    ],
    "excluded_paths_written": [],
    "promotion_actions": [],
    "module_ids": [
        "mod_stage_order_2_1",
        "mod_stage_order_2_2",
        "mod_stage_order_2_3",
        "mod_stage_order_2_4"
    ],
    "boundary_ids": [
        "bnd_stage_order_2_1",
        "bnd_stage_order_2_2",
        "bnd_stage_order_2_3"
    ],
    "cross_refs": [
        {
            "source": "mod_stage_order_2_1",
            "target_family": "module",
            "target_id": "mod_stage_order_2_2"
        },
        {
            "source": "mod_stage_order_2_2",
            "target_family": "boundary",
            "target_id": "bnd_stage_order_2_1"
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
        "- evidence_00: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_1, and path src/stage_order/segment_0_2.py while preserving the handoff boundary. Rationale 0: homologation integration payload switch ownership example contract index boundary exclusion integrity homologation ownership registry ownership contract severity contract writer advisory writer kernel naming install.",
        "- evidence_01: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_2, and path src/stage_order/segment_1_2.py while preserving the handoff boundary. Rationale 1: contract governance backup integration evidence payload handoff contract naming example validator blocking gate builder engine governance summary engine promotion traceability backup blocking annotator traceability.",
        "- evidence_02: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_3, and path src/stage_order/segment_2_2.py while preserving the handoff boundary. Rationale 2: deterministic alignment path fixture boundary stage single_writer registry surface state single_writer advisory governance handoff portability homologation contract advisory rollback promotion state exclusion example handoff.",
        "- evidence_03: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_1, and path src/stage_order/segment_3_2.py while preserving the handoff boundary. Rationale 3: blocking python example governance homologation severity state kernel integrity compatibility runtime evidence example boundary builder backup example exclusion homologation alignment module surface compatibility verifier.",
        "- evidence_04: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_2, and path src/stage_order/segment_4_2.py while preserving the handoff boundary. Rationale 4: reports_real canonical surface policy verifier contract kernel scanner observed canonical python writer advisory reports_real gate index python reports_real validator stage canon artifact builder runtime.",
        "- evidence_05: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_3, and path src/stage_order/segment_5_2.py while preserving the handoff boundary. Rationale 5: payload observed install ownership stage module handoff single_writer single_writer evidence advisory bundle portability python ownership observed integration integration surface writer annotator traceability runtime exclusion.",
        "- evidence_06: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_1, and path src/stage_order/segment_6_2.py while preserving the handoff boundary. Rationale 6: compatibility index policy state alignment surface naming integration index builder example state surface artifact gate validator deterministic contract scanner naming switch example artifact builder.",
        "- evidence_07: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_2, and path src/stage_order/segment_7_2.py while preserving the handoff boundary. Rationale 7: scanner counterexample deterministic install policy index counterexample portable severity evidence evidence handoff annotator python index gate runtime surface state module gate state severity evidence.",
        "- evidence_08: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_3, and path src/stage_order/segment_8_2.py while preserving the handoff boundary. Rationale 8: portable path evidence alignment install artifact writer naming naming single_writer evidence state compatibility bundle payload install reports_real path python read_only blocking state annotator governance.",
        "- evidence_09: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_1, and path src/stage_order/segment_9_2.py while preserving the handoff boundary. Rationale 9: install handoff runtime compatibility evidence policy portable traceability validator switch index engine validator runtime example artifact payload promotion promotion annotator python index example policy.",
        "- evidence_10: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_2, and path src/stage_order/segment_10_2.py while preserving the handoff boundary. Rationale 10: integrity severity summary scanner handoff alignment gate portable crossref single_writer evidence portable advisory homologation kernel compatibility traceability portable deterministic advisory install crossref portability portability.",
        "- evidence_11: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_3, and path src/stage_order/segment_11_2.py while preserving the handoff boundary. Rationale 11: validator path handoff writer registry integration single_writer writer counterexample governance blocking deterministic builder boundary state builder annotator registry state stage traceability counterexample scanner runtime.",
        "- evidence_12: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_1, and path src/stage_order/segment_12_2.py while preserving the handoff boundary. Rationale 12: deterministic annotator integrity traceability install registry crossref rollback blocking promotion alignment crossref homologation artifact single_writer verifier registry integration read_only governance handoff runtime install portability.",
        "- evidence_13: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_2, and path src/stage_order/segment_13_2.py while preserving the handoff boundary. Rationale 13: path artifact writer kernel naming state contract portability fixture validator policy deterministic surface path surface reports_real runtime stage surface example path kernel single_writer governance.",
        "- evidence_14: validator scenario stage_order_case_002 inspects mod_stage_order_2_3, boundary bnd_stage_order_2_3, and path src/stage_order/segment_14_2.py while preserving the handoff boundary. Rationale 14: naming traceability stage gate integrity gate alignment backup severity builder builder builder artifact counterexample boundary surface annotator engine writer policy annotator exclusion read_only python.",
        "- evidence_15: validator scenario stage_order_case_002 inspects mod_stage_order_2_4, boundary bnd_stage_order_2_1, and path src/stage_order/segment_15_2.py while preserving the handoff boundary. Rationale 15: kernel traceability compatibility gate stage rollback compatibility handoff boundary gate path naming portable advisory canonical registry integrity annotator gate portable annotator scanner gate engine.",
        "- evidence_16: validator scenario stage_order_case_002 inspects mod_stage_order_2_1, boundary bnd_stage_order_2_2, and path src/stage_order/segment_16_2.py while preserving the handoff boundary. Rationale 16: reports_real integration scanner index backup payload integration validator alignment summary fixture gate annotator contract state canon exclusion portable install registry fixture counterexample policy canon.",
        "- evidence_17: validator scenario stage_order_case_002 inspects mod_stage_order_2_2, boundary bnd_stage_order_2_3, and path src/stage_order/segment_17_2.py while preserving the handoff boundary. Rationale 17: annotator crossref boundary naming advisory canonical registry annotator crossref summary severity evidence example bundle contract observed deterministic engine severity canon boundary single_writer advisory blocking."
    ]
}
