# UI Dictionary

- version: `1.0.0`
- generated_by: `tools/ui_map deterministic`
- routes: `9`
- components: `604`
- states: `10`
- styles: `7`
- assets: `2`
- hotspots: `11`

## Routes
| route_id | path | entry_file | screen_component_id |
| --- | --- | --- | --- |
| rte_46efb84e93 | /pitch | apps/keystone/app/pitch/page.tsx | cmp_6cb06e50cd |
| rte_588c6fe0cc | /pitch/06-shipments-receiving | apps/keystone/app/pitch/06-shipments-receiving/page.tsx | cmp_bf1d0f2e29 |
| rte_64b18eb3cd | /dev/scene-studio | apps/keystone/app/dev/scene-studio/page.tsx |  |
| rte_6c122ba817 | /pitch/04-valuation | apps/keystone/app/pitch/04-valuation/page.tsx | cmp_1b31a3432a |
| rte_8a5edab282 | / | apps/keystone/app/page.tsx |  |
| rte_9225911e8f | /pitch/01-double-engine | apps/keystone/app/pitch/01-double-engine/page.tsx | cmp_f14bfffde5 |
| rte_d2b3868d72 | /pitch/02-industrial-flow | apps/keystone/app/pitch/02-industrial-flow/page.tsx | cmp_88852e131f |
| rte_e78399e664 | /pitch/05-inventory-foundation | apps/keystone/app/pitch/05-inventory-foundation/page.tsx | cmp_114f4ca07f |
| rte_fe70914ec1 | /pitch/03-hitech-os | apps/keystone/app/pitch/03-hitech-os/page.tsx | cmp_4daf0963df |

