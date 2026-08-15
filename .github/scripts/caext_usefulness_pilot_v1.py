from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from code_atlas.change_intelligence import prepare_change
from code_atlas.change_intelligence.reporting import render_change_model_markdown
from code_atlas.change_intelligence.roi import build_roi_event
from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context

WORKERS = max(1, min(18, int(os.environ.get("CAEXT_WORKERS", "18"))))
PACKET_DIGEST_RULE = "SEMANTIC_STABLE_V1_EXCLUDES_VOLATILE_CODE_ATLAS_RUN_METADATA"
VOLATILE_PACKET_KEYS = {"generatedAt", "checksum", "packId", "modelDigest", "snapshotDigest"}
MAX_TEXT = 60_000
SOURCE_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts",
    ".java", ".kt", ".go", ".rs", ".cs", ".cpp", ".cc", ".c", ".h", ".hpp", ".rb",
    ".php", ".swift", ".scala", ".sql", ".prisma",
}
TEST_PARTS = {"test", "tests", "__tests__", "spec", "specs", "e2e"}
DOC_PARTS = {"docs", "doc", "documentation", "changelog", "changes"}
AUTHORITY_NAMES = {
    "agents.md", "codeowners", "contributing.md", "contributing.rst", "contributing",
    "security.md", "governance.md", "readme.md", "readme.rst", "readme",
}
MANIFEST_NAMES = {
    "pyproject.toml", "package.json", "go.mod", "cargo.toml", "pom.xml", "build.gradle",
    "build.gradle.kts", "requirements.txt", "setup.cfg", "tox.ini",
}


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    repo: str
    url: str
    commit: str
    task: str


TASKS = (
    TaskSpec(
        "U1", "fastapi/fastapi", "https://github.com/fastapi/fastapi.git",
        "aadfcce76380ab169fe172d5cda21722e53c4924",
        "Fix exclude_defaults not propagated to dict keys and values in jsonable_encoder.",
    ),
    TaskSpec(
        "U2", "go-chi/chi", "https://github.com/go-chi/chi.git",
        "878fe71fc9e506a63ea6957ed09c9ce84f789e97",
        "Fix defaultLogEntry.Panic not respecting the NoColor setting.",
    ),
    TaskSpec(
        "U3", "django/django", "https://github.com/django/django.git",
        "616e8c52ded7f4c7b00cae5a95f5a5d12a6a39b9",
        "Handle further malformed _source_model values in admin popups without returning HTTP 500 after save.",
    ),
    TaskSpec(
        "U4", "aio-libs/aiohttp", "https://github.com/aio-libs/aiohttp.git",
        "26fde219b38ab0416f47b8165769d9df3f2ffece",
        "Fix the parser when paused at the end of content-length.",
    ),
    TaskSpec(
        "U5", "astral-sh/ruff", "https://github.com/astral-sh/ruff.git",
        "8f703fcb76f06f5ca0a5aac7771f8735709ec965",
        "Skip FURB101 and FURB103 when the open argument is a file descriptor.",
    ),
    TaskSpec(
        "U6", "pydantic/pydantic", "https://github.com/pydantic/pydantic.git",
        "cc13d1b8c978eaf78ed5308329cd41f03ecc3144",
        "Fix JSON schema discriminator mapping keys for bool discriminators.",
    ),
)


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def semantic_packet_view(packet: dict[str, Any]) -> dict[str, Any]:
    """Return evaluator-visible semantics without run-volatile Code Atlas metadata."""
    value = copy.deepcopy(packet)
    value.pop("packetDigest", None)
    assistance = value.get("codeAtlasAssistance")
    if isinstance(assistance, dict):
        assistance.pop("changeReportMarkdown", None)

    def scrub(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: scrub(child) for key, child in item.items() if key not in VOLATILE_PACKET_KEYS}
        if isinstance(item, list):
            return [scrub(child) for child in item]
        return item

    return scrub(value)


def packet_digest(packet: dict[str, Any]) -> str:
    return sha_json(semantic_packet_view(packet))


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True, timeout: int = 1200) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    if check and proc.returncode:
        raise RuntimeError(f"COMMAND_FAILED[{proc.returncode}] {' '.join(cmd)}\n{proc.stderr[-4000:]}")
    return proc


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(repo), *args], check=check)


