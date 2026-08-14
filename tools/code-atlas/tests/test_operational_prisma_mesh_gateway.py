from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from code_atlas.motors.prisma_mesh_gateway import GatewayError, compose, preflight, validate_request


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


def _repo(base: Path) -> Path:
    repo = base / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    ledger = repo/"PRISMA Factory Ledger"
    ledger.mkdir()
    (ledger/"PRISMA_FACTORY_LEDGER.json").write_text(json.dumps({
        "capabilities":[{"id":"cap.done","classification":"DONE","status":"LOCAL_VERIFIED","doNotRebuild":True}]
    }), encoding="utf-8")
    (ledger/"PRISMA_FACTORY_LEDGER_DO_NOT_REBUILD_MAP.json").write_text(json.dumps({
        "doNotRebuild":{"cap.done":{"value":True}}
    }), encoding="utf-8")
    (ledger/"PRISMA_FACTORY_LEDGER_REGISTRATION_INDEX.json").write_text(json.dumps({
        "registrations":{"cap.done":{"status":"DONE","doNotRebuild":True}}
    }), encoding="utf-8")
    (ledger/"PRISMA_EVIDENCE_INDEX.json").write_text(json.dumps({"artifacts":[]}), encoding="utf-8")
    (ledger/"PRISMA_FACTORY_LEDGER_AGENT_GATE.md").write_text("# Agent Gate\n", encoding="utf-8")
    manual = repo/"apps/terminal-de-venta-system/docs/ops"
    manual.mkdir(parents=True)
    (manual/"PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md").write_text("# Manual\n", encoding="utf-8")
    neutral = repo/"tools/code-atlas"
    neutral.mkdir(parents=True)
    (neutral/"CODE_ATLAS_NEUTRALITY_CONTRACT.json").write_text(json.dumps({
        "neutralRoots":["src/code_atlas"],"adapterRoots":[],"adapterFiles":[],"forbiddenNeutralLiterals":[]
    }), encoding="utf-8")
    (repo/"docs").mkdir()
    (repo/"docs/authority file.md").write_text("# Task authority\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "base")
    return repo


def _request(repo: Path) -> dict:
    return {
        "schemaVersion":"v2",
        "expectedHead":_git(repo, "rev-parse", "HEAD"),
        "tasks":[
            {
                "id":"lane-one","surface":"governance","task":"Audit task one with explicit structured authority requirements.",
                "intent":"AUDIT","domain":"governance",
                "requiredAuthorities":["docs/authority file.md"],
                "requiredDirectories":[],
                "requiredCapabilities":["cap.done"],
                "minimumCoverage":100,
                "failOnMissingAuthority":True,
            },
            {
                "id":"lane-two","surface":"","task":"Audit task two and preserve repository read-only provenance evidence.",
                "intent":"VERIFY","domain":"testing",
                "requiredAuthorities":[],"requiredDirectories":[],
                "requiredCapabilities":[],"minimumCoverage":100,
                "failOnMissingAuthority":True,
            },
        ]
    }


def _fake_mesh(path: Path, repo: Path, task_ids: list[str], *, stable: bool=True) -> None:
    head=_git(repo,"rev-parse","HEAD")
    cert={"status":"PASS","read_only_repo":True,"run_id":"fake-run"}
    drift={"stable":stable,"changed_count":0 if stable else 1,"head_before":head,"head_after":head}
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("PARALLEL_CERTIFICATION.json",json.dumps(cert))
        z.writestr("REPO_DRIFT_REPORT.json",json.dumps(drift))
        for tid in task_ids:
            readset={"git_state":{"head":{"stdout":head+"\n"}},"selected_files":[]}
            z.writestr(f"tasks/{tid}/authority_mesh/.governance/current/AUTHORITY_READSET.lock.json",json.dumps(readset))


class GatewayTests(unittest.TestCase):
    def test_structured_request_preserves_paths_with_spaces(self):
        with tempfile.TemporaryDirectory() as td:
            repo=_repo(Path(td))
            req=validate_request(repo,_request(repo))
            self.assertEqual(req["tasks"][0]["requiredAuthorities"],["docs/authority file.md"])
            self.assertEqual(req["expectedHead"],_git(repo,"rev-parse","HEAD"))

    def test_expected_head_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo=_repo(Path(td))
            raw=_request(repo)
            raw["expectedHead"]="0"*40
            with self.assertRaises(GatewayError):
                validate_request(repo,raw)

    def test_preflight_requires_core_authorities_and_capability(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); repo=_repo(base)
            request=base/"request.json"; request.write_text(json.dumps(_request(repo)),encoding="utf-8")
            out=base/"preflight"
            result=preflight(repo,request,out)
            self.assertEqual(result["status"],"PASS_PREFLIGHT")
            lane=json.loads((out/"lanes/lane-one/AUTHORITY_READSET.lock.json").read_text())
            self.assertIn("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json",lane["requiredAuthorities"])
            self.assertIn("docs/authority file.md",lane["requiredAuthorities"])
            self.assertEqual(lane["coverage"]["requiredAuthoritiesMissing"],0)
            self.assertEqual(lane["requiredCapabilities"],["cap.done"])

    def test_missing_capability_blocks_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); repo=_repo(base)
            raw=_request(repo); raw["tasks"][0]["requiredCapabilities"]=["cap.missing"]
            request=base/"request.json"; request.write_text(json.dumps(raw),encoding="utf-8")
            with self.assertRaises(GatewayError):
                preflight(repo,request,base/"preflight")

    def test_compose_binds_preflight_and_legacy_mesh_to_same_head(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); repo=_repo(base)
            raw=_request(repo)
            request=base/"request.json"; request.write_text(json.dumps(raw),encoding="utf-8")
            pre=base/"preflight"; preflight(repo,request,pre)
            mesh=base/"mesh_result.zip"; _fake_mesh(mesh,repo,["lane-one","lane-two"])
            report=compose(repo,request,pre,mesh,base/"composed")
            self.assertEqual(report["status"],"PASS_COMPOSED_AUTHORITY_MESH")
            self.assertTrue(report["legacyRepoDriftStable"])
            self.assertTrue(Path(report["artifact"]).is_file())

    def test_compose_rejects_legacy_drift(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); repo=_repo(base)
            request=base/"request.json"; request.write_text(json.dumps(_request(repo)),encoding="utf-8")
            pre=base/"preflight"; preflight(repo,request,pre)
            mesh=base/"mesh_result.zip"; _fake_mesh(mesh,repo,["lane-one","lane-two"],stable=False)
            with self.assertRaises(GatewayError):
                compose(repo,request,pre,mesh,base/"composed")


if __name__=="__main__":
    unittest.main()
