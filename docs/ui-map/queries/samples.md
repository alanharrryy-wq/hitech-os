# Query Samples

Each sample is deterministic for the same dictionary input.

## dependents_of_file

- expected_output_shape: `[{component_id,file_path,reason}]`
- sample_output:
```json
[
  {
    "component_id": "cmp_5451c45023",
    "file_path": "apps/keystone/components/pitch/shell/pitch-shell.tsx",
    "reason": "imports_file"
  }
]
```

## screens_using_component

- expected_output_shape: `[screen_id]`
- sample_output:
```json
[]
```

## files_touched_by_screen

- expected_output_shape: `[file_path]`
- sample_output:
```json
[
  "apps/keystone/app/pitch/01-double-engine/page.tsx",
  "apps/keystone/components/pitch/layout/pitch-bullet-cards.tsx",
  "apps/keystone/components/pitch/layout/pitch-card-grid.tsx",
  "apps/keystone/components/pitch/layout/pitch-data-chip.tsx",
  "apps/keystone/components/pitch/layout/pitch-expandable-panel.tsx",
  "apps/keystone/components/pitch/layout/pitch-section.tsx",
  "apps/keystone/components/pitch/screen-double-engine.tsx",
  "apps/keystone/components/pitch/screens/screen-01-double-engine-cinematic.tsx",
  "apps/keystone/components/pitch/shell/pitch-shell-context.tsx",
  "apps/keystone/components/pitch/visuals/pitch-comparison-meter.tsx",
  "apps/keystone/components/pitch/visuals/pitch-kpi-chip-cloud.tsx",
  "apps/keystone/components/pitch/visuals/pitch-mini-bars.tsx",
  "apps/keystone/components/pitch/visuals/pitch-radial-gauge.tsx",
  "apps/keystone/components/pitch/visuals/pitch-sparkline.tsx",
  "apps/keystone/components/pitch/visuals/pitch-vs-divider.tsx",
  "apps/keystone/lib/pitch/deck-view-model.ts",
  "packages/ui-kit/src/components/feedback/Badge.tsx",
  "packages/ui-kit/src/lib/cn.ts"
]
```

## state_readers

- expected_output_shape: `[component_id]`
- sample_output:
```json
[]
```

## state_writers

- expected_output_shape: `[component_id]`
- sample_output:
```json
[]
```

## assets_used_by_screen

- expected_output_shape: `[{asset_id,file_path,kind}]`
- sample_output:
```json
[]
```

## styles_used_by_screen

- expected_output_shape: `[{style_id,file_path}]`
- sample_output:
```json
[]
```

## hotspots_by_risk

