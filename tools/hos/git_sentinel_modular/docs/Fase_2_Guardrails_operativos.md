# Fase 2 — Guardrails operativos

## Meta
Hacer que el modular sea seguro por default y difícil de usar mal en operación real.

## Objetivo operativo
Reducir el riesgo de side effects accidentales, activaciones peligrosas y drift de runtime.

## Incluye
- Endurecimiento de safe defaults.
- Revisión de `dry-run` como comportamiento por defecto donde aplique.
- Aislamiento de rutas de runtime, outputs, temporales y reportes.
- Revisión de execution lock y protecciones de concurrencia.
- Revisión de scheduler y CI gate para evitar activación accidental.
- Validaciones tempranas de bootstrap/config/runtime.

## Riesgos que busca eliminar
- Ejecuciones mutantes no intencionales.
- Escrituras en rutas ambiguas o compartidas.
- Corridas simultáneas peligrosas.
- Activación de scheduler o gates sin controles suficientes.
- Fallos tardíos por config o entorno mal inicializado.

## Entregables
- Matriz de defaults seguros por componente operativo.
- Reglas de runtime y outputs segregados.
- Lista de validaciones de arranque obligatorias.
- Diagnóstico de locks, scheduler y gating.
- Lista de tests negativos para garantizar comportamiento seguro.

## Criterio de salida
La fase termina cuando el modular puede arrancar y operar en modo seguro por default, con validaciones tempranas y controles mínimos contra usos peligrosos.
