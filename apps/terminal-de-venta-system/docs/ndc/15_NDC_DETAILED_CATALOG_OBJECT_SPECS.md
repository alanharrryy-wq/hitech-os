# 15. NDC Detailed Catalog Object Specifications

> Deep catalog specifications for every generated matrix/view.


## 01. Scope_Registry

**Group:** `scope`
**View ID:** `CAT.scope.Scope_Registry`
**Generated export:** `Scope_Registry.csv`
**Purpose:** identidades operativas de tenant, business, store, terminal, device, user, role, plan, license, slot, session.

### Grain

One row represents a governed NDC observation or decision for `Scope_Registry`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: role grant. |
| `name` | human-readable name; local emphasis: business hierarchy. |
| `type` | object family/type; local emphasis: business hierarchy. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: device slot. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: session context. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: session context. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: license scope. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: business hierarchy. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: role grant. |
| `owner` | human/system owner; local emphasis: license scope. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: multi-site protection. |
| `confidence` | low/medium/high/verified; local emphasis: role grant. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: role grant. |
| `updated_at` | timestamp of generation or curation; local emphasis: role grant. |

### Validators

- `Scope_Registry` must preserve tenant isolation; if missing, status becomes `needs_review`, not `ready`.
- `Scope_Registry` must preserve store boundary; if missing, status becomes `needs_review`, not `ready`.
- `Scope_Registry` must preserve device slot; if missing, status becomes `needs_review`, not `ready`.
- `Scope_Registry` must preserve role grant; if missing, status becomes `needs_review`, not `ready`.
- `Scope_Registry` must preserve session context; if missing, status becomes `needs_review`, not `ready`.
- `Scope_Registry` must preserve business hierarchy; if missing, status becomes `needs_review`, not `ready`.
- `Scope_Registry` must preserve license scope; if missing, status becomes `needs_review`, not `ready`.
- `Scope_Registry` must preserve multi-site protection; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Scope_Registry.id.example",
  "name": "Scope_Registry.name.example",
  "type": "Scope_Registry.type.example",
  "scope_ref": "Scope_Registry.scope_ref.example",
  "neutral_ref": "Scope_Registry.neutral_ref.example",
  "surface_ref": "Scope_Registry.surface_ref.example",
  "canonical_ref": "Scope_Registry.canonical_ref.example",
  "evidence_ref": "Scope_Registry.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 02. Tenant_Master

**Group:** `scope`
**View ID:** `CAT.scope.Tenant_Master`
**Generated export:** `Tenant_Master.csv`
**Purpose:** tenant comercial, límites, estado, owners, aislamiento.

### Grain

One row represents a governed NDC observation or decision for `Tenant_Master`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: session context. |
| `name` | human-readable name; local emphasis: license scope. |
| `type` | object family/type; local emphasis: license scope. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: role grant. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: business hierarchy. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: business hierarchy. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: multi-site protection. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: license scope. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: session context. |
| `owner` | human/system owner; local emphasis: multi-site protection. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: tenant isolation. |
| `confidence` | low/medium/high/verified; local emphasis: session context. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: session context. |
| `updated_at` | timestamp of generation or curation; local emphasis: session context. |

### Validators

- `Tenant_Master` must preserve tenant isolation; if missing, status becomes `needs_review`, not `ready`.
- `Tenant_Master` must preserve store boundary; if missing, status becomes `needs_review`, not `ready`.
- `Tenant_Master` must preserve device slot; if missing, status becomes `needs_review`, not `ready`.
- `Tenant_Master` must preserve role grant; if missing, status becomes `needs_review`, not `ready`.
- `Tenant_Master` must preserve session context; if missing, status becomes `needs_review`, not `ready`.
- `Tenant_Master` must preserve business hierarchy; if missing, status becomes `needs_review`, not `ready`.
- `Tenant_Master` must preserve license scope; if missing, status becomes `needs_review`, not `ready`.
- `Tenant_Master` must preserve multi-site protection; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Tenant_Master.id.example",
  "name": "Tenant_Master.name.example",
  "type": "Tenant_Master.type.example",
  "scope_ref": "Tenant_Master.scope_ref.example",
  "neutral_ref": "Tenant_Master.neutral_ref.example",
  "surface_ref": "Tenant_Master.surface_ref.example",
  "canonical_ref": "Tenant_Master.canonical_ref.example",
  "evidence_ref": "Tenant_Master.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 03. Business_Site_Map

**Group:** `scope`
**View ID:** `CAT.scope.Business_Site_Map`
**Generated export:** `Business_Site_Map.csv`
**Purpose:** negocios, sucursales, sitios, terminales y jerarquía.

### Grain

One row represents a governed NDC observation or decision for `Business_Site_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: business hierarchy. |
| `name` | human-readable name; local emphasis: multi-site protection. |
| `type` | object family/type; local emphasis: multi-site protection. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: session context. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: license scope. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: license scope. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: tenant isolation. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: multi-site protection. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: business hierarchy. |
| `owner` | human/system owner; local emphasis: tenant isolation. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: store boundary. |
| `confidence` | low/medium/high/verified; local emphasis: business hierarchy. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: business hierarchy. |
| `updated_at` | timestamp of generation or curation; local emphasis: business hierarchy. |

### Validators

- `Business_Site_Map` must preserve tenant isolation; if missing, status becomes `needs_review`, not `ready`.
- `Business_Site_Map` must preserve store boundary; if missing, status becomes `needs_review`, not `ready`.
- `Business_Site_Map` must preserve device slot; if missing, status becomes `needs_review`, not `ready`.
- `Business_Site_Map` must preserve role grant; if missing, status becomes `needs_review`, not `ready`.
- `Business_Site_Map` must preserve session context; if missing, status becomes `needs_review`, not `ready`.
- `Business_Site_Map` must preserve business hierarchy; if missing, status becomes `needs_review`, not `ready`.
- `Business_Site_Map` must preserve license scope; if missing, status becomes `needs_review`, not `ready`.
- `Business_Site_Map` must preserve multi-site protection; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Business_Site_Map.id.example",
  "name": "Business_Site_Map.name.example",
  "type": "Business_Site_Map.type.example",
  "scope_ref": "Business_Site_Map.scope_ref.example",
  "neutral_ref": "Business_Site_Map.neutral_ref.example",
  "surface_ref": "Business_Site_Map.surface_ref.example",
  "canonical_ref": "Business_Site_Map.canonical_ref.example",
  "evidence_ref": "Business_Site_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 04. Device_License_Map

**Group:** `scope`
**View ID:** `CAT.scope.Device_License_Map`
**Generated export:** `Device_License_Map.csv`
**Purpose:** licencias, slots, devices, surfaces autorizadas.

### Grain

One row represents a governed NDC observation or decision for `Device_License_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: license scope. |
| `name` | human-readable name; local emphasis: tenant isolation. |
| `type` | object family/type; local emphasis: tenant isolation. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: business hierarchy. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: multi-site protection. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: multi-site protection. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: store boundary. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: tenant isolation. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: license scope. |
| `owner` | human/system owner; local emphasis: store boundary. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: device slot. |
| `confidence` | low/medium/high/verified; local emphasis: license scope. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: license scope. |
| `updated_at` | timestamp of generation or curation; local emphasis: license scope. |

### Validators

- `Device_License_Map` must preserve tenant isolation; if missing, status becomes `needs_review`, not `ready`.
- `Device_License_Map` must preserve store boundary; if missing, status becomes `needs_review`, not `ready`.
- `Device_License_Map` must preserve device slot; if missing, status becomes `needs_review`, not `ready`.
- `Device_License_Map` must preserve role grant; if missing, status becomes `needs_review`, not `ready`.
- `Device_License_Map` must preserve session context; if missing, status becomes `needs_review`, not `ready`.
- `Device_License_Map` must preserve business hierarchy; if missing, status becomes `needs_review`, not `ready`.
- `Device_License_Map` must preserve license scope; if missing, status becomes `needs_review`, not `ready`.
- `Device_License_Map` must preserve multi-site protection; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Device_License_Map.id.example",
  "name": "Device_License_Map.name.example",
  "type": "Device_License_Map.type.example",
  "scope_ref": "Device_License_Map.scope_ref.example",
  "neutral_ref": "Device_License_Map.neutral_ref.example",
  "surface_ref": "Device_License_Map.surface_ref.example",
  "canonical_ref": "Device_License_Map.canonical_ref.example",
  "evidence_ref": "Device_License_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 05. Role_Module_Map

**Group:** `scope`
**View ID:** `CAT.scope.Role_Module_Map`
**Generated export:** `Role_Module_Map.csv`
**Purpose:** roles, módulos, grants y capabilities visibles.

### Grain

One row represents a governed NDC observation or decision for `Role_Module_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: multi-site protection. |
| `name` | human-readable name; local emphasis: store boundary. |
| `type` | object family/type; local emphasis: store boundary. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: license scope. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: tenant isolation. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: tenant isolation. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: device slot. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: store boundary. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: multi-site protection. |
| `owner` | human/system owner; local emphasis: device slot. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: role grant. |
| `confidence` | low/medium/high/verified; local emphasis: multi-site protection. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: multi-site protection. |
| `updated_at` | timestamp of generation or curation; local emphasis: multi-site protection. |

### Validators

- `Role_Module_Map` must preserve tenant isolation; if missing, status becomes `needs_review`, not `ready`.
- `Role_Module_Map` must preserve store boundary; if missing, status becomes `needs_review`, not `ready`.
- `Role_Module_Map` must preserve device slot; if missing, status becomes `needs_review`, not `ready`.
- `Role_Module_Map` must preserve role grant; if missing, status becomes `needs_review`, not `ready`.
- `Role_Module_Map` must preserve session context; if missing, status becomes `needs_review`, not `ready`.
- `Role_Module_Map` must preserve business hierarchy; if missing, status becomes `needs_review`, not `ready`.
- `Role_Module_Map` must preserve license scope; if missing, status becomes `needs_review`, not `ready`.
- `Role_Module_Map` must preserve multi-site protection; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Role_Module_Map.id.example",
  "name": "Role_Module_Map.name.example",
  "type": "Role_Module_Map.type.example",
  "scope_ref": "Role_Module_Map.scope_ref.example",
  "neutral_ref": "Role_Module_Map.neutral_ref.example",
  "surface_ref": "Role_Module_Map.surface_ref.example",
  "canonical_ref": "Role_Module_Map.canonical_ref.example",
  "evidence_ref": "Role_Module_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 06. Session_Context_Map

**Group:** `scope`
**View ID:** `CAT.scope.Session_Context_Map`
**Generated export:** `Session_Context_Map.csv`
**Purpose:** sesiones de caja, turno, login y device context.

### Grain

One row represents a governed NDC observation or decision for `Session_Context_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: tenant isolation. |
| `name` | human-readable name; local emphasis: device slot. |
| `type` | object family/type; local emphasis: device slot. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: multi-site protection. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: store boundary. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: store boundary. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: role grant. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: device slot. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: tenant isolation. |
| `owner` | human/system owner; local emphasis: role grant. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: session context. |
| `confidence` | low/medium/high/verified; local emphasis: tenant isolation. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: tenant isolation. |
| `updated_at` | timestamp of generation or curation; local emphasis: tenant isolation. |

### Validators

- `Session_Context_Map` must preserve tenant isolation; if missing, status becomes `needs_review`, not `ready`.
- `Session_Context_Map` must preserve store boundary; if missing, status becomes `needs_review`, not `ready`.
- `Session_Context_Map` must preserve device slot; if missing, status becomes `needs_review`, not `ready`.
- `Session_Context_Map` must preserve role grant; if missing, status becomes `needs_review`, not `ready`.
- `Session_Context_Map` must preserve session context; if missing, status becomes `needs_review`, not `ready`.
- `Session_Context_Map` must preserve business hierarchy; if missing, status becomes `needs_review`, not `ready`.
- `Session_Context_Map` must preserve license scope; if missing, status becomes `needs_review`, not `ready`.
- `Session_Context_Map` must preserve multi-site protection; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Session_Context_Map.id.example",
  "name": "Session_Context_Map.name.example",
  "type": "Session_Context_Map.type.example",
  "scope_ref": "Session_Context_Map.scope_ref.example",
  "neutral_ref": "Session_Context_Map.neutral_ref.example",
  "surface_ref": "Session_Context_Map.surface_ref.example",
  "canonical_ref": "Session_Context_Map.canonical_ref.example",
  "evidence_ref": "Session_Context_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 07. Neutral_Object_Registry

**Group:** `neutral`
**View ID:** `CAT.neutral.Neutral_Object_Registry`
**Generated export:** `Neutral_Object_Registry.csv`
**Purpose:** ENT/EVT/ACT/STA/MET/ALT/EVD/CAP/CAN.

### Grain

One row represents a governed NDC observation or decision for `Neutral_Object_Registry`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: canonical vocabulary. |
| `name` | human-readable name; local emphasis: meaning layer. |
| `type` | object family/type; local emphasis: meaning layer. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: semantic identity. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: neutral object. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: neutral object. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: event dependency. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: meaning layer. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: canonical vocabulary. |
| `owner` | human/system owner; local emphasis: event dependency. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: metric lineage. |
| `confidence` | low/medium/high/verified; local emphasis: canonical vocabulary. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: canonical vocabulary. |
| `updated_at` | timestamp of generation or curation; local emphasis: canonical vocabulary. |

### Validators

- `Neutral_Object_Registry` must preserve semantic identity; if missing, status becomes `needs_review`, not `ready`.
- `Neutral_Object_Registry` must preserve canonical vocabulary; if missing, status becomes `needs_review`, not `ready`.
- `Neutral_Object_Registry` must preserve neutral object; if missing, status becomes `needs_review`, not `ready`.
- `Neutral_Object_Registry` must preserve meaning layer; if missing, status becomes `needs_review`, not `ready`.
- `Neutral_Object_Registry` must preserve event dependency; if missing, status becomes `needs_review`, not `ready`.
- `Neutral_Object_Registry` must preserve metric lineage; if missing, status becomes `needs_review`, not `ready`.
- `Neutral_Object_Registry` must preserve capability truth; if missing, status becomes `needs_review`, not `ready`.
- `Neutral_Object_Registry` must preserve projection independence; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Neutral_Object_Registry.id.example",
  "name": "Neutral_Object_Registry.name.example",
  "type": "Neutral_Object_Registry.type.example",
  "scope_ref": "Neutral_Object_Registry.scope_ref.example",
  "neutral_ref": "Neutral_Object_Registry.neutral_ref.example",
  "surface_ref": "Neutral_Object_Registry.surface_ref.example",
  "canonical_ref": "Neutral_Object_Registry.canonical_ref.example",
  "evidence_ref": "Neutral_Object_Registry.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 08. Entity_Master

**Group:** `neutral`
**View ID:** `CAT.neutral.Entity_Master`
**Generated export:** `Entity_Master.csv`
**Purpose:** sale, sale_line, payment, item, inventory_position, cash_session.

### Grain

One row represents a governed NDC observation or decision for `Entity_Master`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: neutral object. |
| `name` | human-readable name; local emphasis: event dependency. |
| `type` | object family/type; local emphasis: event dependency. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: canonical vocabulary. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: meaning layer. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: meaning layer. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: metric lineage. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: event dependency. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: neutral object. |
| `owner` | human/system owner; local emphasis: metric lineage. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: capability truth. |
| `confidence` | low/medium/high/verified; local emphasis: neutral object. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: neutral object. |
| `updated_at` | timestamp of generation or curation; local emphasis: neutral object. |

### Validators

- `Entity_Master` must preserve semantic identity; if missing, status becomes `needs_review`, not `ready`.
- `Entity_Master` must preserve canonical vocabulary; if missing, status becomes `needs_review`, not `ready`.
- `Entity_Master` must preserve neutral object; if missing, status becomes `needs_review`, not `ready`.
- `Entity_Master` must preserve meaning layer; if missing, status becomes `needs_review`, not `ready`.
- `Entity_Master` must preserve event dependency; if missing, status becomes `needs_review`, not `ready`.
- `Entity_Master` must preserve metric lineage; if missing, status becomes `needs_review`, not `ready`.
- `Entity_Master` must preserve capability truth; if missing, status becomes `needs_review`, not `ready`.
- `Entity_Master` must preserve projection independence; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Entity_Master.id.example",
  "name": "Entity_Master.name.example",
  "type": "Entity_Master.type.example",
  "scope_ref": "Entity_Master.scope_ref.example",
  "neutral_ref": "Entity_Master.neutral_ref.example",
  "surface_ref": "Entity_Master.surface_ref.example",
  "canonical_ref": "Entity_Master.canonical_ref.example",
  "evidence_ref": "Entity_Master.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 09. Event_Provenance_Log

**Group:** `event`
**View ID:** `CAT.event.Event_Provenance_Log`
**Generated export:** `Event_Provenance_Log.csv`
**Purpose:** eventos con origen, actor, device, surface, timestamp y evidence.

### Grain

One row represents a governed NDC observation or decision for `Event_Provenance_Log`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: source device. |
| `name` | human-readable name; local emphasis: timestamp integrity. |
| `type` | object family/type; local emphasis: timestamp integrity. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: state transition. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: audit trail. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: audit trail. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: idempotency. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: timestamp integrity. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: source device. |
| `owner` | human/system owner; local emphasis: idempotency. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: replay safety. |
| `confidence` | low/medium/high/verified; local emphasis: source device. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: source device. |
| `updated_at` | timestamp of generation or curation; local emphasis: source device. |

