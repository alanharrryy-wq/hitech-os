from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .lifecycle import CapabilityLifecycle, CapabilityRuntimeState


@dataclass(frozen=True)
class ExportBundleResult:
    bundle_path: str
    manifest_path: str
    included_files: int


class ExportArtifactsCapability:
    """Shared export capability for domain-neutral artifact bundling."""

    capability_id = "forge.commons.export_artifacts"

    def __init__(self) -> None:
        self.lifecycle = CapabilityLifecycle(self.capability_id)

    def activate(self) -> CapabilityRuntimeState:
        return self.lifecycle.activate()

    def dispose(self) -> CapabilityRuntimeState:
        return self.lifecycle.dispose()

    def export_bundle(
        self,
        output_dir: str,
        bundle_name: str,
        manifest: Mapping[str, object],
        file_paths: list[str],
    ) -> ExportBundleResult:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        staging = output / f"{bundle_name}_staging"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=True)

        copied = 0
        for raw_file in file_paths:
            source = Path(raw_file)
            if not source.exists() or not source.is_file():
                continue
            destination = staging / source.name
            shutil.copy2(source, destination)
            copied += 1

        bundle_base = output / bundle_name
        archive_path = shutil.make_archive(str(bundle_base), "zip", root_dir=staging)
        shutil.rmtree(staging)

        manifest_path = output / f"{bundle_name}.manifest.json"
        with manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2, ensure_ascii=True)

        return ExportBundleResult(
            bundle_path=archive_path,
            manifest_path=str(manifest_path),
            included_files=copied,
        )
