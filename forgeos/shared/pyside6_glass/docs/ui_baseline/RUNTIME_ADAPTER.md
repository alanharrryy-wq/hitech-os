# Runtime adapter

## Responsabilidades

`runtime.py` debe hacer exactamente esto:

- levantar intención desde la screen,
- normalizarla,
- traducirla a `VisualIntelligenceContext`,
- invocar `create_visual_runtime(...)`,
- devolver un `BaselineRuntimeBundle`.

## Qué sí hace

- detección razonable del factory oficial,
- invocación flexible del factory,
- fallback explícito cuando falta el runtime oficial,
- transporte limpio de contexto e intención.

## Qué no hace

- no decide tokens finales,
- no pinta la screen,
- no renderiza charts,
- no valida repositorios,
- no genera código.

## Política de fallback

El fallback no compite por autoridad visual.
Solo conserva contrato, habilita preview temprano y deja evidencia de que el
core sigue siendo necesario.