### Validators

- `Event_Provenance_Log` must preserve event envelope; if missing, status becomes `needs_review`, not `ready`.
- `Event_Provenance_Log` must preserve action emission; if missing, status becomes `needs_review`, not `ready`.
- `Event_Provenance_Log` must preserve state transition; if missing, status becomes `needs_review`, not `ready`.
- `Event_Provenance_Log` must preserve source device; if missing, status becomes `needs_review`, not `ready`.
- `Event_Provenance_Log` must preserve audit trail; if missing, status becomes `needs_review`, not `ready`.
- `Event_Provenance_Log` must preserve timestamp integrity; if missing, status becomes `needs_review`, not `ready`.
- `Event_Provenance_Log` must preserve idempotency; if missing, status becomes `needs_review`, not `ready`.
- `Event_Provenance_Log` must preserve replay safety; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Event_Provenance_Log.id.example",
  "name": "Event_Provenance_Log.name.example",
  "type": "Event_Provenance_Log.type.example",
  "scope_ref": "Event_Provenance_Log.scope_ref.example",
  "neutral_ref": "Event_Provenance_Log.neutral_ref.example",
  "surface_ref": "Event_Provenance_Log.surface_ref.example",
  "canonical_ref": "Event_Provenance_Log.canonical_ref.example",
  "evidence_ref": "Event_Provenance_Log.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 10. Action_Event_Map

**Group:** `event`
**View ID:** `CAT.event.Action_Event_Map`
**Generated export:** `Action_Event_Map.csv`
**Purpose:** acciones que emiten eventos y escriben entidades.

### Grain

One row represents a governed NDC observation or decision for `Action_Event_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: audit trail. |
| `name` | human-readable name; local emphasis: idempotency. |
| `type` | object family/type; local emphasis: idempotency. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: source device. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: timestamp integrity. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: timestamp integrity. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: replay safety. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: idempotency. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: audit trail. |
| `owner` | human/system owner; local emphasis: replay safety. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: event envelope. |
| `confidence` | low/medium/high/verified; local emphasis: audit trail. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: audit trail. |
| `updated_at` | timestamp of generation or curation; local emphasis: audit trail. |

### Validators

- `Action_Event_Map` must preserve event envelope; if missing, status becomes `needs_review`, not `ready`.
- `Action_Event_Map` must preserve action emission; if missing, status becomes `needs_review`, not `ready`.
- `Action_Event_Map` must preserve state transition; if missing, status becomes `needs_review`, not `ready`.
- `Action_Event_Map` must preserve source device; if missing, status becomes `needs_review`, not `ready`.
- `Action_Event_Map` must preserve audit trail; if missing, status becomes `needs_review`, not `ready`.
- `Action_Event_Map` must preserve timestamp integrity; if missing, status becomes `needs_review`, not `ready`.
- `Action_Event_Map` must preserve idempotency; if missing, status becomes `needs_review`, not `ready`.
- `Action_Event_Map` must preserve replay safety; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Action_Event_Map.id.example",
  "name": "Action_Event_Map.name.example",
  "type": "Action_Event_Map.type.example",
  "scope_ref": "Action_Event_Map.scope_ref.example",
  "neutral_ref": "Action_Event_Map.neutral_ref.example",
  "surface_ref": "Action_Event_Map.surface_ref.example",
  "canonical_ref": "Action_Event_Map.canonical_ref.example",
  "evidence_ref": "Action_Event_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 11. State_Transition_Map

**Group:** `event`
**View ID:** `CAT.event.State_Transition_Map`
**Generated export:** `State_Transition_Map.csv`
**Purpose:** transiciones de estado y reglas.

### Grain

One row represents a governed NDC observation or decision for `State_Transition_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: timestamp integrity. |
| `name` | human-readable name; local emphasis: replay safety. |
| `type` | object family/type; local emphasis: replay safety. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: audit trail. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: idempotency. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: idempotency. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: event envelope. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: replay safety. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: timestamp integrity. |
| `owner` | human/system owner; local emphasis: event envelope. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: action emission. |
| `confidence` | low/medium/high/verified; local emphasis: timestamp integrity. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: timestamp integrity. |
| `updated_at` | timestamp of generation or curation; local emphasis: timestamp integrity. |

### Validators

- `State_Transition_Map` must preserve event envelope; if missing, status becomes `needs_review`, not `ready`.
- `State_Transition_Map` must preserve action emission; if missing, status becomes `needs_review`, not `ready`.
- `State_Transition_Map` must preserve state transition; if missing, status becomes `needs_review`, not `ready`.
- `State_Transition_Map` must preserve source device; if missing, status becomes `needs_review`, not `ready`.
- `State_Transition_Map` must preserve audit trail; if missing, status becomes `needs_review`, not `ready`.
- `State_Transition_Map` must preserve timestamp integrity; if missing, status becomes `needs_review`, not `ready`.
- `State_Transition_Map` must preserve idempotency; if missing, status becomes `needs_review`, not `ready`.
- `State_Transition_Map` must preserve replay safety; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "State_Transition_Map.id.example",
  "name": "State_Transition_Map.name.example",
  "type": "State_Transition_Map.type.example",
  "scope_ref": "State_Transition_Map.scope_ref.example",
  "neutral_ref": "State_Transition_Map.neutral_ref.example",
  "surface_ref": "State_Transition_Map.surface_ref.example",
  "canonical_ref": "State_Transition_Map.canonical_ref.example",
  "evidence_ref": "State_Transition_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 12. Sync_Outbox_Map

**Group:** `lineage`
**View ID:** `CAT.lineage.Sync_Outbox_Map`
**Generated export:** `Sync_Outbox_Map.csv`
**Purpose:** outbox, retry, ack, rejection, duplicate.

### Grain

One row represents a governed NDC observation or decision for `Sync_Outbox_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: provenance agent. |
| `name` | human-readable name; local emphasis: upstream source. |
| `type` | object family/type; local emphasis: upstream source. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: metric derivation. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: impact radius. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: impact radius. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: downstream consumer. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: upstream source. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: provenance agent. |
| `owner` | human/system owner; local emphasis: downstream consumer. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: outbox delivery. |
| `confidence` | low/medium/high/verified; local emphasis: provenance agent. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: provenance agent. |
| `updated_at` | timestamp of generation or curation; local emphasis: provenance agent. |

### Validators

- `Sync_Outbox_Map` must preserve upstream source; if missing, status becomes `needs_review`, not `ready`.
- `Sync_Outbox_Map` must preserve downstream consumer; if missing, status becomes `needs_review`, not `ready`.
- `Sync_Outbox_Map` must preserve outbox delivery; if missing, status becomes `needs_review`, not `ready`.
- `Sync_Outbox_Map` must preserve canonical reducer; if missing, status becomes `needs_review`, not `ready`.
- `Sync_Outbox_Map` must preserve dataset dependency; if missing, status becomes `needs_review`, not `ready`.
- `Sync_Outbox_Map` must preserve metric derivation; if missing, status becomes `needs_review`, not `ready`.
- `Sync_Outbox_Map` must preserve provenance agent; if missing, status becomes `needs_review`, not `ready`.
- `Sync_Outbox_Map` must preserve impact radius; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Sync_Outbox_Map.id.example",
  "name": "Sync_Outbox_Map.name.example",
  "type": "Sync_Outbox_Map.type.example",
  "scope_ref": "Sync_Outbox_Map.scope_ref.example",
  "neutral_ref": "Sync_Outbox_Map.neutral_ref.example",
  "surface_ref": "Sync_Outbox_Map.surface_ref.example",
  "canonical_ref": "Sync_Outbox_Map.canonical_ref.example",
  "evidence_ref": "Sync_Outbox_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 13. Canonical_Projection_Map

**Group:** `canonical`
**View ID:** `CAT.canonical.Canonical_Projection_Map`
**Generated export:** `Canonical_Projection_Map.csv`
**Purpose:** proyecciones canónicas y reglas.

### Grain

One row represents a governed NDC observation or decision for `Canonical_Projection_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: reconciliation path. |
| `name` | human-readable name; local emphasis: rejection rule. |
| `type` | object family/type; local emphasis: rejection rule. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: projection contract. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: acceptance rule. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: acceptance rule. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: duplicate policy. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: rejection rule. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: reconciliation path. |
| `owner` | human/system owner; local emphasis: duplicate policy. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: freshness window. |
| `confidence` | low/medium/high/verified; local emphasis: reconciliation path. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: reconciliation path. |
| `updated_at` | timestamp of generation or curation; local emphasis: reconciliation path. |

### Validators

- `Canonical_Projection_Map` must preserve acceptance rule; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Projection_Map` must preserve rejection rule; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Projection_Map` must preserve duplicate policy; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Projection_Map` must preserve freshness window; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Projection_Map` must preserve dispute state; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Projection_Map` must preserve canonical status; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Projection_Map` must preserve projection contract; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Projection_Map` must preserve reconciliation path; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Canonical_Projection_Map.id.example",
  "name": "Canonical_Projection_Map.name.example",
  "type": "Canonical_Projection_Map.type.example",
  "scope_ref": "Canonical_Projection_Map.scope_ref.example",
  "neutral_ref": "Canonical_Projection_Map.neutral_ref.example",
  "surface_ref": "Canonical_Projection_Map.surface_ref.example",
  "canonical_ref": "Canonical_Projection_Map.canonical_ref.example",
  "evidence_ref": "Canonical_Projection_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 14. Canonical_Status_Map

**Group:** `canonical`
**View ID:** `CAT.canonical.Canonical_Status_Map`
**Generated export:** `Canonical_Status_Map.csv`
**Purpose:** accepted, pending, duplicate, rejected, stale, disputed.

### Grain

One row represents a governed NDC observation or decision for `Canonical_Status_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: acceptance rule. |
| `name` | human-readable name; local emphasis: duplicate policy. |
| `type` | object family/type; local emphasis: duplicate policy. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: reconciliation path. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: rejection rule. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: rejection rule. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: freshness window. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: duplicate policy. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: acceptance rule. |
| `owner` | human/system owner; local emphasis: freshness window. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: dispute state. |
| `confidence` | low/medium/high/verified; local emphasis: acceptance rule. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: acceptance rule. |
| `updated_at` | timestamp of generation or curation; local emphasis: acceptance rule. |

### Validators

- `Canonical_Status_Map` must preserve acceptance rule; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Status_Map` must preserve rejection rule; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Status_Map` must preserve duplicate policy; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Status_Map` must preserve freshness window; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Status_Map` must preserve dispute state; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Status_Map` must preserve canonical status; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Status_Map` must preserve projection contract; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Status_Map` must preserve reconciliation path; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Canonical_Status_Map.id.example",
  "name": "Canonical_Status_Map.name.example",
  "type": "Canonical_Status_Map.type.example",
  "scope_ref": "Canonical_Status_Map.scope_ref.example",
  "neutral_ref": "Canonical_Status_Map.neutral_ref.example",
  "surface_ref": "Canonical_Status_Map.surface_ref.example",
  "canonical_ref": "Canonical_Status_Map.canonical_ref.example",
  "evidence_ref": "Canonical_Status_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 15. Data_Lineage_Map

**Group:** `lineage`
**View ID:** `CAT.lineage.Data_Lineage_Map`
**Generated export:** `Data_Lineage_Map.csv`
**Purpose:** linaje de event/source a canonical, metric, surface y widget.

### Grain

One row represents a governed NDC observation or decision for `Data_Lineage_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: downstream consumer. |
| `name` | human-readable name; local emphasis: canonical reducer. |
| `type` | object family/type; local emphasis: canonical reducer. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: upstream source. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: outbox delivery. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: outbox delivery. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: dataset dependency. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: canonical reducer. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: downstream consumer. |
| `owner` | human/system owner; local emphasis: dataset dependency. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: metric derivation. |
| `confidence` | low/medium/high/verified; local emphasis: downstream consumer. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: downstream consumer. |
| `updated_at` | timestamp of generation or curation; local emphasis: downstream consumer. |

### Validators

- `Data_Lineage_Map` must preserve upstream source; if missing, status becomes `needs_review`, not `ready`.
- `Data_Lineage_Map` must preserve downstream consumer; if missing, status becomes `needs_review`, not `ready`.
- `Data_Lineage_Map` must preserve outbox delivery; if missing, status becomes `needs_review`, not `ready`.
- `Data_Lineage_Map` must preserve canonical reducer; if missing, status becomes `needs_review`, not `ready`.
- `Data_Lineage_Map` must preserve dataset dependency; if missing, status becomes `needs_review`, not `ready`.
- `Data_Lineage_Map` must preserve metric derivation; if missing, status becomes `needs_review`, not `ready`.
- `Data_Lineage_Map` must preserve provenance agent; if missing, status becomes `needs_review`, not `ready`.
- `Data_Lineage_Map` must preserve impact radius; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Data_Lineage_Map.id.example",
  "name": "Data_Lineage_Map.name.example",
  "type": "Data_Lineage_Map.type.example",
  "scope_ref": "Data_Lineage_Map.scope_ref.example",
  "neutral_ref": "Data_Lineage_Map.neutral_ref.example",
  "surface_ref": "Data_Lineage_Map.surface_ref.example",
  "canonical_ref": "Data_Lineage_Map.canonical_ref.example",
  "evidence_ref": "Data_Lineage_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 16. Provenance_Agent_Map

**Group:** `lineage`
**View ID:** `CAT.lineage.Provenance_Agent_Map`
**Generated export:** `Provenance_Agent_Map.csv`
**Purpose:** agentes, devices, tools y runtimes responsables.

### Grain

One row represents a governed NDC observation or decision for `Provenance_Agent_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: outbox delivery. |
| `name` | human-readable name; local emphasis: dataset dependency. |
| `type` | object family/type; local emphasis: dataset dependency. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: downstream consumer. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: canonical reducer. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: canonical reducer. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: metric derivation. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: dataset dependency. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: outbox delivery. |
| `owner` | human/system owner; local emphasis: metric derivation. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: provenance agent. |
| `confidence` | low/medium/high/verified; local emphasis: outbox delivery. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: outbox delivery. |
| `updated_at` | timestamp of generation or curation; local emphasis: outbox delivery. |

### Validators

- `Provenance_Agent_Map` must preserve upstream source; if missing, status becomes `needs_review`, not `ready`.
- `Provenance_Agent_Map` must preserve downstream consumer; if missing, status becomes `needs_review`, not `ready`.
- `Provenance_Agent_Map` must preserve outbox delivery; if missing, status becomes `needs_review`, not `ready`.
- `Provenance_Agent_Map` must preserve canonical reducer; if missing, status becomes `needs_review`, not `ready`.
- `Provenance_Agent_Map` must preserve dataset dependency; if missing, status becomes `needs_review`, not `ready`.
- `Provenance_Agent_Map` must preserve metric derivation; if missing, status becomes `needs_review`, not `ready`.
- `Provenance_Agent_Map` must preserve provenance agent; if missing, status becomes `needs_review`, not `ready`.
- `Provenance_Agent_Map` must preserve impact radius; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Provenance_Agent_Map.id.example",
  "name": "Provenance_Agent_Map.name.example",
  "type": "Provenance_Agent_Map.type.example",
  "scope_ref": "Provenance_Agent_Map.scope_ref.example",
  "neutral_ref": "Provenance_Agent_Map.neutral_ref.example",
  "surface_ref": "Provenance_Agent_Map.surface_ref.example",
  "canonical_ref": "Provenance_Agent_Map.canonical_ref.example",
  "evidence_ref": "Provenance_Agent_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 17. Surface_Projection_Map

**Group:** `projection`
**View ID:** `CAT.projection.Surface_Projection_Map`
**Generated export:** `Surface_Projection_Map.csv`
**Purpose:** superficies que muestran/escriben/auditan neutrales.

### Grain

One row represents a governed NDC observation or decision for `Surface_Projection_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: role visibility. |
| `name` | human-readable name; local emphasis: client-facing limit. |
| `type` | object family/type; local emphasis: client-facing limit. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: read/write mode. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: surface owner. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: surface owner. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: internal boundary. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: client-facing limit. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: role visibility. |
| `owner` | human/system owner; local emphasis: internal boundary. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: projection filter. |
| `confidence` | low/medium/high/verified; local emphasis: role visibility. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: role visibility. |
| `updated_at` | timestamp of generation or curation; local emphasis: role visibility. |

### Validators

- `Surface_Projection_Map` must preserve surface grant; if missing, status becomes `needs_review`, not `ready`.
- `Surface_Projection_Map` must preserve runtime boundary; if missing, status becomes `needs_review`, not `ready`.
- `Surface_Projection_Map` must preserve read/write mode; if missing, status becomes `needs_review`, not `ready`.
- `Surface_Projection_Map` must preserve role visibility; if missing, status becomes `needs_review`, not `ready`.
- `Surface_Projection_Map` must preserve surface owner; if missing, status becomes `needs_review`, not `ready`.
- `Surface_Projection_Map` must preserve client-facing limit; if missing, status becomes `needs_review`, not `ready`.
- `Surface_Projection_Map` must preserve internal boundary; if missing, status becomes `needs_review`, not `ready`.
- `Surface_Projection_Map` must preserve projection filter; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Surface_Projection_Map.id.example",
  "name": "Surface_Projection_Map.name.example",
  "type": "Surface_Projection_Map.type.example",
  "scope_ref": "Surface_Projection_Map.scope_ref.example",
  "neutral_ref": "Surface_Projection_Map.neutral_ref.example",
  "surface_ref": "Surface_Projection_Map.surface_ref.example",
  "canonical_ref": "Surface_Projection_Map.canonical_ref.example",
  "evidence_ref": "Surface_Projection_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 18. Runtime_Surface_Catalog

