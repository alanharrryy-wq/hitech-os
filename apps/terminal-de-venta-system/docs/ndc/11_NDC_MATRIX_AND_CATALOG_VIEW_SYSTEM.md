# 11. NDC Matrix and Catalog View System

> Estado: NDC CANON1 repack validado. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas; la verdad vive en records, edges, evidence y curation.

## 11.1 Propósito

Este documento define el sistema completo de catálogos y matrices NDC. Su trabajo no es producir una sábana de Excel con pretensiones de oráculo, sino convertir el Neutral Data Center en vistas humanas, exportables, validables e incrementales. La matriz sirve para revisar; el catálogo sirve para gobernar; el record neutral sirve para identificar; el edge sirve para explicar; la evidencia sirve para probar; la curation sirve para decidir.

## 11.2 Cadena regenerativa

```text
raw_inputs
→ candidates
→ normalized records
→ normalized edges
→ evidence bindings
→ curation decisions
→ catalog views
→ matrix exports
→ reports / dashboards / Prisma OCR handoff later
```

La regla de oro: ningún CSV generado se edita a mano. Una corrección humana entra por curation y el siguiente ingest/normalize regenera la vista.

## 11.3 Familias de catálogos

| Familia | Función |
|---|---|
| scope | Identidad operacional: tenant, business, store/site, terminal, device, user, role, license, plan, module, session. |
| neutral | Significado PRISMA reutilizable: entidad, evento, acción, estado, métrica, alerta, evidencia, capacidad, canonical. |
| capability | Módulos, packs, licencias, grants, monetización y readiness comercial. |
| lineage | Provenance, sync, source device, source surface, outbox, canonical path y agentes responsables. |
| canonical | Verdad consolidada, estados canónicos, reconciliación y drift. |
| projection | Runtimes, superficies, representaciones y boundary interno/cliente. |
| ui | Componentes, paneles, widgets, formularios, tablas, estados visuales y acciones. |
| chartlab | Analytics, métricas, charts, widgets visuales y oportunidades monetizables. |
| data | Bindings, APIs, datasets, DB hints, quality rules y contratos de datos. |
| evidence | Artifacts, runtime evidence, tool outputs, screenshots, DOM, traces, API/DB/outbox proof. |
| curation | Decisiones humanas, aliases, overrides, promotions, notes y rechazos. |
| tooling | Cobertura de herramientas, authority, Factory Ledger y continuidad. |
| governance | Claims, blockers, risk, readiness y gates. |
| handoff | Preparación para Prisma OCR posterior, sin crear DB todavía. |

## 11.4 Catálogo maestro de vistas