- expected_output_shape: `[hotspot]`
- sample_output:
```json
[
  {
    "change_types": [
      "brand",
      "state"
    ],
    "components": [
      "cmp_077b3ee2ad",
      "cmp_0b3b4055d8",
      "cmp_23d99c659f",
      "cmp_241ed781ed",
      "cmp_3af8aa64d1",
      "cmp_ab49225ce3",
      "cmp_d5aab75574"
    ],
    "files": [
      "apps/keystone/components/pitch/shell/pitch-shell-brand-layer.tsx",
      "packages/ui-kit/src/brand/brand-presence.config.ts",
      "packages/ui-kit/src/brand/BrandPresenceLayer.tsx"
    ],
    "hotspot_id": "hsp_e1a795cd44",
    "notes": "Edit brand only through central config and createBrandPresenceRootStyle; never override :root globally.",
    "risk": "high",
    "screen_or_global": "global",
    "title": "Brand presence central config"
  },
  {
    "change_types": [
      "interactions",
      "state",
      "validation"
    ],
    "components": [
      "cmp_0b3b4055d8",
      "cmp_13159ad4c6",
      "cmp_13de148174",
      "cmp_14a504c3ed",
      "cmp_16c468c2d6",
      "cmp_1d64a6eac7",
      "cmp_2100b40d4a",
      "cmp_2a48db8a31",
      "cmp_432c46b32d",
      "cmp_45b5a64481",
      "cmp_46d3f6738b",
      "cmp_48b3a15c8f",
      "cmp_4b76d1e46d",
      "cmp_4c2da80405",
      "cmp_4e3f8729d7",
      "cmp_4f5e8cc303",
      "cmp_51ab9b9b34",
      "cmp_535bf7270f",
      "cmp_5965ccefa8",
      "cmp_5a7611b5d6",
      "cmp_5f87b72dbe",
      "cmp_62ea04ad4f",
      "cmp_65dfb85232",
      "cmp_67c4101751",
      "cmp_685388607c",
      "cmp_6cb06e50cd",
      "cmp_736dbfbd88",
      "cmp_78be8e7da7",
      "cmp_7c123a5c08",
      "cmp_817817e84e",
      "cmp_8832e0d534",
      "cmp_91d5a352c2",
      "cmp_92c5078638",
      "cmp_a421334569",
      "cmp_a94debf8ad",
      "cmp_aa5506ce35",
      "cmp_aa9f1dd5b7",
      "cmp_ab49225ce3",
      "cmp_b6fb900f26",
      "cmp_ba2f1463d1",
      "cmp_bc2c865d76",
      "cmp_bd6ef93995",
      "cmp_c36404b994",
      "cmp_d2126a2b14",
      "cmp_dae81b3152",
      "cmp_de9c0a16e6",
      "cmp_df8c73eff1",
      "cmp_e49e5f31b9",
      "cmp_fbdd0af3a0"
    ],
    "files": [
      "apps/keystone/app/pitch/page.tsx",
      "apps/keystone/lib/pitch/layer-resolution.ts",
      "packages/ui-kit/src/layers/resolveLayerFlags.ts"
    ],
    "hotspot_id": "hsp_97a6c9dbf0",
    "notes": "Layer flags control profile rendering and debug overlays.",
    "risk": "high",
    "screen_or_global": "global",
    "title": "Layer resolution and profile flags"
  },
  {
    "change_types": [
      "interactions",
      "layout"
    ],
    "components": [
      "cmp_0b3b4055d8",
      "cmp_1265e2650d",
      "cmp_5451c45023",
      "cmp_5628844317",
      "cmp_6a38a5fa79",
      "cmp_89cfa98853",
      "cmp_a1ab716332",
      "cmp_a67f1720f0",
      "cmp_dd9d94eef4",
      "cmp_e7d026d7b9"
    ],
    "files": [
      "apps/keystone/components/pitch/pitch-shell.tsx",
      "apps/keystone/components/pitch/shell/pitch-shell.tsx",
      "apps/keystone/components/pitch/view-model/pitch-shell-model.ts"
    ],
    "hotspot_id": "hsp_236a87856a",
    "notes": "Global shell wraps all pitch routes; changes cascade across slides.",
    "risk": "high",
    "screen_or_global": "global",
    "title": "Pitch shell orchestration"
  },
  {
    "change_types": [
      "charts",
      "interactions",
      "layout"
    ],
    "components": [
      "cmp_1b31a3432a",
      "cmp_1eedae57a4"
    ],
    "files": [
      "apps/keystone/app/pitch/04-valuation/page.tsx",
      "apps/keystone/components/pitch/screen-valuation.tsx",
      "apps/keystone/components/pitch/valuation-blocks.tsx"
    ],
    "hotspot_id": "hsp_16b33a0cb5",
    "notes": "Valuation and charts are high-risk for metric interpretation.",
    "risk": "high",
    "screen_or_global": "screen-04",
    "title": "Screen 04 valuation controls"
  },
  {
    "change_types": [
      "interactions",
      "layout",
      "state",
      "validation"
    ],
    "components": [
      "cmp_06cabd4ed7",
      "cmp_114f4ca07f",
      "cmp_1c003d2c50",
      "cmp_279f34edd5",
      "cmp_2fd978854b",
      "cmp_4b0b787c25",
      "cmp_4e209170ae",
      "cmp_9d073825da",
      "cmp_a1589fdb5b",
      "cmp_a1ec1fd452"
    ],
    "files": [
      "apps/keystone/app/pitch/05-inventory-foundation/page.tsx",
      "apps/keystone/components/pitch/run1/DocumentVaultPanel.tsx",
      "apps/keystone/components/pitch/run1/InventoryFoundationControlRoom.tsx",
      "apps/keystone/components/pitch/run1/RBACMatrixPanel.tsx",
      "apps/keystone/components/pitch/run1/store.ts"
    ],
    "hotspot_id": "hsp_c5ff5805d6",
    "notes": "Deepest overlap hotspot: deterministic state transitions, gating, document vault lifecycle, and RBAC controls.",
    "risk": "high",
    "screen_or_global": "screen-05",
    "title": "Screen 05 deepest: state machine + gating + docs vault + RBAC"
  },
  {
    "change_types": [
      "interactions",
      "layout",
      "state",
      "validation"
    ],
    "components": [
      "cmp_015c59ef59",
      "cmp_0b80292dff",
      "cmp_47156dd84d",
      "cmp_7a25fd4d19",
      "cmp_7b9d562259",
      "cmp_b499325617",
      "cmp_bf1d0f2e29",
      "cmp_f375c9cdbc"
    ],
    "files": [
      "apps/keystone/app/pitch/06-shipments-receiving/page.tsx",
      "apps/keystone/components/pitch/run2/MismatchHandlingPanel.tsx",
      "apps/keystone/components/pitch/run2/RiskAndNextGatePanel.tsx",
      "apps/keystone/components/pitch/run2/ShipmentsReceivingControlRoom.tsx",
      "apps/keystone/components/pitch/run2/store.ts"
    ],
    "hotspot_id": "hsp_019d3ef3db",
    "notes": "Deepest overlap hotspot: receiving state machine, customs/doc gates, mismatch/deviation, and gate progression logic.",
    "risk": "high",
    "screen_or_global": "screen-06",
    "title": "Screen 06 deepest: receiving gate + controls + mismatch handling + RBAC handoff"
  }
]
```

