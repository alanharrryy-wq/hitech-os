HITECH-OS Git Sentinel | execute candidate wiring bundle v2
===========================================================

Qué corrige este bundle
-----------------------
1. Usa el run_sentinel_execute.ps1 real como backend.
2. No depende de que sentinel_execute acepte candidate_root como argumento CLI.
3. Inyecta el candidate cableado donde el flujo real lo resuelve: dentro del shadow workspace.
4. Aplica overlay sobre candidate base sin tocar el target vivo.
5. Restaura candidate y metadata originales al terminar, salvo que se pida KeepCandidateWired.
6. Deja resultado .md/.json y log principal directo en F:\OneDrive\Descargas.

Artefactos que instala en operator_tools
----------------------------------------
- run_execute_candidate_wiring_v2.ps1
- restore_execute_candidate_wiring_backup_v2.ps1

Suposición operativa
--------------------
- Si existe controlled_diff_lab\overlay_candidate dentro del shadow workspace, se usa como overlay.
- Si no, se puede pasar FullCandidateRoot para forzar un candidate completo alterno.

Comando principal recomendado
-----------------------------
powershell -ExecutionPolicy Bypass -File F:\repos\hitech-os\tools\hos\git_sentinel_modular\operator_tools\run_execute_candidate_wiring_v2.ps1

Resultado esperado
------------------
- Corre run_sentinel_execute.ps1 -Mode plan con workspace\candidate ya cableado.
- Exporta execute_candidate_wiring_v2_result_<timestamp>.md/json a F:\OneDrive\Descargas.
- Mantiene el shadow workspace como estado interno canónico restaurando candidate al final.
