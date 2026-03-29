
#!/usr/bin/env python3
"""Dataset vault CLI (stdlib only).

Commands:
  - list
  - validate
  - add
  - export
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


DEFAULT_VAULT_ROOT = Path("apps/keystone/dev-datasets")
INDEX_FILE = "index.json"


def read_json(path: Path) -> Any:
  with path.open("r", encoding="utf-8") as handle:
    return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open("w", encoding="utf-8", newline="\n") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")


def is_non_empty_string(value: Any) -> bool:
  return isinstance(value, str) and len(value.strip()) > 0


def parse_string_list(value: Any) -> List[str]:
  if not isinstance(value, list):
    return []
  output: List[str] = []
  for entry in value:
    if is_non_empty_string(entry):
      output.append(entry.strip())
  return output


def validate_index_payload(payload: Any) -> List[str]:
  errors: List[str] = []
  if not isinstance(payload, dict):
    return ["index.json must contain an object"]

  datasets = payload.get("datasets")
  if not isinstance(datasets, list):
    return ["index.json must contain datasets[]"]

  seen_ids: set[str] = set()

  for idx, entry in enumerate(datasets):
    prefix = f"datasets[{idx}]"
    if not isinstance(entry, dict):
      errors.append(f"{prefix} must be an object")
      continue

    dataset_id = entry.get("datasetId")
    data_shape_id = entry.get("dataShapeId")
    semantic_intent = entry.get("semanticIntent")
    widgets = entry.get("recommendedWidgets")
    tags = entry.get("tags")
    file_ref = entry.get("file")

    if not is_non_empty_string(dataset_id):
      errors.append(f"{prefix}.datasetId must be a non-empty string")
    else:
      normalized = dataset_id.strip()
      if normalized in seen_ids:
        errors.append(f"{prefix}.datasetId '{normalized}' is duplicated")
      seen_ids.add(normalized)

    if not is_non_empty_string(data_shape_id):
      errors.append(f"{prefix}.dataShapeId must be a non-empty string")

    if not is_non_empty_string(semantic_intent):
      errors.append(f"{prefix}.semanticIntent must be a non-empty string")

    if len(parse_string_list(widgets)) == 0:
      errors.append(f"{prefix}.recommendedWidgets must include at least one string")

    if len(parse_string_list(tags)) == 0:
      errors.append(f"{prefix}.tags must include at least one string")

    if not is_non_empty_string(file_ref):
      errors.append(f"{prefix}.file must be a non-empty string")

  return errors


def find_dataset_entry(index_payload: Dict[str, Any], dataset_id: str) -> Dict[str, Any] | None:
  for entry in index_payload.get("datasets", []):
    if isinstance(entry, dict) and entry.get("datasetId") == dataset_id:
      return entry
  return None


def validate_dataset_file(path: Path, dataset_entry: Dict[str, Any]) -> List[str]:
  errors: List[str] = []

  if not path.exists():
    return [f"missing dataset file: {path.as_posix()}"]

  try:
    payload = read_json(path)
  except Exception as exc:  # pylint: disable=broad-exception-caught
    return [f"invalid json at {path.as_posix()}: {exc}"]

  if not isinstance(payload, dict):
    return [f"dataset file {path.as_posix()} must contain an object"]

  dataset_id = payload.get("datasetId")
  data_shape_id = payload.get("dataShapeId")
  semantic_intent = payload.get("semanticIntent")
  body = payload.get("payload")

  if dataset_id != dataset_entry.get("datasetId"):
    errors.append(
      f"{path.as_posix()} datasetId mismatch: expected '{dataset_entry.get('datasetId')}', got '{dataset_id}'"
    )

  if data_shape_id != dataset_entry.get("dataShapeId"):
    errors.append(
      f"{path.as_posix()} dataShapeId mismatch: expected '{dataset_entry.get('dataShapeId')}', got '{data_shape_id}'"
    )

  if not is_non_empty_string(semantic_intent):
    errors.append(f"{path.as_posix()} semanticIntent must be a non-empty string")

  if body is None:
    errors.append(f"{path.as_posix()} payload is required")

  return errors


def load_index(vault_root: Path) -> Tuple[Path, Dict[str, Any]]:
  index_path = vault_root / INDEX_FILE
  payload = read_json(index_path)
  if not isinstance(payload, dict):
    raise ValueError(f"{index_path.as_posix()} must be a JSON object")
  return index_path, payload


def cmd_list(args: argparse.Namespace) -> int:
  _, payload = load_index(args.vault_root)
  datasets = payload.get("datasets", [])
  for entry in datasets:
    if not isinstance(entry, dict):
      continue
    dataset_id = entry.get("datasetId", "")
    shape = entry.get("dataShapeId", "")
    intent = entry.get("semanticIntent", "")
    file_ref = entry.get("file", "")
    print(f"{dataset_id}\t{shape}\t{intent}\t{file_ref}")
  return 0


def cmd_validate(args: argparse.Namespace) -> int:
  _, payload = load_index(args.vault_root)
  errors = validate_index_payload(payload)

  for entry in payload.get("datasets", []):
    if not isinstance(entry, dict):
      continue
    file_ref = entry.get("file")
    if not is_non_empty_string(file_ref):
      continue
    dataset_path = (args.vault_root / file_ref).resolve()
    errors.extend(validate_dataset_file(dataset_path, entry))

  if errors:
    print("validation failed:")
    for item in errors:
      print(f"- {item}")
    return 1

  print("validation passed")
  return 0


def cmd_add(args: argparse.Namespace) -> int:
  index_path, payload = load_index(args.vault_root)
  datasets = payload.setdefault("datasets", [])
  if not isinstance(datasets, list):
    raise ValueError("index.json datasets must be a list")

  if find_dataset_entry(payload, args.dataset_id) is not None:
    raise ValueError(f"dataset '{args.dataset_id}' already exists")

  file_ref = args.file or f"datasets/{args.dataset_id}.json"
  entry = {
    "datasetId": args.dataset_id,
    "dataShapeId": args.data_shape_id,
    "semanticIntent": args.semantic_intent,
    "recommendedWidgets": args.recommended_widgets,
    "tags": args.tags,
    "file": file_ref,
  }

  if args.default_seed or args.supported_seed:
    seed_opts: Dict[str, Any] = {}
    if args.default_seed:
      seed_opts["defaultSeed"] = args.default_seed
    if args.supported_seed:
      seed_opts["supportedSeeds"] = args.supported_seed
    entry["seedOptions"] = seed_opts

  datasets.append(entry)
  datasets.sort(key=lambda item: str(item.get("datasetId", "")))

  write_json(index_path, payload)

  dataset_path = args.vault_root / file_ref
  if not dataset_path.exists():
    dataset_payload = {
      "datasetId": args.dataset_id,
      "dataShapeId": args.data_shape_id,
      "semanticIntent": args.semantic_intent,
      "recommendedWidgets": args.recommended_widgets,
      "tags": args.tags,
      "payload": {},
    }
    write_json(dataset_path, dataset_payload)

  print(f"added dataset '{args.dataset_id}'")
  return 0


def cmd_export(args: argparse.Namespace) -> int:
  _, payload = load_index(args.vault_root)
  entry = find_dataset_entry(payload, args.dataset_id)
  if entry is None:
    raise ValueError(f"dataset '{args.dataset_id}' not found")

  file_ref = entry.get("file")
  if not is_non_empty_string(file_ref):
    raise ValueError(f"dataset '{args.dataset_id}' has invalid file reference")

  dataset_payload = read_json(args.vault_root / str(file_ref))
  if not isinstance(dataset_payload, dict) or "payload" not in dataset_payload:
    raise ValueError(f"dataset '{args.dataset_id}' has no payload")

  output = {
    "datasetId": dataset_payload.get("datasetId", args.dataset_id),
    "dataShapeId": dataset_payload.get("dataShapeId", entry.get("dataShapeId")),
    "payload": dataset_payload["payload"],
  }

  write_json(args.output, output)
  print(f"exported '{args.dataset_id}' to {args.output.as_posix()}")
  return 0


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Dataset vault CLI")
  parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)

  subparsers = parser.add_subparsers(dest="command", required=True)

  subparsers.add_parser("list", help="List dataset registry entries")
  subparsers.add_parser("validate", help="Validate index and dataset files")

  add_parser = subparsers.add_parser("add", help="Add a dataset registry entry")
  add_parser.add_argument("dataset_id")
  add_parser.add_argument("data_shape_id")
  add_parser.add_argument("semantic_intent")
  add_parser.add_argument("--recommended-widgets", nargs="+", required=True)
  add_parser.add_argument("--tags", nargs="+", required=True)
  add_parser.add_argument("--file", default="")
  add_parser.add_argument("--default-seed", default="")
  add_parser.add_argument("--supported-seed", action="append", default=[])

  export_parser = subparsers.add_parser("export", help="Export dataset payload to standalone JSON")
  export_parser.add_argument("dataset_id")
  export_parser.add_argument("output", type=Path)

  return parser


def main(argv: Sequence[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)

  if args.command == "list":
    return cmd_list(args)
  if args.command == "validate":
    return cmd_validate(args)
  if args.command == "add":
    return cmd_add(args)
  if args.command == "export":
    return cmd_export(args)

  raise ValueError(f"unknown command: {args.command}")


if __name__ == "__main__":
  raise SystemExit(main())