**Group:** `projection`
**View ID:** `CAT.projection.Runtime_Surface_Catalog`
**Generated export:** `Runtime_Surface_Catalog.csv`
**Purpose:** runtimes 3000-3160, visibilidad y boundaries.

### Grain

One row represents a governed NDC observation or decision for `Runtime_Surface_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: surface owner. |
| `name` | human-readable name; local emphasis: internal boundary. |
| `type` | object family/type; local emphasis: internal boundary. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: role visibility. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: client-facing limit. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: client-facing limit. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: projection filter. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: internal boundary. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: surface owner. |
| `owner` | human/system owner; local emphasis: projection filter. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: surface grant. |
| `confidence` | low/medium/high/verified; local emphasis: surface owner. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: surface owner. |
| `updated_at` | timestamp of generation or curation; local emphasis: surface owner. |

### Validators

- `Runtime_Surface_Catalog` must preserve surface grant; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Surface_Catalog` must preserve runtime boundary; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Surface_Catalog` must preserve read/write mode; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Surface_Catalog` must preserve role visibility; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Surface_Catalog` must preserve surface owner; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Surface_Catalog` must preserve client-facing limit; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Surface_Catalog` must preserve internal boundary; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Surface_Catalog` must preserve projection filter; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Runtime_Surface_Catalog.id.example",
  "name": "Runtime_Surface_Catalog.name.example",
  "type": "Runtime_Surface_Catalog.type.example",
  "scope_ref": "Runtime_Surface_Catalog.scope_ref.example",
  "neutral_ref": "Runtime_Surface_Catalog.neutral_ref.example",
  "surface_ref": "Runtime_Surface_Catalog.surface_ref.example",
  "canonical_ref": "Runtime_Surface_Catalog.canonical_ref.example",
  "evidence_ref": "Runtime_Surface_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 19. UI_Component_Atlas

**Group:** `ui`
**View ID:** `CAT.ui.UI_Component_Atlas`
**Generated export:** `UI_Component_Atlas.csv`
**Purpose:** surface, zone, panel, widget, table, form, chart, action.

### Grain

One row represents a governed NDC observation or decision for `UI_Component_Atlas`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: drilldown. |
| `name` | human-readable name; local emphasis: action affordance. |
| `type` | object family/type; local emphasis: action affordance. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: error state. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: visual evidence. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: visual evidence. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: panel role. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: action affordance. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: drilldown. |
| `owner` | human/system owner; local emphasis: panel role. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: widget binding. |
| `confidence` | low/medium/high/verified; local emphasis: drilldown. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: drilldown. |
| `updated_at` | timestamp of generation or curation; local emphasis: drilldown. |

### Validators

- `UI_Component_Atlas` must preserve panel role; if missing, status becomes `needs_review`, not `ready`.
- `UI_Component_Atlas` must preserve widget binding; if missing, status becomes `needs_review`, not `ready`.
- `UI_Component_Atlas` must preserve interaction contract; if missing, status becomes `needs_review`, not `ready`.
- `UI_Component_Atlas` must preserve empty state; if missing, status becomes `needs_review`, not `ready`.
- `UI_Component_Atlas` must preserve error state; if missing, status becomes `needs_review`, not `ready`.
- `UI_Component_Atlas` must preserve drilldown; if missing, status becomes `needs_review`, not `ready`.
- `UI_Component_Atlas` must preserve visual evidence; if missing, status becomes `needs_review`, not `ready`.
- `UI_Component_Atlas` must preserve action affordance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "UI_Component_Atlas.id.example",
  "name": "UI_Component_Atlas.name.example",
  "type": "UI_Component_Atlas.type.example",
  "scope_ref": "UI_Component_Atlas.scope_ref.example",
  "neutral_ref": "UI_Component_Atlas.neutral_ref.example",
  "surface_ref": "UI_Component_Atlas.surface_ref.example",
  "canonical_ref": "UI_Component_Atlas.canonical_ref.example",
  "evidence_ref": "UI_Component_Atlas.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 20. Panel_Insight_Catalog

**Group:** `ui`
**View ID:** `CAT.ui.Panel_Insight_Catalog`
**Generated export:** `Panel_Insight_Catalog.csv`
**Purpose:** paneles de KPI, acción, auditoría, alerta, evidencia y licensing.

### Grain

One row represents a governed NDC observation or decision for `Panel_Insight_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: visual evidence. |
| `name` | human-readable name; local emphasis: panel role. |
| `type` | object family/type; local emphasis: panel role. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: drilldown. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: action affordance. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: action affordance. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: widget binding. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: panel role. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: visual evidence. |
| `owner` | human/system owner; local emphasis: widget binding. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: interaction contract. |
| `confidence` | low/medium/high/verified; local emphasis: visual evidence. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: visual evidence. |
| `updated_at` | timestamp of generation or curation; local emphasis: visual evidence. |

### Validators

- `Panel_Insight_Catalog` must preserve panel role; if missing, status becomes `needs_review`, not `ready`.
- `Panel_Insight_Catalog` must preserve widget binding; if missing, status becomes `needs_review`, not `ready`.
- `Panel_Insight_Catalog` must preserve interaction contract; if missing, status becomes `needs_review`, not `ready`.
- `Panel_Insight_Catalog` must preserve empty state; if missing, status becomes `needs_review`, not `ready`.
- `Panel_Insight_Catalog` must preserve error state; if missing, status becomes `needs_review`, not `ready`.
- `Panel_Insight_Catalog` must preserve drilldown; if missing, status becomes `needs_review`, not `ready`.
- `Panel_Insight_Catalog` must preserve visual evidence; if missing, status becomes `needs_review`, not `ready`.
- `Panel_Insight_Catalog` must preserve action affordance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Panel_Insight_Catalog.id.example",
  "name": "Panel_Insight_Catalog.name.example",
  "type": "Panel_Insight_Catalog.type.example",
  "scope_ref": "Panel_Insight_Catalog.scope_ref.example",
  "neutral_ref": "Panel_Insight_Catalog.neutral_ref.example",
  "surface_ref": "Panel_Insight_Catalog.surface_ref.example",
  "canonical_ref": "Panel_Insight_Catalog.canonical_ref.example",
  "evidence_ref": "Panel_Insight_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 21. Widget_Interaction_Catalog

**Group:** `ui`
**View ID:** `CAT.ui.Widget_Interaction_Catalog`
**Generated export:** `Widget_Interaction_Catalog.csv`
**Purpose:** click, filter, submit, approve, export, drilldown, warning.

### Grain

One row represents a governed NDC observation or decision for `Widget_Interaction_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: action affordance. |
| `name` | human-readable name; local emphasis: widget binding. |
| `type` | object family/type; local emphasis: widget binding. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: visual evidence. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: panel role. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: panel role. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: interaction contract. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: widget binding. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: action affordance. |
| `owner` | human/system owner; local emphasis: interaction contract. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: empty state. |
| `confidence` | low/medium/high/verified; local emphasis: action affordance. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: action affordance. |
| `updated_at` | timestamp of generation or curation; local emphasis: action affordance. |

### Validators

- `Widget_Interaction_Catalog` must preserve panel role; if missing, status becomes `needs_review`, not `ready`.
- `Widget_Interaction_Catalog` must preserve widget binding; if missing, status becomes `needs_review`, not `ready`.
- `Widget_Interaction_Catalog` must preserve interaction contract; if missing, status becomes `needs_review`, not `ready`.
- `Widget_Interaction_Catalog` must preserve empty state; if missing, status becomes `needs_review`, not `ready`.
- `Widget_Interaction_Catalog` must preserve error state; if missing, status becomes `needs_review`, not `ready`.
- `Widget_Interaction_Catalog` must preserve drilldown; if missing, status becomes `needs_review`, not `ready`.
- `Widget_Interaction_Catalog` must preserve visual evidence; if missing, status becomes `needs_review`, not `ready`.
- `Widget_Interaction_Catalog` must preserve action affordance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Widget_Interaction_Catalog.id.example",
  "name": "Widget_Interaction_Catalog.name.example",
  "type": "Widget_Interaction_Catalog.type.example",
  "scope_ref": "Widget_Interaction_Catalog.scope_ref.example",
  "neutral_ref": "Widget_Interaction_Catalog.neutral_ref.example",
  "surface_ref": "Widget_Interaction_Catalog.surface_ref.example",
  "canonical_ref": "Widget_Interaction_Catalog.canonical_ref.example",
  "evidence_ref": "Widget_Interaction_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 22. Table_View_Catalog

**Group:** `ui`
**View ID:** `CAT.ui.Table_View_Catalog`
**Generated export:** `Table_View_Catalog.csv`
**Purpose:** tablas, columnas, filtros, empty/error states.

### Grain

One row represents a governed NDC observation or decision for `Table_View_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: panel role. |
| `name` | human-readable name; local emphasis: interaction contract. |
| `type` | object family/type; local emphasis: interaction contract. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: action affordance. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: widget binding. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: widget binding. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: empty state. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: interaction contract. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: panel role. |
| `owner` | human/system owner; local emphasis: empty state. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: error state. |
| `confidence` | low/medium/high/verified; local emphasis: panel role. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: panel role. |
| `updated_at` | timestamp of generation or curation; local emphasis: panel role. |

### Validators

- `Table_View_Catalog` must preserve panel role; if missing, status becomes `needs_review`, not `ready`.
- `Table_View_Catalog` must preserve widget binding; if missing, status becomes `needs_review`, not `ready`.
- `Table_View_Catalog` must preserve interaction contract; if missing, status becomes `needs_review`, not `ready`.
- `Table_View_Catalog` must preserve empty state; if missing, status becomes `needs_review`, not `ready`.
- `Table_View_Catalog` must preserve error state; if missing, status becomes `needs_review`, not `ready`.
- `Table_View_Catalog` must preserve drilldown; if missing, status becomes `needs_review`, not `ready`.
- `Table_View_Catalog` must preserve visual evidence; if missing, status becomes `needs_review`, not `ready`.
- `Table_View_Catalog` must preserve action affordance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Table_View_Catalog.id.example",
  "name": "Table_View_Catalog.name.example",
  "type": "Table_View_Catalog.type.example",
  "scope_ref": "Table_View_Catalog.scope_ref.example",
  "neutral_ref": "Table_View_Catalog.neutral_ref.example",
  "surface_ref": "Table_View_Catalog.surface_ref.example",
  "canonical_ref": "Table_View_Catalog.canonical_ref.example",
  "evidence_ref": "Table_View_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 23. Form_Field_Catalog

**Group:** `ui`
**View ID:** `CAT.ui.Form_Field_Catalog`
**Generated export:** `Form_Field_Catalog.csv`
**Purpose:** formularios, campos, validaciones, entidades impactadas.

### Grain

One row represents a governed NDC observation or decision for `Form_Field_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: widget binding. |
| `name` | human-readable name; local emphasis: empty state. |
| `type` | object family/type; local emphasis: empty state. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: panel role. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: interaction contract. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: interaction contract. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: error state. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: empty state. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: widget binding. |
| `owner` | human/system owner; local emphasis: error state. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: drilldown. |
| `confidence` | low/medium/high/verified; local emphasis: widget binding. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: widget binding. |
| `updated_at` | timestamp of generation or curation; local emphasis: widget binding. |

### Validators

- `Form_Field_Catalog` must preserve panel role; if missing, status becomes `needs_review`, not `ready`.
- `Form_Field_Catalog` must preserve widget binding; if missing, status becomes `needs_review`, not `ready`.
- `Form_Field_Catalog` must preserve interaction contract; if missing, status becomes `needs_review`, not `ready`.
- `Form_Field_Catalog` must preserve empty state; if missing, status becomes `needs_review`, not `ready`.
- `Form_Field_Catalog` must preserve error state; if missing, status becomes `needs_review`, not `ready`.
- `Form_Field_Catalog` must preserve drilldown; if missing, status becomes `needs_review`, not `ready`.
- `Form_Field_Catalog` must preserve visual evidence; if missing, status becomes `needs_review`, not `ready`.
- `Form_Field_Catalog` must preserve action affordance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Form_Field_Catalog.id.example",
  "name": "Form_Field_Catalog.name.example",
  "type": "Form_Field_Catalog.type.example",
  "scope_ref": "Form_Field_Catalog.scope_ref.example",
  "neutral_ref": "Form_Field_Catalog.neutral_ref.example",
  "surface_ref": "Form_Field_Catalog.surface_ref.example",
  "canonical_ref": "Form_Field_Catalog.canonical_ref.example",
  "evidence_ref": "Form_Field_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 24. Button_Action_Catalog

**Group:** `ui`
**View ID:** `CAT.ui.Button_Action_Catalog`
**Generated export:** `Button_Action_Catalog.csv`
**Purpose:** botones ligados a ACT/EVT, permissions y audit.

### Grain

One row represents a governed NDC observation or decision for `Button_Action_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: interaction contract. |
| `name` | human-readable name; local emphasis: error state. |
| `type` | object family/type; local emphasis: error state. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: widget binding. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: empty state. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: empty state. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: drilldown. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: error state. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: interaction contract. |
| `owner` | human/system owner; local emphasis: drilldown. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: visual evidence. |
| `confidence` | low/medium/high/verified; local emphasis: interaction contract. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: interaction contract. |
| `updated_at` | timestamp of generation or curation; local emphasis: interaction contract. |

### Validators

- `Button_Action_Catalog` must preserve panel role; if missing, status becomes `needs_review`, not `ready`.
- `Button_Action_Catalog` must preserve widget binding; if missing, status becomes `needs_review`, not `ready`.
- `Button_Action_Catalog` must preserve interaction contract; if missing, status becomes `needs_review`, not `ready`.
- `Button_Action_Catalog` must preserve empty state; if missing, status becomes `needs_review`, not `ready`.
- `Button_Action_Catalog` must preserve error state; if missing, status becomes `needs_review`, not `ready`.
- `Button_Action_Catalog` must preserve drilldown; if missing, status becomes `needs_review`, not `ready`.
- `Button_Action_Catalog` must preserve visual evidence; if missing, status becomes `needs_review`, not `ready`.
- `Button_Action_Catalog` must preserve action affordance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Button_Action_Catalog.id.example",
  "name": "Button_Action_Catalog.name.example",
  "type": "Button_Action_Catalog.type.example",
  "scope_ref": "Button_Action_Catalog.scope_ref.example",
  "neutral_ref": "Button_Action_Catalog.neutral_ref.example",
  "surface_ref": "Button_Action_Catalog.surface_ref.example",
  "canonical_ref": "Button_Action_Catalog.canonical_ref.example",
  "evidence_ref": "Button_Action_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 25. Chart_Metric_Catalog

**Group:** `chart`
**View ID:** `CAT.chart.Chart_Metric_Catalog`
**Generated export:** `Chart_Metric_Catalog.csv`
**Purpose:** charts, fórmulas, datasets, destino, rol, licencia.

### Grain

One row represents a governed NDC observation or decision for `Chart_Metric_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: analytics value. |
| `name` | human-readable name; local emphasis: demo evidence. |
| `type` | object family/type; local emphasis: demo evidence. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: chart grammar. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: pricing class. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: pricing class. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: data freshness. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: demo evidence. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: analytics value. |
| `owner` | human/system owner; local emphasis: data freshness. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: success criterion. |
| `confidence` | low/medium/high/verified; local emphasis: analytics value. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: analytics value. |
| `updated_at` | timestamp of generation or curation; local emphasis: analytics value. |

### Validators

- `Chart_Metric_Catalog` must preserve metric formula; if missing, status becomes `needs_review`, not `ready`.
- `Chart_Metric_Catalog` must preserve dataset contract; if missing, status becomes `needs_review`, not `ready`.
- `Chart_Metric_Catalog` must preserve chart grammar; if missing, status becomes `needs_review`, not `ready`.
- `Chart_Metric_Catalog` must preserve analytics value; if missing, status becomes `needs_review`, not `ready`.
- `Chart_Metric_Catalog` must preserve pricing class; if missing, status becomes `needs_review`, not `ready`.
- `Chart_Metric_Catalog` must preserve demo evidence; if missing, status becomes `needs_review`, not `ready`.
- `Chart_Metric_Catalog` must preserve data freshness; if missing, status becomes `needs_review`, not `ready`.
- `Chart_Metric_Catalog` must preserve success criterion; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Chart_Metric_Catalog.id.example",
  "name": "Chart_Metric_Catalog.name.example",
  "type": "Chart_Metric_Catalog.type.example",
  "scope_ref": "Chart_Metric_Catalog.scope_ref.example",
  "neutral_ref": "Chart_Metric_Catalog.neutral_ref.example",
  "surface_ref": "Chart_Metric_Catalog.surface_ref.example",
  "canonical_ref": "Chart_Metric_Catalog.canonical_ref.example",
  "evidence_ref": "Chart_Metric_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 26. ChartLab_Opportunity_Catalog

