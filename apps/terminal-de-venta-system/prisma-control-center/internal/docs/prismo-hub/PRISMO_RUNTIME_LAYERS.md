# PRISMO Runtime Layers

This hub maps PRISMO files without relocating runtime source-of-truth files.

## Layer rule

- Runtime files stay where imports and launchers already expect them.
- `internal/prismo` is the trace hub, not a replacement runtime root.
- Codex must edit source-of-truth files, not scaffold copies.

## 01_learning_core_runtime

- `internal/py/prismo_learning/__init__.py`
- `internal/py/prismo_learning/action_contracts.py`
- `internal/py/prismo_learning/action_preview.py`
- `internal/py/prismo_learning/answer_pack_builder.py`
- `internal/py/prismo_learning/api.py`
- `internal/py/prismo_learning/approval_gate.py`
- `internal/py/prismo_learning/atomic_io.py`
- `internal/py/prismo_learning/authority_resolver.py`
- `internal/py/prismo_learning/authority_store.py`
- `internal/py/prismo_learning/canon_resolver.py`
- `internal/py/prismo_learning/clock.py`
- `internal/py/prismo_learning/compaction_engine.py`
- `internal/py/prismo_learning/compaction_policy.py`
- `internal/py/prismo_learning/constants.py`
- `internal/py/prismo_learning/context_enrichment.py`
- `internal/py/prismo_learning/context_resolver.py`
- `internal/py/prismo_learning/context_scoring.py`
- `internal/py/prismo_learning/contracts.py`
- `internal/py/prismo_learning/controlled_action_layer.py`
- `internal/py/prismo_learning/decision_trace.py`
- `internal/py/prismo_learning/diagnostics.py`
- `internal/py/prismo_learning/drawer_payloads.py`
- `internal/py/prismo_learning/endpoint_contracts.py`
- `internal/py/prismo_learning/episodic_memory.py`
- `internal/py/prismo_learning/evidence_classifier.py`
- `internal/py/prismo_learning/evidence_digest.py`
- `internal/py/prismo_learning/evidence_ingestor.py`
- `internal/py/prismo_learning/evidence_intake.py`
- `internal/py/prismo_learning/evidence_registry.py`
- `internal/py/prismo_learning/evidence_summary.py`
- `internal/py/prismo_learning/f3_engine.py`
- `internal/py/prismo_learning/f4_to_f9_engine.py`
- `internal/py/prismo_learning/feedback_loop.py`
- `internal/py/prismo_learning/feedback_schema.py`
- `internal/py/prismo_learning/feedback_stats.py`
- `internal/py/prismo_learning/file_fingerprints.py`
- `internal/py/prismo_learning/fixtures.py`
- `internal/py/prismo_learning/governance_bridge.py`
- `internal/py/prismo_learning/governance_report.py`
- `internal/py/prismo_learning/graph_builder.py`
- `internal/py/prismo_learning/graph_digest.py`
- `internal/py/prismo_learning/hashes.py`
- `internal/py/prismo_learning/intake_policy.py`
- `internal/py/prismo_learning/locks.py`
- `internal/py/prismo_learning/manifest_detector.py`
- `internal/py/prismo_learning/memory_compactor.py`
- `internal/py/prismo_learning/memory_store.py`
- `internal/py/prismo_learning/noise_budget.py`
- `internal/py/prismo_learning/outcome_recorder.py`
- `internal/py/prismo_learning/pass_fail_detector.py`
- `internal/py/prismo_learning/paths.py`
- `internal/py/prismo_learning/pattern_digest.py`
- `internal/py/prismo_learning/pattern_miner.py`
- `internal/py/prismo_learning/pattern_reporter.py`
- `internal/py/prismo_learning/policy_checks.py`
- `internal/py/prismo_learning/procedural_memory.py`
- `internal/py/prismo_learning/protocol_recipes.py`
- `internal/py/prismo_learning/protocol_router.py`
- `internal/py/prismo_learning/protocol_stats_writer.py`
- `internal/py/prismo_learning/public_redaction.py`
- `internal/py/prismo_learning/query_classifier.py`
- `internal/py/prismo_learning/query_context.py`
- `internal/py/prismo_learning/query_enricher.py`
- `internal/py/prismo_learning/recommendation_engine.py`
- `internal/py/prismo_learning/release_train_alignment.py`
- `internal/py/prismo_learning/render_plan.py`
- `internal/py/prismo_learning/report_json.py`
- `internal/py/prismo_learning/report_markdown.py`
- `internal/py/prismo_learning/reports.py`
- `internal/py/prismo_learning/retention_rules.py`
- `internal/py/prismo_learning/rollback_planner.py`
- `internal/py/prismo_learning/runtime_probe.py`
- `internal/py/prismo_learning/safe_response_composer.py`
- `internal/py/prismo_learning/safe_ui_governor.py`
- `internal/py/prismo_learning/safety.py`
- `internal/py/prismo_learning/sanitize.py`
- `internal/py/prismo_learning/scoring.py`
- `internal/py/prismo_learning/secret_scanner.py`
- `internal/py/prismo_learning/semantic_memory.py`
- `internal/py/prismo_learning/snapshot_manager.py`
- ... plus 9 more.

