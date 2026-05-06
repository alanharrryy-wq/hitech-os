from __future__ import annotations

"""Single-writer law and read policy for the homologated bundle."""

from payload_manifest import WRITER_OWNERSHIP

READERS = {
    "signals": ["registry_builder", "switch_engine", "contract_validator", "ai_annotator"],
    "module_registry": ["switch_engine", "contract_validator", "ai_annotator"],
    "boundary_registry": ["switch_engine", "contract_validator", "ai_annotator"],
    "registry_index": ["switch_engine", "contract_validator", "ai_annotator"],
}


def sole_writer(artifact_key: str) -> str | None:
    return WRITER_OWNERSHIP.get(artifact_key)


def may_write(engine_id: str, artifact_key: str) -> bool:
    return sole_writer(artifact_key) == engine_id


def may_read(engine_id: str, artifact_key: str) -> bool:
    writer = sole_writer(artifact_key)
    if writer is None:
        return True
    return engine_id == writer or engine_id in READERS.get(artifact_key, [])
