# UI Dictionary

- version: `1.0.0`
- generated_by: `tools/ui_map deterministic`
- routes: `11`
- components: `982`
- states: `10`
- styles: `10`
- assets: `2`
- hotspots: `11`

## Routes
| route_id | path | entry_file | screen_component_id |
| --- | --- | --- | --- |
| rte_46efb84e93 | /pitch | apps/keystone/app/pitch/page.tsx | cmp_23eef8d3c0 |
| rte_588c6fe0cc | /pitch/06-shipments-receiving | apps/keystone/app/pitch/06-shipments-receiving/page.tsx | cmp_bf1d0f2e29 |
| rte_64b18eb3cd | /dev/scene-studio | apps/keystone/app/dev/scene-studio/page.tsx |  |
| rte_6c122ba817 | /pitch/04-valuation | apps/keystone/app/pitch/04-valuation/page.tsx | cmp_1b31a3432a |
| rte_8a5edab282 | / | apps/keystone/app/page.tsx |  |
| rte_9225911e8f | /pitch/01-double-engine | apps/keystone/app/pitch/01-double-engine/page.tsx | cmp_f14bfffde5 |
| rte_bf321ec7dd | /dev/style-lab | apps/keystone/app/dev/style-lab/page.tsx |  |
| rte_d2b3868d72 | /pitch/02-industrial-flow | apps/keystone/app/pitch/02-industrial-flow/page.tsx | cmp_88852e131f |
| rte_e78399e664 | /pitch/05-inventory-foundation | apps/keystone/app/pitch/05-inventory-foundation/page.tsx | cmp_114f4ca07f |
| rte_fc9a4ff828 | /dev/kpi-supermarket | apps/keystone/app/dev/kpi-supermarket/page.tsx |  |
| rte_fe70914ec1 | /pitch/03-hitech-os | apps/keystone/app/pitch/03-hitech-os/page.tsx | cmp_4daf0963df |