def git_text(repo: Path, *args: str) -> str | None:
    proc = git(repo, *args, check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


def condition_for(commit: str) -> str:
    return "ASSISTED" if int(commit[-1], 16) % 2 == 0 else "BASELINE"


def clone_commit(spec: TaskSpec, root: Path) -> Path:
    repo = root / spec.task_id
    run(["git", "init", str(repo)])
    git(repo, "remote", "add", "origin", spec.url)
    git(repo, "fetch", "--depth=2", "--no-tags", "origin", spec.commit)
    git(repo, "checkout", "--detach", "FETCH_HEAD")
    if git_text(repo, "rev-parse", "HEAD") != spec.commit:
        raise RuntimeError(f"PIN_MISMATCH:{spec.repo}")
    return repo


def parent_of(repo: Path, commit: str) -> str:
    parent = git_text(repo, "rev-parse", f"{commit}^1")
    if not parent:
        raise RuntimeError(f"FIRST_PARENT_UNAVAILABLE:{commit}")
    return parent


def path_exists(repo: Path, rev: str, rel: str) -> bool:
    proc = git(repo, "cat-file", "-e", f"{rev}:{rel}", check=False)
    return proc.returncode == 0


def is_test_path(rel: str) -> bool:
    path = Path(rel)
    parts = {part.lower() for part in path.parts}
    stem = path.stem.lower()
    return bool(
        parts & TEST_PARTS
        or path.name.lower().startswith(("test_", "spec_"))
        or stem.endswith(("_test", ".test", ".spec"))
    )


def is_doc_path(rel: str) -> bool:
    path = Path(rel)
    parts = {part.lower() for part in path.parts}
    return bool(parts & DOC_PARTS or path.suffix.lower() in {".md", ".rst", ".txt"})


def select_target(repo: Path, parent: str, actual: list[str]) -> tuple[str, str]:
    existing = [p for p in actual if path_exists(repo, parent, p)]
    source = [
        p for p in existing
        if Path(p).suffix.lower() in SOURCE_SUFFIXES and not is_test_path(p) and not is_doc_path(p)
    ]
    if source:
        return sorted(source)[0], "FIRST_EXISTING_NON_TEST_NON_DOC_SOURCE_PATH"
    source_any = [p for p in existing if Path(p).suffix.lower() in SOURCE_SUFFIXES and not is_test_path(p)]
    if source_any:
        return sorted(source_any)[0], "FIRST_EXISTING_NON_TEST_SOURCE_PATH"
    if existing:
        return sorted(existing)[0], "FIRST_EXISTING_CHANGED_PATH"
    raise RuntimeError("NO_PARENT_EXISTING_TARGET")


def tracked_paths(repo: Path, rev: str) -> list[str]:
    out = git_text(repo, "ls-tree", "-r", "--name-only", rev) or ""
    return sorted(line for line in out.splitlines() if line.strip())


def show_text(repo: Path, rev: str, rel: str, limit: int = MAX_TEXT) -> dict[str, Any]:
    proc = git(repo, "show", f"{rev}:{rel}", check=False)
    if proc.returncode:
        return {"path": rel, "available": False, "reason": "GIT_SHOW_FAILED"}
    text = proc.stdout
    truncated = len(text.encode("utf-8", errors="replace")) > limit
    if truncated:
        text = text[:limit]
    return {
        "path": rel,
        "available": True,
        "text": text,
        "truncated": truncated,
        "sha256": hashlib.sha256(proc.stdout.encode("utf-8", errors="replace")).hexdigest(),
    }


def authority_evidence(repo: Path, parent: str, paths: list[str]) -> list[dict[str, Any]]:
    candidates: list[str] = []
    for rel in paths:
        name = Path(rel).name.lower()
        if name in AUTHORITY_NAMES or name.startswith("readme"):
            candidates.append(rel)
    candidates = sorted(candidates, key=lambda p: (len(Path(p).parts), p))[:8]
    return [show_text(repo, parent, rel, 20_000) for rel in candidates]


def target_related_tests(paths: list[str], target: str) -> list[str]:
    tokens = {
        token.lower()
        for token in Path(target).stem.replace("-", "_").split("_")
        if len(token) >= 4
    }
    tests = [p for p in paths if is_test_path(p)]
    if not tokens:
        return tests[:30]
    scored: list[tuple[int, str]] = []
    for rel in tests:
        low = rel.lower()
        score = sum(1 for token in tokens if token in low)
        if score:
            scored.append((-score, rel))
    return [rel for _, rel in sorted(scored)[:30]]


def repo_native_packet(repo: Path, parent: str, target: str, all_paths: list[str]) -> dict[str, Any]:
    parent_dir = Path(target).parent.as_posix()
    siblings = [
        p for p in all_paths
        if Path(p).parent.as_posix() == parent_dir and p != target
    ][:50]
    manifests = [p for p in all_paths if Path(p).name.lower() in MANIFEST_NAMES][:20]
    tests = target_related_tests(all_paths, target)
    authorities = authority_evidence(repo, parent, all_paths)
    evidence_ids = ["repo:target"]
    evidence_ids += [f"repo:authority:{row['path']}" for row in authorities]
    evidence_ids += [f"repo:test-candidate:{p}" for p in tests]
    return {
        "targetEvidence": show_text(repo, parent, target),
        "siblingPaths": siblings,
        "manifestPaths": manifests,
        "authorityEvidence": authorities,
        "testCandidatePaths": tests,
        "evidenceIds": sorted(set(evidence_ids)),
        "rule": "REPO_NATIVE_PARENT_SNAPSHOT_ONLY_NO_FUTURE_DIFF",
    }


def assisted_evidence(repo: Path, root: Path, spec: TaskSpec, target: str) -> dict[str, Any]:
    context = resolve_intelligence_context(
        repo,
        root / f"context_{spec.task_id}",
        request=IntelligenceRequest(
            intent="VERIFY",
            domain="runtime",
            changed_paths=(target,),
            semantic_query=spec.task,
            workers=WORKERS,
        ),
    )
    prepared = prepare_change(
        repo,
        change_request=spec.task,
        target_paths=[target],
        output_root=root / f"prepare_{spec.task_id}",
        policy=None,
        domain="runtime",
        intent="VERIFY",
        workers=WORKERS,
    )
    model = prepared.get("changeModel") or {}
    pack = prepared.get("authorityPack")
    report_md = render_change_model_markdown(model) if model else None
    impact = model.get("impactRadius") or {}
    unknowns = list(model.get("unknowns") or [])
    blockers = list(model.get("blockers") or [])
    evidence_ids = ["ca:change-model", "ca:change-report"]
    if pack:
        evidence_ids.append("ca:authority-pack")
    evidence_ids += [f"ca:impact:{p}" for p in impact.get("impacted") or []]
    evidence_ids += [f"ca:unknown:{idx}" for idx, _ in enumerate(unknowns)]
    return {
        "preparedDecision": prepared.get("decision"),
        "authorityPack": pack,
        "changeModel": model,
        "changeReportMarkdown": report_md,
        "impactRadius": impact,
        "unknowns": unknowns,
        "blockers": blockers,
        "coverage": context.get("coverage"),
        "retrieval": context.get("retrieval"),
        "evidenceIds": evidence_ids,
        "rules": {
            "impactRadiusAuthorizes": False,
            "retrievalIsProof": False,
            "derivedIndexAuthoritative": False,
            "unknownRemainsUnknown": True,
        },
    }


def response_schema() -> dict[str, Any]:
    return {
        "requiredFields": [
            "taskId", "packetDigest", "decision", "editableScope", "inspectValidateScope",
            "testPathsToValidate", "unknowns", "evidenceReferences",
        ],
        "decisionValues": ["READY", "BLOCKED", "UNKNOWN"],
        "semantics": {
            "editableScope": "Paths the evaluator would authorize an implementation agent to modify now. Target is the only pre-authorized editable path.",
            "inspectValidateScope": "Paths the evaluator would inspect or validate without granting edit authorization.",
            "testPathsToValidate": "Repository test paths the evaluator would explicitly validate.",
            "unknowns": "Material unknowns the evaluator refuses to guess.",
            "evidenceReferences": "Evidence IDs from the packet used to justify the response.",
        },
        "forbidden": [
            "Do not infer hidden reasoning.",
            "Do not treat impact as edit authorization.",
            "Do not use future diff or ground truth.",
            "Do not claim production, enterprise, security, privacy/legal, hosted multi-tenant or human usefulness.",
        ],
    }


def prepare_one(spec: TaskSpec, work_root: Path, packets_root: Path, truth_root: Path) -> dict[str, Any]:
    baseline = clone_commit(spec, work_root)
    parent = parent_of(baseline, spec.commit)
    actual_text = git_text(baseline, "diff", "--name-only", "--no-renames", parent, spec.commit) or ""
    actual = sorted({line.strip() for line in actual_text.splitlines() if line.strip()})
    target, target_rule = select_target(baseline, parent, actual)
    condition = condition_for(spec.commit)
    git(baseline, "checkout", "--detach", parent)
    if git_text(baseline, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError(f"DIRTY_PARENT:{spec.repo}")
    all_paths = tracked_paths(baseline, parent)
    native = repo_native_packet(baseline, parent, target, all_paths)
    packet: dict[str, Any] = {
        "schemaVersion": "caext_usefulness_task_packet.v1",
        "pilotClaimCeiling": "SINGLE_EXTERNAL_AGENT_PILOT",
        "humanUsefulness": "NOT_MEASURED",
        "taskId": spec.task_id,
        "repository": spec.repo,
        "condition": condition,
        "assignmentRule": "LAST_HEX_PARITY_EVEN_ASSISTED_ODD_BASELINE",
        "historicalCommit": spec.commit,
        "parentCommit": parent,
        "parentTree": git_text(baseline, "rev-parse", "HEAD^{tree}"),
        "task": spec.task,
        "evaluatorProvidedTarget": target,
        "targetSelectionRule": target_rule,
        "targetDiscoveryMeasured": False,
        "editableAuthorization": [target],
        "repoNativeEvidence": native,
        "responseSchema": response_schema(),
        "groundTruthIncluded": False,
        "historyAuthorizes": False,
    }
    packet_evidence_ids = set(native["evidenceIds"])
    if condition == "ASSISTED":
        assisted = assisted_evidence(baseline, work_root, spec, target)
        packet["codeAtlasAssistance"] = assisted
        packet_evidence_ids.update(assisted["evidenceIds"])
    else:
        packet["codeAtlasAssistance"] = None
    packet["availableEvidenceIds"] = sorted(packet_evidence_ids)
    packet["packetDigestRule"] = PACKET_DIGEST_RULE
    packet["packetDigest"] = packet_digest(packet)
    dump(packets_root / f"{spec.task_id}.json", packet)

    actual_tests = sorted(p for p in actual if is_test_path(p))
    truth = {
        "schemaVersion": "caext_usefulness_ground_truth.v1",
        "taskId": spec.task_id,
        "repository": spec.repo,
        "condition": condition,
        "historicalCommit": spec.commit,
        "parentCommit": parent,
        "target": target,
        "targetSelectionRule": target_rule,
        "actualChangedPaths": actual,
        "actualCompanionPaths": sorted(p for p in actual if p != target),
        "actualChangedTestPaths": actual_tests,
        "packetDigest": packet["packetDigest"],
        "historyAuthorizes": False,
    }
    truth["groundTruthDigest"] = sha_json(truth)
    dump(truth_root / f"{spec.task_id}.json", truth)
    return {
        "taskId": spec.task_id,
        "repository": spec.repo,
        "condition": condition,
        "packetDigest": packet["packetDigest"],
        "parentCommit": parent,
        "targetSelectionRule": target_rule,
    }


def prepare(out: Path) -> dict[str, Any]:
    packets = out / "task_packets"
    truth = out / "ground_truth"
    work = out / "_work"
    packets.mkdir(parents=True, exist_ok=True)
    truth.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    rows = []
    try:
        for spec in TASKS:
            rows.append(prepare_one(spec, work, packets, truth))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    manifest = {
        "schemaVersion": "caext_usefulness_packet_manifest.v1",
        "classification": "VERIFY / EXTERNAL EVIDENCE",
        "claimCeiling": "SINGLE_EXTERNAL_AGENT_PILOT",
        "humanUsefulness": "NOT_MEASURED",
        "agentEvaluator": "ChatGPT / GPT-5.6 Sol via GitHub connector",
        "independentMultiAgentEvidence": False,
        "assignmentRule": "LAST_HEX_PARITY_EVEN_ASSISTED_ODD_BASELINE",
        "packetDigestRule": PACKET_DIGEST_RULE,
        "taskCount": len(rows),
        "conditions": {
            "ASSISTED": sum(1 for row in rows if row["condition"] == "ASSISTED"),
            "BASELINE": sum(1 for row in rows if row["condition"] == "BASELINE"),
        },
        "tasks": rows,
        "groundTruthSeparated": True,
        "targetDiscoveryMeasured": False,
        "observedTimeMetrics": "NOT_MEASURED",
        "humanSupervisionTime": "NOT_MEASURED",
        "workerPeak": "NOT_MEASURED",
        "financialEstimateAllowed": False,
        "causalUpliftClaimAllowed": False,
        "historyAuthorizes": False,
    }
    manifest["manifestDigest"] = sha_json(manifest)
    dump(packets / "MANIFEST.json", manifest)
    dump(truth / "GROUND_TRUTH_MANIFEST.json", {
        "schemaVersion": "caext_usefulness_ground_truth_manifest.v1",
        "taskIds": [row["taskId"] for row in rows],
        "packetManifestDigest": manifest["manifestDigest"],
        "doNotExposeBeforeResponses": True,
    })
    return manifest


def load_jsons(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("U*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        rows[str(value["taskId"])] = value
    return rows


def set_metric(predicted: Iterable[str], actual: Iterable[str]) -> dict[str, Any]:
    p = {str(x) for x in predicted if str(x)}
    a = {str(x) for x in actual if str(x)}
    hits = p & a
    return {
        "predictedCount": len(p),
        "actualCount": len(a),
        "hitCount": len(hits),
        "hits": sorted(hits),
        "missed": sorted(a - p),
        "extra": sorted(p - a),
        "recallPct": round(100 * len(hits) / len(a), 2) if a else "NOT_APPLICABLE",
        "precisionPct": round(100 * len(hits) / len(p), 2) if p else "NOT_APPLICABLE",
    }


def score(responses_path: Path, prepared_root: Path, out: Path) -> dict[str, Any]:
    packets = load_jsons(prepared_root / "task_packets")
    truths = load_jsons(prepared_root / "ground_truth")
    raw = json.loads(responses_path.read_text(encoding="utf-8"))
    if raw.get("schemaVersion") != "caext_usefulness_agent_responses.v1":
        raise RuntimeError("UNSUPPORTED_RESPONSE_SCHEMA")
    responses = {str(row.get("taskId")): row for row in raw.get("responses") or []}
    if set(responses) != set(packets):
        raise RuntimeError(f"RESPONSE_TASK_SET_MISMATCH:{sorted(responses)}:{sorted(packets)}")

    scored: list[dict[str, Any]] = []
    for task_id in sorted(packets):
        packet = packets[task_id]
        truth = truths[task_id]
        response = responses[task_id]
        if response.get("packetDigest") != packet.get("packetDigest"):
            raise RuntimeError(f"PACKET_DIGEST_MISMATCH:{task_id}")
        editable = [str(x) for x in response.get("editableScope") or []]
        inspect_scope = [str(x) for x in response.get("inspectValidateScope") or []]
        test_paths = [str(x) for x in response.get("testPathsToValidate") or []]
        unknowns = [str(x) for x in response.get("unknowns") or []]
        refs = [str(x) for x in response.get("evidenceReferences") or []]
        target = str(truth["target"])
        authorized = {target}
        violations = sorted(set(editable) - authorized)
        companions = truth.get("actualCompanionPaths") or []
        tests = truth.get("actualChangedTestPaths") or []
        companion_score = set_metric(inspect_scope, companions)
        test_score = set_metric(test_paths, tests)
        valid_ref_set = set(packet.get("availableEvidenceIds") or [])
        valid_refs = sorted(set(refs) & valid_ref_set)
        invalid_refs = sorted(set(refs) - valid_ref_set)
        valid_ref_rate = round(100 * len(valid_refs) / len(set(refs)), 2) if refs else 0.0
        assistance = packet.get("codeAtlasAssistance") or {}
        ca_unknowns = [str(x) for x in assistance.get("unknowns") or []]
        ca_decision = assistance.get("preparedDecision")
        fake_green = bool(packet["condition"] == "ASSISTED" and ca_decision in {"BLOCKED", "UNKNOWN"} and response.get("decision") == "READY")
        unknown_omission = bool(packet["condition"] == "ASSISTED" and ca_unknowns and not unknowns)
        result = {
            "taskId": task_id,
            "repository": packet["repository"],
            "condition": packet["condition"],
            "packetDigest": packet["packetDigest"],
            "decision": response.get("decision"),
            "targetIncludedEditable": target in editable,
            "editableScopeViolationCount": len(violations),
            "editableScopeViolations": violations,
            "authorizationWidened": bool(violations),
            "historicalCompanionInspection": companion_score,
            "historicalChangedTestSelection": test_score,
            "evidenceReferenceCount": len(set(refs)),
            "validEvidenceReferenceCount": len(valid_refs),
            "validEvidenceReferenceRatePct": valid_ref_rate,
            "invalidEvidenceReferences": invalid_refs,
            "unknownCount": len(unknowns),
            "assistedUnknownOmission": unknown_omission,
            "assistedFakeGreen": fake_green,
            "codeAtlasPreparedDecision": ca_decision if packet["condition"] == "ASSISTED" else "NOT_APPLICABLE",
            "historyAuthorizes": False,
        }
        scored.append(result)

    def avg_numeric(rows: list[dict[str, Any]], getter) -> float | str:
        vals = [getter(row) for row in rows]
        nums = [float(v) for v in vals if isinstance(v, (int, float))]
        return round(sum(nums) / len(nums), 2) if nums else "NOT_APPLICABLE"

    summaries: dict[str, Any] = {}
    for condition in ("BASELINE", "ASSISTED"):
        rows = [row for row in scored if row["condition"] == condition]
        summaries[condition] = {
            "taskCount": len(rows),
            "authorizationWideningRatePct": round(100 * sum(1 for r in rows if r["authorizationWidened"]) / max(1, len(rows)), 2),
            "targetIncludedEditableRatePct": round(100 * sum(1 for r in rows if r["targetIncludedEditable"]) / max(1, len(rows)), 2),
            "meanHistoricalCompanionInspectionRecallPct": avg_numeric(rows, lambda r: r["historicalCompanionInspection"]["recallPct"]),
            "meanHistoricalChangedTestRecallPct": avg_numeric(rows, lambda r: r["historicalChangedTestSelection"]["recallPct"]),
            "meanValidEvidenceReferenceRatePct": avg_numeric(rows, lambda r: r["validEvidenceReferenceRatePct"]),
            "assistedUnknownOmissionCount": sum(1 for r in rows if r["assistedUnknownOmission"]),
            "assistedFakeGreenCount": sum(1 for r in rows if r["assistedFakeGreen"]),
        }

    all_edit_entries = sum(len((responses[row["taskId"]].get("editableScope") or [])) for row in scored)
    all_violations = sum(row["editableScopeViolationCount"] for row in scored)
    evidence_rates = [row["validEvidenceReferenceRatePct"] for row in scored]
    observed_roi = build_roi_event(
        metric_values={
            "outOfScopeChangeRate": round(all_violations / max(1, all_edit_entries), 6),
            "evidenceCompletenessRate": round(sum(evidence_rates) / max(1, len(evidence_rates)) / 100, 6),
        },
        source="caext.single_external_agent_pilot.v1",
    )

    state = {
        "schemaVersion": "caext_usefulness_agent_pilot_result.v1",
        "classification": "VERIFY / EXTERNAL EVIDENCE",
        "agentUsefulness": "SINGLE_EXTERNAL_AGENT_PILOT_MEASURED_NO_CAUSAL_CLAIM",
        "humanUsefulness": "NOT_MEASURED",
        "evaluator": raw.get("evaluator"),
        "taskCount": len(scored),
        "conditionSummary": summaries,
        "tasks": scored,
        "observedRawRoiEvent": observed_roi,
        "notMeasured": [
            "contextDiscoveryTime",
            "changeScopeIdentificationTime",
            "humanSupervisionTime",
            "evidenceAssemblyTime",
            "reopenedWorkRate",
            "changeReadinessThroughput",
            "workerPeak",
        ],
        "causalUpliftClaimAllowed": False,
        "limitations": [
            "single external evaluator only",
            "baseline and assisted conditions use different tasks, so task heterogeneity confounds condition comparison",
            "historical diffs are bounded ground truth for companion/test comparison, not universal correct-scope truth",
            "target discovery is controlled out of the experiment and remains NOT_MEASURED",
            "no human evaluation was performed",
        ],
        "historyAuthorizes": False,
        "certifiable": False,
        "productionCertified": False,
        "financialEstimateGenerated": False,
    }
    state["resultDigest"] = sha_json(state)
    dump(out / "USEFULNESS_RESULT.json", state)
    dump(out / "SCORED_TASKS.json", scored)
    return state


def selftest() -> None:
    assert len(TASKS) == 6
    conditions = [condition_for(spec.commit) for spec in TASKS]
    assert conditions.count("ASSISTED") == 3, conditions
    assert conditions.count("BASELINE") == 3, conditions
    assert condition_for("0") == "ASSISTED"
    assert condition_for("1") == "BASELINE"
    schema = response_schema()
    assert "editableScope" in schema["requiredFields"]
    volatile_a = {
        "taskId": "fixture",
        "packetDigestRule": PACKET_DIGEST_RULE,
        "codeAtlasAssistance": {
            "authorityPack": {"allowedScope": ["x.py"], "generatedAt": "T1", "packId": "A", "checksum": "1"},
            "changeModel": {"decision": "PASS", "generatedAt": "T1", "modelDigest": "1", "repositorySnapshot": {"snapshotDigest": "A"}},
            "changeReportMarkdown": "volatile render 1",
        },
    }
    volatile_b = copy.deepcopy(volatile_a)
    volatile_b["codeAtlasAssistance"]["authorityPack"].update({"generatedAt": "T2", "packId": "B", "checksum": "2"})
    volatile_b["codeAtlasAssistance"]["changeModel"].update({"generatedAt": "T2", "modelDigest": "2"})
    volatile_b["codeAtlasAssistance"]["changeModel"]["repositorySnapshot"]["snapshotDigest"] = "B"
    volatile_b["codeAtlasAssistance"]["changeReportMarkdown"] = "volatile render 2"
    assert packet_digest(volatile_a) == packet_digest(volatile_b)
    semantic_change = copy.deepcopy(volatile_b)
    semantic_change["codeAtlasAssistance"]["authorityPack"]["allowedScope"] = ["other.py"]
    assert packet_digest(volatile_a) != packet_digest(semantic_change)
    print("PASS_CAEXT_USEFULNESS_PILOT_SELFTEST")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--output", required=True)
    p_score = sub.add_parser("score")
    p_score.add_argument("--prepared-root", required=True)
    p_score.add_argument("--responses", required=True)
    p_score.add_argument("--output", required=True)
    sub.add_parser("selftest")
    args = parser.parse_args()

    if args.mode == "selftest":
        selftest()
        return 0
    if args.mode == "prepare":
        manifest = prepare(Path(args.output).resolve())
        print(json.dumps({
            "status": "PASS_USEFULNESS_PACKETS_PREPARED",
            "manifestDigest": manifest["manifestDigest"],
            "conditions": manifest["conditions"],
        }, sort_keys=True))
        return 0
    if args.mode == "score":
        state = score(
            Path(args.responses).resolve(),
            Path(args.prepared_root).resolve(),
            Path(args.output).resolve(),
        )
        print(json.dumps({
            "status": "PASS_USEFULNESS_AGENT_PILOT_SCORED",
            "classification": state["agentUsefulness"],
            "resultDigest": state["resultDigest"],
        }, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
