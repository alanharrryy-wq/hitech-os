# 09 · Auto Render Ensemble

## Por qué existe
El usuario no debe elegir el formato de respuesta. PRISMO debe inferir la composición visual según intención, dominio, lente, evidencia, memoria y protocolos.

## Entrada
- objective
- domain
- lens
- freeText
- contextNote

## Salida
- hero
- blocks[] ordenados
- actions[]
- evidenceRefs[]
- memoryRefs[]
- technicalTrace
- feedbackHooks

## Regla
No renderizar bloques vacíos. No mostrar tabs sin contenido. No usar raw HTML. No convertir la respuesta en Markdown plano.
