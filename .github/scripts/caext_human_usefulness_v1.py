from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import statistics
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

SCHEMA_PACKET = "caext_human_usefulness_packet.v1"
SCHEMA_REVIEWER_MANIFEST = "caext_human_usefulness_reviewer_manifest.v1"
SCHEMA_STUDY_MAP = "caext_human_usefulness_study_map.v1"
SCHEMA_SCORING_MANIFEST = "caext_human_usefulness_scoring_manifest.v1"
SCHEMA_RESPONSES = "caext_human_usefulness_responses.v1"
SCHEMA_SCORE = "caext_human_usefulness_score.v1"
DEFAULT_SEED = "ca-human-usefulness-v1"
CONDITIONS = ("BASELINE", "ASSISTED")
DECISIONS = {"READY", "BLOCKED", "UNKNOWN"}
ELAPSED_SOURCES = {"OBSERVED", "SELF_REPORTED", "NOT_MEASURED"}
MATERIAL_VALUES = {"YES", "NO", "UNCERTAIN"}
REASON_CODES = {
    "SCOPE_CLARITY",
    "DEPENDENCY_CONTEXT",
    "TEST_SELECTION",
    "EVIDENCE_QUALITY",
    "UNKNOWN_HANDLING",
    "DECISION_CONFIDENCE",
    "FASTER_REVIEW",
    "NO_MATERIAL_DIFFERENCE",
    "OTHER",
}
PSEUDONYM_RE = re.compile(r"^[A-Za-z0-9._-]{3,64}$")
VOLATILE_PACKET_KEYS = {"generatedAt", "checksum", "packId", "modelDigest", "snapshotDigest"}
FORBIDDEN_REVIEWER_KEYS = {
    "condition",
    "historicalCommit",
    "actualChangedPaths",
    "actualCompanionPaths",
    "actualChangedTestPaths",
    "groundTruthDigest",
    "futureDiff",
}