| Catálogo | Grupo | Descripción | Export |
|---|---|---|---|
| Scope_Registry | scope | All neutral operational identities: tenant, business, site, terminal, device, user, role, license, module, plan, surface, session. | Scope_Registry.csv |
| Tenant_Master | scope | Commercial tenant master record, lifecycle, isolation, plan, owner, billing and data boundary. | Tenant_Master.csv |
| Business_Site_Map | scope | Business hierarchy and store/site topology under each tenant. | Business_Site_Map.csv |
| Terminal_Device_Map | scope | Terminals, physical devices, logical device identity, claim status and authorized surfaces. | Terminal_Device_Map.csv |
| Device_License_Map | scope | License-device-slot assignments and replacement history. | Device_License_Map.csv |
| Role_Module_Map | scope | Roles, grants, modules and surface visibility. | Role_Module_Map.csv |
| Session_Context_Map | scope | Cash, user, device and runtime sessions that give context to operational events. | Session_Context_Map.csv |
| Neutral_Object_Registry | neutral | ENT/EVT/ACT/STA/MET/ALT/EVD/CAP/CAN registry with lifecycle and ownership. | Neutral_Object_Registry.csv |
| Entity_Catalog | neutral | Business entities independent of UI/app implementation. | Entity_Catalog.csv |
| Event_Catalog | neutral | Events emitted by operations, normalized to PRISMA event grammar. | Event_Catalog.csv |
| Action_Catalog | neutral | Actions users/systems can perform and the events they emit. | Action_Catalog.csv |
| State_Catalog | neutral | Operational states such as sync, license, sale, device, stock and evidence states. | State_Catalog.csv |
| Metric_Catalog | neutral | Metrics, formulas, datasets, periods, scope and chart destinations. | Metric_Catalog.csv |
| Alert_Catalog | neutral | Alerts, triggers, owners, severity and target surfaces. | Alert_Catalog.csv |
| Evidence_Object_Catalog | neutral | Evidence objects and how they support records, events and claims. | Evidence_Object_Catalog.csv |
| Capability_Catalog | capability | Business capabilities, module ownership, visibility, monetization and evidence. | Capability_Catalog.csv |
| Module_Registry | capability | Modules/add-ons/packs that activate capabilities by tenant/license. | Module_Registry.csv |
| Capability_Pack_Map | capability | Packs such as Abarrotes Base/Pro/Premium and their included capabilities. | Capability_Pack_Map.csv |
| License_Plan_Grant_Map | capability | Plan, license, role, module and surface grants. | License_Plan_Grant_Map.csv |
| Commercial_Readiness_Map | capability | Whether a capability can be sold, demoed or must remain internal. | Commercial_Readiness_Map.csv |
| Event_Provenance_Log | lineage | Normalized event provenance: source, actor, device, surface, time, payload and evidence. | Event_Provenance_Log.csv |
| Lineage_Edge_Map | lineage | Entity/event/action/metric/canonical lineage edges. | Lineage_Edge_Map.csv |
| Sync_Outbox_Map | lineage | Outbox, queue, cloud gateway and sync stages. | Sync_Outbox_Map.csv |
| Provenance_Agent_Map | lineage | Actors, devices, tools and systems responsible for activities. | Provenance_Agent_Map.csv |
| Canonical_Projection_Map | canonical | Consolidated truth projections such as CAN.sale, CAN.stock, CAN.metric. | Canonical_Projection_Map.csv |
| Canonical_Status_Map | canonical | Accepted, pending, rejected, duplicate and stale canonical states. | Canonical_Status_Map.csv |
| Reconciliation_Case_Map | canonical | Explains discrepancies such as Tablet 231 vs PC 228. | Reconciliation_Case_Map.csv |
| Drift_And_Reconciliation_Map | canonical | Drift cases across UI, DB, runtime, evidence and canonical views. | Drift_And_Reconciliation_Map.csv |
| Surface_Projection_Map | projection | Where neutral objects appear across Tablet, PC, Mobile, Chart Lab, Control Center, Portal. | Surface_Projection_Map.csv |
| Runtime_Surface_Map | projection | Runtime ports/apps and their surfaces, boundaries and users. | Runtime_Surface_Map.csv |
| App_Surface_Readiness_Map | projection | Readiness of each surface as a projection, not as source of truth. | App_Surface_Readiness_Map.csv |
| Portal_Control_Surface_Map | projection | Portal/Control Center/Command Center split and client/internal exposure. | Portal_Control_Surface_Map.csv |
| UI_Component_Atlas | ui | Widgets/components, location, states, actions and bindings. | UI_Component_Atlas.csv |
| Panel_Catalog | ui | Panel types, layout zones, data requirements and governed states. | Panel_Catalog.csv |
| Widget_Catalog | ui | KPI cards, tables, buttons, dropdowns, forms, charts, drawers, modals, toasts, nav items. | Widget_Catalog.csv |
| Panel_Insight_Catalog | ui | Human-readable panel insights, explaining what a panel decides or proves. | Panel_Insight_Catalog.csv |
| Interaction_Action_Map | ui | UI interactions mapped to neutral actions and emitted events. | Interaction_Action_Map.csv |
| Form_Field_Catalog | ui | Fields, validation, source entity, sensitive status and data binding. | Form_Field_Catalog.csv |
| Table_Column_Catalog | ui | Table columns and their neutral/canonical bindings. | Table_Column_Catalog.csv |
| Navigation_Route_Map | ui | Routes, tabs, nav items and their surface/context meaning. | Navigation_Route_Map.csv |
| Visual_State_Catalog | ui | Loading, empty, error, synced, pending, stale, locked, unauthorized and review states. | Visual_State_Catalog.csv |
| ChartLab_Metric_Map | chartlab | Chart Lab metric formulas, visual specs, destinations and pricing class. | ChartLab_Metric_Map.csv |
| Chart_Widget_Catalog | chartlab | Chart widgets, ECharts/spec metadata, required dataset and UX constraints. | Chart_Widget_Catalog.csv |
| Analytics_Opportunity_Map | chartlab | Analytics opportunities, commercial value, required data and target surfaces. | Analytics_Opportunity_Map.csv |
| Dataset_Contract_Map | data | Datasets, producers, consumers, fields, quality and ownership. | Dataset_Contract_Map.csv |
| Data_Binding_Map | data | Binds UI/chart/API/table fields to neutral/canonical objects. | Data_Binding_Map.csv |
| API_Endpoint_Map | data | APIs, events, entities, auth, scope and evidence. | API_Endpoint_Map.csv |
| DB_Table_Field_Map | data | Future DB mapping hints without declaring Prisma OCR DB yet. | DB_Table_Field_Map.csv |
| Data_Quality_Rule_Map | data | Completeness, uniqueness, freshness, validity and reconciliation rules. | Data_Quality_Rule_Map.csv |
| Evidence_Readiness_Map | evidence | Evidence per record/edge/catalog/export and whether it is ready or needs review. | Evidence_Readiness_Map.csv |
| Evidence_Source_Map | evidence | Tool/source output mapping: Code Atlas, DB Glass, Mamastrophic, ScreensQA, Chart Lab, Factory Ledger, Mesh. | Evidence_Source_Map.csv |
| Artifact_Index | evidence | Raw inputs and extracted artifacts with classification. | Artifact_Index.csv |
| Runtime_Evidence_Map | evidence | Screenshots, DOM, traces, network, DB rows, API responses, outbox events and smokes. | Runtime_Evidence_Map.csv |
| Curation_Decision_Log | curation | Human decisions: alias, override, canonical promotion, reject, split, merge, note. | Curation_Decision_Log.csv |
| Alias_Registry | curation | Human-approved aliases from tool names to neutral IDs. | Alias_Registry.csv |
| Override_Registry | curation | Governed overrides that change generated inference. | Override_Registry.csv |
| Canonical_Promotion_Queue | curation | Candidates waiting to become canonical. | Canonical_Promotion_Queue.csv |
| Review_Notes_Index | curation | Notes that explain why a candidate remains uncertain. | Review_Notes_Index.csv |
| Tool_Coverage_Map | tooling | What each tool contributed and where gaps remain. | Tool_Coverage_Map.csv |
| Authority_Coverage_Map | tooling | Authority Mesh / governance coverage over catalogs and surfaces. | Authority_Coverage_Map.csv |
| Factory_Ledger_Link_Map | tooling | Factory Ledger anti-retrabajo links to NDC records and decisions. | Factory_Ledger_Link_Map.csv |
| No_Humo_Claim_Map | governance | Claims allowed/prohibited by evidence, scope, license and surface. | No_Humo_Claim_Map.csv |
| Risk_Blocker_Map | governance | Risks and blockers for normalization, projection, evidence and DB handoff. | Risk_Blocker_Map.csv |
| Release_Readiness_Map | governance | Readiness gates for demo, RC, live, premium and enterprise states. | Release_Readiness_Map.csv |
| OCR_Handoff_Map | handoff | Future Prisma OCR table/model/seed candidates with blocked/ready status. | OCR_Handoff_Map.csv |
| Seed_Strategy_Map | handoff | Which docs/canon/curation records can become seeds later. | Seed_Strategy_Map.csv |