**Group:** `chart`
**View ID:** `CAT.chart.ChartLab_Opportunity_Catalog`
**Generated export:** `ChartLab_Opportunity_Catalog.csv`
**Purpose:** oportunidades analytics, valor, destino, pricing.

### Grain

One row represents a governed NDC observation or decision for `ChartLab_Opportunity_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: pricing class. |
| `name` | human-readable name; local emphasis: data freshness. |
| `type` | object family/type; local emphasis: data freshness. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: analytics value. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: demo evidence. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: demo evidence. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: success criterion. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: data freshness. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: pricing class. |
| `owner` | human/system owner; local emphasis: success criterion. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: metric formula. |
| `confidence` | low/medium/high/verified; local emphasis: pricing class. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: pricing class. |
| `updated_at` | timestamp of generation or curation; local emphasis: pricing class. |

### Validators

- `ChartLab_Opportunity_Catalog` must preserve metric formula; if missing, status becomes `needs_review`, not `ready`.
- `ChartLab_Opportunity_Catalog` must preserve dataset contract; if missing, status becomes `needs_review`, not `ready`.
- `ChartLab_Opportunity_Catalog` must preserve chart grammar; if missing, status becomes `needs_review`, not `ready`.
- `ChartLab_Opportunity_Catalog` must preserve analytics value; if missing, status becomes `needs_review`, not `ready`.
- `ChartLab_Opportunity_Catalog` must preserve pricing class; if missing, status becomes `needs_review`, not `ready`.
- `ChartLab_Opportunity_Catalog` must preserve demo evidence; if missing, status becomes `needs_review`, not `ready`.
- `ChartLab_Opportunity_Catalog` must preserve data freshness; if missing, status becomes `needs_review`, not `ready`.
- `ChartLab_Opportunity_Catalog` must preserve success criterion; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "ChartLab_Opportunity_Catalog.id.example",
  "name": "ChartLab_Opportunity_Catalog.name.example",
  "type": "ChartLab_Opportunity_Catalog.type.example",
  "scope_ref": "ChartLab_Opportunity_Catalog.scope_ref.example",
  "neutral_ref": "ChartLab_Opportunity_Catalog.neutral_ref.example",
  "surface_ref": "ChartLab_Opportunity_Catalog.surface_ref.example",
  "canonical_ref": "ChartLab_Opportunity_Catalog.canonical_ref.example",
  "evidence_ref": "ChartLab_Opportunity_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 27. Metric_Formula_Catalog

**Group:** `chart`
**View ID:** `CAT.chart.Metric_Formula_Catalog`
**Generated export:** `Metric_Formula_Catalog.csv`
**Purpose:** MET.*, granularidad, ventana, filtros, dependencies.

### Grain

One row represents a governed NDC observation or decision for `Metric_Formula_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: demo evidence. |
| `name` | human-readable name; local emphasis: success criterion. |
| `type` | object family/type; local emphasis: success criterion. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: pricing class. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: data freshness. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: data freshness. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: metric formula. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: success criterion. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: demo evidence. |
| `owner` | human/system owner; local emphasis: metric formula. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: dataset contract. |
| `confidence` | low/medium/high/verified; local emphasis: demo evidence. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: demo evidence. |
| `updated_at` | timestamp of generation or curation; local emphasis: demo evidence. |

### Validators

- `Metric_Formula_Catalog` must preserve metric formula; if missing, status becomes `needs_review`, not `ready`.
- `Metric_Formula_Catalog` must preserve dataset contract; if missing, status becomes `needs_review`, not `ready`.
- `Metric_Formula_Catalog` must preserve chart grammar; if missing, status becomes `needs_review`, not `ready`.
- `Metric_Formula_Catalog` must preserve analytics value; if missing, status becomes `needs_review`, not `ready`.
- `Metric_Formula_Catalog` must preserve pricing class; if missing, status becomes `needs_review`, not `ready`.
- `Metric_Formula_Catalog` must preserve demo evidence; if missing, status becomes `needs_review`, not `ready`.
- `Metric_Formula_Catalog` must preserve data freshness; if missing, status becomes `needs_review`, not `ready`.
- `Metric_Formula_Catalog` must preserve success criterion; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Metric_Formula_Catalog.id.example",
  "name": "Metric_Formula_Catalog.name.example",
  "type": "Metric_Formula_Catalog.type.example",
  "scope_ref": "Metric_Formula_Catalog.scope_ref.example",
  "neutral_ref": "Metric_Formula_Catalog.neutral_ref.example",
  "surface_ref": "Metric_Formula_Catalog.surface_ref.example",
  "canonical_ref": "Metric_Formula_Catalog.canonical_ref.example",
  "evidence_ref": "Metric_Formula_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 28. Dataset_Contract_Catalog

**Group:** `data`
**View ID:** `CAT.data.Dataset_Contract_Catalog`
**Generated export:** `Dataset_Contract_Catalog.csv`
**Purpose:** DS.*, productores, consumidores, freshness, quality.

### Grain

One row represents a governed NDC observation or decision for `Dataset_Contract_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: field dictionary. |
| `name` | human-readable name; local emphasis: producer contract. |
| `type` | object family/type; local emphasis: producer contract. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: schema mapping. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: semantic binding. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: semantic binding. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: consumer contract. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: producer contract. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: field dictionary. |
| `owner` | human/system owner; local emphasis: consumer contract. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: quality expectation. |
| `confidence` | low/medium/high/verified; local emphasis: field dictionary. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: field dictionary. |
| `updated_at` | timestamp of generation or curation; local emphasis: field dictionary. |

### Validators

- `Dataset_Contract_Catalog` must preserve producer contract; if missing, status becomes `needs_review`, not `ready`.
- `Dataset_Contract_Catalog` must preserve consumer contract; if missing, status becomes `needs_review`, not `ready`.
- `Dataset_Contract_Catalog` must preserve quality expectation; if missing, status becomes `needs_review`, not `ready`.
- `Dataset_Contract_Catalog` must preserve freshness SLA; if missing, status becomes `needs_review`, not `ready`.
- `Dataset_Contract_Catalog` must preserve dataset grain; if missing, status becomes `needs_review`, not `ready`.
- `Dataset_Contract_Catalog` must preserve schema mapping; if missing, status becomes `needs_review`, not `ready`.
- `Dataset_Contract_Catalog` must preserve field dictionary; if missing, status becomes `needs_review`, not `ready`.
- `Dataset_Contract_Catalog` must preserve semantic binding; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Dataset_Contract_Catalog.id.example",
  "name": "Dataset_Contract_Catalog.name.example",
  "type": "Dataset_Contract_Catalog.type.example",
  "scope_ref": "Dataset_Contract_Catalog.scope_ref.example",
  "neutral_ref": "Dataset_Contract_Catalog.neutral_ref.example",
  "surface_ref": "Dataset_Contract_Catalog.surface_ref.example",
  "canonical_ref": "Dataset_Contract_Catalog.canonical_ref.example",
  "evidence_ref": "Dataset_Contract_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 29. Data_Binding_Map

**Group:** `data`
**View ID:** `CAT.data.Data_Binding_Map`
**Generated export:** `Data_Binding_Map.csv`
**Purpose:** binding neutral ↔ API/DB/DS/UI.

### Grain

One row represents a governed NDC observation or decision for `Data_Binding_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: semantic binding. |
| `name` | human-readable name; local emphasis: consumer contract. |
| `type` | object family/type; local emphasis: consumer contract. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: field dictionary. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: producer contract. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: producer contract. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: quality expectation. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: consumer contract. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: semantic binding. |
| `owner` | human/system owner; local emphasis: quality expectation. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: freshness SLA. |
| `confidence` | low/medium/high/verified; local emphasis: semantic binding. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: semantic binding. |
| `updated_at` | timestamp of generation or curation; local emphasis: semantic binding. |

### Validators

- `Data_Binding_Map` must preserve producer contract; if missing, status becomes `needs_review`, not `ready`.
- `Data_Binding_Map` must preserve consumer contract; if missing, status becomes `needs_review`, not `ready`.
- `Data_Binding_Map` must preserve quality expectation; if missing, status becomes `needs_review`, not `ready`.
- `Data_Binding_Map` must preserve freshness SLA; if missing, status becomes `needs_review`, not `ready`.
- `Data_Binding_Map` must preserve dataset grain; if missing, status becomes `needs_review`, not `ready`.
- `Data_Binding_Map` must preserve schema mapping; if missing, status becomes `needs_review`, not `ready`.
- `Data_Binding_Map` must preserve field dictionary; if missing, status becomes `needs_review`, not `ready`.
- `Data_Binding_Map` must preserve semantic binding; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Data_Binding_Map.id.example",
  "name": "Data_Binding_Map.name.example",
  "type": "Data_Binding_Map.type.example",
  "scope_ref": "Data_Binding_Map.scope_ref.example",
  "neutral_ref": "Data_Binding_Map.neutral_ref.example",
  "surface_ref": "Data_Binding_Map.surface_ref.example",
  "canonical_ref": "Data_Binding_Map.canonical_ref.example",
  "evidence_ref": "Data_Binding_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 30. API_Endpoint_Map

**Group:** `implementation`
**View ID:** `CAT.implementation.API_Endpoint_Map`
**Generated export:** `API_Endpoint_Map.csv`
**Purpose:** endpoints, scopes, eventos, auth/licensing.

### Grain

One row represents a governed NDC observation or decision for `API_Endpoint_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: API route. |
| `name` | human-readable name; local emphasis: component path. |
| `type` | object family/type; local emphasis: component path. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: contract boundary. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: DB table. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: DB table. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: source file. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: component path. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: API route. |
| `owner` | human/system owner; local emphasis: source file. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: technical owner. |
| `confidence` | low/medium/high/verified; local emphasis: API route. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: API route. |
| `updated_at` | timestamp of generation or curation; local emphasis: API route. |

### Validators

- `API_Endpoint_Map` must preserve API route; if missing, status becomes `needs_review`, not `ready`.
- `API_Endpoint_Map` must preserve DB table; if missing, status becomes `needs_review`, not `ready`.
- `API_Endpoint_Map` must preserve component path; if missing, status becomes `needs_review`, not `ready`.
- `API_Endpoint_Map` must preserve source file; if missing, status becomes `needs_review`, not `ready`.
- `API_Endpoint_Map` must preserve technical owner; if missing, status becomes `needs_review`, not `ready`.
- `API_Endpoint_Map` must preserve implementation limit; if missing, status becomes `needs_review`, not `ready`.
- `API_Endpoint_Map` must preserve runtime adapter; if missing, status becomes `needs_review`, not `ready`.
- `API_Endpoint_Map` must preserve contract boundary; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "API_Endpoint_Map.id.example",
  "name": "API_Endpoint_Map.name.example",
  "type": "API_Endpoint_Map.type.example",
  "scope_ref": "API_Endpoint_Map.scope_ref.example",
  "neutral_ref": "API_Endpoint_Map.neutral_ref.example",
  "surface_ref": "API_Endpoint_Map.surface_ref.example",
  "canonical_ref": "API_Endpoint_Map.canonical_ref.example",
  "evidence_ref": "API_Endpoint_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 31. DB_Implementation_Map

**Group:** `implementation`
**View ID:** `CAT.implementation.DB_Implementation_Map`
**Generated export:** `DB_Implementation_Map.csv`
**Purpose:** tablas actuales/futuras y semantic mapping.

### Grain

One row represents a governed NDC observation or decision for `DB_Implementation_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: DB table. |
| `name` | human-readable name; local emphasis: source file. |
| `type` | object family/type; local emphasis: source file. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: API route. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: component path. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: component path. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: technical owner. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: source file. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: DB table. |
| `owner` | human/system owner; local emphasis: technical owner. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: implementation limit. |
| `confidence` | low/medium/high/verified; local emphasis: DB table. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: DB table. |
| `updated_at` | timestamp of generation or curation; local emphasis: DB table. |

### Validators

- `DB_Implementation_Map` must preserve API route; if missing, status becomes `needs_review`, not `ready`.
- `DB_Implementation_Map` must preserve DB table; if missing, status becomes `needs_review`, not `ready`.
- `DB_Implementation_Map` must preserve component path; if missing, status becomes `needs_review`, not `ready`.
- `DB_Implementation_Map` must preserve source file; if missing, status becomes `needs_review`, not `ready`.
- `DB_Implementation_Map` must preserve technical owner; if missing, status becomes `needs_review`, not `ready`.
- `DB_Implementation_Map` must preserve implementation limit; if missing, status becomes `needs_review`, not `ready`.
- `DB_Implementation_Map` must preserve runtime adapter; if missing, status becomes `needs_review`, not `ready`.
- `DB_Implementation_Map` must preserve contract boundary; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "DB_Implementation_Map.id.example",
  "name": "DB_Implementation_Map.name.example",
  "type": "DB_Implementation_Map.type.example",
  "scope_ref": "DB_Implementation_Map.scope_ref.example",
  "neutral_ref": "DB_Implementation_Map.neutral_ref.example",
  "surface_ref": "DB_Implementation_Map.surface_ref.example",
  "canonical_ref": "DB_Implementation_Map.canonical_ref.example",
  "evidence_ref": "DB_Implementation_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 32. File_Component_Map

**Group:** `implementation`
**View ID:** `CAT.implementation.File_Component_Map`
**Generated export:** `File_Component_Map.csv`
**Purpose:** rutas, componentes, assets y owners técnicos.

### Grain

One row represents a governed NDC observation or decision for `File_Component_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: component path. |
| `name` | human-readable name; local emphasis: technical owner. |
| `type` | object family/type; local emphasis: technical owner. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: DB table. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: source file. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: source file. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: implementation limit. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: technical owner. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: component path. |
| `owner` | human/system owner; local emphasis: implementation limit. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: runtime adapter. |
| `confidence` | low/medium/high/verified; local emphasis: component path. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: component path. |
| `updated_at` | timestamp of generation or curation; local emphasis: component path. |

### Validators

- `File_Component_Map` must preserve API route; if missing, status becomes `needs_review`, not `ready`.
- `File_Component_Map` must preserve DB table; if missing, status becomes `needs_review`, not `ready`.
- `File_Component_Map` must preserve component path; if missing, status becomes `needs_review`, not `ready`.
- `File_Component_Map` must preserve source file; if missing, status becomes `needs_review`, not `ready`.
- `File_Component_Map` must preserve technical owner; if missing, status becomes `needs_review`, not `ready`.
- `File_Component_Map` must preserve implementation limit; if missing, status becomes `needs_review`, not `ready`.
- `File_Component_Map` must preserve runtime adapter; if missing, status becomes `needs_review`, not `ready`.
- `File_Component_Map` must preserve contract boundary; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "File_Component_Map.id.example",
  "name": "File_Component_Map.name.example",
  "type": "File_Component_Map.type.example",
  "scope_ref": "File_Component_Map.scope_ref.example",
  "neutral_ref": "File_Component_Map.neutral_ref.example",
  "surface_ref": "File_Component_Map.surface_ref.example",
  "canonical_ref": "File_Component_Map.canonical_ref.example",
  "evidence_ref": "File_Component_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 33. Capability_Registry

**Group:** `capability`
**View ID:** `CAT.capability.Capability_Registry`
**Generated export:** `Capability_Registry.csv`
**Purpose:** CAP.*, valor, users, surfaces, events, license.

### Grain

One row represents a governed NDC observation or decision for `Capability_Registry`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: module grant. |
| `name` | human-readable name; local emphasis: customer outcome. |
| `type` | object family/type; local emphasis: customer outcome. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: destination surfaces. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: base/pro/premium. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: base/pro/premium. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: evidence requirement. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: customer outcome. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: module grant. |
| `owner` | human/system owner; local emphasis: evidence requirement. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: pack membership. |
| `confidence` | low/medium/high/verified; local emphasis: module grant. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: module grant. |
| `updated_at` | timestamp of generation or curation; local emphasis: module grant. |

### Validators

- `Capability_Registry` must preserve commercial value; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Registry` must preserve required events; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Registry` must preserve destination surfaces; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Registry` must preserve module grant; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Registry` must preserve base/pro/premium; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Registry` must preserve customer outcome; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Registry` must preserve evidence requirement; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Registry` must preserve pack membership; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Capability_Registry.id.example",
  "name": "Capability_Registry.name.example",
  "type": "Capability_Registry.type.example",
  "scope_ref": "Capability_Registry.scope_ref.example",
  "neutral_ref": "Capability_Registry.neutral_ref.example",
  "surface_ref": "Capability_Registry.surface_ref.example",
  "canonical_ref": "Capability_Registry.canonical_ref.example",
  "evidence_ref": "Capability_Registry.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 34. Module_Registry

**Group:** `capability`
**View ID:** `CAT.capability.Module_Registry`
**Generated export:** `Module_Registry.csv`
**Purpose:** MOD.*, origen, destinos, grants, status.

### Grain

One row represents a governed NDC observation or decision for `Module_Registry`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: base/pro/premium. |
| `name` | human-readable name; local emphasis: evidence requirement. |
| `type` | object family/type; local emphasis: evidence requirement. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: module grant. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: customer outcome. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: customer outcome. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: pack membership. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: evidence requirement. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: base/pro/premium. |
| `owner` | human/system owner; local emphasis: pack membership. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: commercial value. |
| `confidence` | low/medium/high/verified; local emphasis: base/pro/premium. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: base/pro/premium. |
| `updated_at` | timestamp of generation or curation; local emphasis: base/pro/premium. |

### Validators

