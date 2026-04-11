from __future__ import annotations

from typing import Any, Mapping

from pya.contracts.contract_registry import CONTRACT_VALIDATORS


def validate_contract(contract_name: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    validator = CONTRACT_VALIDATORS[contract_name]
    return validator(payload)


def validate_contract_list(contract_name: str, items: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [validate_contract(contract_name, item) for item in items]