## 11.5 Columnas mínimas por catálogo

Cada catálogo puede crecer sin romper compatibilidad si conserva sus columnas base y agrega columnas opcionales al final. No se eliminan columnas sin migración documental.

| Catálogo | Columnas base |
|---|---|
| Scope_Registry | scope_id,scope_type,parent_scope_id,display_name,status,owner,evidence_count,confidence,curation_state |
| Tenant_Master | tenant_id,name,legal_name,commercial_status,plan_id,license_id,primary_contact,data_region,status,evidence_ref |
| Business_Site_Map | tenant_id,business_id,site_id,parent_site_id,site_type,address_label,status,device_count,terminal_count |
| Terminal_Device_Map | terminal_id,device_id,device_kind,slot_id,license_id,source_surface,claim_status,last_seen_at,health_state |
| Device_License_Map | license_id,slot_id,device_id,device_kind,surface_grants,module_grants,claimed_at,replaced_by,status |
| Role_Module_Map | role_id,module_id,capability_id,surface_id,permission_level,visibility,license_required,status |
| Session_Context_Map | session_id,session_type,tenant_id,store_id,device_id,user_id,started_at,ended_at,status |
| Neutral_Object_Registry | object_id,prefix,domain,display_name,definition,owner,status,canonical_allowed,evidence_required |
| Entity_Catalog | entity_id,domain,definition,primary_scope,required_events,canonical_projection,status |
| Event_Catalog | event_id,type,subject_entity,action_id,required_scope,producer_surface,required_payload,status |
| Action_Catalog | action_id,actor_role,source_surface,emits_event,writes_entity,requires_license,requires_evidence |
| State_Catalog | state_id,state_family,allowed_values,default_state,terminal_states,drift_sensitive |
| Metric_Catalog | metric_id,formula_id,source_entities,grain,scope_required,chart_lab_allowed,license_required |
| Alert_Catalog | alert_id,trigger_metric,threshold_rule,severity,owner_role,target_surfaces,ack_event |
| Evidence_Object_Catalog | evidence_object_id,evidence_type,target_id,source_tool,artifact_uri,confidence,review_state |
| Capability_Catalog | capability_id,name,pricing_class,module_id,required_events,license_required,visible_surfaces,evidence_required |
| Module_Registry | module_id,name,origin_runtime,destination_surfaces,required_events,license_required,pricing_class,status |
| Capability_Pack_Map | pack_id,vertical,capability_id,included_by_default,addon_allowed,commercial_status |
| License_Plan_Grant_Map | plan_id,license_id,module_id,capability_id,role_id,surface_id,grant_state,limit_rule |
| Commercial_Readiness_Map | capability_id,pricing_class,claim_allowed,evidence_ready,license_ready,surface_ready,no_humo_status |
| Event_Provenance_Log | event_instance_id,event_id,tenant_id,device_id,source_surface,actor_id,occurred_at,sync_status,evidence_ref |
| Lineage_Edge_Map | edge_id,from_id,to_id,edge_type,confidence,evidence_ref,curation_state |
| Sync_Outbox_Map | outbox_id,event_instance_id,source_device,sync_state,last_attempt,canonical_projection,status_reason |
| Provenance_Agent_Map | agent_id,agent_type,role,device_id,tool_id,responsibility_scope,evidence_ref |
| Canonical_Projection_Map | canonical_id,source_entities,acceptance_rule,status_rule,reconciliation_rule,surface_outputs |
| Canonical_Status_Map | canonical_id,instance_id,canonical_status,sync_status,reason,last_evidence,review_required |
| Reconciliation_Case_Map | case_id,metric_id,scope_a,scope_b,observed_delta,cause_class,status,next_action |
| Drift_And_Reconciliation_Map | drift_id,drift_type,affected_ids,severity,cause_hypothesis,evidence_refs,owner,status |
| Surface_Projection_Map | surface_id,runtime_id,neutral_object_id,projection_role,visibility,license_required,status |
| Runtime_Surface_Map | runtime_id,port,surface_id,visibility,user_type,boundary,internal_default |
| App_Surface_Readiness_Map | surface_id,records_count,neutral_links,evidence_count,orphans,readiness,needs_review |
| Portal_Control_Surface_Map | surface_id,runtime_id,client_facing,role_scope,license_scope,exposure_gate,evidence_required |
| UI_Component_Atlas | ui_id,surface_id,zone_id,panel_id,component_type,neutral_object_id,action_id,state_id,status |
| Panel_Catalog | panel_id,panel_type,surface_id,zone_id,data_binding_id,allowed_widgets,empty_state,error_state |
| Widget_Catalog | widget_id,widget_type,panel_id,neutral_object_id,interaction_type,required_state,evidence_ref |
| Panel_Insight_Catalog | insight_id,panel_id,metric_id,decision_supported,owner_role,confidence,commercial_value |
| Interaction_Action_Map | ui_id,interaction,action_id,event_id,requires_confirm,requires_role,requires_evidence |
| Form_Field_Catalog | field_id,form_id,label,data_type,entity_field,validation_rule,sensitivity,required |
| Table_Column_Catalog | table_id,column_id,label,entity_field,metric_id,sortable,filterable,visibility_rule |
| Navigation_Route_Map | route_id,path,surface_id,zone_id,required_role,required_license,neutral_context |
| Visual_State_Catalog | state_id,applies_to,meaning,allowed_surfaces,required_copy,blocking_level |
| ChartLab_Metric_Map | chart_id,metric_id,formula_id,dataset_id,visual_type,destination_surfaces,pricing_class,status |
| Chart_Widget_Catalog | chart_widget_id,chart_id,panel_id,visual_encoding,required_grain,empty_state,license_required |
| Analytics_Opportunity_Map | opportunity_id,vertical,metric_id,value_story,target_surface,pricing_class,evidence_required |
| Dataset_Contract_Map | dataset_id,producer,consumer,grain,owner,quality_rules,schema_ref,contract_status |
| Data_Binding_Map | binding_id,consumer_id,source_object_id,source_field,canonical_id,transform_rule,quality_rule |
| API_Endpoint_Map | endpoint_id,path,method,reads,writes,emits_event,requires_role,tenant_scope_required |
| DB_Table_Field_Map | future_table,future_field,neutral_object_id,canonical_projection,sensitivity,required_index |
| Data_Quality_Rule_Map | rule_id,applies_to,rule_type,threshold,blocking_level,owner,evidence_ref |
| Evidence_Readiness_Map | target_id,evidence_count,source_tools,confidence,readiness,needs_review,missing_evidence |
| Evidence_Source_Map | source_id,tool_name,artifact_type,artifact_uri,produced_at,trust_level,scope_hint |
| Artifact_Index | artifact_id,raw_input_path,artifact_type,tool_name,hash,target_guess,review_state |
| Runtime_Evidence_Map | evidence_id,evidence_type,runtime_id,surface_id,target_id,artifact_uri,confidence |
| Curation_Decision_Log | decision_id,decision_type,target_id,previous_value,new_value,reason,author,created_at |
| Alias_Registry | alias_id,source_name,canonical_id,context,confidence,approved_by,status |
| Override_Registry | override_id,target_id,field,generated_value,override_value,reason,expiry,status |
| Canonical_Promotion_Queue | candidate_id,target_id,required_evidence,missing_evidence,reviewer,status |
| Review_Notes_Index | note_id,target_id,note_type,body,owner,next_action,status |
| Tool_Coverage_Map | tool_name,records,edges,evidence,orphan_count,high_confidence_count,missing_slots |
| Authority_Coverage_Map | authority_id,target_id,governing_doc,gate,status,missing_contracts |
| Factory_Ledger_Link_Map | ledger_entry_id,target_id,decision_type,status,continuation_ref,result_zip |
| No_Humo_Claim_Map | claim_id,capability_id,evidence_ready,license_ready,limit_declared,claim_status |
| Risk_Blocker_Map | risk_id,target_id,risk_type,severity,blocking_rule,owner,next_action |
| Release_Readiness_Map | target_id,release_gate,status,evidence_count,blocking_risks,decision_required |
| OCR_Handoff_Map | handoff_id,neutral_object_id,recommended_model,required_edges,required_evidence,status,blocked_reason |
| Seed_Strategy_Map | seed_id,source_doc,source_record,target_model,seed_type,stability,review_required |