- `Module_Registry` must preserve commercial value; if missing, status becomes `needs_review`, not `ready`.
- `Module_Registry` must preserve required events; if missing, status becomes `needs_review`, not `ready`.
- `Module_Registry` must preserve destination surfaces; if missing, status becomes `needs_review`, not `ready`.
- `Module_Registry` must preserve module grant; if missing, status becomes `needs_review`, not `ready`.
- `Module_Registry` must preserve base/pro/premium; if missing, status becomes `needs_review`, not `ready`.
- `Module_Registry` must preserve customer outcome; if missing, status becomes `needs_review`, not `ready`.
- `Module_Registry` must preserve evidence requirement; if missing, status becomes `needs_review`, not `ready`.
- `Module_Registry` must preserve pack membership; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Module_Registry.id.example",
  "name": "Module_Registry.name.example",
  "type": "Module_Registry.type.example",
  "scope_ref": "Module_Registry.scope_ref.example",
  "neutral_ref": "Module_Registry.neutral_ref.example",
  "surface_ref": "Module_Registry.surface_ref.example",
  "canonical_ref": "Module_Registry.canonical_ref.example",
  "evidence_ref": "Module_Registry.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 35. Capability_Pack_Catalog

**Group:** `capability`
**View ID:** `CAT.capability.Capability_Pack_Catalog`
**Generated export:** `Capability_Pack_Catalog.csv`
**Purpose:** packs base/pro/premium/custom/enterprise.

### Grain

One row represents a governed NDC observation or decision for `Capability_Pack_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: customer outcome. |
| `name` | human-readable name; local emphasis: pack membership. |
| `type` | object family/type; local emphasis: pack membership. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: base/pro/premium. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: evidence requirement. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: evidence requirement. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: commercial value. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: pack membership. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: customer outcome. |
| `owner` | human/system owner; local emphasis: commercial value. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: required events. |
| `confidence` | low/medium/high/verified; local emphasis: customer outcome. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: customer outcome. |
| `updated_at` | timestamp of generation or curation; local emphasis: customer outcome. |

### Validators

- `Capability_Pack_Catalog` must preserve commercial value; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Pack_Catalog` must preserve required events; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Pack_Catalog` must preserve destination surfaces; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Pack_Catalog` must preserve module grant; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Pack_Catalog` must preserve base/pro/premium; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Pack_Catalog` must preserve customer outcome; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Pack_Catalog` must preserve evidence requirement; if missing, status becomes `needs_review`, not `ready`.
- `Capability_Pack_Catalog` must preserve pack membership; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Capability_Pack_Catalog.id.example",
  "name": "Capability_Pack_Catalog.name.example",
  "type": "Capability_Pack_Catalog.type.example",
  "scope_ref": "Capability_Pack_Catalog.scope_ref.example",
  "neutral_ref": "Capability_Pack_Catalog.neutral_ref.example",
  "surface_ref": "Capability_Pack_Catalog.surface_ref.example",
  "canonical_ref": "Capability_Pack_Catalog.canonical_ref.example",
  "evidence_ref": "Capability_Pack_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 36. License_Grant_Map

**Group:** `commercial`
**View ID:** `CAT.commercial.License_Grant_Map`
**Generated export:** `License_Grant_Map.csv`
**Purpose:** planes, licencias, add-ons, grants y límites.

### Grain

One row represents a governed NDC observation or decision for `License_Grant_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: no-humo proof. |
| `name` | human-readable name; local emphasis: license grant. |
| `type` | object family/type; local emphasis: license grant. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: addon activation. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: customer visibility. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: customer visibility. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: pricing class. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: license grant. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: no-humo proof. |
| `owner` | human/system owner; local emphasis: pricing class. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: claim limit. |
| `confidence` | low/medium/high/verified; local emphasis: no-humo proof. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: no-humo proof. |
| `updated_at` | timestamp of generation or curation; local emphasis: no-humo proof. |

### Validators

- `License_Grant_Map` must preserve license grant; if missing, status becomes `needs_review`, not `ready`.
- `License_Grant_Map` must preserve pricing class; if missing, status becomes `needs_review`, not `ready`.
- `License_Grant_Map` must preserve claim limit; if missing, status becomes `needs_review`, not `ready`.
- `License_Grant_Map` must preserve billing state; if missing, status becomes `needs_review`, not `ready`.
- `License_Grant_Map` must preserve surface entitlement; if missing, status becomes `needs_review`, not `ready`.
- `License_Grant_Map` must preserve addon activation; if missing, status becomes `needs_review`, not `ready`.
- `License_Grant_Map` must preserve no-humo proof; if missing, status becomes `needs_review`, not `ready`.
- `License_Grant_Map` must preserve customer visibility; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "License_Grant_Map.id.example",
  "name": "License_Grant_Map.name.example",
  "type": "License_Grant_Map.type.example",
  "scope_ref": "License_Grant_Map.scope_ref.example",
  "neutral_ref": "License_Grant_Map.neutral_ref.example",
  "surface_ref": "License_Grant_Map.surface_ref.example",
  "canonical_ref": "License_Grant_Map.canonical_ref.example",
  "evidence_ref": "License_Grant_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 37. Commercial_Readiness_Map

**Group:** `commercial`
**View ID:** `CAT.commercial.Commercial_Readiness_Map`
**Generated export:** `Commercial_Readiness_Map.csv`
**Purpose:** readiness comercial de claims/capabilities.

### Grain

One row represents a governed NDC observation or decision for `Commercial_Readiness_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: customer visibility. |
| `name` | human-readable name; local emphasis: pricing class. |
| `type` | object family/type; local emphasis: pricing class. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: no-humo proof. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: license grant. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: license grant. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: claim limit. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: pricing class. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: customer visibility. |
| `owner` | human/system owner; local emphasis: claim limit. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: billing state. |
| `confidence` | low/medium/high/verified; local emphasis: customer visibility. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: customer visibility. |
| `updated_at` | timestamp of generation or curation; local emphasis: customer visibility. |

### Validators

- `Commercial_Readiness_Map` must preserve license grant; if missing, status becomes `needs_review`, not `ready`.
- `Commercial_Readiness_Map` must preserve pricing class; if missing, status becomes `needs_review`, not `ready`.
- `Commercial_Readiness_Map` must preserve claim limit; if missing, status becomes `needs_review`, not `ready`.
- `Commercial_Readiness_Map` must preserve billing state; if missing, status becomes `needs_review`, not `ready`.
- `Commercial_Readiness_Map` must preserve surface entitlement; if missing, status becomes `needs_review`, not `ready`.
- `Commercial_Readiness_Map` must preserve addon activation; if missing, status becomes `needs_review`, not `ready`.
- `Commercial_Readiness_Map` must preserve no-humo proof; if missing, status becomes `needs_review`, not `ready`.
- `Commercial_Readiness_Map` must preserve customer visibility; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Commercial_Readiness_Map.id.example",
  "name": "Commercial_Readiness_Map.name.example",
  "type": "Commercial_Readiness_Map.type.example",
  "scope_ref": "Commercial_Readiness_Map.scope_ref.example",
  "neutral_ref": "Commercial_Readiness_Map.neutral_ref.example",
  "surface_ref": "Commercial_Readiness_Map.surface_ref.example",
  "canonical_ref": "Commercial_Readiness_Map.canonical_ref.example",
  "evidence_ref": "Commercial_Readiness_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 38. No_Humo_Claims_Ledger

**Group:** `commercial`
**View ID:** `CAT.commercial.No_Humo_Claims_Ledger`
**Generated export:** `No_Humo_Claims_Ledger.csv`
**Purpose:** claims permitidos/prohibidos con evidencia.

### Grain

One row represents a governed NDC observation or decision for `No_Humo_Claims_Ledger`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: license grant. |
| `name` | human-readable name; local emphasis: claim limit. |
| `type` | object family/type; local emphasis: claim limit. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: customer visibility. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: pricing class. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: pricing class. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: billing state. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: claim limit. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: license grant. |
| `owner` | human/system owner; local emphasis: billing state. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: surface entitlement. |
| `confidence` | low/medium/high/verified; local emphasis: license grant. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: license grant. |
| `updated_at` | timestamp of generation or curation; local emphasis: license grant. |

### Validators

- `No_Humo_Claims_Ledger` must preserve license grant; if missing, status becomes `needs_review`, not `ready`.
- `No_Humo_Claims_Ledger` must preserve pricing class; if missing, status becomes `needs_review`, not `ready`.
- `No_Humo_Claims_Ledger` must preserve claim limit; if missing, status becomes `needs_review`, not `ready`.
- `No_Humo_Claims_Ledger` must preserve billing state; if missing, status becomes `needs_review`, not `ready`.
- `No_Humo_Claims_Ledger` must preserve surface entitlement; if missing, status becomes `needs_review`, not `ready`.
- `No_Humo_Claims_Ledger` must preserve addon activation; if missing, status becomes `needs_review`, not `ready`.
- `No_Humo_Claims_Ledger` must preserve no-humo proof; if missing, status becomes `needs_review`, not `ready`.
- `No_Humo_Claims_Ledger` must preserve customer visibility; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "No_Humo_Claims_Ledger.id.example",
  "name": "No_Humo_Claims_Ledger.name.example",
  "type": "No_Humo_Claims_Ledger.type.example",
  "scope_ref": "No_Humo_Claims_Ledger.scope_ref.example",
  "neutral_ref": "No_Humo_Claims_Ledger.neutral_ref.example",
  "surface_ref": "No_Humo_Claims_Ledger.surface_ref.example",
  "canonical_ref": "No_Humo_Claims_Ledger.canonical_ref.example",
  "evidence_ref": "No_Humo_Claims_Ledger.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 39. Evidence_Index

**Group:** `evidence`
**View ID:** `CAT.evidence.Evidence_Index`
**Generated export:** `Evidence_Index.csv`
**Purpose:** EVD.*, source_tool, artifact, targets, freshness.

### Grain

One row represents a governed NDC observation or decision for `Evidence_Index`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: source tool. |
| `name` | human-readable name; local emphasis: freshness. |
| `type` | object family/type; local emphasis: freshness. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: artifact URI. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: confidence. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: confidence. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: review status. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: freshness. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: source tool. |
| `owner` | human/system owner; local emphasis: review status. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: does-not-prove. |
| `confidence` | low/medium/high/verified; local emphasis: source tool. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: source tool. |
| `updated_at` | timestamp of generation or curation; local emphasis: source tool. |

### Validators

- `Evidence_Index` must preserve artifact URI; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Index` must preserve source tool; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Index` must preserve confidence; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Index` must preserve freshness; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Index` must preserve review status; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Index` must preserve does-not-prove; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Index` must preserve target refs; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Index` must preserve support type; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Evidence_Index.id.example",
  "name": "Evidence_Index.name.example",
  "type": "Evidence_Index.type.example",
  "scope_ref": "Evidence_Index.scope_ref.example",
  "neutral_ref": "Evidence_Index.neutral_ref.example",
  "surface_ref": "Evidence_Index.surface_ref.example",
  "canonical_ref": "Evidence_Index.canonical_ref.example",
  "evidence_ref": "Evidence_Index.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 40. Evidence_Readiness_Map

**Group:** `evidence`
**View ID:** `CAT.evidence.Evidence_Readiness_Map`
**Generated export:** `Evidence_Readiness_Map.csv`
**Purpose:** ready/needs_review/blocked/partial/stale/orphan/conflict.

### Grain

One row represents a governed NDC observation or decision for `Evidence_Readiness_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: confidence. |
| `name` | human-readable name; local emphasis: review status. |
| `type` | object family/type; local emphasis: review status. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: source tool. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: freshness. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: freshness. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: does-not-prove. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: review status. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: confidence. |
| `owner` | human/system owner; local emphasis: does-not-prove. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: target refs. |
| `confidence` | low/medium/high/verified; local emphasis: confidence. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: confidence. |
| `updated_at` | timestamp of generation or curation; local emphasis: confidence. |

### Validators

- `Evidence_Readiness_Map` must preserve artifact URI; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Readiness_Map` must preserve source tool; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Readiness_Map` must preserve confidence; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Readiness_Map` must preserve freshness; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Readiness_Map` must preserve review status; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Readiness_Map` must preserve does-not-prove; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Readiness_Map` must preserve target refs; if missing, status becomes `needs_review`, not `ready`.
- `Evidence_Readiness_Map` must preserve support type; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Evidence_Readiness_Map.id.example",
  "name": "Evidence_Readiness_Map.name.example",
  "type": "Evidence_Readiness_Map.type.example",
  "scope_ref": "Evidence_Readiness_Map.scope_ref.example",
  "neutral_ref": "Evidence_Readiness_Map.neutral_ref.example",
  "surface_ref": "Evidence_Readiness_Map.surface_ref.example",
  "canonical_ref": "Evidence_Readiness_Map.canonical_ref.example",
  "evidence_ref": "Evidence_Readiness_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 41. Runtime_Evidence_Map

**Group:** `evidence`
**View ID:** `CAT.evidence.Runtime_Evidence_Map`
**Generated export:** `Runtime_Evidence_Map.csv`
**Purpose:** screenshots, DOM, traces, API, DB, tests.

### Grain

One row represents a governed NDC observation or decision for `Runtime_Evidence_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: freshness. |
| `name` | human-readable name; local emphasis: does-not-prove. |
| `type` | object family/type; local emphasis: does-not-prove. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: confidence. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: review status. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: review status. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: target refs. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: does-not-prove. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: freshness. |
| `owner` | human/system owner; local emphasis: target refs. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: support type. |
| `confidence` | low/medium/high/verified; local emphasis: freshness. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: freshness. |
| `updated_at` | timestamp of generation or curation; local emphasis: freshness. |

### Validators

- `Runtime_Evidence_Map` must preserve artifact URI; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Evidence_Map` must preserve source tool; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Evidence_Map` must preserve confidence; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Evidence_Map` must preserve freshness; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Evidence_Map` must preserve review status; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Evidence_Map` must preserve does-not-prove; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Evidence_Map` must preserve target refs; if missing, status becomes `needs_review`, not `ready`.
- `Runtime_Evidence_Map` must preserve support type; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Runtime_Evidence_Map.id.example",
  "name": "Runtime_Evidence_Map.name.example",
  "type": "Runtime_Evidence_Map.type.example",
  "scope_ref": "Runtime_Evidence_Map.scope_ref.example",
  "neutral_ref": "Runtime_Evidence_Map.neutral_ref.example",
  "surface_ref": "Runtime_Evidence_Map.surface_ref.example",
  "canonical_ref": "Runtime_Evidence_Map.canonical_ref.example",
  "evidence_ref": "Runtime_Evidence_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 42. Curation_Decision_Log

**Group:** `curation`
**View ID:** `CAT.curation.Curation_Decision_Log`
**Generated export:** `Curation_Decision_Log.csv`
**Purpose:** alias, override, promotion, rejection, dispute.

### Grain

One row represents a governed NDC observation or decision for `Curation_Decision_Log`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: review note. |
| `name` | human-readable name; local emphasis: append-only log. |
| `type` | object family/type; local emphasis: append-only log. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: promotion gate. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: conflict handling. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: conflict handling. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: decision provenance. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: append-only log. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: review note. |
| `owner` | human/system owner; local emphasis: decision provenance. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: human decision. |
| `confidence` | low/medium/high/verified; local emphasis: review note. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: review note. |
| `updated_at` | timestamp of generation or curation; local emphasis: review note. |

### Validators

- `Curation_Decision_Log` must preserve human decision; if missing, status becomes `needs_review`, not `ready`.
- `Curation_Decision_Log` must preserve alias mapping; if missing, status becomes `needs_review`, not `ready`.
- `Curation_Decision_Log` must preserve override reason; if missing, status becomes `needs_review`, not `ready`.
- `Curation_Decision_Log` must preserve promotion gate; if missing, status becomes `needs_review`, not `ready`.
- `Curation_Decision_Log` must preserve review note; if missing, status becomes `needs_review`, not `ready`.
- `Curation_Decision_Log` must preserve conflict handling; if missing, status becomes `needs_review`, not `ready`.
- `Curation_Decision_Log` must preserve append-only log; if missing, status becomes `needs_review`, not `ready`.
- `Curation_Decision_Log` must preserve decision provenance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Curation_Decision_Log.id.example",
  "name": "Curation_Decision_Log.name.example",
  "type": "Curation_Decision_Log.type.example",
  "scope_ref": "Curation_Decision_Log.scope_ref.example",
  "neutral_ref": "Curation_Decision_Log.neutral_ref.example",
  "surface_ref": "Curation_Decision_Log.surface_ref.example",
  "canonical_ref": "Curation_Decision_Log.canonical_ref.example",
  "evidence_ref": "Curation_Decision_Log.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 43. Alias_Map

**Group:** `curation`
**View ID:** `CAT.curation.Alias_Map`
**Generated export:** `Alias_Map.csv`
**Purpose:** alias de nombres detectados a neutral IDs.

### Grain