## Components (first 120)
| component_id | export_name | kind | file_path |
| --- | --- | --- | --- |
| cmp_003267a333 | PitchHero | block | apps/keystone/components/pitch/shell/pitch-hero.tsx |
| cmp_005058f357 | SCENE_MOTION_VALUES | block | apps/keystone/lib/scene-studio/scene-constants.ts |
| cmp_00558dfee2 | TableBody | block | packages/ui-kit/src/components/data/Table.tsx |
| cmp_015c59ef59 | RiskAndNextGatePanel | control | apps/keystone/components/pitch/run2/RiskAndNextGatePanel.tsx |
| cmp_01d4823875 | PitchIconHub | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0260d3ce32 | PitchIconPlay | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_02ed842dd9 | activityQueryKey | block | apps/keystone/lib/queries/activity.ts |
| cmp_0351c3ca7b | NeonButton | block | apps/keystone/components/pitch/run1/primitives.tsx |
| cmp_03e84dbf35 | useActivityQuery | block | apps/keystone/lib/queries/activity.ts |
| cmp_044ceddc68 | INCOTERMS | block | apps/keystone/components/pitch/run1/types.ts |
| cmp_048265afb6 | PitchIconRisk | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_04a0c7e82f | waitForDeterministicReady | dataviz | apps/keystone/visual-tests/helpers/deterministic.ts |
| cmp_04f54bd3f3 | captureScene | dataviz | apps/keystone/visual-tests/helpers/scene-capture.ts |
| cmp_051d307492 | PitchIconSatellite | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0691342735 | PitchIconCloud | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0695b05495 | PitchIconFire | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_06987e5a47 | Stage | layout | packages/ui-kit/src/components/layout/Stage.tsx |
| cmp_06cabd4ed7 | getSupplierLifecycleTone | state | apps/keystone/components/pitch/run1/store.ts |
| cmp_06ea624681 | runsQueryKey | block | apps/keystone/lib/queries/runs.ts |
| cmp_06fa5a7ff5 | dynamic | route | apps/keystone/app/pitch/05-inventory-foundation/page.tsx |
| cmp_075347cd7a | SCENES_MANIFEST_PATH | dataviz | apps/keystone/visual-tests/helpers/paths.ts |
| cmp_0760ab5e76 | DialogDescription | block | packages/ui-kit/src/components/overlays/Dialog.tsx |
| cmp_077b3ee2ad | resolveBrandModeEnabled | brand | packages/ui-kit/src/brand/brand-presence.config.ts |
| cmp_07e0dc2880 | PitchIconStop | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0805226cf6 | PitchRouteCard | block | apps/keystone/components/pitch/route-index/pitch-route-card.tsx |
| cmp_0890609e12 | PitchIconBackward | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_08b67ff1e9 | createPixelDiff | dataviz | apps/keystone/visual-tests/helpers/diff.ts |
| cmp_0948794dd2 | PitchIconMinus | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_09fce7bb33 | PitchIconNode | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0ab6307b9d | PitchIconVault | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0acb82cd64 | PitchIconCpu | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0b3b4055d8 | PitchShellBrandLayer | brand | apps/keystone/components/pitch/shell/pitch-shell-brand-layer.tsx |
| cmp_0b80292dff | getCustomsStatusTone | state | apps/keystone/components/pitch/run2/store.ts |
| cmp_0bade2bc81 | GET | block | apps/keystone/app/api/runs/route.ts |
| cmp_0cea8bfba1 | GlassHeader | layout | packages/ui-kit/src/components/premium/layout/GlassHeader.tsx |
| cmp_0cff2c82da | PitchIconChip | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0d339b71f7 | PitchIconLeaf | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0d43aff805 | ReceivingControlPanel | control | apps/keystone/components/pitch/run2/ReceivingControlPanel.tsx |
| cmp_0dc055c5a2 | PitchIconFlow | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_0e18d237a4 | createDefaultSceneLibrary | block | apps/keystone/lib/scene-studio/default-scenes.ts |
| cmp_0ef45dc6b4 | sceneQueryObjectToSearchParams | block | apps/keystone/lib/scene-studio/scene-query.ts |
| cmp_0f1bc4f36f | SceneStudioEditor | block | apps/keystone/components/scene-studio/scene-studio-editor.tsx |
| cmp_10405d1738 | SCENE_SCHEMA_V1 | block | apps/keystone/lib/scene-studio/scene-schema.ts |
| cmp_105875c51d | PitchIconForward | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_107a4b287e | VIEWPORT_PRESETS | dataviz | apps/keystone/visual-tests/helpers/deterministic.ts |
| cmp_109f9bd9d9 | normalizeSceneId | block | apps/keystone/lib/scene-studio/scene-id.ts |
| cmp_113609dbcd | HITECH_BRAND_COLORS | brand | packages/ui-kit/src/brand/hitech-theme.ts |
| cmp_114f4ca07f | InventoryFoundationControlRoom | control | apps/keystone/components/pitch/run1/InventoryFoundationControlRoom.tsx |
| cmp_1265e2650d | buildPitchShellFrameModel | block | apps/keystone/components/pitch/view-model/pitch-shell-model.ts |
| cmp_12de42b70d | buildDemoScreens | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_13159ad4c6 | LAYER_DOM_METADATA_PROFILE_ATTRIBUTE | block | packages/ui-kit/src/layers/applyLayerFlagsToDom.ts |
| cmp_131eb79a6f | PitchScrollAffordance | block | apps/keystone/components/pitch/shell/pitch-scroll-affordance.tsx |
| cmp_133d7dec91 | PitchComparisonMeter | dataviz | apps/keystone/components/pitch/visuals/pitch-comparison-meter.tsx |
| cmp_13de148174 | mergeLayerFlags | block | packages/ui-kit/src/layers/layerIds.ts |
| cmp_13dedb9777 | DropdownMenu | control | packages/ui-kit/src/components/navigation/DropdownMenu.tsx |
| cmp_146f04c888 | RECEIVING_INCOTERMS | block | apps/keystone/components/pitch/run2/types.ts |
| cmp_14a504c3ed | areAllLayersEnabled | block | packages/ui-kit/src/layers/layerIds.ts |
| cmp_14d67d6cc1 | INDUSTRIAL_CATALOG_ENTRIES | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_16248ef76b | PitchIconBolt | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_16baf9714d | PopoverCloseButton | block | packages/ui-kit/src/components/premium/overlays/Popover.tsx |
| cmp_16c468c2d6 | encodeLayersParam | block | packages/ui-kit/src/layers/resolveLayerFlags.ts |
| cmp_18345cc450 | PitchDemoScreen | block | apps/keystone/components/pitch/demo-screen.tsx |
| cmp_188d1ee7b5 | IconButton | control | packages/ui-kit/src/components/forms/IconButton.tsx |
| cmp_18bf321312 | PitchIconMountain | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_18fd0b35c2 | createDemoState | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_195def9dff | PitchIconArrow | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_1a5db429e9 | usePathname | nav | packages/ui-kit/src/types/next-navigation.d.ts |
| cmp_1a6a25d40f | ScrollArea | block | packages/ui-kit/src/components/navigation/ScrollArea.tsx |
| cmp_1a8f7d90ca | RECEIVING_STATES | block | apps/keystone/components/pitch/run2/types.ts |
| cmp_1a9fa7556a | setSupplierStatus | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_1b07f76600 | DialogPortal | block | packages/ui-kit/src/components/overlays/Dialog.tsx |
| cmp_1b28f82009 | resolveRunId | dataviz | apps/keystone/visual-tests/helpers/paths.ts |
| cmp_1b31a3432a | ScreenValuation | screen | apps/keystone/components/pitch/screen-valuation.tsx |
| cmp_1be6da462c | PitchIconDollar | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_1c003d2c50 | useInventoryFoundationStore | state | apps/keystone/components/pitch/run1/store.ts |
| cmp_1c4555d654 | DialogOverlay | block | packages/ui-kit/src/components/overlays/Dialog.tsx |
| cmp_1cc73d6ff9 | FOUNDATION_ROLES | block | apps/keystone/components/pitch/run1/types.ts |
| cmp_1d64a6eac7 | LayerFlagsProvider | block | packages/ui-kit/src/layers/LayerFlagsProvider.tsx |
| cmp_1d72ad9a8a | normalizeLayersList | block | apps/keystone/lib/scene-studio/scene-query.ts |
| cmp_1d9e0d5b23 | parseSceneMotion | block | apps/keystone/lib/scene-studio/scene-query.ts |
| cmp_1d9fcb3211 | PitchIconRefresh | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_1eedae57a4 | ValuationBlocks | block | apps/keystone/components/pitch/valuation-blocks.tsx |
| cmp_1f8d1ba188 | Chip | block | apps/keystone/components/pitch/run2/primitives.tsx |
| cmp_2100b40d4a | PROFILE_PRESETS | block | packages/ui-kit/src/layers/layerIds.ts |
| cmp_2161224437 | PitchIconSpark | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_2177bf5c47 | PitchIconQuality | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_217a574a9a | PitchIconCalendar | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_2236484dad | DEMO_DOCUMENT_LIFECYCLES | state | apps/keystone/lib/pitch/demo-state.ts |
| cmp_22bfaa2518 | ValuationEquityVisual | dataviz | apps/keystone/components/pitch/valuation-visuals.tsx |
| cmp_2387441951 | inferLayersFromQuery | block | apps/keystone/lib/scene-studio/scene-schema.ts |
| cmp_23893d3f81 | PitchIconMap | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_23cdf1104b | PitchIconThermal | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_23d99c659f | resolveBrandModeOpacity | brand | packages/ui-kit/src/brand/brand-presence.config.ts |
| cmp_23e9d34b62 | PitchIconCapital | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_241ed781ed | brandPresenceConfig | brand | packages/ui-kit/src/brand/brand-presence.config.ts |
| cmp_24e728f035 | PitchCardGrid | layout | apps/keystone/components/pitch/layout/pitch-card-grid.tsx |
| cmp_25287ab19a | DropdownMenuLabel | control | packages/ui-kit/src/components/navigation/DropdownMenu.tsx |
| cmp_2532dc9141 | ScreenInventoryFoundation | screen | apps/keystone/components/pitch/screen-inventory-foundation.tsx |
| cmp_2540eba227 | useDemoScreens | state | apps/keystone/lib/pitch/use-demo-state.ts |
| cmp_257f0d4c1c | useRunsQuery | block | apps/keystone/lib/queries/runs.ts |
| cmp_258c981ea8 | PitchIconHex | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_25c00cc5f4 | PitchIconRoute | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_262a7f305a | PitchDataChip | layout | apps/keystone/components/pitch/layout/pitch-data-chip.tsx |
| cmp_26819c9f9a | PitchSection | layout | apps/keystone/components/pitch/layout/pitch-section.tsx |
| cmp_27250f66fb | parseSceneUrlState | block | apps/keystone/lib/scene-studio/scene-url.ts |
| cmp_2769aeb2cb | PitchIconCrown | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_276e587982 | PitchIconEngine | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_279f34edd5 | useInventoryFoundationPanelContext | state | apps/keystone/components/pitch/run1/store.ts |
| cmp_27bf092c17 | metadata | layout | apps/keystone/app/layout.tsx |
| cmp_27e1a1538b | KpiRow | block | apps/keystone/components/pitch/kpi-row.tsx |
| cmp_286dbfc1b9 | PitchIconTree | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_289c6f22f9 | PitchIconBell | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_28ff580207 | ScreenShipmentsReceiving | screen | apps/keystone/components/pitch/screen-shipments-receiving.tsx |
| cmp_2913c65c2b | SCENE_EXPORT_ENVELOPE_SCHEMA | block | apps/keystone/lib/scene-studio/scene-schema.ts |
| cmp_2917294077 | PitchIconGauge | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_2927b6c7ce | isDiagnosticsResponseMessage | block | apps/keystone/lib/scene-studio/scene-bridge.ts |
| cmp_29b292d7e7 | PitchIconWater | dataviz | apps/keystone/components/pitch/visuals/pitch-icon-library.tsx |
| cmp_2a48db8a31 | canonicalizeLayerQuery | block | packages/ui-kit/src/layers/resolveLayerFlags.ts |
| cmp_2a7a52f69b | useReducedMotionPreference | block | packages/ui-kit/src/lib/motion.ts |
| cmp_2aefaeee83 | getHitechThemeCssText | brand | packages/ui-kit/src/brand/hitech-theme.ts |

## States
| state_id | file_path | readers | writers |
| --- | --- | --- | --- |
| stt_042e635804 | apps/keystone/tests/scene-studio-store.test.ts | 0 | 0 |
| stt_3a3607b40d | apps/keystone/lib/store/ui-store.ts | 4 | 3 |
| stt_53db6891ed | apps/keystone/components/scene-studio/use-scene-studio-state.ts | 1 | 1 |
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
| sty_562b50e8fe | packages/ui-kit/src/styles/hitech-premium.css | 0 |
| sty_5b5a57301b | packages/ui-kit/src/styles.css | 2 |
| sty_67feb9dc78 | apps/keystone/app/globals.css | 2 |
| sty_89ebb78f51 | packages/ui-kit/src/styles/layers.css | 0 |
| sty_b698d50b48 | apps/keystone/components/scene-studio/scene-studio.module.css | 6 |
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