## 11.6 Contrato común de export

Todo export debe declarar metadata acompañante en JSON para evitar CSV huérfano:

```json
{
  "matrix_id": "Surface_Projection_Map",
  "generated_from": ["records", "edges", "evidence", "curation"],
  "generated_at": "<iso8601>",
  "generator": "ndc-normalize2-or-later",
  "schema_version": "ndc.catalog.v1",
  "row_count": 0,
  "source_hashes": [],
  "curation_applied": true,
  "readiness": "DRAFT|NEEDS_REVIEW|READY|BLOCKED",
  "no_manual_edit": true
}
```

## 11.7 Reglas de extensión

1. Un catálogo nuevo debe pertenecer a una familia.
2. Debe tener nombre `Pascal_Case_Map` o `Pascal_Case_Catalog` si es vista exportada.
3. Debe declarar qué records consume, qué edges requiere, qué evidencias acepta y qué curation puede modificarlo.
4. Debe tener owner conceptual: scope, neutral, canonical, projection, ui, chartlab, data, evidence, governance o handoff.
5. Debe tener estado: `DRAFT`, `ACTIVE`, `NEEDS_REVIEW`, `DEPRECATED`, `BLOCKED`.
6. Si alimenta Prisma OCR después, debe declarar `ocr_handoff_status`, pero no crear DB en doc1/canon1.

