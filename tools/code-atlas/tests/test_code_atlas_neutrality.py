from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from code_atlas.core.neutrality_gate import scan_code_atlas
from code_atlas.db_glass.reality_check import run_reality_check, save_reality_check
from code_atlas.legal_readiness.contracts import LegalPipelineConfig
from code_atlas.manifest.todo_el_show_plus import run_todo_plus
from code_atlas.operational import runner as operational_runner
from code_atlas.operational.runtime_profile import public_path, resolve_runtime_profile
from code_atlas.surface_target_atlas.runner import run_surface_target_atlas


REPO_ROOT = Path(__file__).resolve().parents[3]
CODE_ATLAS_ROOT = REPO_ROOT / "tools" / "code-atlas"
NEUTRAL_SOURCE_ROOTS = (
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "core",
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "operational",
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "surface_target_atlas",
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "legal_readiness",
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "coverage",
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "db_glass",
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "manifest",
    CODE_ATLAS_ROOT / "src" / "code_atlas" / "cli",
)
DETECTOR_DEFINITION = CODE_ATLAS_ROOT / "src" / "code_atlas" / "core" / "neutrality_gate.py"
BANNED_LITERAL_FRAGMENTS = (
    "f:\\",
    "f:/",
    "apps/terminal-de-venta-system",
    "hitech-os",
    "descargasf",
    "powershell.exe",
    "mamastrophic",
    "prisma-control-center",
    "prisma cloud ctr",
    "prisma-support-resolver",
    "licscope_bridge",
    "prisma_surface_target_atlas",
    "prisma_control_graph",
    "prisma_patch_readiness",
    "prisma_atlas_dropdown_model",
)


def _all_neutral_python_files() -> list[Path]:
    files: list[Path] = []
    for root in NEUTRAL_SOURCE_ROOTS:
        if root.exists():
            files.extend(root.rglob("*.py"))
    return sorted(path for path in set(files) if path.resolve() != DETECTOR_DEFINITION.resolve())


def _write_fixture_repo(root: Path) -> Path:
    repo = root / "arbitrary-workspace" / "customer-repository"
    (repo / "apps" / "alpha" / "app").mkdir(parents=True)
    (repo / "services" / "billing").mkdir(parents=True)
    (repo / "package.json").write_text('{"name":"neutral-fixture","private":true}\n', encoding="utf-8")
    (repo / "apps" / "alpha" / "app" / "page.tsx").write_text(
        "export function Checkout(){return <button data-surface=\"alpha\" data-screen=\"checkout\" data-zone=\"footer\" data-panel=\"actions\" data-target=\"pay\" data-kind=\"button\" data-role=\"primary_action\">Pay</button>}\n",
        encoding="utf-8",
    )
    (repo / "services" / "billing" / "scope.py").write_text(
        "def scoped(tenant_id, organization_id): return tenant_id, organization_id\n",
        encoding="utf-8",
    )
    db = repo / "sample.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("create table customers (id text primary key, tenant_id text, organization_id text, created_at text)")
    conn.execute("insert into customers values ('c1','t1','o1','2026-08-14T00:00:00Z')")
    conn.commit()
    conn.close()
    return repo


def _text_outputs(root: Path) -> str:
    chunks: list[str] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".html", ".csv", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


