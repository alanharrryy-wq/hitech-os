# PRISMO UI1P FIX1 · Visual Presets Anti-Opacidad

## Decisión clave
El cuarto dropdown se elimina. La salida visual ya no la escoge el usuario antes de preguntar. PRISMO usa **Auto Render Ensemble** y decide qué bloques convienen.

## Presets visuales obligatorios

1. `refrigerant_emerald_theater` · escena principal PRISMO, verde refrigerante translúcido.
2. `crystal_dropdown_refrigerant` · dropdowns interdependientes tipo cajita de cristal.
3. `evidence_vault_luminous_board` · evidencia densa pero legible.
4. `technical_drawer_hydro_panel` · detalle técnico premium, no modal opaco.
5. `action_bar_mint_circuit` · acciones potentes sin botón-rancho.
6. `presentation_scene_glacier` · escena presumible para demo/uso real.
7. `error_recovery_coral_glass` · errores accionables y elegantes.

## Guardrails anti-vidrio-leche

- No subir opacidad para “mejorar legibilidad”. Primero ajustar hairline, scrim, sombra y tipografía.
- No usar blur gigante sobre texto.
- No usar paneles sólidos en Composer/Theater/Drawer.
- No llenar todo de glow. Si todo brilla, nada importa.
- No enseñar `safe mode`, `preview only`, `coming soon`, `future`.

## Tests que Codex debe dejar

- Screenshot dropdown abierto con glass verde translúcido.
- Screenshot respuesta renderizada con hero + bloques.
- Screenshot drawer técnico.
- Verificador de tokens o CSS para detectar fill alpha exagerado.
- Reporte visual que diga qué preset aplica a cada superficie.