def _dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha_json(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _opaque(prefix: str, seed: str, *parts: str, length: int = 14) -> str:
    material = "\x1f".join((seed, *parts)).encode("utf-8")
    return f"{prefix}{hashlib.sha256(material).hexdigest()[:length]}"


def _stable_rank(seed: str, bucket: str, value: str) -> str:
    return hashlib.sha256(f"{seed}\x1f{bucket}\x1f{value}".encode("utf-8")).hexdigest()


def _progress(stage: str, done: int, total: int) -> None:
    pct = round(100 * done / max(1, total), 1)
    print(f"HUMAN_KIT_PROGRESS={pct}% stage={stage} done={done}/{total}", flush=True)


def _new_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise RuntimeError(f"OUTPUT_NOT_EMPTY:{path}")
    path.mkdir(parents=True, exist_ok=True)


def _load_pilot(repo_root: Path) -> Any:
    path = repo_root / ".github" / "scripts" / "caext_usefulness_pilot_v1.py"
    if not path.is_file():
        raise RuntimeError(f"EXISTING_USEFULNESS_PILOT_MISSING:{path}")
    spec = importlib.util.spec_from_file_location("caext_usefulness_pilot_v1_readonly", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("EXISTING_USEFULNESS_PILOT_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    required = {
        "TASKS", "clone_commit", "parent_of", "git_text", "git", "select_target",
        "tracked_paths", "repo_native_packet", "assisted_evidence", "is_test_path", "packet_digest",
    }
    missing = sorted(name for name in required if not hasattr(module, name))
    if missing:
        raise RuntimeError(f"EXISTING_USEFULNESS_PILOT_CONTRACT_MISSING:{missing}")
    return module


def _study_id(seed: str, tasks: Iterable[Any]) -> str:
    facts = [
        {
            "taskId": str(task.task_id),
            "repository": str(task.repo),
            "historicalCommit": str(task.commit),
            "task": str(task.task),
        }
        for task in tasks
    ]
    return "HUS-" + hashlib.sha256((seed + "\x1e").encode("utf-8") + _canonical_bytes(facts)).hexdigest()[:16]


def _semantic_packet_view(packet: dict[str, Any]) -> dict[str, Any]:
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


def _packet_digest(packet: dict[str, Any], pilot: Any | None = None) -> str:
    del pilot
    return _sha_json(_semantic_packet_view(packet))


def _response_schema() -> dict[str, Any]:
    return {
        "requiredResponseFields": [
            "packetId", "packetDigest", "decision", "editableScope", "inspectValidateScope",
            "testPathsToValidate", "unknowns", "evidenceReferences", "elapsedSource",
        ],
        "decisionValues": sorted(DECISIONS),
        "elapsedSourceValues": sorted(ELAPSED_SOURCES),
        "pairComparisonFields": ["caseId", "preferredPacketId", "materialDifference", "reasonCodes"],
        "materialDifferenceValues": sorted(MATERIAL_VALUES),
        "reasonCodeValues": sorted(REASON_CODES),
        "semantics": {
            "editableScope": "Paths the reviewer would authorize an implementation agent to modify now.",
            "inspectValidateScope": "Paths the reviewer would inspect or validate without edit authorization.",
            "testPathsToValidate": "Repository test paths the reviewer would explicitly validate.",
            "unknowns": "Material unknowns the reviewer refuses to guess.",
            "evidenceReferences": "Evidence IDs from the packet used to justify the response.",
            "elapsedSeconds": "Optional observed or self-reported task time. Omit when not measured.",
        },
        "rules": [
            "Do not use future history or the sealed scoring bundle while answering packets.",
            "Impact radius is not edit authorization.",
            "Unknown remains unknown when evidence is insufficient.",
            "Complete all packet responses before the pair-comparison debrief.",
        ],
    }


def _presentation_order(seed: str, cases: list[dict[str, Any]]) -> list[str]:
    first_rows: list[tuple[str, str, str]] = []
    second_rows: list[tuple[str, str, str]] = []
    for case in cases:
        case_id = str(case["caseId"])
        variants = case["variants"]
        flip = int(_stable_rank(seed, "flip", case_id), 16) % 2
        first_condition = CONDITIONS[flip]
        second_condition = CONDITIONS[1 - flip]
        first_rows.append((_stable_rank(seed, "block1", case_id), case_id, variants[first_condition]))
        second_rows.append((_stable_rank(seed, "block2", case_id), case_id, variants[second_condition]))
    first_rows.sort()
    second_rows.sort()
    if first_rows and second_rows and first_rows[-1][1] == second_rows[0][1] and len(second_rows) > 1:
        second_rows = second_rows[1:] + second_rows[:1]
    order = [row[2] for row in first_rows] + [row[2] for row in second_rows]
    if len(order) != len(set(order)):
        raise RuntimeError("PRESENTATION_ORDER_NOT_UNIQUE")
    return order


def _assert_no_ground_truth_leak(value: Any, *, where: str, root: bool = True) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_REVIEWER_KEYS if root else {
            "actualChangedPaths", "actualCompanionPaths", "actualChangedTestPaths",
            "groundTruthDigest", "futureDiff",
        }
        bad = forbidden & set(value)
        if bad:
            raise RuntimeError(f"GROUND_TRUTH_KEY_LEAK:{where}:{sorted(bad)}")
        for key, child in value.items():
            _assert_no_ground_truth_leak(child, where=f"{where}.{key}", root=False)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            _assert_no_ground_truth_leak(child, where=f"{where}[{idx}]", root=False)


def _build_case(
    pilot: Any,
    spec: Any,
    *,
    work_root: Path,
    packets_root: Path,
    truth_root: Path,
    seed: str,
    study_id: str,
) -> dict[str, Any]:
    repo = pilot.clone_commit(spec, work_root)
    parent = pilot.parent_of(repo, spec.commit)
    actual_text = pilot.git_text(repo, "diff", "--name-only", "--no-renames", parent, spec.commit) or ""
    actual = sorted({line.strip() for line in actual_text.splitlines() if line.strip()})
    target, target_rule = pilot.select_target(repo, parent, actual)
    pilot.git(repo, "checkout", "--detach", parent)
    if pilot.git_text(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError(f"DIRTY_PARENT:{spec.repo}")
    all_paths = pilot.tracked_paths(repo, parent)
    native = pilot.repo_native_packet(repo, parent, target, all_paths)
    assistance = pilot.assisted_evidence(repo, work_root, spec, target)
    case_id = _opaque("C", seed, str(spec.task_id), str(spec.repo))
    packet_ids = {
        condition: _opaque("P", seed, str(spec.task_id), condition)
        for condition in CONDITIONS
    }
    packet_digests: dict[str, str] = {}
    for condition in CONDITIONS:
        packet_id = packet_ids[condition]
        evidence_ids = set(native.get("evidenceIds") or [])
        packet: dict[str, Any] = {
            "schemaVersion": SCHEMA_PACKET,
            "studyId": study_id,
            "caseId": case_id,
            "packetId": packet_id,
            "repository": str(spec.repo),
            "parentCommit": parent,
            "parentTree": pilot.git_text(repo, "rev-parse", "HEAD^{tree}"),
            "task": str(spec.task),
            "evaluatorProvidedTarget": target,
            "targetSelectionRule": target_rule,
            "targetDiscoveryMeasured": False,
            "editableAuthorization": [target],
            "repoNativeEvidence": copy.deepcopy(native),
            "codeAtlasAssistance": None,
            "responseSchema": _response_schema(),
            "availableEvidenceIds": [],
            "groundTruthIncluded": False,
            "futureDiffIncluded": False,
            "historyAuthorizes": False,
            "humanUsefulness": "NOT_MEASURED",
            "claimCeiling": "STUDY_PACKET_ONLY",
        }
        if condition == "ASSISTED":
            packet["codeAtlasAssistance"] = copy.deepcopy(assistance)
            evidence_ids.update(assistance.get("evidenceIds") or [])
        packet["availableEvidenceIds"] = sorted(str(x) for x in evidence_ids)
        _assert_no_ground_truth_leak(packet, where=packet_id)
        packet["packetDigest"] = _packet_digest(packet, pilot)
        packet_digests[condition] = packet["packetDigest"]
        _dump(packets_root / f"{packet_id}.json", packet)

    truth = {
        "schemaVersion": "caext_human_usefulness_ground_truth.v1",
        "studyId": study_id,
        "caseId": case_id,
        "taskId": str(spec.task_id),
        "repository": str(spec.repo),
        "historicalCommit": str(spec.commit),
        "parentCommit": parent,
        "target": target,
        "targetSelectionRule": target_rule,
        "actualChangedPaths": actual,
        "actualCompanionPaths": sorted(path for path in actual if path != target),
        "actualChangedTestPaths": sorted(path for path in actual if pilot.is_test_path(path)),
        "packetIds": packet_ids,
        "packetDigests": packet_digests,
        "historyAuthorizes": False,
    }
    truth["groundTruthDigest"] = _sha_json(truth)
    _dump(truth_root / f"{case_id}.json", truth)
    return {
        "caseId": case_id,
        "repository": str(spec.repo),
        "variants": packet_ids,
        "packetDigests": packet_digests,
        "parentCommit": parent,
        "parentTree": pilot.git_text(repo, "rev-parse", "HEAD^{tree}"),
        "target": target,
        "historicalCommit": str(spec.commit),
        "groundTruthDigest": truth["groundTruthDigest"],
    }


def _write_study_manifests(
    *,
    reviewer_root: Path,
    sealed_root: Path,
    seed: str,
    study_id: str,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    public_cases = [
        {
            "caseId": case["caseId"],
            "repository": case["repository"],
            "packetIds": sorted(case["variants"].values()),
        }
        for case in cases
    ]
    order = _presentation_order(seed, cases)
    manifest = {
        "schemaVersion": SCHEMA_REVIEWER_MANIFEST,
        "studyId": study_id,
        "protocol": "PAIRED_SAME_TASK_SINGLE_EXTERNAL_HUMAN_V1",
        "humanUsefulness": "NOT_MEASURED",
        "claimCeiling": "STUDY_KIT_READY_NOT_MEASURED",
        "taskPairCount": len(cases),
        "packetCount": len(order),
        "presentationOrder": order,
        "casePairs": public_cases,
        "conditionLabelsExposed": False,
        "groundTruthSeparated": True,
        "futureDiffIncluded": False,
        "targetDiscoveryMeasured": False,
        "singleReviewerGeneralizationAllowed": False,
        "causalClaimAllowed": False,
        "orderEffectEliminated": False,
        "orderMitigation": "TWO_BLOCK_DETERMINISTIC_COUNTERBALANCING_NON_ADJACENT_PAIRS_WHERE_POSSIBLE",
        "responseSchema": _response_schema(),
    }
    manifest["manifestDigest"] = _sha_json(manifest)
    _dump(reviewer_root / "MANIFEST.json", manifest)

    response_template = {
        "schemaVersion": SCHEMA_RESPONSES,
        "studyId": study_id,
        "reviewer": {
            "reviewerId": "REPLACE_WITH_PSEUDONYM",
            "reviewerType": "EXTERNAL_HUMAN",
            "independenceAttested": True,
            "role": "TECHNICAL_REVIEWER",
        },
        "responses": [
            {
                "packetId": packet_id,
                "packetDigest": _load(reviewer_root / "packets" / f"{packet_id}.json")["packetDigest"],
                "decision": "UNKNOWN",
                "editableScope": [],
                "inspectValidateScope": [],
                "testPathsToValidate": [],
                "unknowns": [],
                "evidenceReferences": [],
                "elapsedSource": "NOT_MEASURED",
            }
            for packet_id in order
        ],
        "pairComparisons": [
            {
                "caseId": case["caseId"],
                "preferredPacketId": "TIE",
                "materialDifference": "UNCERTAIN",
                "reasonCodes": ["NO_MATERIAL_DIFFERENCE"],
            }
            for case in public_cases
        ],
    }
    _dump(reviewer_root / "RESPONSE_TEMPLATE.json", response_template)
    _dump(reviewer_root / "REVIEWER_PROTOCOL.json", {
        "schemaVersion": "caext_human_usefulness_reviewer_protocol.v1",
        "studyId": study_id,
        "instructions": [
            "Use packets in MANIFEST.presentationOrder.",
            "Do not inspect the sealed scoring bundle or future repository history before submitting all packet responses.",
            "Treat evaluatorProvidedTarget as the only pre-authorized editable path unless repository evidence blocks the task.",
            "Impact or dependency evidence may expand inspection, never edit authorization.",
            "Preserve material unknowns instead of guessing.",
            "Complete pairComparisons only after all packet responses are complete.",
        ],
        "identityRule": "PSEUDONYM_ONLY_NO_EMAIL_REQUIRED",
        "timeRule": "OBSERVED_OR_SELF_REPORTED_MAY_BE_RECORDED; OTHERWISE_NOT_MEASURED",
        "claimRule": "ONE_REVIEWER_IS_DESCRIPTIVE_AND_NON_GENERALIZABLE",
    })

    study_map = {
        "schemaVersion": SCHEMA_STUDY_MAP,
        "studyId": study_id,
        "seedDigest": _sha_bytes(seed.encode("utf-8")),
        "variants": {
            packet_id: {
                "caseId": case["caseId"],
                "taskId": _load(sealed_root / "truth" / f"{case['caseId']}.json")["taskId"],
                "repository": case["repository"],
                "condition": condition,
                "packetDigest": case["packetDigests"][condition],
                "historicalCommit": case["historicalCommit"],
                "parentCommit": case["parentCommit"],
                "target": case["target"],
            }
            for case in cases
            for condition, packet_id in case["variants"].items()
        },
        "presentationOrder": order,
        "doNotExposeBeforeResponses": True,
    }
    study_map["studyMapDigest"] = _sha_json(study_map)
    _dump(sealed_root / "STUDY_MAP.json", study_map)
    truth_digests = {
        case["caseId"]: case["groundTruthDigest"]
        for case in cases
    }
    scoring_manifest = {
        "schemaVersion": SCHEMA_SCORING_MANIFEST,
        "studyId": study_id,
        "reviewerManifestDigest": manifest["manifestDigest"],
        "studyMapDigest": study_map["studyMapDigest"],
        "truthDigests": truth_digests,
        "packetDigests": {
            packet_id: row["packetDigest"]
            for packet_id, row in study_map["variants"].items()
        },
        "groundTruthSeparated": True,
        "humanUsefulness": "NOT_MEASURED",
        "productionCertified": False,
    }
    scoring_manifest["scoringManifestDigest"] = _sha_json(scoring_manifest)
    _dump(sealed_root / "SCORING_MANIFEST.json", scoring_manifest)
    return manifest


def prepare(out: Path, *, repo_root: Path, seed: str) -> dict[str, Any]:
    _new_output(out)
    reviewer = out / "reviewer_bundle"
    sealed = out / "sealed_scoring_bundle"
    packets = reviewer / "packets"
    truth = sealed / "truth"
    work = out / "_work"
    packets.mkdir(parents=True, exist_ok=True)
    truth.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    pilot = _load_pilot(repo_root)
    tasks = tuple(pilot.TASKS)
    if len(tasks) < 2:
        raise RuntimeError("INSUFFICIENT_PINNED_TASKS_FOR_PAIRED_STUDY")
    study_id = _study_id(seed, tasks)
    cases: list[dict[str, Any]] = []
    try:
        for idx, task in enumerate(tasks, start=1):
            _progress(f"prepare:{task.task_id}", idx - 1, len(tasks))
            cases.append(
                _build_case(
                    pilot,
                    task,
                    work_root=work,
                    packets_root=packets,
                    truth_root=truth,
                    seed=seed,
                    study_id=study_id,
                )
            )
            _progress(f"prepared:{task.task_id}", idx, len(tasks))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    manifest = _write_study_manifests(
        reviewer_root=reviewer,
        sealed_root=sealed,
        seed=seed,
        study_id=study_id,
        cases=cases,
    )
    validate_prepared(out)
    print(f"HUMAN_USEFULNESS_PREPARED={study_id}")
    return manifest


def _load_packets(reviewer_root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted((reviewer_root / "packets").glob("P*.json")):
        row = _load(path)
        packet_id = str(row.get("packetId") or "")
        if not packet_id or packet_id in result:
            raise RuntimeError(f"PACKET_ID_INVALID_OR_DUPLICATE:{path}")
        result[packet_id] = row
    return result


def _load_truths(sealed_root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted((sealed_root / "truth").glob("C*.json")):
        row = _load(path)
        case_id = str(row.get("caseId") or "")
        if not case_id or case_id in result:
            raise RuntimeError(f"CASE_ID_INVALID_OR_DUPLICATE:{path}")
        result[case_id] = row
    return result


def validate_prepared(prepared_root: Path) -> dict[str, Any]:
    reviewer = prepared_root / "reviewer_bundle"
    sealed = prepared_root / "sealed_scoring_bundle"
    manifest = _load(reviewer / "MANIFEST.json")
    if manifest.get("schemaVersion") != SCHEMA_REVIEWER_MANIFEST:
        raise RuntimeError("REVIEWER_MANIFEST_SCHEMA_MISMATCH")
    manifest_copy = dict(manifest)
    manifest_digest = manifest_copy.pop("manifestDigest", None)
    if manifest_digest != _sha_json(manifest_copy):
        raise RuntimeError("REVIEWER_MANIFEST_DIGEST_MISMATCH")
    packets = _load_packets(reviewer)
    order = [str(x) for x in manifest.get("presentationOrder") or []]
    if len(order) != len(packets) or set(order) != set(packets):
        raise RuntimeError("PRESENTATION_PACKET_SET_MISMATCH")
    for packet_id, packet in packets.items():
        if packet.get("schemaVersion") != SCHEMA_PACKET:
            raise RuntimeError(f"PACKET_SCHEMA_MISMATCH:{packet_id}")
        _assert_no_ground_truth_leak(packet, where=packet_id)
        expected = packet.get("packetDigest")
        actual = _packet_digest(packet)
        if expected != actual:
            raise RuntimeError(f"PACKET_DIGEST_MISMATCH:{packet_id}")
        if packet.get("studyId") != manifest.get("studyId"):
            raise RuntimeError(f"PACKET_STUDY_MISMATCH:{packet_id}")
    study_map = _load(sealed / "STUDY_MAP.json")
    if study_map.get("schemaVersion") != SCHEMA_STUDY_MAP:
        raise RuntimeError("STUDY_MAP_SCHEMA_MISMATCH")
    study_map_copy = dict(study_map)
    map_digest = study_map_copy.pop("studyMapDigest", None)
    if map_digest != _sha_json(study_map_copy):
        raise RuntimeError("STUDY_MAP_DIGEST_MISMATCH")
    if set(study_map.get("variants") or {}) != set(packets):
        raise RuntimeError("STUDY_MAP_PACKET_SET_MISMATCH")
    truths = _load_truths(sealed)
    for case_id, truth in truths.items():
        truth_copy = dict(truth)
        expected = truth_copy.pop("groundTruthDigest", None)
        if expected != _sha_json(truth_copy):
            raise RuntimeError(f"GROUND_TRUTH_DIGEST_MISMATCH:{case_id}")
    scoring = _load(sealed / "SCORING_MANIFEST.json")
    if scoring.get("schemaVersion") != SCHEMA_SCORING_MANIFEST:
        raise RuntimeError("SCORING_MANIFEST_SCHEMA_MISMATCH")
    scoring_copy = dict(scoring)
    scoring_digest = scoring_copy.pop("scoringManifestDigest", None)
    if scoring_digest != _sha_json(scoring_copy):
        raise RuntimeError("SCORING_MANIFEST_DIGEST_MISMATCH")
    if scoring.get("reviewerManifestDigest") != manifest_digest:
        raise RuntimeError("SCORING_REVIEWER_MANIFEST_BINDING_MISMATCH")
    if scoring.get("studyMapDigest") != map_digest:
        raise RuntimeError("SCORING_STUDY_MAP_BINDING_MISMATCH")
    if scoring.get("packetDigests") != {
        packet_id: packet["packetDigest"] for packet_id, packet in sorted(packets.items())
    }:
        raise RuntimeError("SCORING_PACKET_DIGEST_BINDING_MISMATCH")
    expected_truth = {case_id: truth["groundTruthDigest"] for case_id, truth in sorted(truths.items())}
    if scoring.get("truthDigests") != expected_truth:
        raise RuntimeError("SCORING_TRUTH_DIGEST_BINDING_MISMATCH")
    return {
        "studyId": manifest["studyId"],
        "packetCount": len(packets),
        "caseCount": len(truths),
        "status": "PASS_PREPARED_STUDY_INTEGRITY",
    }


def _set_metric(predicted: Iterable[str], actual: Iterable[str]) -> dict[str, Any]:
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


def _avg_numeric(values: Iterable[Any]) -> float | str:
    nums = [float(value) for value in values if isinstance(value, (int, float))]
    return round(sum(nums) / len(nums), 2) if nums else "NOT_APPLICABLE"


def _median_numeric(values: Iterable[Any]) -> float | str:
    nums = [float(value) for value in values if isinstance(value, (int, float))]
    return round(float(statistics.median(nums)), 2) if nums else "NOT_APPLICABLE"


def _validate_reviewer(reviewer: dict[str, Any]) -> dict[str, Any]:
    reviewer_id = str(reviewer.get("reviewerId") or "")
    if not PSEUDONYM_RE.fullmatch(reviewer_id) or "@" in reviewer_id:
        raise RuntimeError("REVIEWER_ID_MUST_BE_PSEUDONYMOUS")
    if reviewer.get("reviewerType") != "EXTERNAL_HUMAN":
        raise RuntimeError("REVIEWER_TYPE_MUST_BE_EXTERNAL_HUMAN")
    if reviewer.get("independenceAttested") is not True:
        raise RuntimeError("REVIEWER_INDEPENDENCE_ATTESTATION_REQUIRED")
    return {
        "reviewerId": reviewer_id,
        "reviewerType": "EXTERNAL_HUMAN",
        "independenceAttested": True,
        "role": str(reviewer.get("role") or "TECHNICAL_REVIEWER"),
        "identityIndependentlyVerified": False,
        "independenceEvidence": "REVIEWER_SELF_ATTESTATION_ONLY",
    }


def score(*, prepared_root: Path, responses_path: Path, out: Path) -> dict[str, Any]:
    _new_output(out)
    validation = validate_prepared(prepared_root)
    reviewer_root = prepared_root / "reviewer_bundle"
    sealed_root = prepared_root / "sealed_scoring_bundle"
    packets = _load_packets(reviewer_root)
    truths = _load_truths(sealed_root)
    study_map = _load(sealed_root / "STUDY_MAP.json")
    raw_bytes = responses_path.read_bytes()
    raw = json.loads(raw_bytes.decode("utf-8"))
    if raw.get("schemaVersion") != SCHEMA_RESPONSES:
        raise RuntimeError("UNSUPPORTED_HUMAN_RESPONSE_SCHEMA")
    if raw.get("studyId") != validation["studyId"]:
        raise RuntimeError("RESPONSE_STUDY_ID_MISMATCH")
    reviewer = _validate_reviewer(raw.get("reviewer") or {})
    response_rows = raw.get("responses") or []
    responses = {str(row.get("packetId") or ""): row for row in response_rows}
    if len(responses) != len(response_rows):
        raise RuntimeError("DUPLICATE_RESPONSE_PACKET_ID")
    if set(responses) != set(packets):
        raise RuntimeError("RESPONSE_PACKET_SET_MISMATCH")
    pair_rows = raw.get("pairComparisons") or []
    pairs = {str(row.get("caseId") or ""): row for row in pair_rows}
    if len(pairs) != len(pair_rows) or set(pairs) != set(truths):
        raise RuntimeError("PAIR_COMPARISON_CASE_SET_MISMATCH")

    raw_copy = out / "RAW_RESPONSES.json"
    raw_copy.write_bytes(raw_bytes)
    raw_digest = _sha_bytes(raw_bytes)
    scored: list[dict[str, Any]] = []
    for packet_id in sorted(packets):
        packet = packets[packet_id]
        variant = (study_map.get("variants") or {}).get(packet_id) or {}
        case_id = str(variant.get("caseId") or "")
        truth = truths.get(case_id)
        if truth is None:
            raise RuntimeError(f"TRUTH_MISSING_FOR_PACKET:{packet_id}")
        response = responses[packet_id]
        if response.get("packetDigest") != packet.get("packetDigest"):
            raise RuntimeError(f"RESPONSE_PACKET_DIGEST_MISMATCH:{packet_id}")
        if response.get("decision") not in DECISIONS:
            raise RuntimeError(f"INVALID_DECISION:{packet_id}")
        editable = [str(x) for x in response.get("editableScope") or []]
        inspect_scope = [str(x) for x in response.get("inspectValidateScope") or []]
        test_paths = [str(x) for x in response.get("testPathsToValidate") or []]
        unknowns = [str(x) for x in response.get("unknowns") or []]
        refs = [str(x) for x in response.get("evidenceReferences") or []]
        elapsed_source = str(response.get("elapsedSource") or "")
        if elapsed_source not in ELAPSED_SOURCES:
            raise RuntimeError(f"INVALID_ELAPSED_SOURCE:{packet_id}")
        elapsed = response.get("elapsedSeconds")
        if elapsed_source == "NOT_MEASURED":
            if elapsed is not None:
                raise RuntimeError(f"ELAPSED_PRESENT_WHEN_NOT_MEASURED:{packet_id}")
        else:
            if not isinstance(elapsed, (int, float)) or elapsed < 0:
                raise RuntimeError(f"INVALID_ELAPSED_SECONDS:{packet_id}")
            elapsed = round(float(elapsed), 3)
        target = str(truth["target"])
        authorized = {target}
        violations = sorted(set(editable) - authorized)
        companion_metric = _set_metric(inspect_scope, truth.get("actualCompanionPaths") or [])
        test_metric = _set_metric(test_paths, truth.get("actualChangedTestPaths") or [])
        valid_ids = set(packet.get("availableEvidenceIds") or [])
        valid_refs = sorted(set(refs) & valid_ids)
        invalid_refs = sorted(set(refs) - valid_ids)
        assistance = packet.get("codeAtlasAssistance") or {}
        condition = str(variant.get("condition") or "")
        ca_unknowns = [str(x) for x in assistance.get("unknowns") or []]
        ca_decision = assistance.get("preparedDecision") if condition == "ASSISTED" else "NOT_APPLICABLE"
        scored.append({
            "packetId": packet_id,
            "caseId": case_id,
            "taskId": variant.get("taskId"),
            "repository": variant.get("repository"),
            "condition": condition,
            "packetDigest": packet["packetDigest"],
            "decision": response["decision"],
            "targetIncludedEditable": target in editable,
            "editableScopeViolationCount": len(violations),
            "editableScopeViolations": violations,
            "authorizationWidened": bool(violations),
            "historicalCompanionInspection": companion_metric,
            "historicalChangedTestSelection": test_metric,
            "evidenceReferenceCount": len(set(refs)),
            "validEvidenceReferenceCount": len(valid_refs),
            "validEvidenceReferenceRatePct": round(100 * len(valid_refs) / len(set(refs)), 2) if refs else 0.0,
            "invalidEvidenceReferences": invalid_refs,
            "unknownCount": len(unknowns),
            "assistedUnknownOmission": bool(condition == "ASSISTED" and ca_unknowns and not unknowns),
            "assistedFakeGreen": bool(condition == "ASSISTED" and ca_decision in {"BLOCKED", "UNKNOWN"} and response["decision"] == "READY"),
            "codeAtlasPreparedDecision": ca_decision,
            "elapsedSeconds": elapsed if elapsed_source != "NOT_MEASURED" else "NOT_MEASURED",
            "elapsedSource": elapsed_source,
            "historyAuthorizes": False,
        })

    summaries: dict[str, Any] = {}
    for condition in CONDITIONS:
        rows = [row for row in scored if row["condition"] == condition]
        elapsed_values = [row["elapsedSeconds"] for row in rows]
        summaries[condition] = {
            "taskCount": len(rows),
            "authorizationWideningRatePct": round(100 * sum(1 for row in rows if row["authorizationWidened"]) / max(1, len(rows)), 2),
            "targetIncludedEditableRatePct": round(100 * sum(1 for row in rows if row["targetIncludedEditable"]) / max(1, len(rows)), 2),
            "meanHistoricalCompanionInspectionRecallPct": _avg_numeric(row["historicalCompanionInspection"]["recallPct"] for row in rows),
            "meanHistoricalChangedTestRecallPct": _avg_numeric(row["historicalChangedTestSelection"]["recallPct"] for row in rows),
            "meanValidEvidenceReferenceRatePct": _avg_numeric(row["validEvidenceReferenceRatePct"] for row in rows),
            "meanElapsedSeconds": _avg_numeric(elapsed_values),
            "medianElapsedSeconds": _median_numeric(elapsed_values),
            "elapsedMeasuredCount": sum(1 for value in elapsed_values if isinstance(value, (int, float))),
            "assistedUnknownOmissionCount": sum(1 for row in rows if row["assistedUnknownOmission"]),
            "assistedFakeGreenCount": sum(1 for row in rows if row["assistedFakeGreen"]),
        }

    preferences = {"ASSISTED": 0, "BASELINE": 0, "TIE": 0}
    materially_better = {"ASSISTED": 0, "BASELINE": 0, "TIE": 0, "UNCERTAIN": 0}
    pair_results: list[dict[str, Any]] = []
    for case_id in sorted(truths):
        pair = pairs[case_id]
        truth = truths[case_id]
        packet_ids = set((truth.get("packetIds") or {}).values())
        preferred = str(pair.get("preferredPacketId") or "")
        if preferred != "TIE" and preferred not in packet_ids:
            raise RuntimeError(f"INVALID_PREFERRED_PACKET:{case_id}")
        material = str(pair.get("materialDifference") or "")
        if material not in MATERIAL_VALUES:
            raise RuntimeError(f"INVALID_MATERIAL_DIFFERENCE:{case_id}")
        reasons = [str(x) for x in pair.get("reasonCodes") or []]
        invalid_reasons = sorted(set(reasons) - REASON_CODES)
        if invalid_reasons:
            raise RuntimeError(f"INVALID_REASON_CODES:{case_id}:{invalid_reasons}")
        if preferred == "TIE":
            preferred_condition = "TIE"
        else:
            preferred_condition = str((study_map["variants"][preferred]).get("condition"))
        preferences[preferred_condition] += 1
        if material == "YES":
            materially_better[preferred_condition] += 1
        elif material == "UNCERTAIN":
            materially_better["UNCERTAIN"] += 1
        pair_results.append({
            "caseId": case_id,
            "repository": truth["repository"],
            "preferredPacketId": preferred,
            "preferredCondition": preferred_condition,
            "materialDifference": material,
            "reasonCodes": reasons,
        })

    report = {
        "schemaVersion": SCHEMA_SCORE,
        "studyId": validation["studyId"],
        "classification": "VERIFY / HUMAN USEFULNESS EVIDENCE",
        "humanUsefulness": "SINGLE_EXTERNAL_HUMAN_PAIRED_STUDY_MEASURED_NO_GENERALIZATION",
        "reviewer": reviewer,
        "rawResponsesSha256": raw_digest,
        "rawResponsesPreserved": True,
        "taskPairCount": len(truths),
        "packetCount": len(packets),
        "scores": scored,
        "conditionSummaries": summaries,
        "pairPreferences": preferences,
        "materialPreferenceCounts": materially_better,
        "pairResults": pair_results,
        "claimBoundaries": {
            "singleReviewerGeneralizationAllowed": False,
            "causalClaimAllowed": False,
            "productionCertified": False,
            "paidPilotReadyPromoted": False,
            "enterpriseReadyPromoted": False,
            "independentEvaluatorReplicationProven": False,
            "externalReviewerIdentityIndependentlyVerified": False,
            "orderEffectEliminated": False,
            "selfAttestationIsIndependentVerification": False,
        },
        "interpretationRule": "DESCRIPTIVE_PAIRED_SINGLE_HUMAN_EVIDENCE_ONLY_NO_AUTOMATIC_MATURITY_PROMOTION",
    }
    report["reportDigest"] = _sha_json(report)
    _dump(out / "HUMAN_USEFULNESS_SCORE.json", report)
    summary = [
        "# Code Atlas Human Usefulness V1 — Scored Evidence",
        "",
        f"- Study: `{report['studyId']}`",
        f"- Human usefulness: `{report['humanUsefulness']}`",
        f"- Reviewer: `{reviewer['reviewerId']}` (self-attested external human; identity not independently verified)",
        f"- Paired tasks: `{len(truths)}`",
        f"- Assisted preferred: `{preferences['ASSISTED']}`",
        f"- Baseline preferred: `{preferences['BASELINE']}`",
        f"- Ties: `{preferences['TIE']}`",
        "",
        "This is bounded single-reviewer descriptive evidence. It does not prove causal uplift, general human usefulness, paid-pilot readiness, production readiness, enterprise readiness, or independent evaluator replication.",
    ]
    (out / "HUMAN_USEFULNESS_SCORE.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"HUMAN_USEFULNESS_SCORED={report['studyId']}")
    return report


def _synthetic_prepared(root: Path, seed: str = "selftest-seed") -> dict[str, Any]:
    reviewer = root / "reviewer_bundle"
    sealed = root / "sealed_scoring_bundle"
    packets_root = reviewer / "packets"
    truth_root = sealed / "truth"
    packets_root.mkdir(parents=True, exist_ok=True)
    truth_root.mkdir(parents=True, exist_ok=True)
    study_id = "HUS-SELFTEST"
    cases: list[dict[str, Any]] = []
    for idx in range(2):
        case_id = _opaque("C", seed, f"U{idx+1}")
        variants = {condition: _opaque("P", seed, f"U{idx+1}", condition) for condition in CONDITIONS}
        digests: dict[str, str] = {}
        target = f"src/target{idx}.py"
        for condition, packet_id in variants.items():
            packet = {
                "schemaVersion": SCHEMA_PACKET,
                "studyId": study_id,
                "caseId": case_id,
                "packetId": packet_id,
                "repository": f"example/repo{idx}",
                "parentCommit": f"parent{idx}",
                "parentTree": f"tree{idx}",
                "task": f"Synthetic task {idx}",
                "evaluatorProvidedTarget": target,
                "targetSelectionRule": "SELFTEST",
                "targetDiscoveryMeasured": False,
                "editableAuthorization": [target],
                "repoNativeEvidence": {"evidenceIds": ["repo:target"], "testCandidatePaths": [f"tests/test_target{idx}.py"]},
                "codeAtlasAssistance": ({"evidenceIds": ["ca:change-model"], "preparedDecision": "UNKNOWN", "unknowns": ["synthetic unknown"]} if condition == "ASSISTED" else None),
                "responseSchema": _response_schema(),
                "availableEvidenceIds": (["ca:change-model", "repo:target"] if condition == "ASSISTED" else ["repo:target"]),
                "groundTruthIncluded": False,
                "futureDiffIncluded": False,
                "historyAuthorizes": False,
                "humanUsefulness": "NOT_MEASURED",
                "claimCeiling": "STUDY_PACKET_ONLY",
            }
            packet["packetDigest"] = _packet_digest(packet)
            digests[condition] = packet["packetDigest"]
            _dump(packets_root / f"{packet_id}.json", packet)
        truth = {
            "schemaVersion": "caext_human_usefulness_ground_truth.v1",
            "studyId": study_id,
            "caseId": case_id,
            "taskId": f"U{idx+1}",
            "repository": f"example/repo{idx}",
            "historicalCommit": f"future{idx}",
            "parentCommit": f"parent{idx}",
            "target": target,
            "targetSelectionRule": "SELFTEST",
            "actualChangedPaths": [target, f"tests/test_target{idx}.py"],
            "actualCompanionPaths": [f"tests/test_target{idx}.py"],
            "actualChangedTestPaths": [f"tests/test_target{idx}.py"],
            "packetIds": variants,
            "packetDigests": digests,
            "historyAuthorizes": False,
        }
        truth["groundTruthDigest"] = _sha_json(truth)
        _dump(truth_root / f"{case_id}.json", truth)
        cases.append({
            "caseId": case_id,
            "repository": truth["repository"],
            "variants": variants,
            "packetDigests": digests,
            "parentCommit": truth["parentCommit"],
            "parentTree": f"tree{idx}",
            "target": target,
            "historicalCommit": truth["historicalCommit"],
            "groundTruthDigest": truth["groundTruthDigest"],
        })
    return _write_study_manifests(reviewer_root=reviewer, sealed_root=sealed, seed=seed, study_id=study_id, cases=cases)


def selftest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "prepared"
        _synthetic_prepared(root)
        first = validate_prepared(root)
        if first["packetCount"] != 4 or first["caseCount"] != 2:
            raise RuntimeError("SELFTEST_PREPARED_COUNTS")
        manifest = _load(root / "reviewer_bundle" / "MANIFEST.json")
        order_a = manifest["presentationOrder"]
        second_root = Path(tmp) / "prepared2"
        _synthetic_prepared(second_root)
        order_b = _load(second_root / "reviewer_bundle" / "MANIFEST.json")["presentationOrder"]
        if order_a != order_b:
            raise RuntimeError("SELFTEST_ORDER_NONDETERMINISTIC")
        packets = _load_packets(root / "reviewer_bundle")
        for packet in packets.values():
            _assert_no_ground_truth_leak(packet, where="selftest")
        response = _load(root / "reviewer_bundle" / "RESPONSE_TEMPLATE.json")
        response["reviewer"] = {
            "reviewerId": "reviewer-01",
            "reviewerType": "EXTERNAL_HUMAN",
            "independenceAttested": True,
            "role": "TECHNICAL_REVIEWER",
        }
        sealed_map = _load(root / "sealed_scoring_bundle" / "STUDY_MAP.json")
        truths = _load_truths(root / "sealed_scoring_bundle")
        for row in response["responses"]:
            packet_id = row["packetId"]
            variant = sealed_map["variants"][packet_id]
            truth = truths[variant["caseId"]]
            row["decision"] = "UNKNOWN"
            row["editableScope"] = [truth["target"]]
            row["inspectValidateScope"] = list(truth["actualCompanionPaths"])
            row["testPathsToValidate"] = list(truth["actualChangedTestPaths"])
            row["unknowns"] = ["synthetic unknown"]
            packet = packets[packet_id]
            row["evidenceReferences"] = [packet["availableEvidenceIds"][0]]
            row["elapsedSource"] = "OBSERVED"
            row["elapsedSeconds"] = 10.0 if variant["condition"] == "ASSISTED" else 15.0
        for pair in response["pairComparisons"]:
            truth = truths[pair["caseId"]]
            pair["preferredPacketId"] = truth["packetIds"]["ASSISTED"]
            pair["materialDifference"] = "YES"
            pair["reasonCodes"] = ["FASTER_REVIEW"]
        response_path = Path(tmp) / "responses.json"
        _dump(response_path, response)
        report = score(prepared_root=root, responses_path=response_path, out=Path(tmp) / "scored")
        if report["pairPreferences"]["ASSISTED"] != 2:
            raise RuntimeError("SELFTEST_PAIR_PREFERENCE")
        if report["conditionSummaries"]["ASSISTED"]["meanElapsedSeconds"] != 10.0:
            raise RuntimeError("SELFTEST_TIME_SUMMARY")

        tampered = next(iter((root / "reviewer_bundle" / "packets").glob("P*.json")))
        original = tampered.read_text(encoding="utf-8")
        value = json.loads(original)
        value["task"] = "tampered"
        _dump(tampered, value)
        try:
            validate_prepared(root)
        except RuntimeError as exc:
            if "PACKET_DIGEST_MISMATCH" not in str(exc):
                raise
        else:
            raise RuntimeError("SELFTEST_TAMPER_NOT_REJECTED")
        tampered.write_text(original, encoding="utf-8")
        validate_prepared(root)

        response_bad = copy.deepcopy(response)
        response_bad["reviewer"]["reviewerId"] = "person@example.com"
        bad_path = Path(tmp) / "bad-responses.json"
        _dump(bad_path, response_bad)
        try:
            score(prepared_root=root, responses_path=bad_path, out=Path(tmp) / "bad-score")
        except RuntimeError as exc:
            if "PSEUDONYMOUS" not in str(exc):
                raise
        else:
            raise RuntimeError("SELFTEST_PII_REVIEWER_ID_NOT_REJECTED")
    print("PASS_CAEXT_HUMAN_USEFULNESS_V1_SELFTEST")


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Atlas bounded paired external-human usefulness study kit")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("selftest")

    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--output", required=True)
    p_prepare.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    p_prepare.add_argument("--seed", default=DEFAULT_SEED)

    p_score = sub.add_parser("score")
    p_score.add_argument("--prepared-root", required=True)
    p_score.add_argument("--responses", required=True)
    p_score.add_argument("--output", required=True)

    args = parser.parse_args()
    if args.command == "selftest":
        selftest()
        return 0
    if args.command == "prepare":
        prepare(Path(args.output).resolve(), repo_root=Path(args.repo_root).resolve(), seed=str(args.seed))
        return 0
    if args.command == "score":
        score(
            prepared_root=Path(args.prepared_root).resolve(),
            responses_path=Path(args.responses).resolve(),
            out=Path(args.output).resolve(),
        )
        return 0
    raise RuntimeError(f"UNKNOWN_COMMAND:{args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
