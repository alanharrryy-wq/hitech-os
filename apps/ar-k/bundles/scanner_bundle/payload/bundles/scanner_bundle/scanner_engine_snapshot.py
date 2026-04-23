from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .scanner_kernel_discovery import discover_files_with_stats
from .scanner_kernel_identity import normalize_relpath
from .scanner_parser_snapshot import classify_file, parse_python_file, parse_text_surface
from .scanner_path_policy import classify_path_policy


@dataclass
class ScannerEngineSnapshot:
    manifest: dict[str, Any]
    engine_id: str = "scanner"
    stage: str = "stage_01_scan"

    def run_on_tree(self, target_root, execution_id: str, created_at: str) -> dict[str, Any]:
        observed_modules: list[dict[str, Any]] = []
        observed_boundaries: list[dict[str, Any]] = []
        observed_paths: list[dict[str, Any]] = []
        files, stats = discover_files_with_stats(target_root)
        for path in files:
            rel = normalize_relpath(path, target_root)
            policy = classify_path_policy(rel)
            record = {
                "path": rel,
                "action": policy.action,
                "reason": policy.reason,
                "canonical_source": policy.canonical_source,
                "non_product_class": policy.non_product_class,
            }
            observed_paths.append(record)
            if policy.action == "exclude":
                continue
            kind = classify_file(rel)
            module_record = {
                "path": rel,
                "kind": kind,
                "canonical_source": policy.canonical_source,
                "non_product_class": policy.non_product_class,
                "imports": [],
                "exports": [],
                "routes": [],
                "boundaries": [],
            }
            if kind == "python":
                parsed = parse_python_file(path)
                module_record["imports"] = parsed["imports"]
                module_record["exports"] = parsed["exports"]
                module_record["parse_ok"] = parsed["ok"]
                module_record["error"] = parsed["error"]
            else:
                parsed = parse_text_surface(path, rel)
                module_record["imports"] = parsed["imports"]
                module_record["exports"] = parsed.get("exports", [])
                module_record["routes"] = parsed["routes"]
                module_record["boundaries"] = parsed["boundaries"]
                module_record["surface_kind"] = parsed["surface_kind"]
            observed_modules.append(module_record)
            for boundary in module_record.get("boundaries", []):
                observed_boundaries.append({
                    "source_path": rel,
                    "boundary_kind": boundary,
                    "canonical_source": policy.canonical_source,
                })
        summary = {
            "status": "observed_only",
            "stage": self.stage,
            "execution_id": execution_id,
            "created_at": created_at,
            "files_seen": len(observed_paths),
            "modules_emitted": len(observed_modules),
            "boundaries_emitted": len(observed_boundaries),
            "skipped_vendor_dir_count": stats["skipped_vendor_dir_count"],
            "skipped_external_path_count": stats["skipped_external_path_count"],
            "forbidden_writes": [
                "module_registry.json",
                "boundary_registry.json",
                "registry_index.json",
                "switch_decision_registry.json",
                "switch_decision_trace.json",
                "validation_report.json",
                "gate_decisions.json",
                "annotations.json",
                "annotation_index.json",
            ],
        }
        return {
            "scan_observed_modules.json": observed_modules,
            "scan_observed_boundaries.json": observed_boundaries,
            "scan_observed_paths.json": observed_paths,
            "scan_observed_summary.json": summary,
        }