## component_tree

- expected_output_shape: `{screen_id,root_component_id,component_ids,edges}`
- sample_output:
```json
{
  "component_ids": [
    "cmp_133d7dec91",
    "cmp_24e728f035",
    "cmp_262a7f305a",
    "cmp_26819c9f9a",
    "cmp_5628844317",
    "cmp_73815c5199",
    "cmp_90fb220e30",
    "cmp_934d4e8c97",
    "cmp_a56a27fc43",
    "cmp_ad4bf2dc06",
    "cmp_ade61a11b0",
    "cmp_b3decd4d6e",
    "cmp_cbf3af2004",
    "cmp_ddfd33abd4",
    "cmp_de3f8d1ee9",
    "cmp_f14bfffde5",
    "cmp_f2b3612ca2",
    "cmp_f5c8a56456"
  ],
  "edges": [
    {
      "from": "cmp_133d7dec91",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_24e728f035",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_262a7f305a",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_26819c9f9a",
      "to": "cmp_5628844317",
      "type": "imports"
    },
    {
      "from": "cmp_26819c9f9a",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_26819c9f9a",
      "to": "cmp_ddfd33abd4",
      "type": "imports"
    },
    {
      "from": "cmp_73815c5199",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_90fb220e30",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_934d4e8c97",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_ad4bf2dc06",
      "to": "cmp_262a7f305a",
      "type": "imports"
    },
    {
      "from": "cmp_ad4bf2dc06",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_ade61a11b0",
      "to": "cmp_73815c5199",
      "type": "imports"
    },
    {
      "from": "cmp_ade61a11b0",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_133d7dec91",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_24e728f035",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_262a7f305a",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_26819c9f9a",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_73815c5199",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_90fb220e30",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_934d4e8c97",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_ad4bf2dc06",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_ade61a11b0",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_cbf3af2004",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_ddfd33abd4",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_de3f8d1ee9",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_f2b3612ca2",
      "type": "imports"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_f5c8a56456",
      "type": "imports"
    },
    {
      "from": "cmp_cbf3af2004",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_ddfd33abd4",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_f14bfffde5",
      "to": "cmp_b3decd4d6e",
      "type": "imports"
    },
    {
      "from": "cmp_f2b3612ca2",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_f5c8a56456",
      "to": "cmp_a56a27fc43",
      "type": "imports"
    },
    {
      "from": "cmp_26819c9f9a",
      "to": "cmp_ddfd33abd4",
      "type": "renders"
    },
    {
      "from": "cmp_ad4bf2dc06",
      "to": "cmp_262a7f305a",
      "type": "renders"
    },
    {
      "from": "cmp_ade61a11b0",
      "to": "cmp_73815c5199",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_133d7dec91",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_24e728f035",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_262a7f305a",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_26819c9f9a",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_73815c5199",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_90fb220e30",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_934d4e8c97",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_ad4bf2dc06",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_ade61a11b0",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_cbf3af2004",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_ddfd33abd4",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_f2b3612ca2",
      "type": "renders"
    },
    {
      "from": "cmp_b3decd4d6e",
      "to": "cmp_f5c8a56456",
      "type": "renders"
    },
    {
      "from": "cmp_f14bfffde5",
      "to": "cmp_b3decd4d6e",
      "type": "renders"
    }
  ],
  "root_component_id": "cmp_f14bfffde5",
  "screen_id": "screen-01"
}
```