One row represents a governed NDC observation or decision for `Alias_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: conflict handling. |
| `name` | human-readable name; local emphasis: decision provenance. |
| `type` | object family/type; local emphasis: decision provenance. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: review note. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: append-only log. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: append-only log. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: human decision. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: decision provenance. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: conflict handling. |
| `owner` | human/system owner; local emphasis: human decision. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: alias mapping. |
| `confidence` | low/medium/high/verified; local emphasis: conflict handling. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: conflict handling. |
| `updated_at` | timestamp of generation or curation; local emphasis: conflict handling. |

### Validators

- `Alias_Map` must preserve human decision; if missing, status becomes `needs_review`, not `ready`.
- `Alias_Map` must preserve alias mapping; if missing, status becomes `needs_review`, not `ready`.
- `Alias_Map` must preserve override reason; if missing, status becomes `needs_review`, not `ready`.
- `Alias_Map` must preserve promotion gate; if missing, status becomes `needs_review`, not `ready`.
- `Alias_Map` must preserve review note; if missing, status becomes `needs_review`, not `ready`.
- `Alias_Map` must preserve conflict handling; if missing, status becomes `needs_review`, not `ready`.
- `Alias_Map` must preserve append-only log; if missing, status becomes `needs_review`, not `ready`.
- `Alias_Map` must preserve decision provenance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Alias_Map.id.example",
  "name": "Alias_Map.name.example",
  "type": "Alias_Map.type.example",
  "scope_ref": "Alias_Map.scope_ref.example",
  "neutral_ref": "Alias_Map.neutral_ref.example",
  "surface_ref": "Alias_Map.surface_ref.example",
  "canonical_ref": "Alias_Map.canonical_ref.example",
  "evidence_ref": "Alias_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 44. Override_Map

**Group:** `curation`
**View ID:** `CAT.curation.Override_Map`
**Generated export:** `Override_Map.csv`
**Purpose:** correcciones explícitas de mapping/readiness.

### Grain

One row represents a governed NDC observation or decision for `Override_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: append-only log. |
| `name` | human-readable name; local emphasis: human decision. |
| `type` | object family/type; local emphasis: human decision. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: conflict handling. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: decision provenance. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: decision provenance. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: alias mapping. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: human decision. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: append-only log. |
| `owner` | human/system owner; local emphasis: alias mapping. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: override reason. |
| `confidence` | low/medium/high/verified; local emphasis: append-only log. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: append-only log. |
| `updated_at` | timestamp of generation or curation; local emphasis: append-only log. |

### Validators

- `Override_Map` must preserve human decision; if missing, status becomes `needs_review`, not `ready`.
- `Override_Map` must preserve alias mapping; if missing, status becomes `needs_review`, not `ready`.
- `Override_Map` must preserve override reason; if missing, status becomes `needs_review`, not `ready`.
- `Override_Map` must preserve promotion gate; if missing, status becomes `needs_review`, not `ready`.
- `Override_Map` must preserve review note; if missing, status becomes `needs_review`, not `ready`.
- `Override_Map` must preserve conflict handling; if missing, status becomes `needs_review`, not `ready`.
- `Override_Map` must preserve append-only log; if missing, status becomes `needs_review`, not `ready`.
- `Override_Map` must preserve decision provenance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Override_Map.id.example",
  "name": "Override_Map.name.example",
  "type": "Override_Map.type.example",
  "scope_ref": "Override_Map.scope_ref.example",
  "neutral_ref": "Override_Map.neutral_ref.example",
  "surface_ref": "Override_Map.surface_ref.example",
  "canonical_ref": "Override_Map.canonical_ref.example",
  "evidence_ref": "Override_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 45. Canonical_Promotion_Log

**Group:** `curation`
**View ID:** `CAT.curation.Canonical_Promotion_Log`
**Generated export:** `Canonical_Promotion_Log.csv`
**Purpose:** promociones a canonical.

### Grain

One row represents a governed NDC observation or decision for `Canonical_Promotion_Log`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: decision provenance. |
| `name` | human-readable name; local emphasis: alias mapping. |
| `type` | object family/type; local emphasis: alias mapping. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: append-only log. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: human decision. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: human decision. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: override reason. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: alias mapping. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: decision provenance. |
| `owner` | human/system owner; local emphasis: override reason. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: promotion gate. |
| `confidence` | low/medium/high/verified; local emphasis: decision provenance. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: decision provenance. |
| `updated_at` | timestamp of generation or curation; local emphasis: decision provenance. |

### Validators

- `Canonical_Promotion_Log` must preserve human decision; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Promotion_Log` must preserve alias mapping; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Promotion_Log` must preserve override reason; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Promotion_Log` must preserve promotion gate; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Promotion_Log` must preserve review note; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Promotion_Log` must preserve conflict handling; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Promotion_Log` must preserve append-only log; if missing, status becomes `needs_review`, not `ready`.
- `Canonical_Promotion_Log` must preserve decision provenance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Canonical_Promotion_Log.id.example",
  "name": "Canonical_Promotion_Log.name.example",
  "type": "Canonical_Promotion_Log.type.example",
  "scope_ref": "Canonical_Promotion_Log.scope_ref.example",
  "neutral_ref": "Canonical_Promotion_Log.neutral_ref.example",
  "surface_ref": "Canonical_Promotion_Log.surface_ref.example",
  "canonical_ref": "Canonical_Promotion_Log.canonical_ref.example",
  "evidence_ref": "Canonical_Promotion_Log.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 46. Review_Notes_Index

**Group:** `curation`
**View ID:** `CAT.curation.Review_Notes_Index`
**Generated export:** `Review_Notes_Index.csv`
**Purpose:** notas humanas y pendientes.

### Grain

One row represents a governed NDC observation or decision for `Review_Notes_Index`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: human decision. |
| `name` | human-readable name; local emphasis: override reason. |
| `type` | object family/type; local emphasis: override reason. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: decision provenance. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: alias mapping. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: alias mapping. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: promotion gate. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: override reason. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: human decision. |
| `owner` | human/system owner; local emphasis: promotion gate. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: review note. |
| `confidence` | low/medium/high/verified; local emphasis: human decision. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: human decision. |
| `updated_at` | timestamp of generation or curation; local emphasis: human decision. |

### Validators

- `Review_Notes_Index` must preserve human decision; if missing, status becomes `needs_review`, not `ready`.
- `Review_Notes_Index` must preserve alias mapping; if missing, status becomes `needs_review`, not `ready`.
- `Review_Notes_Index` must preserve override reason; if missing, status becomes `needs_review`, not `ready`.
- `Review_Notes_Index` must preserve promotion gate; if missing, status becomes `needs_review`, not `ready`.
- `Review_Notes_Index` must preserve review note; if missing, status becomes `needs_review`, not `ready`.
- `Review_Notes_Index` must preserve conflict handling; if missing, status becomes `needs_review`, not `ready`.
- `Review_Notes_Index` must preserve append-only log; if missing, status becomes `needs_review`, not `ready`.
- `Review_Notes_Index` must preserve decision provenance; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Review_Notes_Index.id.example",
  "name": "Review_Notes_Index.name.example",
  "type": "Review_Notes_Index.type.example",
  "scope_ref": "Review_Notes_Index.scope_ref.example",
  "neutral_ref": "Review_Notes_Index.neutral_ref.example",
  "surface_ref": "Review_Notes_Index.surface_ref.example",
  "canonical_ref": "Review_Notes_Index.canonical_ref.example",
  "evidence_ref": "Review_Notes_Index.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 47. Drift_And_Reconciliation_Map

**Group:** `drift`
**View ID:** `CAT.drift.Drift_And_Reconciliation_Map`
**Generated export:** `Drift_And_Reconciliation_Map.csv`
**Purpose:** discrepancias 231 vs 228 por scope/status/sync.

### Grain

One row represents a governed NDC observation or decision for `Drift_And_Reconciliation_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: hypothesis. |
| `name` | human-readable name; local emphasis: sync pending. |
| `type` | object family/type; local emphasis: sync pending. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: difference case. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: scope mismatch. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: scope mismatch. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: duplicate rejected. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: sync pending. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: hypothesis. |
| `owner` | human/system owner; local emphasis: duplicate rejected. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: filter mismatch. |
| `confidence` | low/medium/high/verified; local emphasis: hypothesis. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: hypothesis. |
| `updated_at` | timestamp of generation or curation; local emphasis: hypothesis. |

### Validators

- `Drift_And_Reconciliation_Map` must preserve difference case; if missing, status becomes `needs_review`, not `ready`.
- `Drift_And_Reconciliation_Map` must preserve hypothesis; if missing, status becomes `needs_review`, not `ready`.
- `Drift_And_Reconciliation_Map` must preserve scope mismatch; if missing, status becomes `needs_review`, not `ready`.
- `Drift_And_Reconciliation_Map` must preserve sync pending; if missing, status becomes `needs_review`, not `ready`.
- `Drift_And_Reconciliation_Map` must preserve duplicate rejected; if missing, status becomes `needs_review`, not `ready`.
- `Drift_And_Reconciliation_Map` must preserve filter mismatch; if missing, status becomes `needs_review`, not `ready`.
- `Drift_And_Reconciliation_Map` must preserve evidence gap; if missing, status becomes `needs_review`, not `ready`.
- `Drift_And_Reconciliation_Map` must preserve reconciliation status; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Drift_And_Reconciliation_Map.id.example",
  "name": "Drift_And_Reconciliation_Map.name.example",
  "type": "Drift_And_Reconciliation_Map.type.example",
  "scope_ref": "Drift_And_Reconciliation_Map.scope_ref.example",
  "neutral_ref": "Drift_And_Reconciliation_Map.neutral_ref.example",
  "surface_ref": "Drift_And_Reconciliation_Map.surface_ref.example",
  "canonical_ref": "Drift_And_Reconciliation_Map.canonical_ref.example",
  "evidence_ref": "Drift_And_Reconciliation_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 48. Conflict_Register

**Group:** `drift`
**View ID:** `CAT.drift.Conflict_Register`
**Generated export:** `Conflict_Register.csv`
**Purpose:** conflictos entre fuentes.

### Grain

One row represents a governed NDC observation or decision for `Conflict_Register`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: scope mismatch. |
| `name` | human-readable name; local emphasis: duplicate rejected. |
| `type` | object family/type; local emphasis: duplicate rejected. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: hypothesis. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: sync pending. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: sync pending. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: filter mismatch. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: duplicate rejected. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: scope mismatch. |
| `owner` | human/system owner; local emphasis: filter mismatch. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: evidence gap. |
| `confidence` | low/medium/high/verified; local emphasis: scope mismatch. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: scope mismatch. |
| `updated_at` | timestamp of generation or curation; local emphasis: scope mismatch. |

### Validators

- `Conflict_Register` must preserve difference case; if missing, status becomes `needs_review`, not `ready`.
- `Conflict_Register` must preserve hypothesis; if missing, status becomes `needs_review`, not `ready`.
- `Conflict_Register` must preserve scope mismatch; if missing, status becomes `needs_review`, not `ready`.
- `Conflict_Register` must preserve sync pending; if missing, status becomes `needs_review`, not `ready`.
- `Conflict_Register` must preserve duplicate rejected; if missing, status becomes `needs_review`, not `ready`.
- `Conflict_Register` must preserve filter mismatch; if missing, status becomes `needs_review`, not `ready`.
- `Conflict_Register` must preserve evidence gap; if missing, status becomes `needs_review`, not `ready`.
- `Conflict_Register` must preserve reconciliation status; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Conflict_Register.id.example",
  "name": "Conflict_Register.name.example",
  "type": "Conflict_Register.type.example",
  "scope_ref": "Conflict_Register.scope_ref.example",
  "neutral_ref": "Conflict_Register.neutral_ref.example",
  "surface_ref": "Conflict_Register.surface_ref.example",
  "canonical_ref": "Conflict_Register.canonical_ref.example",
  "evidence_ref": "Conflict_Register.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 49. Orphan_Evidence_Register

**Group:** `drift`
**View ID:** `CAT.drift.Orphan_Evidence_Register`
**Generated export:** `Orphan_Evidence_Register.csv`
**Purpose:** evidencias sin target claro.

### Grain

One row represents a governed NDC observation or decision for `Orphan_Evidence_Register`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: sync pending. |
| `name` | human-readable name; local emphasis: filter mismatch. |
| `type` | object family/type; local emphasis: filter mismatch. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: scope mismatch. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: duplicate rejected. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: duplicate rejected. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: evidence gap. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: filter mismatch. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: sync pending. |
| `owner` | human/system owner; local emphasis: evidence gap. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: reconciliation status. |
| `confidence` | low/medium/high/verified; local emphasis: sync pending. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: sync pending. |
| `updated_at` | timestamp of generation or curation; local emphasis: sync pending. |

### Validators

- `Orphan_Evidence_Register` must preserve difference case; if missing, status becomes `needs_review`, not `ready`.
- `Orphan_Evidence_Register` must preserve hypothesis; if missing, status becomes `needs_review`, not `ready`.
- `Orphan_Evidence_Register` must preserve scope mismatch; if missing, status becomes `needs_review`, not `ready`.
- `Orphan_Evidence_Register` must preserve sync pending; if missing, status becomes `needs_review`, not `ready`.
- `Orphan_Evidence_Register` must preserve duplicate rejected; if missing, status becomes `needs_review`, not `ready`.
- `Orphan_Evidence_Register` must preserve filter mismatch; if missing, status becomes `needs_review`, not `ready`.
- `Orphan_Evidence_Register` must preserve evidence gap; if missing, status becomes `needs_review`, not `ready`.
- `Orphan_Evidence_Register` must preserve reconciliation status; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Orphan_Evidence_Register.id.example",
  "name": "Orphan_Evidence_Register.name.example",
  "type": "Orphan_Evidence_Register.type.example",
  "scope_ref": "Orphan_Evidence_Register.scope_ref.example",
  "neutral_ref": "Orphan_Evidence_Register.neutral_ref.example",
  "surface_ref": "Orphan_Evidence_Register.surface_ref.example",
  "canonical_ref": "Orphan_Evidence_Register.canonical_ref.example",
  "evidence_ref": "Orphan_Evidence_Register.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 50. Quality_Rule_Catalog

**Group:** `governance`
**View ID:** `CAT.governance.Quality_Rule_Catalog`
**Generated export:** `Quality_Rule_Catalog.csv`
**Purpose:** reglas de calidad.

### Grain

One row represents a governed NDC observation or decision for `Quality_Rule_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: warning. |
| `name` | human-readable name; local emphasis: no fake green. |
| `type` | object family/type; local emphasis: no fake green. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: blocker. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: allow condition. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: allow condition. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: review owner. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: no fake green. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: warning. |
| `owner` | human/system owner; local emphasis: review owner. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: gate result. |
| `confidence` | low/medium/high/verified; local emphasis: warning. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: warning. |
| `updated_at` | timestamp of generation or curation; local emphasis: warning. |

### Validators

- `Quality_Rule_Catalog` must preserve gate result; if missing, status becomes `needs_review`, not `ready`.
- `Quality_Rule_Catalog` must preserve quality rule; if missing, status becomes `needs_review`, not `ready`.
- `Quality_Rule_Catalog` must preserve authority source; if missing, status becomes `needs_review`, not `ready`.
- `Quality_Rule_Catalog` must preserve blocker; if missing, status becomes `needs_review`, not `ready`.
- `Quality_Rule_Catalog` must preserve warning; if missing, status becomes `needs_review`, not `ready`.
- `Quality_Rule_Catalog` must preserve allow condition; if missing, status becomes `needs_review`, not `ready`.
- `Quality_Rule_Catalog` must preserve no fake green; if missing, status becomes `needs_review`, not `ready`.
- `Quality_Rule_Catalog` must preserve review owner; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Quality_Rule_Catalog.id.example",
  "name": "Quality_Rule_Catalog.name.example",
  "type": "Quality_Rule_Catalog.type.example",
  "scope_ref": "Quality_Rule_Catalog.scope_ref.example",
  "neutral_ref": "Quality_Rule_Catalog.neutral_ref.example",
  "surface_ref": "Quality_Rule_Catalog.surface_ref.example",
  "canonical_ref": "Quality_Rule_Catalog.canonical_ref.example",
  "evidence_ref": "Quality_Rule_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 51. Validation_Gate_Catalog

**Group:** `governance`
**View ID:** `CAT.governance.Validation_Gate_Catalog`
**Generated export:** `Validation_Gate_Catalog.csv`
**Purpose:** gates de scope, neutral, evidence, lineage, projection.

### Grain

