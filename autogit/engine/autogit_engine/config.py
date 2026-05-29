from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, os
@dataclass
class Policy:
    repo_expected_branch: str = "main"
    out_dir: str = r"F:\descargasf"
    trash_root: str = r"F:\Trash-old"
    max_workers: int = 18
    fail_fast: bool = True
    never_delete: bool = True
    remote: str = "origin"
    remote_branch_prefix: str = "autogit-curated"
    allow_remote_branch_delete: bool = False
    auto_merge_wait_seconds: int = 2700
    max_git_buffer_bytes: int = 128*1024*1024
    allow_admin_merge: bool = False
    keep_pr_open_on_policy_block: bool = True
    mode: str = "full"
    @classmethod
    def load(cls, package_root: Path | None = None) -> "Policy":
        data={}
        if package_root:
            cfg=package_root/"config"/"default_policy.json"
            if cfg.exists(): data.update(json.loads(cfg.read_text(encoding="utf-8")))
        for env,key in {"AUTOGIT_OUT":"out_dir","AUTOGIT_TRASH":"trash_root","AUTOGIT_MODE":"mode"}.items():
            if os.environ.get(env): data[key]=os.environ[env]
        if os.environ.get("AUTOGIT_ALLOW_ADMIN_MERGE", "").strip().lower() in {"1", "true", "yes", "si", "sí"}:
            data["allow_admin_merge"] = True
        if os.environ.get("AUTOGIT_ALLOW_ADMIN_MERGE", "").strip().lower() in {"0", "false", "no"}:
            data["allow_admin_merge"] = False
        return cls(**{k:v for k,v in data.items() if k in cls.__dataclass_fields__})
