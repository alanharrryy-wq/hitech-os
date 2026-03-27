# Operación canónica de Engine Guardian v3

## Comandos humanos
- `igniters\start_all.cmd`
- `igniters\heal_all.cmd`
- `igniters\validate_all.cmd`
- `igniters\check_health.cmd`
- `igniters\report_status.cmd`
- `igniters\start_keystone.cmd`
- `igniters\heal_cloudflare.cmd`
- `igniters\restart_guardian.cmd`
- `igniters\tail_logs.cmd`
- `igniters\open_repo_analyzer.cmd`
- `igniters\validate_repo_analyzer.cmd`
- `igniters\heal_repo_analyzer.cmd`
- `igniters\report_repo_analyzer_status.cmd`

## Scheduler oficial
- `HITECH-EngineGuardian-Boot`
  - trigger: `AtStartup`
  - delay: `75s`
  - principal: `SYSTEM`
  - run level: `HighestAvailable`
  - acción: `python_abs engine_guardian\cli.py cycle --reason boot`
- `HITECH-EngineGuardian-Pulse`
  - trigger: `AtStartup`
  - delay: `75s`
  - principal: `SYSTEM`
  - run level: `HighestAvailable`
  - acción: `python_abs engine_guardian\cli.py cycle --reason pulse`
  - repetición: `cada 5 minutos` mediante el contrato XML del task

## Flujo unificado
1. preflight
2. runtime hydration
3. origin check or remediation
4. cloudflared service check or remediation
5. tunnel validation
6. public endpoint truth check
7. escalación si origin+túnel están sanos pero público sigue roto
8. snapshot + report + JSONL action log

## Repo Analyzer
Es dominio hermano.
No entra al health crítico del engine público.
