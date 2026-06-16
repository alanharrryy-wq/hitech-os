from __future__ import annotations

import json
import os
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def make_output_root() -> Path:
    override = os.environ.get('CAPATCH_AUDIT_EXPORT_DIR', '').strip()
    if override:
        return Path(override).expanduser().resolve()
    if os.name == 'nt':
        return Path(r'F:\descargasf').resolve()
    return (Path.cwd() / '.capatch_external').resolve()


@dataclass
class RunBundle:
    name: str
    output_root: Path | None = None

    def __post_init__(self) -> None:
        self.output_root = Path(self.output_root or make_output_root()).resolve()
        self.output_root.mkdir(parents=True, exist_ok=True)
        token = datetime.now().strftime('%d%m %H%M%S')
        safe = ' '.join(''.join(c if c.isalnum() or c in {' ', '-', '_'} else ' ' for c in self.name).split()) or 'capatch run'
        self.run_dir = self.output_root / '_capatch_runtime' / f'{safe} {token}'
        self.run_dir.mkdir(parents=True, exist_ok=False)

    def path(self, *parts: str) -> Path:
        path_value = self.run_dir.joinpath(*parts)
        path_value.parent.mkdir(parents=True, exist_ok=True)
        return path_value

    def write_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        path_value = self.path(*relative_path.split('/'))
        path_value.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='')
        return path_value

    def zip(self, status: str) -> Path:
        zip_path = self.output_root / f'{self.run_dir.name} {status}.zip'
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for path_value in sorted(self.run_dir.rglob('*')):
                if path_value.is_file():
                    zf.write(path_value, path_value.relative_to(self.run_dir).as_posix())
        try:
            from capatch_runtime.run_dir_policy import keep_run_dir_default
            keep_dir = keep_run_dir_default()
        except Exception:
            keep_dir = os.environ.get('CAPATCH_KEEP_RUN_DIR', '1').strip().lower() not in {'0', 'false', 'no', 'off'}
        if not keep_dir:
            shutil.rmtree(self.run_dir, ignore_errors=True)
        return zip_path