## imports_of_file

- expected_output_shape: `[file_path]`
- sample_output:
```json
[
  "apps/keystone/components/pitch/shell/types.ts",
  "packages/ui-kit/src/index.ts"
]
```

## routes_index

- expected_output_shape: `[{route_id,path,entry_file,screen_component_id}]`
- sample_output:
```json
[
  {
    "entry_file": "apps/keystone/app/page.tsx",
    "path": "/",
    "route_id": "rte_8a5edab282",
    "screen_component_id": ""
  },
  {
    "entry_file": "apps/keystone/app/dev/scene-studio/page.tsx",
    "path": "/dev/scene-studio",
    "route_id": "rte_64b18eb3cd",
    "screen_component_id": ""
  },
  {
    "entry_file": "apps/keystone/app/pitch/page.tsx",
    "path": "/pitch",
    "route_id": "rte_46efb84e93",
    "screen_component_id": "cmp_6cb06e50cd"
  },
  {
    "entry_file": "apps/keystone/app/pitch/01-double-engine/page.tsx",
    "path": "/pitch/01-double-engine",
    "route_id": "rte_9225911e8f",
    "screen_component_id": "cmp_f14bfffde5"
  },
  {
    "entry_file": "apps/keystone/app/pitch/02-industrial-flow/page.tsx",
    "path": "/pitch/02-industrial-flow",
    "route_id": "rte_d2b3868d72",
    "screen_component_id": "cmp_88852e131f"
  },
  {
    "entry_file": "apps/keystone/app/pitch/03-hitech-os/page.tsx",
    "path": "/pitch/03-hitech-os",
    "route_id": "rte_fe70914ec1",
    "screen_component_id": "cmp_4daf0963df"
  },
  {
    "entry_file": "apps/keystone/app/pitch/04-valuation/page.tsx",
    "path": "/pitch/04-valuation",
    "route_id": "rte_6c122ba817",
    "screen_component_id": "cmp_1b31a3432a"
  },
  {
    "entry_file": "apps/keystone/app/pitch/05-inventory-foundation/page.tsx",
    "path": "/pitch/05-inventory-foundation",
    "route_id": "rte_e78399e664",
    "screen_component_id": "cmp_114f4ca07f"
  },
  {
    "entry_file": "apps/keystone/app/pitch/06-shipments-receiving/page.tsx",
    "path": "/pitch/06-shipments-receiving",
    "route_id": "rte_588c6fe0cc",
    "screen_component_id": "cmp_bf1d0f2e29"
  }
]
```

## changeset_hint

- expected_output_shape: `{type,target,...}`
- sample_output:
```json
{
  "file_path": "apps/keystone/components/pitch/shell/pitch-hero.tsx",
  "kind": "block",
  "target": "cmp_003267a333",
  "touches": [],
  "type": "component"
}
```
