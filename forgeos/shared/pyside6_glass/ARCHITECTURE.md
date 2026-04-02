# PySide6 Glass Framework Architecture

## 1) Framework Core

Path: `F:\repos\hitech-os\forgeos\shared\pyside6_glass`

Responsibilities:

- visual/system contracts (`contracts.py`)
- configuration schema and layered resolution (`config.py`)
- theme/token mapping (`theme.py`)
- icon registry (`icons.py`)
- shell/tabs/panels/layout primitives (`template.py`)
- workspace persistence (`persistence.py`)
- reusable widgets/primitives (`primitives.py`)
- diagnostics (`diagnostics.py`)

Rules:

- no domain logic
- no app-specific path assumptions
- no DeltaForge naming in shared contracts

## 2) Runtime Orchestration Layer

Implemented in `runtime.py`.

Responsibilities:

- resolved config application
- preset activation
- layout registration/switching
- visibility policy application
- keyboard routing
- persistence save/load orchestration
- runtime diagnostics snapshot

Key contracts:

- `GlassWorkspaceRuntime`
- `GlassVisibilityPolicy`
- `GlassVisibilityRule`
- `GlassRuntimeContext`

## 3) Extension Layer

Implemented in `extensions.py`.

Responsibilities:

- register capabilities
- register presets (and preset inheritance)
- register themes and theme overrides
- register icon packs

Key API:

- `register_capability`
- `register_preset_extension`
- `register_theme_extension`
- `register_theme_override_extension`
- `register_icon_pack_extension`

## 4) Integration Boundary Layer

Implemented in `integration/`.

Responsibilities:

- define neutral command/query/snapshot/event contracts
- validate inbound payload envelopes
- provide application-facing dispatch service
- provide transport adapters without polluting framework core
- expose runtime behavior via bridge contracts (not widget internals)

Key modules:

- `integration/contracts.py`
- `integration/service.py`
- `integration/adapters.py`
- `integration/runtime_bridge.py`

Implemented adapters:

- `InProcessIntegrationAdapter` (fully implemented)
- `LocalHttpIntegrationAdapter` (local-only transport)

Prepared/scaffold direction:

- websocket/event-stream adapter
- IPC adapter

## 5) App Adapter Layer

Example:

- `F:\repos\hitech-os\apps\deltaforge\ui\adapters\glass_framework_adapter.py`

Responsibilities:

- app icon pack registration
- app baseline config wrappers
- app wiring integration

Rules:

- adapters consume framework APIs
- adapters do not edit framework internals in-place
- app-specific business behavior remains outside shared framework

## 6) Demo / Example Layer

Path: `F:\repos\hitech-os\forgeos\shared\pyside6_glass\examples`

Purpose:

- provide living reference compositions
- prove expected usage paths (not hacks)

Included:

- form-oriented sample
- dashboard sample
- inspector sample
- tabbed/collapsible workspace
- alternate preset sample
- runtime orchestration sample (theme/layout/persistence/visibility)
- integration sample (command/query/snapshot/event via adapters)

## Config Resolution Model

Resolution layers:

1. framework defaults
2. theme defaults
3. preset defaults
4. app overrides
5. workspace overrides
6. runtime overrides
7. explicit config

Traceability:

- `GlassResolvedConfig.layers_applied`
- `GlassResolvedConfig.field_sources`

## Persistence Compatibility

- current schema: `2`
- migration path from `1` handled in `persistence.py`
- stale/unknown payloads degrade safely via normalization

## API Stability Guidance

Stable:

- `GlassTemplateConfig` family
- `GlassPanelTemplate` public methods
- theme registration APIs
- icon registration APIs
- persistence schema contract + migration behavior
- runtime orchestration entry points
- integration contracts/service boundary

Evolving:

- advanced demo composition patterns
- optional runtime interaction affordances
- additional transport adapters beyond in-process + local HTTP

## Adoption Sequence for a New App

1. register app icon pack in adapter
2. define app preset wrapper (without mutating core contracts)
3. create composition with `GlassPanelTemplate`
4. wire runtime (`GlassWorkspaceRuntime`) for preset/layout/state orchestration
5. wire integration service + runtime bridge (`IntegrationService` + `GlassRuntimeIntegrationBridge`)
6. expose one adapter for client ingress (`InProcessIntegrationAdapter` or local HTTP)
7. add app-specific visibility policy rules
8. persist workspace state with schema-aware APIs
