# Codex Apply Notes

Apply this patch from the **existing framework root**.

## Safe apply sequence
1. Back up the current framework root, especially `universal_execution_starter_kit_v1.zip`.
2. Change directory into the current framework root.
3. Extract this patch zip **into that root** so paths overlay in place.
4. Re-run:
   - `python tools/execution_framework/smoke_framework_checks.py`
   - `python tools/execution_framework/check_framework_readiness.py`
5. For the first real project, run:
   - `python tools/execution_framework/init_project.py --project-id <project_id> --project-name "<name>" --initiative-type <type> --objective "<objective>"`
6. Replace starter placeholder path policies in `configs/execution_framework/path_policies.json` with project-real runtime paths before opening package chats.

## Apply rules
- Do not extract this patch one directory above the framework root.
- Do not create a second framework root.
- Treat this patch as additive. It extends the current baseline in place.
- The updated `universal_execution_starter_kit_v1.zip` should replace the older nested starter zip.