## Components (first 120)
| component_id | export_name | kind | file_path |
| --- | --- | --- | --- |
| cmp_003267a333 | PitchHero | block | apps/keystone/components/pitch/shell/pitch-hero.tsx |
| cmp_005058f357 | SCENE_MOTION_VALUES | block | apps/keystone/lib/scene-studio/scene-constants.ts |
| cmp_00558dfee2 | TableBody | block | packages/ui-kit/src/components/data/Table.tsx |
| cmp_00a85cbf81 | FRAME_PRESETS | block | packages/ui-kit/src/luxury/frames/frames.ts |
| cmp_015c59ef59 | RiskAndNextGatePanel | control | apps/keystone/components/pitch/run2/RiskAndNextGatePanel.tsx |
| cmp_0174434e39 | isBuiltinPreset | block | apps/keystone/app/dev/scene-studio/window-manager/presets.ts |
| cmp_019ff3773b | HERO_QUALITY_CATALOG_COUNT | block | packages/ui-kit/src/motion/catalogs/heroQualityCatalog.ts |
| cmp_01b648fb75 | ControlRoom | control | apps/keystone/app/dev/scene-studio/ControlRoom.tsx |
| cmp_01d4823875 | PitchIconHub | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_01fe8c8ed6 | frameCatalogAsMap | block | packages/ui-kit/src/luxury/frames/signatures/graphitePrismSignatureCatalog.ts |
| cmp_022d09ab2e | readSystemReducedMotion | block | packages/ui-kit/src/motion/reducedMotion.ts |
| cmp_0251f5af5d | LINE_CHART_SAMPLE | dataviz | packages/ui-kit/src/kpi/charts/line-area.tsx |
| cmp_0260d3ce32 | PitchIconPlay | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_02ed842dd9 | activityQueryKey | block | apps/keystone/lib/queries/activity.ts |
| cmp_0351c3ca7b | NeonButton | block | apps/keystone/components/pitch/run1/primitives.tsx |
| cmp_03dd01c487 | COMPACT_BARS_SAMPLE | dataviz | packages/ui-kit/src/kpi/charts/bar-matrix.tsx |
| cmp_03e84dbf35 | useActivityQuery | block | apps/keystone/lib/queries/activity.ts |
| cmp_044ceddc68 | INCOTERMS | block | apps/keystone/components/pitch/run1/types.ts |
| cmp_048265afb6 | PitchIconRisk | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_04a0c7e82f | waitForDeterministicReady | dataviz | apps/keystone/visual-tests/helpers/deterministic.ts |
| cmp_04c93c0cd3 | listBulkCatalogByMaturity | block | apps/keystone/app/dev/_luxury/registry/kpiCatalogBulk.ts |
| cmp_04f54bd3f3 | captureScene | dataviz | apps/keystone/visual-tests/helpers/scene-capture.ts |
| cmp_04fbad1a55 | evaluateGovernanceBudget | block | packages/ui-kit/src/luxury/governancePolicy.ts |
| cmp_051d307492 | PitchIconSatellite | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_051f812073 | default | layout | apps/keystone/app/dev/layout.tsx |
| cmp_05a31fb3e6 | saveLastPreset | block | apps/keystone/app/dev/scene-studio/window-manager/storage.ts |
| cmp_0691342735 | PitchIconCloud | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0695b05495 | PitchIconFire | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_06987e5a47 | Stage | layout | packages/ui-kit/src/components/layout/Stage.tsx |
| cmp_06cabd4ed7 | getSupplierLifecycleTone | state | apps/keystone/components/pitch/run1/store.ts |
| cmp_06ea624681 | runsQueryKey | block | apps/keystone/lib/queries/runs.ts |
| cmp_06fa5a7ff5 | dynamic | route | apps/keystone/app/pitch/05-inventory-foundation/page.tsx |
| cmp_075347cd7a | SCENES_MANIFEST_PATH | dataviz | apps/keystone/visual-tests/helpers/paths.ts |
| cmp_075cef23b4 | loadActiveLayout | block | apps/keystone/app/dev/scene-studio/window-manager/storage.ts |
| cmp_0760ab5e76 | DialogDescription | block | packages/ui-kit/src/components/overlays/Dialog.tsx |
| cmp_0771cf758d | createCatalogSnapshot | block | apps/keystone/app/dev/_luxury/tools/catalogSnapshot.ts |
| cmp_077b3ee2ad | resolveBrandModeEnabled | brand | packages/ui-kit/src/brand/brand-presence.config.ts |
| cmp_07d05da9ff | pressedInset | block | packages/ui-kit/src/motion/primitives.ts |
| cmp_07e0dc2880 | PitchIconStop | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0805226cf6 | PitchRouteCard | block | apps/keystone/components/pitch/route-index/pitch-route-card.tsx |
| cmp_0890609e12 | PitchIconBackward | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_08b67ff1e9 | createPixelDiff | dataviz | apps/keystone/visual-tests/helpers/diff.ts |
| cmp_0948794dd2 | PitchIconMinus | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_09aa2a435a | governanceWarnings | block | packages/ui-kit/src/luxury/governancePolicy.ts |
| cmp_09fce7bb33 | PitchIconNode | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0ab6307b9d | PitchIconVault | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0acb82cd64 | PitchIconCpu | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0b2ee9c333 | LIQUID_GLASS_SIGNATURE_CATALOG_COUNT | block | packages/ui-kit/src/luxury/frames/signatures/liquidGlassSignatureCatalog.ts |
| cmp_0b3b4055d8 | PitchShellBrandLayer | brand | apps/keystone/components/pitch/shell/pitch-shell-brand-layer.tsx |
| cmp_0b44c77175 | HERO_QUALITY_CATALOG | block | packages/ui-kit/src/motion/catalogs/heroQualityCatalog.ts |
| cmp_0b80292dff | getCustomsStatusTone | state | apps/keystone/components/pitch/run2/store.ts |
| cmp_0bade2bc81 | GET | block | apps/keystone/app/api/runs/route.ts |
| cmp_0c108c8235 | frameCatalogAsMap | block | packages/ui-kit/src/luxury/frames/signatures/liquidGlassSignatureCatalog.ts |
| cmp_0cbb6ee8b9 | KpiWidgetFrame | block | packages/ui-kit/src/kpi/frame/KpiWidgetFrame.tsx |
| cmp_0cea8bfba1 | GlassHeader | layout | packages/ui-kit/src/components/premium/layout/GlassHeader.tsx |
| cmp_0cff2c82da | PitchIconChip | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0d339b71f7 | PitchIconLeaf | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0d43aff805 | ReceivingControlPanel | control | apps/keystone/components/pitch/run2/ReceivingControlPanel.tsx |
| cmp_0dc055c5a2 | PitchIconFlow | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0dc8c6d74e | FRAME_SIGNATURE_CATALOG_COUNTS | block | packages/ui-kit/src/luxury/frames/frames.ts |
| cmp_0df0981f69 | AreaChart | dataviz | packages/ui-kit/src/kpi/charts/line-area.tsx |
| cmp_0e18d237a4 | createDefaultSceneLibrary | block | apps/keystone/lib/scene-studio/default-scenes.ts |
| cmp_0ef39ee252 | PRESETS_STORAGE_KEY | block | apps/keystone/app/dev/scene-studio/window-manager/storage.ts |
| cmp_0ef45dc6b4 | sceneQueryObjectToSearchParams | block | apps/keystone/lib/scene-studio/scene-query.ts |
| cmp_0f00607a49 | PitchVisualOverlayPanel | dataviz | apps/keystone/components/dev-console/panels/PitchVisualOverlayPanel.tsx |
| cmp_0f1bc4f36f | SceneStudioEditor | block | apps/keystone/components/scene-studio/scene-studio-editor.tsx |
| cmp_0f82c02092 | goldNoirTerminalTokens | block | packages/ui-kit/src/luxury/tokens/goldNoirTerminal.ts |
| cmp_10391d9c35 | ControlRoomToolbar | control | apps/keystone/app/dev/scene-studio/ControlRoomToolbar.tsx |
| cmp_10405d1738 | SCENE_SCHEMA_V1 | block | apps/keystone/lib/scene-studio/scene-schema.ts |
| cmp_105875c51d | PitchIconForward | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_107a4b287e | VIEWPORT_PRESETS | dataviz | apps/keystone/visual-tests/helpers/deterministic.ts |
| cmp_109f9bd9d9 | normalizeSceneId | block | apps/keystone/lib/scene-studio/scene-id.ts |
| cmp_113609dbcd | HITECH_BRAND_COLORS | brand | packages/ui-kit/src/brand/hitech-theme.ts |
| cmp_114f4ca07f | InventoryFoundationControlRoom | control | apps/keystone/components/pitch/run1/InventoryFoundationControlRoom.tsx |
| cmp_1199d17a95 | validateGauge | block | packages/ui-kit/src/data-spine/schema/guards.ts |
| cmp_11cea10dfe | ConsolePerfPanel | control | apps/keystone/components/dev-console/panels/ConsolePerfPanel.tsx |
| cmp_11d5be1368 | VISUAL_BOUNDS | block | apps/keystone/app/dev/_luxury/registry/luxuryRegistry.ts |
| cmp_1265e2650d | buildPitchShellFrameModel | block | apps/keystone/components/pitch/view-model/pitch-shell-model.ts |
| cmp_12de42b70d | buildDemoScreens | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_13159ad4c6 | LAYER_DOM_METADATA_PROFILE_ATTRIBUTE | block | packages/ui-kit/src/layers/applyLayerFlagsToDom.ts |
| cmp_131eb79a6f | PitchScrollAffordance | block | apps/keystone/components/pitch/shell/pitch-scroll-affordance.tsx |
| cmp_133d7dec91 | PitchComparisonMeter | dataviz | apps/keystone/components/pitch/visuals/pitch-comparison-meter.tsx |
| cmp_13de148174 | mergeLayerFlags | block | packages/ui-kit/src/layers/layerIds.ts |
| cmp_13dedb9777 | DropdownMenu | control | packages/ui-kit/src/components/navigation/DropdownMenu.tsx |
| cmp_1444fa6a17 | ExampleKpiTile | block | apps/keystone/app/dev/_luxury/registry/kpiCatalogBulk.ts |
| cmp_146f04c888 | RECEIVING_INCOTERMS | block | apps/keystone/components/pitch/run2/types.ts |
| cmp_14a504c3ed | areAllLayersEnabled | block | packages/ui-kit/src/layers/layerIds.ts |
| cmp_14d67d6cc1 | INDUSTRIAL_CATALOG_ENTRIES | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_153a62a5a8 | buildFloatingWindowDragPath | block | apps/keystone/app/dev/scene-studio/floating-window-drag-policy.ts |
| cmp_16248ef76b | PitchIconBolt | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_16baf9714d | PopoverCloseButton | block | packages/ui-kit/src/components/premium/overlays/Popover.tsx |
| cmp_16c468c2d6 | encodeLayersParam | block | packages/ui-kit/src/layers/resolveLayerFlags.ts |
| cmp_18345cc450 | PitchDemoScreen | block | apps/keystone/components/pitch/demo-screen.tsx |
| cmp_188d1ee7b5 | IconButton | control | packages/ui-kit/src/components/forms/IconButton.tsx |
| cmp_18bf321312 | PitchIconMountain | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_18fd0b35c2 | createDemoState | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_19593ae00a | arcPath | dataviz | packages/ui-kit/src/kpi/charts/common.tsx |
| cmp_195def9dff | PitchIconArrow | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_1a5db429e9 | usePathname | nav | packages/ui-kit/src/types/next-navigation.d.ts |
| cmp_1a6a25d40f | ScrollArea | block | packages/ui-kit/src/components/navigation/ScrollArea.tsx |
| cmp_1a8f7d90ca | RECEIVING_STATES | block | apps/keystone/components/pitch/run2/types.ts |
| cmp_1a9fa7556a | setSupplierStatus | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_1aa184ab6b | KPI_JSON_PROVIDER_SOURCE | block | apps/keystone/app/dev/_luxury/registry/kpiRegistry.ts |
| cmp_1aa60f6f5e | listCatalogWithSnippets | block | packages/ui-kit/src/kpi/registry/catalog.ts |
| cmp_1b07f76600 | DialogPortal | block | packages/ui-kit/src/components/overlays/Dialog.tsx |
| cmp_1b28f82009 | resolveRunId | dataviz | apps/keystone/visual-tests/helpers/paths.ts |
| cmp_1b2aa60a4e | WindowManagerProvider | block | apps/keystone/app/dev/scene-studio/window-manager/WindowManagerProvider.tsx |
| cmp_1b31a3432a | ScreenValuation | screen | apps/keystone/components/pitch/screen-valuation.tsx |
| cmp_1b91af9370 | KPI_INTENT_IDS | block | apps/keystone/app/dev/_luxury/types.ts |
| cmp_1bbba9eb94 | VALIDATION_SCENARIOS | block | apps/keystone/app/dev/_luxury/registry/validationScenarioLibrary.ts |
| cmp_1be6da462c | PitchIconDollar | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_1c003d2c50 | useInventoryFoundationStore | state | apps/keystone/components/pitch/run1/store.ts |
| cmp_1c4555d654 | DialogOverlay | block | packages/ui-kit/src/components/overlays/Dialog.tsx |
| cmp_1cc73d6ff9 | FOUNDATION_ROLES | block | apps/keystone/components/pitch/run1/types.ts |
| cmp_1cc745febb | parseMotionCatalogRow | block | packages/ui-kit/src/motion/catalogs/heroQualityCatalog.ts |
| cmp_1cdce83528 | createMockProvider | block | packages/ui-kit/src/data-spine/providers/mock.ts |
| cmp_1d1bf7a406 | LIQUID_GLASS_MANIFEST | block | packages/ui-kit/src/luxury/tokens/liquidGlass.ts |
| cmp_1d64a6eac7 | LayerFlagsProvider | block | packages/ui-kit/src/layers/LayerFlagsProvider.tsx |
| cmp_1d72ad9a8a | normalizeLayersList | block | apps/keystone/lib/scene-studio/scene-query.ts |
| cmp_1d9e0d5b23 | parseSceneMotion | block | apps/keystone/lib/scene-studio/scene-query.ts |