One row represents a governed NDC observation or decision for `Validation_Gate_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: allow condition. |
| `name` | human-readable name; local emphasis: review owner. |
| `type` | object family/type; local emphasis: review owner. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: warning. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: no fake green. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: no fake green. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: gate result. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: review owner. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: allow condition. |
| `owner` | human/system owner; local emphasis: gate result. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: quality rule. |
| `confidence` | low/medium/high/verified; local emphasis: allow condition. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: allow condition. |
| `updated_at` | timestamp of generation or curation; local emphasis: allow condition. |

### Validators

- `Validation_Gate_Catalog` must preserve gate result; if missing, status becomes `needs_review`, not `ready`.
- `Validation_Gate_Catalog` must preserve quality rule; if missing, status becomes `needs_review`, not `ready`.
- `Validation_Gate_Catalog` must preserve authority source; if missing, status becomes `needs_review`, not `ready`.
- `Validation_Gate_Catalog` must preserve blocker; if missing, status becomes `needs_review`, not `ready`.
- `Validation_Gate_Catalog` must preserve warning; if missing, status becomes `needs_review`, not `ready`.
- `Validation_Gate_Catalog` must preserve allow condition; if missing, status becomes `needs_review`, not `ready`.
- `Validation_Gate_Catalog` must preserve no fake green; if missing, status becomes `needs_review`, not `ready`.
- `Validation_Gate_Catalog` must preserve review owner; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Validation_Gate_Catalog.id.example",
  "name": "Validation_Gate_Catalog.name.example",
  "type": "Validation_Gate_Catalog.type.example",
  "scope_ref": "Validation_Gate_Catalog.scope_ref.example",
  "neutral_ref": "Validation_Gate_Catalog.neutral_ref.example",
  "surface_ref": "Validation_Gate_Catalog.surface_ref.example",
  "canonical_ref": "Validation_Gate_Catalog.canonical_ref.example",
  "evidence_ref": "Validation_Gate_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 52. Authority_Source_Map

**Group:** `governance`
**View ID:** `CAT.governance.Authority_Source_Map`
**Generated export:** `Authority_Source_Map.csv`
**Purpose:** orden de autoridad.

### Grain

One row represents a governed NDC observation or decision for `Authority_Source_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: no fake green. |
| `name` | human-readable name; local emphasis: gate result. |
| `type` | object family/type; local emphasis: gate result. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: allow condition. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: review owner. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: review owner. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: quality rule. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: gate result. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: no fake green. |
| `owner` | human/system owner; local emphasis: quality rule. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: authority source. |
| `confidence` | low/medium/high/verified; local emphasis: no fake green. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: no fake green. |
| `updated_at` | timestamp of generation or curation; local emphasis: no fake green. |

### Validators

- `Authority_Source_Map` must preserve gate result; if missing, status becomes `needs_review`, not `ready`.
- `Authority_Source_Map` must preserve quality rule; if missing, status becomes `needs_review`, not `ready`.
- `Authority_Source_Map` must preserve authority source; if missing, status becomes `needs_review`, not `ready`.
- `Authority_Source_Map` must preserve blocker; if missing, status becomes `needs_review`, not `ready`.
- `Authority_Source_Map` must preserve warning; if missing, status becomes `needs_review`, not `ready`.
- `Authority_Source_Map` must preserve allow condition; if missing, status becomes `needs_review`, not `ready`.
- `Authority_Source_Map` must preserve no fake green; if missing, status becomes `needs_review`, not `ready`.
- `Authority_Source_Map` must preserve review owner; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Authority_Source_Map.id.example",
  "name": "Authority_Source_Map.name.example",
  "type": "Authority_Source_Map.type.example",
  "scope_ref": "Authority_Source_Map.scope_ref.example",
  "neutral_ref": "Authority_Source_Map.neutral_ref.example",
  "surface_ref": "Authority_Source_Map.surface_ref.example",
  "canonical_ref": "Authority_Source_Map.canonical_ref.example",
  "evidence_ref": "Authority_Source_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 53. Tool_Input_Slot_Catalog

**Group:** `tooling`
**View ID:** `CAT.tooling.Tool_Input_Slot_Catalog`
**Generated export:** `Tool_Input_Slot_Catalog.csv`
**Purpose:** slots raw_inputs por herramienta.

### Grain

One row represents a governed NDC observation or decision for `Tool_Input_Slot_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: run manifest. |
| `name` | human-readable name; local emphasis: normalizer contract. |
| `type` | object family/type; local emphasis: normalizer contract. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: source adapter. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: raw input slot. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: raw input slot. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: candidate extraction. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: normalizer contract. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: run manifest. |
| `owner` | human/system owner; local emphasis: candidate extraction. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: tool observation. |
| `confidence` | low/medium/high/verified; local emphasis: run manifest. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: run manifest. |
| `updated_at` | timestamp of generation or curation; local emphasis: run manifest. |

### Validators

- `Tool_Input_Slot_Catalog` must preserve raw input slot; if missing, status becomes `needs_review`, not `ready`.
- `Tool_Input_Slot_Catalog` must preserve normalizer contract; if missing, status becomes `needs_review`, not `ready`.
- `Tool_Input_Slot_Catalog` must preserve candidate extraction; if missing, status becomes `needs_review`, not `ready`.
- `Tool_Input_Slot_Catalog` must preserve tool observation; if missing, status becomes `needs_review`, not `ready`.
- `Tool_Input_Slot_Catalog` must preserve artifact mapping; if missing, status becomes `needs_review`, not `ready`.
- `Tool_Input_Slot_Catalog` must preserve safe ingestion; if missing, status becomes `needs_review`, not `ready`.
- `Tool_Input_Slot_Catalog` must preserve source adapter; if missing, status becomes `needs_review`, not `ready`.
- `Tool_Input_Slot_Catalog` must preserve run manifest; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Tool_Input_Slot_Catalog.id.example",
  "name": "Tool_Input_Slot_Catalog.name.example",
  "type": "Tool_Input_Slot_Catalog.type.example",
  "scope_ref": "Tool_Input_Slot_Catalog.scope_ref.example",
  "neutral_ref": "Tool_Input_Slot_Catalog.neutral_ref.example",
  "surface_ref": "Tool_Input_Slot_Catalog.surface_ref.example",
  "canonical_ref": "Tool_Input_Slot_Catalog.canonical_ref.example",
  "evidence_ref": "Tool_Input_Slot_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 54. Normalizer_Contract_Map

**Group:** `tooling`
**View ID:** `CAT.tooling.Normalizer_Contract_Map`
**Generated export:** `Normalizer_Contract_Map.csv`
**Purpose:** contrato input→candidate→record/edge/evidence.

### Grain

One row represents a governed NDC observation or decision for `Normalizer_Contract_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: raw input slot. |
| `name` | human-readable name; local emphasis: candidate extraction. |
| `type` | object family/type; local emphasis: candidate extraction. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: run manifest. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: normalizer contract. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: normalizer contract. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: tool observation. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: candidate extraction. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: raw input slot. |
| `owner` | human/system owner; local emphasis: tool observation. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: artifact mapping. |
| `confidence` | low/medium/high/verified; local emphasis: raw input slot. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: raw input slot. |
| `updated_at` | timestamp of generation or curation; local emphasis: raw input slot. |

### Validators

- `Normalizer_Contract_Map` must preserve raw input slot; if missing, status becomes `needs_review`, not `ready`.
- `Normalizer_Contract_Map` must preserve normalizer contract; if missing, status becomes `needs_review`, not `ready`.
- `Normalizer_Contract_Map` must preserve candidate extraction; if missing, status becomes `needs_review`, not `ready`.
- `Normalizer_Contract_Map` must preserve tool observation; if missing, status becomes `needs_review`, not `ready`.
- `Normalizer_Contract_Map` must preserve artifact mapping; if missing, status becomes `needs_review`, not `ready`.
- `Normalizer_Contract_Map` must preserve safe ingestion; if missing, status becomes `needs_review`, not `ready`.
- `Normalizer_Contract_Map` must preserve source adapter; if missing, status becomes `needs_review`, not `ready`.
- `Normalizer_Contract_Map` must preserve run manifest; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Normalizer_Contract_Map.id.example",
  "name": "Normalizer_Contract_Map.name.example",
  "type": "Normalizer_Contract_Map.type.example",
  "scope_ref": "Normalizer_Contract_Map.scope_ref.example",
  "neutral_ref": "Normalizer_Contract_Map.neutral_ref.example",
  "surface_ref": "Normalizer_Contract_Map.surface_ref.example",
  "canonical_ref": "Normalizer_Contract_Map.canonical_ref.example",
  "evidence_ref": "Normalizer_Contract_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 55. Matrix_View_Catalog

**Group:** `matrix`
**View ID:** `CAT.matrix.Matrix_View_Catalog`
**Generated export:** `Matrix_View_Catalog.csv`
**Purpose:** definición de matrices generadas.

### Grain

One row represents a governed NDC observation or decision for `Matrix_View_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: export columns. |
| `name` | human-readable name; local emphasis: sort order. |
| `type` | object family/type; local emphasis: sort order. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: view grain. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: generated view. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: generated view. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: filter policy. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: sort order. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: export columns. |
| `owner` | human/system owner; local emphasis: filter policy. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: readiness rollup. |
| `confidence` | low/medium/high/verified; local emphasis: export columns. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: export columns. |
| `updated_at` | timestamp of generation or curation; local emphasis: export columns. |

### Validators

- `Matrix_View_Catalog` must preserve view grain; if missing, status becomes `needs_review`, not `ready`.
- `Matrix_View_Catalog` must preserve export columns; if missing, status becomes `needs_review`, not `ready`.
- `Matrix_View_Catalog` must preserve generated view; if missing, status becomes `needs_review`, not `ready`.
- `Matrix_View_Catalog` must preserve sort order; if missing, status becomes `needs_review`, not `ready`.
- `Matrix_View_Catalog` must preserve filter policy; if missing, status becomes `needs_review`, not `ready`.
- `Matrix_View_Catalog` must preserve readiness rollup; if missing, status becomes `needs_review`, not `ready`.
- `Matrix_View_Catalog` must preserve human review; if missing, status becomes `needs_review`, not `ready`.
- `Matrix_View_Catalog` must preserve dashboard query; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Matrix_View_Catalog.id.example",
  "name": "Matrix_View_Catalog.name.example",
  "type": "Matrix_View_Catalog.type.example",
  "scope_ref": "Matrix_View_Catalog.scope_ref.example",
  "neutral_ref": "Matrix_View_Catalog.neutral_ref.example",
  "surface_ref": "Matrix_View_Catalog.surface_ref.example",
  "canonical_ref": "Matrix_View_Catalog.canonical_ref.example",
  "evidence_ref": "Matrix_View_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 56. Dashboard_Query_Catalog

**Group:** `matrix`
**View ID:** `CAT.matrix.Dashboard_Query_Catalog`
**Generated export:** `Dashboard_Query_Catalog.csv`
**Purpose:** consultas/dashboards de revisión.

### Grain

One row represents a governed NDC observation or decision for `Dashboard_Query_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: generated view. |
| `name` | human-readable name; local emphasis: filter policy. |
| `type` | object family/type; local emphasis: filter policy. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: export columns. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: sort order. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: sort order. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: readiness rollup. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: filter policy. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: generated view. |
| `owner` | human/system owner; local emphasis: readiness rollup. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: human review. |
| `confidence` | low/medium/high/verified; local emphasis: generated view. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: generated view. |
| `updated_at` | timestamp of generation or curation; local emphasis: generated view. |

### Validators

- `Dashboard_Query_Catalog` must preserve view grain; if missing, status becomes `needs_review`, not `ready`.
- `Dashboard_Query_Catalog` must preserve export columns; if missing, status becomes `needs_review`, not `ready`.
- `Dashboard_Query_Catalog` must preserve generated view; if missing, status becomes `needs_review`, not `ready`.
- `Dashboard_Query_Catalog` must preserve sort order; if missing, status becomes `needs_review`, not `ready`.
- `Dashboard_Query_Catalog` must preserve filter policy; if missing, status becomes `needs_review`, not `ready`.
- `Dashboard_Query_Catalog` must preserve readiness rollup; if missing, status becomes `needs_review`, not `ready`.
- `Dashboard_Query_Catalog` must preserve human review; if missing, status becomes `needs_review`, not `ready`.
- `Dashboard_Query_Catalog` must preserve dashboard query; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Dashboard_Query_Catalog.id.example",
  "name": "Dashboard_Query_Catalog.name.example",
  "type": "Dashboard_Query_Catalog.type.example",
  "scope_ref": "Dashboard_Query_Catalog.scope_ref.example",
  "neutral_ref": "Dashboard_Query_Catalog.neutral_ref.example",
  "surface_ref": "Dashboard_Query_Catalog.surface_ref.example",
  "canonical_ref": "Dashboard_Query_Catalog.canonical_ref.example",
  "evidence_ref": "Dashboard_Query_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 57. Prisma_OCR_Entity_Blueprint

**Group:** `db_handoff`
**View ID:** `CAT.db_handoff.Prisma_OCR_Entity_Blueprint`
**Generated export:** `Prisma_OCR_Entity_Blueprint.csv`
**Purpose:** blueprint futuro entidades DB.

### Grain

One row represents a governed NDC observation or decision for `Prisma_OCR_Entity_Blueprint`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: unique constraint. |
| `name` | human-readable name; local emphasis: Prisma OCR. |
| `type` | object family/type; local emphasis: Prisma OCR. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: seed strategy. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: append-only decision. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: append-only decision. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: rollback plan. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: Prisma OCR. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: unique constraint. |
| `owner` | human/system owner; local emphasis: rollback plan. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: DB readiness. |
| `confidence` | low/medium/high/verified; local emphasis: unique constraint. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: unique constraint. |
| `updated_at` | timestamp of generation or curation; local emphasis: unique constraint. |

### Validators

- `Prisma_OCR_Entity_Blueprint` must preserve future table; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Entity_Blueprint` must preserve migration blocker; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Entity_Blueprint` must preserve seed strategy; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Entity_Blueprint` must preserve unique constraint; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Entity_Blueprint` must preserve append-only decision; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Entity_Blueprint` must preserve Prisma OCR; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Entity_Blueprint` must preserve rollback plan; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Entity_Blueprint` must preserve DB readiness; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Prisma_OCR_Entity_Blueprint.id.example",
  "name": "Prisma_OCR_Entity_Blueprint.name.example",
  "type": "Prisma_OCR_Entity_Blueprint.type.example",
  "scope_ref": "Prisma_OCR_Entity_Blueprint.scope_ref.example",
  "neutral_ref": "Prisma_OCR_Entity_Blueprint.neutral_ref.example",
  "surface_ref": "Prisma_OCR_Entity_Blueprint.surface_ref.example",
  "canonical_ref": "Prisma_OCR_Entity_Blueprint.canonical_ref.example",
  "evidence_ref": "Prisma_OCR_Entity_Blueprint.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 58. Prisma_OCR_Relationship_Blueprint

**Group:** `db_handoff`
**View ID:** `CAT.db_handoff.Prisma_OCR_Relationship_Blueprint`
**Generated export:** `Prisma_OCR_Relationship_Blueprint.csv`
**Purpose:** blueprint futuro relaciones DB.

### Grain

One row represents a governed NDC observation or decision for `Prisma_OCR_Relationship_Blueprint`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: append-only decision. |
| `name` | human-readable name; local emphasis: rollback plan. |
| `type` | object family/type; local emphasis: rollback plan. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: unique constraint. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: Prisma OCR. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: Prisma OCR. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: DB readiness. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: rollback plan. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: append-only decision. |
| `owner` | human/system owner; local emphasis: DB readiness. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: future table. |
| `confidence` | low/medium/high/verified; local emphasis: append-only decision. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: append-only decision. |
| `updated_at` | timestamp of generation or curation; local emphasis: append-only decision. |

### Validators

- `Prisma_OCR_Relationship_Blueprint` must preserve future table; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Relationship_Blueprint` must preserve migration blocker; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Relationship_Blueprint` must preserve seed strategy; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Relationship_Blueprint` must preserve unique constraint; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Relationship_Blueprint` must preserve append-only decision; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Relationship_Blueprint` must preserve Prisma OCR; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Relationship_Blueprint` must preserve rollback plan; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Relationship_Blueprint` must preserve DB readiness; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Prisma_OCR_Relationship_Blueprint.id.example",
  "name": "Prisma_OCR_Relationship_Blueprint.name.example",
  "type": "Prisma_OCR_Relationship_Blueprint.type.example",
  "scope_ref": "Prisma_OCR_Relationship_Blueprint.scope_ref.example",
  "neutral_ref": "Prisma_OCR_Relationship_Blueprint.neutral_ref.example",
  "surface_ref": "Prisma_OCR_Relationship_Blueprint.surface_ref.example",
  "canonical_ref": "Prisma_OCR_Relationship_Blueprint.canonical_ref.example",
  "evidence_ref": "Prisma_OCR_Relationship_Blueprint.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 59. Prisma_OCR_Seed_Strategy

**Group:** `db_handoff`
**View ID:** `CAT.db_handoff.Prisma_OCR_Seed_Strategy`
**Generated export:** `Prisma_OCR_Seed_Strategy.csv`
**Purpose:** seeds futuros desde registries/curation.

### Grain

One row represents a governed NDC observation or decision for `Prisma_OCR_Seed_Strategy`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: Prisma OCR. |
| `name` | human-readable name; local emphasis: DB readiness. |
| `type` | object family/type; local emphasis: DB readiness. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: append-only decision. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: rollback plan. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: rollback plan. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: future table. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: DB readiness. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: Prisma OCR. |
| `owner` | human/system owner; local emphasis: future table. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: migration blocker. |
| `confidence` | low/medium/high/verified; local emphasis: Prisma OCR. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: Prisma OCR. |
| `updated_at` | timestamp of generation or curation; local emphasis: Prisma OCR. |

### Validators

- `Prisma_OCR_Seed_Strategy` must preserve future table; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Seed_Strategy` must preserve migration blocker; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Seed_Strategy` must preserve seed strategy; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Seed_Strategy` must preserve unique constraint; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Seed_Strategy` must preserve append-only decision; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Seed_Strategy` must preserve Prisma OCR; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Seed_Strategy` must preserve rollback plan; if missing, status becomes `needs_review`, not `ready`.
- `Prisma_OCR_Seed_Strategy` must preserve DB readiness; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Prisma_OCR_Seed_Strategy.id.example",
  "name": "Prisma_OCR_Seed_Strategy.name.example",
  "type": "Prisma_OCR_Seed_Strategy.type.example",
  "scope_ref": "Prisma_OCR_Seed_Strategy.scope_ref.example",
  "neutral_ref": "Prisma_OCR_Seed_Strategy.neutral_ref.example",
  "surface_ref": "Prisma_OCR_Seed_Strategy.surface_ref.example",
  "canonical_ref": "Prisma_OCR_Seed_Strategy.canonical_ref.example",
  "evidence_ref": "Prisma_OCR_Seed_Strategy.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 60. Migration_Readiness_Checklist

