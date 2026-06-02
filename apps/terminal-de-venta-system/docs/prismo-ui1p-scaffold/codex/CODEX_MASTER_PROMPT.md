# CODEX MASTER PROMPT · PRISMO UI1P FIX1 · AUTO RENDER ENSEMBLE

## Contexto
Trabajas en el repo local:

`<REPO_ROOT>`

Este scaffold reemplaza y amplía `prismo ui1p 3005 1121`. Usa este paquete como contrato vivo. No inventes arquitectura.

## Objetivo final
Implementar PRISMO Adaptive Intelligence Theater Pro como experiencia operativa premium, conectada a HTTP/motor real, con respuestas renderizadas, memoria procedural visible, Cloudglass Refrigerant Pro y validación visual.

## Cambio crítico aprobado

### El cuarto dropdown queda eliminado.
Antes había: objetivo + dominio + lente + escena/formato.
Ahora debe quedar:

1. Objetivo.
2. Superficie / Área.
3. Lente / Evidencia.
4. Texto libre y contexto opcional.

La escena/formato la decide PRISMO mediante **Auto Render Ensemble**. El usuario no debe seleccionar `checklist`, `timeline`, `risk_matrix` o `evidence_board` antes de preguntar.

## Regla maestra de implementación
La UI no debe ser maqueta estática. Todo bloque importante debe provenir de endpoint real, adapter real, render_plan, memoria, evidencia o fixture sólo como fallback explícito de desarrollo.

## Contratos que debes leer primero

- `contracts/composer/dependent_crystal_composer.json`
- `contracts/render_blocks/auto_render_ensemble.json`
- `contracts/render_blocks/render_block_registry.json`
- `contracts/visual/refrigerant_cloudglass_presets.json`
- `contracts/memory/memory_taxonomy.json`
- `contracts/codex/codex_150_improvements.json`

## UI final esperada

### Composer
- 3 dropdowns dependientes.
- Dropdowns tipo cristal verde refrigerante.
- Texto libre principal.
- Contexto opcional.
- Chips inteligentes dinámicos.
- Sin dropdown de escena/formato.

### Theater
- Hero response.
- Executive brief.
- Next best action.
- Auto Render Ensemble con bloques aplicables.
- Action bar.
- Feedback hooks.

### Detalle técnico
- Drawer premium.
- Evidencia, memoria, protocolos, trace y technical JSON parcial sólo bajo demanda.

## Auto Render Ensemble
El endpoint/adaptador debe devolver `blocks[]` ordenados por prioridad. Usar bloques como:

- `hero_response`
- `executive_brief`
- `next_best_action`
- `protocol_ladder`
- `procedural_steps`
- `risk_matrix`
- `timeline`
- `flow_diagram`
- `comparison_board`
- `evidence_board`
- `memory_trace`
- `technical_drawer`
- `action_bar`

## HTTP / conexión
Preferir un contrato unificado:

`POST /api/prismo/theater/query`

Si no existe, crear adapter local sobre endpoints existentes de learning/status/evidence/recommend/insights/graph/feedback.

## Memoria
La respuesta debe poder justificar criterios usando memoria:

- semantic_memory
- episodic_memory
- procedural_memory
- working_memory
- operational_memory
- governance_memory
- visual_memory

La memoria procedural debe ser visible cuando guíe una recomendación: “se eligió este protocolo porque antes funcionó en un caso parecido”.

## Visual
Usar `contracts/visual/refrigerant_cloudglass_presets.json` y `src-candidates/styles/prismo-theater-cloudglass-pro.css`.

No permitir paneles opacos. No resolver legibilidad subiendo fill alpha. Usar hairline, scrim, highlight, sombras, tipografía y contraste.

## Prohibido visible
- safe mode
- preview only
- coming soon
- próximamente
- future
- placeholder
- raw JSON gigante
- hashes/paths por defecto

## Seguridad interna
Debe seguir: no DB, no .env, no deploy, no git push, no scripts externos, no acciones destructivas, no fake green.

## Validación obligatoria
- Screenshots: empty, dropdowns abiertos, respuesta renderizada, drawer técnico, error, loading, feedback.
- Verificar que existen 3 dropdowns y no 4.
- Verificar render blocks.
- Verificar presets anti-opacidad.
- Verificar no forbidden labels.
- Verificar result/fail ZIP y rollback.

## Resultado final
PRISMO debe sentirse como teatro visual operativo: vivo, premium, verde cristalino, potente, conectado a motor real y útil para decidir.


---

# FX2 Addendum · Interaction FX Pro

Codex must use the `prismo ui1p 0106 0802 fix2` scaffold as upgraded source of truth.

- There are exactly 3 dependent dropdowns: objective, domain, lens.
- There is no output format dropdown. Auto Render Ensemble selects blocks automatically.
- Use the interaction effect matrix to exploit available libraries with governance.
- Wire to Theater Query / render_plan / learning endpoints/adapters.
- Add command palette, generated chips, feedback dock, evidence drawer, motion reveal, and chart preview blocks where applicable.
- Apply Cloudglass Refrigerant Effects v2; never ship opaque/milky surfaces.
- Produce screenshots and reports for all states.