## States
| state_id | file_path | readers | writers |
| --- | --- | --- | --- |
| stt_042e635804 | apps/keystone/tests/scene-studio-store.test.ts | 0 | 0 |
| stt_3a3607b40d | apps/keystone/lib/store/ui-store.ts | 4 | 3 |
| stt_53db6891ed | apps/keystone/components/scene-studio/use-scene-studio-state.ts | 4 | 4 |
| stt_6d6705f135 | apps/keystone/tests/demo-state.test.ts | 0 | 0 |
| stt_933f512320 | apps/keystone/lib/scene-studio/scene-store.ts | 0 | 0 |
| stt_aecc532ac4 | packages/ui-kit/src/components/feedback/EmptyState.tsx | 0 | 0 |
| stt_c79310c09f | apps/keystone/components/pitch/run2/store.ts | 5 | 4 |
| stt_cda82024e1 | apps/keystone/lib/pitch/demo-state.ts | 6 | 6 |
| stt_e207ad61e8 | apps/keystone/lib/pitch/use-demo-state.ts | 1 | 0 |
| stt_f7c9565a89 | apps/keystone/components/pitch/run1/store.ts | 3 | 2 |

## Styles
| style_id | file_path | referenced_by_count |
| --- | --- | --- |
| sty_00e4d49478 | apps/keystone/components/pitch/theme/pitch-cinematic.css | 0 |
| sty_473cd207b0 | packages/ui-kit/src/motion/keyframes.css | 0 |
| sty_562b50e8fe | packages/ui-kit/src/styles/hitech-premium.css | 0 |
| sty_5b5a57301b | packages/ui-kit/src/styles.css | 2 |
| sty_67feb9dc78 | apps/keystone/app/globals.css | 2 |
| sty_89ebb78f51 | packages/ui-kit/src/styles/layers.css | 0 |
| sty_b4a36b9bf6 | apps/keystone/components/dev-console/dev-console.module.css | 7 |
| sty_b698d50b48 | apps/keystone/components/scene-studio/scene-studio.module.css | 6 |
| sty_b716435591 | packages/ui-kit/src/luxury/frames/frames.css | 0 |
| sty_e6653df517 | packages/ui-kit/src/styles/hitech-foundation.css | 0 |