**Group:** `db_handoff`
**View ID:** `CAT.db_handoff.Migration_Readiness_Checklist`
**Generated export:** `Migration_Readiness_Checklist.csv`
**Purpose:** checklist para permitir db1.

### Grain

One row represents a governed NDC observation or decision for `Migration_Readiness_Checklist`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: rollback plan. |
| `name` | human-readable name; local emphasis: future table. |
| `type` | object family/type; local emphasis: future table. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: Prisma OCR. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: DB readiness. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: DB readiness. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: migration blocker. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: future table. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: rollback plan. |
| `owner` | human/system owner; local emphasis: migration blocker. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: seed strategy. |
| `confidence` | low/medium/high/verified; local emphasis: rollback plan. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: rollback plan. |
| `updated_at` | timestamp of generation or curation; local emphasis: rollback plan. |

### Validators

- `Migration_Readiness_Checklist` must preserve future table; if missing, status becomes `needs_review`, not `ready`.
- `Migration_Readiness_Checklist` must preserve migration blocker; if missing, status becomes `needs_review`, not `ready`.
- `Migration_Readiness_Checklist` must preserve seed strategy; if missing, status becomes `needs_review`, not `ready`.
- `Migration_Readiness_Checklist` must preserve unique constraint; if missing, status becomes `needs_review`, not `ready`.
- `Migration_Readiness_Checklist` must preserve append-only decision; if missing, status becomes `needs_review`, not `ready`.
- `Migration_Readiness_Checklist` must preserve Prisma OCR; if missing, status becomes `needs_review`, not `ready`.
- `Migration_Readiness_Checklist` must preserve rollback plan; if missing, status becomes `needs_review`, not `ready`.
- `Migration_Readiness_Checklist` must preserve DB readiness; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Migration_Readiness_Checklist.id.example",
  "name": "Migration_Readiness_Checklist.name.example",
  "type": "Migration_Readiness_Checklist.type.example",
  "scope_ref": "Migration_Readiness_Checklist.scope_ref.example",
  "neutral_ref": "Migration_Readiness_Checklist.neutral_ref.example",
  "surface_ref": "Migration_Readiness_Checklist.surface_ref.example",
  "canonical_ref": "Migration_Readiness_Checklist.canonical_ref.example",
  "evidence_ref": "Migration_Readiness_Checklist.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 61. Vertical_Translation_Catalog

**Group:** `vertical`
**View ID:** `CAT.vertical.Vertical_Translation_Catalog`
**Generated export:** `Vertical_Translation_Catalog.csv`
**Purpose:** traducción a abarrotes/restaurante/taller/bodega/renta.

### Grain

One row represents a governed NDC observation or decision for `Vertical_Translation_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: workflow equivalent. |
| `name` | human-readable name; local emphasis: vertical wording. |
| `type` | object family/type; local emphasis: vertical wording. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: surface reuse. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: translation layer. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: translation layer. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: common skeleton. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: vertical wording. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: workflow equivalent. |
| `owner` | human/system owner; local emphasis: common skeleton. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: industry variation. |
| `confidence` | low/medium/high/verified; local emphasis: workflow equivalent. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: workflow equivalent. |
| `updated_at` | timestamp of generation or curation; local emphasis: workflow equivalent. |

### Validators

- `Vertical_Translation_Catalog` must preserve translation layer; if missing, status becomes `needs_review`, not `ready`.
- `Vertical_Translation_Catalog` must preserve vertical wording; if missing, status becomes `needs_review`, not `ready`.
- `Vertical_Translation_Catalog` must preserve common skeleton; if missing, status becomes `needs_review`, not `ready`.
- `Vertical_Translation_Catalog` must preserve industry variation; if missing, status becomes `needs_review`, not `ready`.
- `Vertical_Translation_Catalog` must preserve capability pack; if missing, status becomes `needs_review`, not `ready`.
- `Vertical_Translation_Catalog` must preserve role vocabulary; if missing, status becomes `needs_review`, not `ready`.
- `Vertical_Translation_Catalog` must preserve surface reuse; if missing, status becomes `needs_review`, not `ready`.
- `Vertical_Translation_Catalog` must preserve workflow equivalent; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Vertical_Translation_Catalog.id.example",
  "name": "Vertical_Translation_Catalog.name.example",
  "type": "Vertical_Translation_Catalog.type.example",
  "scope_ref": "Vertical_Translation_Catalog.scope_ref.example",
  "neutral_ref": "Vertical_Translation_Catalog.neutral_ref.example",
  "surface_ref": "Vertical_Translation_Catalog.surface_ref.example",
  "canonical_ref": "Vertical_Translation_Catalog.canonical_ref.example",
  "evidence_ref": "Vertical_Translation_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 62. Abarrotes_RC1_Trace_Map

**Group:** `vertical`
**View ID:** `CAT.vertical.Abarrotes_RC1_Trace_Map`
**Generated export:** `Abarrotes_RC1_Trace_Map.csv`
**Purpose:** trazabilidad abarrotes RC1.

### Grain

One row represents a governed NDC observation or decision for `Abarrotes_RC1_Trace_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: translation layer. |
| `name` | human-readable name; local emphasis: common skeleton. |
| `type` | object family/type; local emphasis: common skeleton. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: workflow equivalent. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: vertical wording. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: vertical wording. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: industry variation. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: common skeleton. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: translation layer. |
| `owner` | human/system owner; local emphasis: industry variation. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: capability pack. |
| `confidence` | low/medium/high/verified; local emphasis: translation layer. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: translation layer. |
| `updated_at` | timestamp of generation or curation; local emphasis: translation layer. |

### Validators

- `Abarrotes_RC1_Trace_Map` must preserve translation layer; if missing, status becomes `needs_review`, not `ready`.
- `Abarrotes_RC1_Trace_Map` must preserve vertical wording; if missing, status becomes `needs_review`, not `ready`.
- `Abarrotes_RC1_Trace_Map` must preserve common skeleton; if missing, status becomes `needs_review`, not `ready`.
- `Abarrotes_RC1_Trace_Map` must preserve industry variation; if missing, status becomes `needs_review`, not `ready`.
- `Abarrotes_RC1_Trace_Map` must preserve capability pack; if missing, status becomes `needs_review`, not `ready`.
- `Abarrotes_RC1_Trace_Map` must preserve role vocabulary; if missing, status becomes `needs_review`, not `ready`.
- `Abarrotes_RC1_Trace_Map` must preserve surface reuse; if missing, status becomes `needs_review`, not `ready`.
- `Abarrotes_RC1_Trace_Map` must preserve workflow equivalent; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Abarrotes_RC1_Trace_Map.id.example",
  "name": "Abarrotes_RC1_Trace_Map.name.example",
  "type": "Abarrotes_RC1_Trace_Map.type.example",
  "scope_ref": "Abarrotes_RC1_Trace_Map.scope_ref.example",
  "neutral_ref": "Abarrotes_RC1_Trace_Map.neutral_ref.example",
  "surface_ref": "Abarrotes_RC1_Trace_Map.surface_ref.example",
  "canonical_ref": "Abarrotes_RC1_Trace_Map.canonical_ref.example",
  "evidence_ref": "Abarrotes_RC1_Trace_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 63. Support_Ticket_Catalog

**Group:** `ops`
**View ID:** `CAT.ops.Support_Ticket_Catalog`
**Generated export:** `Support_Ticket_Catalog.csv`
**Purpose:** tickets desde drift/evidence/readiness.

### Grain

One row represents a governed NDC observation or decision for `Support_Ticket_Catalog`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: risk score. |
| `name` | human-readable name; local emphasis: change impact. |
| `type` | object family/type; local emphasis: change impact. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: owner. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: support ticket. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: support ticket. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: triage. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: change impact. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: risk score. |
| `owner` | human/system owner; local emphasis: triage. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: priority. |
| `confidence` | low/medium/high/verified; local emphasis: risk score. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: risk score. |
| `updated_at` | timestamp of generation or curation; local emphasis: risk score. |

### Validators

- `Support_Ticket_Catalog` must preserve owner; if missing, status becomes `needs_review`, not `ready`.
- `Support_Ticket_Catalog` must preserve risk score; if missing, status becomes `needs_review`, not `ready`.
- `Support_Ticket_Catalog` must preserve support ticket; if missing, status becomes `needs_review`, not `ready`.
- `Support_Ticket_Catalog` must preserve change impact; if missing, status becomes `needs_review`, not `ready`.
- `Support_Ticket_Catalog` must preserve triage; if missing, status becomes `needs_review`, not `ready`.
- `Support_Ticket_Catalog` must preserve priority; if missing, status becomes `needs_review`, not `ready`.
- `Support_Ticket_Catalog` must preserve operational risk; if missing, status becomes `needs_review`, not `ready`.
- `Support_Ticket_Catalog` must preserve next action; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Support_Ticket_Catalog.id.example",
  "name": "Support_Ticket_Catalog.name.example",
  "type": "Support_Ticket_Catalog.type.example",
  "scope_ref": "Support_Ticket_Catalog.scope_ref.example",
  "neutral_ref": "Support_Ticket_Catalog.neutral_ref.example",
  "surface_ref": "Support_Ticket_Catalog.surface_ref.example",
  "canonical_ref": "Support_Ticket_Catalog.canonical_ref.example",
  "evidence_ref": "Support_Ticket_Catalog.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 64. Owner_Accountability_Map

**Group:** `ops`
**View ID:** `CAT.ops.Owner_Accountability_Map`
**Generated export:** `Owner_Accountability_Map.csv`
**Purpose:** owners de decisiones/datos/capabilities.

### Grain

One row represents a governed NDC observation or decision for `Owner_Accountability_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: support ticket. |
| `name` | human-readable name; local emphasis: triage. |
| `type` | object family/type; local emphasis: triage. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: risk score. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: change impact. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: change impact. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: priority. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: triage. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: support ticket. |
| `owner` | human/system owner; local emphasis: priority. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: operational risk. |
| `confidence` | low/medium/high/verified; local emphasis: support ticket. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: support ticket. |
| `updated_at` | timestamp of generation or curation; local emphasis: support ticket. |

### Validators

- `Owner_Accountability_Map` must preserve owner; if missing, status becomes `needs_review`, not `ready`.
- `Owner_Accountability_Map` must preserve risk score; if missing, status becomes `needs_review`, not `ready`.
- `Owner_Accountability_Map` must preserve support ticket; if missing, status becomes `needs_review`, not `ready`.
- `Owner_Accountability_Map` must preserve change impact; if missing, status becomes `needs_review`, not `ready`.
- `Owner_Accountability_Map` must preserve triage; if missing, status becomes `needs_review`, not `ready`.
- `Owner_Accountability_Map` must preserve priority; if missing, status becomes `needs_review`, not `ready`.
- `Owner_Accountability_Map` must preserve operational risk; if missing, status becomes `needs_review`, not `ready`.
- `Owner_Accountability_Map` must preserve next action; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Owner_Accountability_Map.id.example",
  "name": "Owner_Accountability_Map.name.example",
  "type": "Owner_Accountability_Map.type.example",
  "scope_ref": "Owner_Accountability_Map.scope_ref.example",
  "neutral_ref": "Owner_Accountability_Map.neutral_ref.example",
  "surface_ref": "Owner_Accountability_Map.surface_ref.example",
  "canonical_ref": "Owner_Accountability_Map.canonical_ref.example",
  "evidence_ref": "Owner_Accountability_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 65. Risk_Score_Map

**Group:** `ops`
**View ID:** `CAT.ops.Risk_Score_Map`
**Generated export:** `Risk_Score_Map.csv`
**Purpose:** riesgo por huecos/conflicts/stale/claims.

### Grain

One row represents a governed NDC observation or decision for `Risk_Score_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: change impact. |
| `name` | human-readable name; local emphasis: priority. |
| `type` | object family/type; local emphasis: priority. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: support ticket. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: triage. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: triage. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: operational risk. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: priority. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: change impact. |
| `owner` | human/system owner; local emphasis: operational risk. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: next action. |
| `confidence` | low/medium/high/verified; local emphasis: change impact. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: change impact. |
| `updated_at` | timestamp of generation or curation; local emphasis: change impact. |

### Validators

- `Risk_Score_Map` must preserve owner; if missing, status becomes `needs_review`, not `ready`.
- `Risk_Score_Map` must preserve risk score; if missing, status becomes `needs_review`, not `ready`.
- `Risk_Score_Map` must preserve support ticket; if missing, status becomes `needs_review`, not `ready`.
- `Risk_Score_Map` must preserve change impact; if missing, status becomes `needs_review`, not `ready`.
- `Risk_Score_Map` must preserve triage; if missing, status becomes `needs_review`, not `ready`.
- `Risk_Score_Map` must preserve priority; if missing, status becomes `needs_review`, not `ready`.
- `Risk_Score_Map` must preserve operational risk; if missing, status becomes `needs_review`, not `ready`.
- `Risk_Score_Map` must preserve next action; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Risk_Score_Map.id.example",
  "name": "Risk_Score_Map.name.example",
  "type": "Risk_Score_Map.type.example",
  "scope_ref": "Risk_Score_Map.scope_ref.example",
  "neutral_ref": "Risk_Score_Map.neutral_ref.example",
  "surface_ref": "Risk_Score_Map.surface_ref.example",
  "canonical_ref": "Risk_Score_Map.canonical_ref.example",
  "evidence_ref": "Risk_Score_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.


## 66. Change_Impact_Map

**Group:** `ops`
**View ID:** `CAT.ops.Change_Impact_Map`
**Generated export:** `Change_Impact_Map.csv`
**Purpose:** impacto de cambios entity/capability/surface/widget/API/DB.

### Grain

One row represents a governed NDC observation or decision for `Change_Impact_Map`. The row is not canonical by itself. It is an export of records, edges, evidence and curation.

### Required fields

| Field | Meaning |
|---|---|
| `id` | stable identifier for this catalog row; local emphasis: triage. |
| `name` | human-readable name; local emphasis: operational risk. |
| `type` | object family/type; local emphasis: operational risk. |
| `scope_ref` | tenant/business/store/device scope where applicable; local emphasis: change impact. |
| `neutral_ref` | ENT/EVT/ACT/MET/CAP/CAN target if applicable; local emphasis: priority. |
| `surface_ref` | SURF/PNL/WID/CHT target if applicable; local emphasis: priority. |
| `canonical_ref` | CAN.* projection if applicable; local emphasis: next action. |
| `evidence_ref` | EVD.* record or artifact binding; local emphasis: operational risk. |
| `source_ref` | tool/doc/runtime/source that produced or authorized the row; local emphasis: triage. |
| `owner` | human/system owner; local emphasis: next action. |
| `status` | candidate/defined/ready/blocked/needs_review/deprecated; local emphasis: owner. |
| `confidence` | low/medium/high/verified; local emphasis: triage. |
| `risk_score` | 0-100 qualitative risk score; local emphasis: triage. |
| `updated_at` | timestamp of generation or curation; local emphasis: triage. |

### Validators

- `Change_Impact_Map` must preserve owner; if missing, status becomes `needs_review`, not `ready`.
- `Change_Impact_Map` must preserve risk score; if missing, status becomes `needs_review`, not `ready`.
- `Change_Impact_Map` must preserve support ticket; if missing, status becomes `needs_review`, not `ready`.
- `Change_Impact_Map` must preserve change impact; if missing, status becomes `needs_review`, not `ready`.
- `Change_Impact_Map` must preserve triage; if missing, status becomes `needs_review`, not `ready`.
- `Change_Impact_Map` must preserve priority; if missing, status becomes `needs_review`, not `ready`.
- `Change_Impact_Map` must preserve operational risk; if missing, status becomes `needs_review`, not `ready`.
- `Change_Impact_Map` must preserve next action; if missing, status becomes `needs_review`, not `ready`.


### Example row

```json
{
  "id": "Change_Impact_Map.id.example",
  "name": "Change_Impact_Map.name.example",
  "type": "Change_Impact_Map.type.example",
  "scope_ref": "Change_Impact_Map.scope_ref.example",
  "neutral_ref": "Change_Impact_Map.neutral_ref.example",
  "surface_ref": "Change_Impact_Map.surface_ref.example",
  "canonical_ref": "Change_Impact_Map.canonical_ref.example",
  "evidence_ref": "Change_Impact_Map.evidence_ref.example"
}
```

### Extension policy

- Add optional fields first.
- Register breaking changes in `Change_Impact_Map`.
- Preserve `id`, `scope_ref`, `source_ref`, `evidence_ref` and `status`.
- Never edit the generated CSV as truth.
- Use curation when human judgment changes mapping or readiness.

### Useful joins

- Join with `Evidence_Index` through `evidence_ref`.
- Join with `Data_Lineage_Map` through `neutral_ref` or `canonical_ref`.
- Join with `Surface_Projection_Map` through `surface_ref`.
- Join with `Curation_Decision_Log` when the row is promoted, rejected or overridden.