## 02_ai_bridge_runtime

- `internal/py/prismo_ai_bridge.py`
- `internal/py/prismo_context.py`
- `internal/py/prismo_demo_provider.py`
- `internal/py/prismo_gemini_provider.py`

## 03_contracts_and_config

- `internal/config/prismo_ai_config.json`
- `internal/config/prismo_prompt_contract.json`
- `internal/config/prismo_render_blocks.schema.json`
- `internal/config/prismo_response_contract.schema.json`
- `internal/py/prismo_render_contracts.py`
- `internal/py/prismo_safety.py`

## 04_theater_web_runtime

- `internal/web/prisma_cc_v56_prismo_safe_retune.css`
- `internal/web/prisma_cc_v56_prismo_safe_retune.js`
- `internal/web/prisma_cc_v57_panel_text_clarity.css`
- `internal/web/prisma_cc_v59_prismo_selector_safe_frost_evidence.css`
- `internal/web/prisma_cc_v59_prismo_selector_safe_frost_evidence.js`
- `internal/web/prisma_cc_v60_prismo_topbar_fix.css`
- `internal/web/prisma_cc_v60_prismo_topbar_fix.js`
- `internal/web/prisma_cc_v61_prismo_compact_premium.css`
- `internal/web/prisma_cc_v62_remove_ghost_rects.css`
- `internal/web/prisma_cc_v63_all_surfaces_glass_repair.css`
- `internal/web/prisma_cc_v63_all_surfaces_glass_repair.js`
- `internal/web/prisma_cc_v64_undo_v63_prismo_glass.css`
- `internal/web/prisma_cc_v65_clean_visual_stack.css`
- `internal/web/prisma_cc_v65_clean_visual_stack.js`
- `internal/web/prisma_cc_v66_prismo_container_only.css`
- `internal/web/prisma_cc_v67_prismo_edge_logo_fix.css`
- `internal/web/prisma_cc_v68_floating_status_pills.css`
- `internal/web/prisma_cc_v69_upload_panel_only.css`
- `internal/web/prisma_cc_v70_status_backplate_only.css`
- `internal/web/prisma_cc_v71_float_response_status_only.css`
- `internal/web/prisma_cc_v72_chip_backplate_only.css`
- `internal/web/prisma_cc_v73_prompt_text_glow.css`
- `internal/web/prisma_cc_v75_prompt_glow_only.css`
- `internal/web/prisma_cc_v76_all_surfaces_neon_contrast.css`
- `internal/web/prisma_cc_v76_all_surfaces_neon_contrast.js`
- `internal/web/prisma_cc_v77_origin_state_lock.css`
- `internal/web/prisma_cc_v77_origin_state_lock.js`
- `internal/web/prismo_ai_theater.css`
- `internal/web/prismo_ai_theater.js`
- `internal/web/prismo_console.css`
- `internal/web/prismo_console.js`
- `internal/web/prismo_demo_payloads.js`
- `internal/web/prismo_renderers.js`

## 05_documentation

- `internal/docs/prismo/README.md`