## Assets
| asset_id | kind | file_path | referenced_by_count |
| --- | --- | --- | --- |
| ast_50107d67d5 | svg | packages/ui-kit/src/brand/assets/hitech-phoenix.svg | 0 |
| ast_59122999d1 | svg | apps/keystone/public/brand/hitech-phoenix.svg | 0 |

## Hotspots
| hotspot_id | screen_or_global | risk | title |
| --- | --- | --- | --- |
| hsp_019d3ef3db | screen-06 | high | Screen 06 deepest: receiving gate + controls + mismatch handling + RBAC handoff |
| hsp_16b33a0cb5 | screen-04 | high | Screen 04 valuation controls |
| hsp_236a87856a | global | high | Pitch shell orchestration |
| hsp_2be6059cd1 | screen-01 | med | Screen 01 double engine narrative |
| hsp_4e38644693 | screen-02 | med | Screen 02 industrial flow |
| hsp_699bc3adf5 | global | med | Pitch navigation and route rail |
| hsp_97a6c9dbf0 | global | high | Layer resolution and profile flags |
| hsp_9fdef7bf22 | screen-03 | med | Screen 03 hitech os map |
| hsp_aacfeea330 | global | med | UI kit premium controls |
| hsp_c5ff5805d6 | screen-05 | high | Screen 05 deepest: state machine + gating + docs vault + RBAC |
| hsp_e1a795cd44 | global | high | Brand presence central config |

_Component table is intentionally truncated; full dataset is in `ui_dictionary.json`._