## 11.8 Readiness por tipo de matriz

| Familia | Readiness rule |
|---|---|
| scope | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| neutral | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| capability | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| lineage | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| canonical | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| projection | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| ui | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| chartlab | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| data | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| evidence | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| curation | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| tooling | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| governance | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |
| handoff | DRAFT si sólo existe definición; NEEDS_REVIEW si falta evidencia o curation; READY sólo si tiene records, edges, evidence y reglas mínimas; BLOCKED si podría producir fake green. |

## 11.9 Catálogos críticos para normalize2

| Catálogo | normalize2 contract |
|---|---|
| Scope_Registry | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Neutral_Object_Registry | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Event_Catalog | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Action_Catalog | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Surface_Projection_Map | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| UI_Component_Atlas | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Data_Binding_Map | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Evidence_Readiness_Map | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Lineage_Edge_Map | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Canonical_Projection_Map | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Tool_Coverage_Map | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |
| Curation_Decision_Log | normalize2 must be able to create or prepare this view without declaring Prisma OCR DB |

## 11.10 Catálogos de paneles, insights y UI

| UI/panel object type | Rule |
|---|---|
| KPI_CARD | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| DATA_TABLE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| ACTION_BUTTON | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| FILTER_BAR | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| DATE_RANGE_PICKER | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| SEARCH_BOX | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| STATUS_BADGE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| SYNC_BADGE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| LICENSE_BADGE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| ROLE_BADGE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| CHART_CARD | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| CHART_CANVAS | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| DRAWER | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| MODAL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| TOAST | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| ALERT_BANNER | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| EMPTY_STATE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| ERROR_STATE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| AUDIT_TIMELINE | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| DETAIL_PANEL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| COMMAND_PANEL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| SETUP_WIZARD | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| CLAIM_SLOT_PANEL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| DEVICE_HEALTH_PANEL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| CASH_SESSION_PANEL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| RECONCILIATION_PANEL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| EVIDENCE_VIEWER | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |
| CANONICAL_STATUS_PANEL | Must bind to neutral_object_id or projection reason; UI ID locates, it does not rule. |

