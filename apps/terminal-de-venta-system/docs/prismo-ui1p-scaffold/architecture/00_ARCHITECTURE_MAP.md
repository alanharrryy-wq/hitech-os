# PRISMO UI1P · Architecture Map

## Propósito
Convertir PRISMO de panel saturado a teatro operativo premium.

## Flujo de alto nivel

```txt
User text + 3 dependent selects
  ↓
Working Memory / Query Intent Model
  ↓
Learning Context: Evidence + Patterns + Authority + Protocols
  ↓
Render Plan Builder
  ↓
Render Block Contract Normalizer
  ↓
Adaptive Intelligence Theater
  ↓
Action Bar + Detail Drawer + Memory Feedback
```

## Principio de diseño
No quitamos potencia. La organizamos en escenas.

## Piezas

| Pieza | Responsabilidad |
|---|---|
| PrismoQueryComposer | captura intención y guía dependiente |
| PrismoMemoryLens | traduce selecciones a memoria/contexto |
| PrismoRenderBlockHost | renderiza bloques contractuales |
| PrismoAdaptiveTheater | composición principal |
| PrismoTechnicalDrawer | evidencia, trace, memoria y JSON bajo demanda |
| PrismoCloudglassSystem | tokens, materiales, motion y feedback visual |
| PrismoActionBar | acciones contextuales seguras |

## Estados maduros
- empty: demo útil y presets reales;
- composing: previews del render plan;
- loading: escena con skeleton premium;
- success: theater renderizado;
- partial: respuesta con warnings elegantes;
- error: acción clara, retry y detalle técnico.
