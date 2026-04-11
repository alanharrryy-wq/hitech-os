from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence, TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonMapping: TypeAlias = Mapping[str, JsonValue]
MutableJsonMapping: TypeAlias = MutableMapping[str, JsonValue]
PathLike: TypeAlias = str | Path
OperationPayload: TypeAlias = Mapping[str, Any]
OperationPayloadSequence: TypeAlias = Sequence[OperationPayload]
