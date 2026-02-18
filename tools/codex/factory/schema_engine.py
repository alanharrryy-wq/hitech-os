from __future__ import annotations

import re
from typing import Any


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _expect_type(value: Any, expected: Any) -> bool:
    if isinstance(expected, str):
        return _type_matches(value, expected)
    if isinstance(expected, list):
        return any(_type_matches(value, item) for item in expected)
    return True


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")

    if "type" in schema and not _expect_type(instance, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']!r}")
        return errors

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required key '{key}'")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(validate_instance(value, properties[key], child_path))
                continue
            if additional is False:
                errors.append(f"{child_path}: additional property is not allowed")
            elif isinstance(additional, dict):
                errors.extend(validate_instance(value, additional, child_path))

        min_props = schema.get("minProperties")
        if min_props is not None and len(instance) < int(min_props):
            errors.append(f"{path}: requires at least {min_props} properties")

        max_props = schema.get("maxProperties")
        if max_props is not None and len(instance) > int(max_props):
            errors.append(f"{path}: allows at most {max_props} properties")

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < int(min_items):
            errors.append(f"{path}: requires at least {min_items} items")

        max_items = schema.get("maxItems")
        if max_items is not None and len(instance) > int(max_items):
            errors.append(f"{path}: allows at most {max_items} items")

        if schema.get("uniqueItems"):
            seen = set()
            for idx, item in enumerate(instance):
                token = repr(item)
                if token in seen:
                    errors.append(f"{path}[{idx}]: duplicate list item")
                seen.add(token)

        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, value in enumerate(instance):
                errors.extend(validate_instance(value, item_schema, f"{path}[{idx}]"))
        elif isinstance(item_schema, list):
            for idx, item_schema_entry in enumerate(item_schema):
                if idx >= len(instance):
                    break
                errors.extend(validate_instance(instance[idx], item_schema_entry, f"{path}[{idx}]"))

    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(instance) < int(min_length):
            errors.append(f"{path}: requires minLength {min_length}")

        max_length = schema.get("maxLength")
        if max_length is not None and len(instance) > int(max_length):
            errors.append(f"{path}: requires maxLength {max_length}")

        pattern = schema.get("pattern")
        if pattern is not None and re.search(str(pattern), instance) is None:
            errors.append(f"{path}: does not match pattern {pattern!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            errors.append(f"{path}: must be >= {minimum}")

        maximum = schema.get("maximum")
        if maximum is not None and instance > maximum:
            errors.append(f"{path}: must be <= {maximum}")

    any_of = schema.get("anyOf")
    if isinstance(any_of, list) and any_of:
        nested = [validate_instance(instance, nested_schema, path) for nested_schema in any_of]
        if all(result for result in nested):
            errors.append(f"{path}: did not satisfy anyOf")

    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        for nested_schema in all_of:
            errors.extend(validate_instance(instance, nested_schema, path))

    return errors


def validate_or_raise(instance: Any, schema: dict[str, Any], label: str) -> None:
    errors = validate_instance(instance, schema)
    if errors:
        details = "\n".join(f"- {item}" for item in errors)
        raise ValueError(f"Schema validation failed for {label}:\n{details}")
