from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path

from .artifacts import discover_stage_artifact, snapshot_zip_files
from .contracts import LegalPipelineConfig
from .registry import build_legal_stage_registry


def _write_zip(path: Path, status: str) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("RUN_MANIFEST.json", json.dumps({"status": status}))


def main() -> int:
    config = LegalPipelineConfig(
        profile="full",
        include_runtime=True,
        workers=18,
        shards=2,
        runtime_root=".",
        runtime_program=sys.executable,
        runtime_script="runtime_adapter.py",
    ).normalized()
    stages = build_legal_stage_registry(config)
    assert len(stages) == 2
    assert stages[0].stage_id == "configured-static-baseline"
    assert stages[1].stage_id == "configured-runtime-evidence"
    assert config.workers == 18
    assert config.shards == 2
    assert not Path(config.output_root).is_absolute()
    assert not Path(config.repo_root).is_absolute()

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        before = snapshot_zip_files(root)
        artifact = root / "legal-static 1408 120000 result.zip"
        _write_zip(artifact, "PARTIAL")
        found = discover_stage_artifact(output_root=root, before=before, expected_prefixes=("legal-static ",))
        assert found is not None
        assert found["manifest"]["status"] == "PARTIAL"

    print("PASS_CODE_ATLAS_LEGAL_BACKEND_SELFTEST")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