## 11.11 Chart Lab catalog variety

| Chart visual type | Contract |
|---|---|
| LINE_TREND | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| BAR_RANKING | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| STACKED_BAR | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| HEATMAP_HOUR_DAY | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| SCATTER_MARGIN_VOLUME | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| FUNNEL_ONBOARDING | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| GAUGE_HEALTH | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| BULLET_TARGET | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| SPARKLINE_KPI | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| TREE_MAP_CATEGORY | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| SANKEY_LINEAGE | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| NETWORK_GRAPH_RELATIONSHIP | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| CALENDAR_HEATMAP | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| WATERFALL_CASH_DIFF | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| BOX_PLOT_VARIANCE | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| AREA_CUMULATIVE | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| PIE_LIMITED_ONLY_WHEN_VALID | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| RADAR_COMPARISON | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| CHOROPLETH_SITE_MAP | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |
| TABLE_VISUAL_HYBRID | Requires metric_id, dataset_contract_id, scope grain, evidence, destination surface, pricing class and no-humo claim check. |

## 11.12 Ejemplo: Tablet 231 vs PC 228

Una discrepancia de ventas no es pleito entre apps. La matriz de drift debe poder explicar: tenant, business, store/site, device, source_surface, date_range, status_filter, sync_state, provenance, canonical_status y accepted/rejected/duplicate/pending counts.

