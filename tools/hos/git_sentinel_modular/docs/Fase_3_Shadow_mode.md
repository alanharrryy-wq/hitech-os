# Fase 3 — Shadow mode

## Meta
Probar el modular en paralelo al legacy sin convertirlo todavía en la ruta viva principal.

## Objetivo operativo
Medir equivalencia y detectar divergencias reales en condiciones controladas y reversibles.

## Incluye
- Diseño del modo shadow para ejecución paralela o comparativa.
- Definición de feature flag explícito para habilitar el camino modular.
- Separación de outputs legacy vs modular.
- Reglas de observabilidad para comparar comportamiento y resultados.
- Criterios de divergencia y abort conditions.
- Estrategia de rollback inmediato apagando el flag.

## Riesgos que busca eliminar
- Cutover prematuro sin evidencia comparativa.
- Divergencias silenciosas.
- Falta de trazabilidad entre resultados legacy y modular.
- Rollback confuso o costoso.

## Entregables
- Propuesta formal de shadow mode.
- Reglas de comparación legacy/modular.
- Criterios de divergencia tolerable vs divergencia bloqueante.
- Esquema de logs/outputs diferenciados.
- Ruta de rollback de un paso.

## Criterio de salida
La fase termina cuando existe una ruta shadow segura, observable y reversible para ejecutar el modular sin tocar el package legacy vivo.
