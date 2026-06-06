from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_runtime.workspace_cleaner import load_workspace_cleaner_policy, patch_backup_dir, run_startup_cleaner



def test_startup_cleaner_migrates_legacy_backups(tmp_path: Path) -> None:
    legacy = tmp_path / '_chatgpt_patch_backups'
    legacy.mkdir(parents=True, exist_ok=True)
    (legacy / 'demo.txt').write_text('hello\\n', encoding='utf-8', newline='')
    (tmp_path / '__pycache__').mkdir(parents=True, exist_ok=True)
    policy = load_workspace_cleaner_policy(tmp_path)
    payload = run_startup_cleaner(tmp_path, policy=policy, dry_run=False)
    assert payload['status'] == 'ok'
    assert (patch_backup_dir(tmp_path) / 'demo.txt').exists()
    assert not (tmp_path / '__pycache__').exists()
    assert (tmp_path / '.capatch' / 'artifacts' / 'cleanup' / 'startup_last_cleanup.json').exists()