class CodeAtlasNeutralityTests(unittest.TestCase):
    maxDiff = None

    def test_neutral_source_has_no_machine_or_project_specific_defaults(self) -> None:
        violations: list[str] = []
        for path in _all_neutral_python_files():
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            for banned in BANNED_LITERAL_FRAGMENTS:
                if banned in text:
                    violations.append(f"{path.relative_to(CODE_ATLAS_ROOT).as_posix()}::{banned}")
        self.assertEqual(violations, [], "Neutral core contains forbidden coupling: " + " | ".join(violations))

    def test_neutrality_detector_does_not_accuse_its_own_pattern_definitions(self) -> None:
        report = scan_code_atlas(CODE_ATLAS_ROOT)
        self.assertNotEqual(report["status"], "WARN_CODE_ATLAS_CORE_HAS_LOCAL_ENV_REFERENCES")
        self.assertFalse(any(row.get("file") == "src/code_atlas/core/neutrality_gate.py" for row in report.get("findings", [])))

    def test_runtime_profile_uses_explicit_repo_and_redacts_external_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = _write_fixture_repo(tmp_path)
            out = tmp_path / "elsewhere" / "atlas-output"
            with mock.patch.dict(os.environ, {}, clear=True):
                profile = resolve_runtime_profile(repo, out)
            self.assertEqual(profile.repo_root, repo.resolve())
            self.assertEqual(profile.output_root, out.resolve())
            self.assertEqual(profile.profile_id, "generic")
            self.assertTrue(any(surface.surface_id.startswith("apps.") for surface in profile.surfaces))
            external = tmp_path / "outside" / "secret-folder" / "evidence.zip"
            rendered = public_path(external, repo)
            self.assertTrue(rendered.startswith("external-sha256:"))
            self.assertNotIn(str(tmp_path), rendered)

    def test_operational_runner_is_repo_neutral_read_only_and_path_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = _write_fixture_repo(tmp_path)
            out = tmp_path / "outputs" / "operational"
            source_before = {path.relative_to(repo).as_posix(): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            env = {"CODE_ATLAS_PROJECT_ROOT": str(repo), "CODE_ATLAS_OUTPUT_ROOT": str(out)}
            with mock.patch.dict(os.environ, env, clear=True):
                manifest = operational_runner.run_operational_atlas(str(repo), str(out), str(tmp_path / "evidence"))
            source_after = {path.relative_to(repo).as_posix(): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            self.assertEqual(source_before, source_after)
            self.assertTrue(manifest["environmentNeutral"])
            self.assertFalse(manifest["productionCertified"])
            self.assertEqual(manifest["repoRootName"], repo.name)
            self.assertNotIn("repo", manifest)
            self.assertEqual(manifest["supportResolverStatus"], "NOT_CONFIGURED")
            payload_text = _text_outputs(out)
            self.assertNotIn(str(repo), payload_text)
            self.assertNotIn(str(tmp_path), payload_text)
            lowered = payload_text.lower()
            for banned in ("terminal-de-venta-system", "prisma operational evidence", "f:\\", "f:/"):
                self.assertNotIn(banned, lowered)

    def test_db_reality_is_read_only_and_never_exports_absolute_project_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = _write_fixture_repo(tmp_path)
            out = tmp_path / "db-output"
            source_before = {path.relative_to(repo).as_posix(): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            report = run_reality_check(repo)
            save_reality_check(report, out)
            source_after = {path.relative_to(repo).as_posix(): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            self.assertEqual(source_before, source_after)
            self.assertTrue(report["environment_neutral"])
            self.assertNotIn("project_root", report)
            self.assertFalse(any("absolute_path" in row for row in report.get("sqlite", [])))
            output_text = _text_outputs(out)
            self.assertNotIn(str(repo), output_text)
            self.assertNotIn(str(tmp_path), output_text)

    def test_surface_target_atlas_discovers_generic_surface_and_emits_no_absolute_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = _write_fixture_repo(tmp_path)
            out = tmp_path / "surface-output"
            profile_path = tmp_path / "neutral-profile.json"
            profile_path.write_text(json.dumps({
                "profileId": "fixture",
                "projectName": "Fixture",
                "projectRoot": str(repo),
                "outputRoot": str(out),
                "apps": [{"id": "alpha", "label": "Alpha", "root": "apps/alpha", "kind": "web"}],
                "metadata": {"scanRoots": ["."], "supportResolverEnabled": False},
            }), encoding="utf-8")
            with mock.patch.dict(os.environ, {"CODE_ATLAS_PROFILE": str(profile_path)}, clear=True):
                result = Path(run_surface_target_atlas(str(repo), target_app="alpha", output_root=str(out)))
            self.assertTrue(result.exists(), result)
            self.assertTrue(result.name.endswith("result.zip"), result.name)
            with zipfile.ZipFile(result) as bundle:
                manifest = json.loads(bundle.read("RUN_MANIFEST.json").decode("utf-8"))
                atlas = json.loads(bundle.read("CODE_ATLAS_SURFACE_TARGET_ATLAS.json").decode("utf-8"))
            self.assertTrue(manifest["environmentNeutral"])
            self.assertFalse(manifest["productionCertified"])
            self.assertEqual(manifest["surfaces"][0]["id"], "alpha")
            self.assertGreaterEqual(atlas["counts"]["confirmedTargets"], 1)
            serialized = json.dumps({"manifest": manifest, "atlas": atlas}, ensure_ascii=False)
            self.assertNotIn(str(repo), serialized)
            self.assertNotIn(str(tmp_path), serialized)

    def test_todo_plus_bundle_is_path_safe_and_repo_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = _write_fixture_repo(tmp_path)
            out = tmp_path / "todo-output"
            source_before = {path.relative_to(repo).as_posix(): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            with mock.patch.dict(os.environ, {"CODE_ATLAS_PROJECT_ROOT": str(repo), "CODE_ATLAS_OUTPUT_ROOT": str(out)}, clear=True):
                manifest = run_todo_plus(repo, out)
            source_after = {path.relative_to(repo).as_posix(): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            self.assertEqual(source_before, source_after)
            self.assertTrue(manifest["environment_neutral"])
            self.assertFalse(manifest["productionCertified"])
            self.assertNotIn("project_root", manifest)
            output_text = _text_outputs(out)
            self.assertNotIn(str(repo), output_text)
            self.assertNotIn(str(tmp_path), output_text)

    def test_legal_readiness_defaults_are_platform_neutral_and_runtime_adapter_is_explicit(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            config = LegalPipelineConfig(profile="full", include_runtime=True).normalized()
        self.assertFalse(Path(config.output_root).is_absolute())
        self.assertFalse(Path(config.repo_root).is_absolute())
        self.assertFalse(Path(config.code_atlas_root).is_absolute())
        self.assertEqual(config.runtime_program, "")
        self.assertEqual(config.runtime_script, "")


if __name__ == "__main__":
    unittest.main()