```yaml
case_id: DRIFT.sales.count.tenant_prisma_rey.2026-07-09
metric: MET.sales.count
observed:
  tablet: 231
  pc: 228
possible_causes:
  - pending_sync: 3
  - duplicate_rejected: 0
  - date_range_mismatch: unknown
  - store_scope_mismatch: unknown
canonical_required: CAN.sale
next_action: collect sync_outbox + canonical_projection evidence
```

## 11.13 Ejemplo de manifest por export

```json
{
  "export": "Evidence_Readiness_Map.csv",
  "rows": 0,
  "orphan_policy": "ORPHAN cannot be READY; ORPHAN is NEEDS_REVIEW until bound or rejected",
  "blocking_rules": [
    "READY requires at least one accepted evidence binding",
    "canonical rows require curation or validated rule",
    "client-facing claim requires license and visibility boundary"
  ]
}
```

## 11.14 Anti-fake-green rules

- `ORPHAN` nunca puede estar READY.
- `SURF.*` sin neutral link queda como projection-only/inferred.
- `MET.*` sin formula/source/grain/scope queda draft.
- `ACT.*` que escribe debe emitir `EVT.*`.
- `CAN.*` requiere regla de aceptación/rechazo/duplicado/pending.
- Un claim comercial necesita capability, evidence, limit, surface, role y license.
- UI ID ubica; no manda.
- La matriz exporta; no gobierna.

## 11.15 Tabla de incremento simple

| Caso | Cómo incrementarlo sin romper |
|---|---|
| Agregar nuevo widget | crear/ingresar UI_Component_Atlas row; bind neutral_object_id; evidence if runtime observed |
| Agregar nueva métrica | Metric_Catalog row + Data_Binding_Map + ChartLab_Metric_Map if visual |
| Agregar nueva surface | Runtime_Surface_Map + Surface_Projection_Map + visibility/license rule |
| Agregar nuevo módulo | Module_Registry + Capability_Catalog + License_Plan_Grant_Map |
| Agregar nueva vertical | Capability_Pack_Map + neutral entity/event/action del vertical + projection rules |
| Agregar evidencia | Artifact_Index + Evidence_Source_Map + Evidence_Readiness_Map regeneration |
| Corregir inferencia | Alias_Registry or Override_Registry, never edit generated CSV |
| Promover canonical | Canonical_Promotion_Queue + acceptance rule + evidence gate |

## 11.16 Minimum viable normalize2 output

normalize2 no debe intentar llenar todo. Debe producir el primer puente serio: scope candidates, neutral object candidates, surface projection links, evidence readiness corregida, edge candidates y orphans clasificados. Eso basta para que curate1 tenga materia real y Prisma OCR no nazca con gastritis ontológica.

## 11.17 Lista completa de export folders

```text
generated_matrices/
  scope/
  neutral/
  capability/
  lineage/
  canonical/
  projection/
  ui/
  chartlab/
  data/
  evidence/
  curation/
  tooling/
  governance/
  handoff/
reports/
  coverage/
  conflicts/
  drift/
  readiness/
  handoff/
```

## 11.18 Final rule

PRISMA no necesita primero un inventario de pantallas. Necesita un registro neutral de scope y significado. Este sistema de catálogos existe para que cada matriz sea regenerable, auditable y ampliable sin convertir el proyecto en una piñata de CSVs contradictorios.
