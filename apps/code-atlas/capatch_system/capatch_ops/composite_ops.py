from __future__ import annotations

from typing import Iterable

from capatch_contracts.operations import OperationSpec


def flatten_operation_specs(operations: Iterable[OperationSpec]) -> list[OperationSpec]:
    flattened: list[OperationSpec] = []
    for operation in operations:
        if operation.type == "ApplySet":
            flattened.extend(flatten_operation_specs(operation.payload.get("operations") or []))
        else:
            flattened.append(operation)
    return flattened
