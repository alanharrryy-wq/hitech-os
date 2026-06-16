from __future__ import annotations
import os
FALSE_VALUES={'0','false','no','off','clean'}
def keep_run_dir_default()->bool:
    raw=os.environ.get('CAPATCH_KEEP_RUN_DIR')
    return True if raw is None or str(raw).strip()=='' else str(raw).strip().lower() not in FALSE_VALUES
def keep_run_dir_reason()->str:
    raw=os.environ.get('CAPATCH_KEEP_RUN_DIR')
    if raw is None or str(raw).strip()=='': return 'default_keep_for_rollback_last'
    return 'env_keep_disabled' if str(raw).strip().lower() in FALSE_VALUES else 'env_keep_enabled'
