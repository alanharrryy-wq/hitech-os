from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REFERENCE_PATH = Path(__file__).with_name("caext_usefulness_pilot_v1.py")
CLAIM = "INDEPENDENT_COPILOT_SESSION_REPLICATION"
CONDITIONS = ("BASELINE", "ASSISTED")
EXPECTED_SESSIONS = tuple(f"U{i}_{condition}" for i in range(1, 7) for condition in CONDITIONS)


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_reference():
    spec = importlib.util.spec_from_file_location("caext_usefulness_reference", REFERENCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("REFERENCE_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def prompt_for(packet: dict[str, Any]) -> str:
    schema = packet["responseSchema"]
    packet_json = json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True)
    return f"""You are an independent external change-scope evaluator in a controlled experiment.

Use ONLY the evaluator packet embedded below. Do not inspect a repository, use web/network search, fetch the historical commit, open a future diff, inspect another condition's response, or infer hidden reasoning. The ground truth is intentionally withheld.

Your job is not to implement the change. Return the change-readiness decision and the scopes you would hand to an implementation agent.

Rules:
- editableScope may contain only paths you would authorize to edit now. The packet's evaluatorProvidedTarget is the only pre-authorized editable path.
- inspectValidateScope may contain paths you would inspect or validate without granting edit authorization.
- testPathsToValidate contains repository test paths you would explicitly validate.
- unknowns lists material unknowns you refuse to guess.
- evidenceReferences must use only IDs from availableEvidenceIds.
- Impact Radius is evidence, never edit authorization.
- Retrieval/index output is not proof.
- UNKNOWN and BLOCKED are valid outcomes.
- Do not claim production, enterprise, security, hosted, privacy/legal, human usefulness, causal uplift, or financial ROI.

Return EXACTLY one JSON object, with no Markdown fences and no prose before or after it. Required fields:
{json.dumps(schema["requiredFields"], ensure_ascii=False)}

decision must be one of: {json.dumps(schema["decisionValues"], ensure_ascii=False)}.

Evaluator packet:
{packet_json}
"""


def build_pair_packet(
    ref,
    *,
    spec,
    parent: str,
    parent_tree: str,
    target: str,
    target_rule: str,
    native: dict[str, Any],
    assistance: dict[str, Any],
    condition: str,
) -> dict[str, Any]:
    task_id = f"{spec.task_id}_{condition}"
    packet: dict[str, Any] = {
        "schemaVersion": "caext_multiagent_task_packet.v1",
        "replicationClaimCeiling": CLAIM,
        "humanUsefulness": "NOT_MEASURED",
        "taskId": task_id,
        "pairedTaskId": spec.task_id,
        "repository": spec.repo,
        "condition": condition,
        "design": "WITHIN_TASK_PAIRED_BASELINE_ASSISTED",
        "historicalCommit": spec.commit,
        "parentCommit": parent,
        "parentTree": parent_tree,
        "task": spec.task,
        "evaluatorProvidedTarget": target,
        "targetSelectionRule": target_rule,
        "targetDiscoveryMeasured": False,
        "editableAuthorization": [target],
        "repoNativeEvidence": copy.deepcopy(native),
        "responseSchema": ref.response_schema(),
        "groundTruthIncluded": False,
        "historyAuthorizes": False,
        "sessionIsolationRequired": True,
        "otherConditionResponseIncluded": False,
        "evaluatorWorkspaceContainsRepositoryCheckout": False,
        "modelIdentity": "NOT_MEASURED",
    }
    ids = set(native.get("evidenceIds") or [])
    if condition == "ASSISTED":
        packet["codeAtlasAssistance"] = copy.deepcopy(assistance)
        ids.update(assistance.get("evidenceIds") or [])
    else:
        packet["codeAtlasAssistance"] = None
    packet["availableEvidenceIds"] = sorted(str(x) for x in ids)
    packet["packetDigestRule"] = ref.PACKET_DIGEST_RULE
    packet["packetDigest"] = ref.packet_digest(packet)
    return packet


def prepare(out: Path) -> dict[str, Any]:
    ref = load_reference()
    if out.exists():
        shutil.rmtree(out)
    packets_root = out / "task_packets"
    prompts_root = out / "prompts"
    truth_root = out / "ground_truth"
    work_root = out / "_work"
    for root in (packets_root, prompts_root, truth_root, work_root):
        root.mkdir(parents=True, exist_ok=True)

    session_rows: list[dict[str, Any]] = []
    truth_rows: list[dict[str, Any]] = []
    try:
        for spec in ref.TASKS:
            repo = ref.clone_commit(spec, work_root)
            parent = ref.parent_of(repo, spec.commit)
            actual_text = ref.git_text(repo, "diff", "--name-only", "--no-renames", parent, spec.commit) or ""
            actual = sorted({line.strip() for line in actual_text.splitlines() if line.strip()})
            target, target_rule = ref.select_target(repo, parent, actual)
            ref.git(repo, "checkout", "--detach", parent)
            if ref.git_text(repo, "status", "--porcelain=v1", "--untracked-files=all"):
                raise RuntimeError(f"DIRTY_PARENT:{spec.repo}")
            parent_tree = ref.git_text(repo, "rev-parse", "HEAD^{tree}") or ""
            all_paths = ref.tracked_paths(repo, parent)
            native = ref.repo_native_packet(repo, parent, target, all_paths)
            assistance = ref.assisted_evidence(repo, work_root, spec, target)
            packet_digests: dict[str, str] = {}

            for condition in CONDITIONS:
                packet = build_pair_packet(
                    ref,
                    spec=spec,
                    parent=parent,
                    parent_tree=parent_tree,
                    target=target,
                    target_rule=target_rule,
                    native=native,
                    assistance=assistance,
                    condition=condition,
                )
                session_id = packet["taskId"]
                packet_digests[condition] = packet["packetDigest"]
                dump(packets_root / f"{session_id}.json", packet)
                (prompts_root / f"{session_id}.txt").write_text(prompt_for(packet), encoding="utf-8")
                session_rows.append(
                    {
                        "sessionId": session_id,
                        "pairedTaskId": spec.task_id,
                        "condition": condition,
                        "repository": spec.repo,
                        "parentCommit": parent,
                        "packetDigest": packet["packetDigest"],
                    }
                )

            truth = {
                "schemaVersion": "caext_multiagent_ground_truth.v1",
                "pairedTaskId": spec.task_id,
                "repository": spec.repo,
                "historicalCommit": spec.commit,
                "parentCommit": parent,
                "target": target,
                "targetSelectionRule": target_rule,
                "actualChangedPaths": actual,
                "actualCompanionPaths": sorted(p for p in actual if p != target),
                "actualChangedTestPaths": sorted(p for p in actual if ref.is_test_path(p)),
                "packetDigests": packet_digests,
                "historyAuthorizes": False,
            }
            truth["groundTruthDigest"] = sha_json(truth)
            dump(truth_root / f"{spec.task_id}.json", truth)
            truth_rows.append(
                {
                    "pairedTaskId": spec.task_id,
                    "groundTruthDigest": truth["groundTruthDigest"],
                }
            )
    finally:
        shutil.rmtree(work_root, ignore_errors=True)

    manifest = {
        "schemaVersion": "caext_multiagent_packet_manifest.v1",
        "classification": "VERIFY / EXTERNAL EVIDENCE",
        "design": "WITHIN_TASK_PAIRED_BASELINE_ASSISTED",
        "claimCeiling": CLAIM,
        "humanUsefulness": "NOT_MEASURED",
        "independentEvaluatorSystem": "GitHub Copilot CLI via isolated GitHub Actions jobs",
        "modelIdentity": "NOT_MEASURED",
        "taskCount": 6,
        "plannedSessionCount": len(session_rows),
        "sessions": session_rows,
        "groundTruthSeparated": True,
        "otherConditionResponsesHidden": True,
        "evaluatorJobsHaveRepositoryCheckout": False,
        "targetDiscoveryMeasured": False,
        "causalUpliftClaimAllowed": False,
        "multiModelClaimAllowed": False,
        "financialEstimateAllowed": False,
        "historyAuthorizes": False,
    }
    manifest["manifestDigest"] = sha_json(manifest)
    dump(packets_root / "MANIFEST.json", manifest)
    dump(
        truth_root / "GROUND_TRUTH_MANIFEST.json",
        {
            "schemaVersion": "caext_multiagent_ground_truth_manifest.v1",
            "packetManifestDigest": manifest["manifestDigest"],
            "tasks": truth_rows,
            "doNotExposeBeforeAllPairedResponsesPersisted": True,
        },
    )
    return manifest


def extract_first_json(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise RuntimeError("NO_JSON_OBJECT_IN_AGENT_OUTPUT")


def validate_response(packet: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    required = packet["responseSchema"]["requiredFields"]
    missing = [field for field in required if field not in value]
    if missing:
        raise RuntimeError("MISSING_RESPONSE_FIELDS:" + ",".join(missing))
    if value.get("taskId") != packet.get("taskId"):
        raise RuntimeError("RESPONSE_TASK_ID_MISMATCH")
    if value.get("packetDigest") != packet.get("packetDigest"):
        raise RuntimeError("RESPONSE_PACKET_DIGEST_MISMATCH")
    if value.get("decision") not in packet["responseSchema"]["decisionValues"]:
        raise RuntimeError("INVALID_RESPONSE_DECISION")
    for field in ("editableScope", "inspectValidateScope", "testPathsToValidate", "unknowns", "evidenceReferences"):
        if not isinstance(value.get(field), list) or not all(isinstance(x, str) for x in value[field]):
            raise RuntimeError(f"INVALID_RESPONSE_LIST:{field}")
    return {field: value[field] for field in required}


def parse_response(packet_path: Path, raw_path: Path, meta_path: Path, out: Path) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    raw = raw_path.read_text(encoding="utf-8", errors="replace")
    value = validate_response(packet, extract_first_json(raw))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    record = {
        "schemaVersion": "caext_multiagent_session_response.v1",
        "sessionId": packet["taskId"],
        "pairedTaskId": packet["pairedTaskId"],
        "condition": packet["condition"],
        "packetDigest": packet["packetDigest"],
        "response": value,
        "evaluator": {
            "system": "GitHub Copilot CLI",
            "cliVersion": meta.get("cliVersion", "NOT_MEASURED"),
            "runnerOs": meta.get("runnerOs", "NOT_MEASURED"),
            "modelIdentity": meta.get("modelIdentity", "NOT_MEASURED"),
            "repositoryCheckoutPresent": False,
            "sessionIsolation": "SEPARATE_GITHUB_ACTIONS_JOB",
        },
    }
    record["recordDigest"] = sha_json(record)
    dump(out, record)
    return record


def collect(responses_root: Path, out: Path) -> dict[str, Any]:
    records: dict[str, dict[str, Any]] = {}
    for path in sorted(responses_root.rglob("response.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        session_id = str(row.get("sessionId") or "")
        if session_id in records:
            raise RuntimeError(f"DUPLICATE_SESSION_RESPONSE:{session_id}")
        records[session_id] = row
    expected = set(EXPECTED_SESSIONS)
    if set(records) != expected:
        raise RuntimeError(
            "SESSION_RESPONSE_SET_MISMATCH:"
            + json.dumps({"expected": sorted(expected), "actual": sorted(records)}, sort_keys=True)
        )
    merged = {
        "schemaVersion": "caext_multiagent_replication_responses.v1",
        "evaluator": "GitHub Copilot CLI / separate GitHub Actions jobs",
        "humanUsefulness": "NOT_MEASURED",
        "modelIdentity": "NOT_MEASURED",
        "sessionCount": len(records),
        "responses": [records[key] for key in sorted(records)],
    }
    merged["responsesDigest"] = sha_json(merged)
    dump(out, merged)
    return merged


def numeric(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def score(responses_path: Path, prepared_root: Path, out: Path) -> dict[str, Any]:
    ref = load_reference()
    raw = json.loads(responses_path.read_text(encoding="utf-8"))
    if raw.get("schemaVersion") != "caext_multiagent_replication_responses.v1":
        raise RuntimeError("UNSUPPORTED_MULTIAGENT_RESPONSE_SCHEMA")
    records = {row["sessionId"]: row for row in raw.get("responses") or []}
    if set(records) != set(EXPECTED_SESSIONS):
        raise RuntimeError("SCORE_SESSION_SET_MISMATCH")

    packets = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in (prepared_root / "task_packets").glob("U*_*.json")
    }
    truths = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in (prepared_root / "ground_truth").glob("U[1-6].json")
    }

    scored: list[dict[str, Any]] = []
    for session_id in sorted(EXPECTED_SESSIONS):
        packet = packets[session_id]
        record = records[session_id]
        response = record["response"]
        if record.get("packetDigest") != packet.get("packetDigest"):
            raise RuntimeError(f"RECORD_PACKET_DIGEST_MISMATCH:{session_id}")
        pair = packet["pairedTaskId"]
        truth = truths[pair]
        target = str(truth["target"])
        editable = [str(x) for x in response.get("editableScope") or []]
        inspect_scope = [str(x) for x in response.get("inspectValidateScope") or []]
        tests = [str(x) for x in response.get("testPathsToValidate") or []]
        refs = [str(x) for x in response.get("evidenceReferences") or []]
        unknowns = [str(x) for x in response.get("unknowns") or []]
        violations = sorted(set(editable) - {target})
        companion_score = ref.set_metric(inspect_scope, truth.get("actualCompanionPaths") or [])
        test_score = ref.set_metric(tests, truth.get("actualChangedTestPaths") or [])
        valid_ids = set(packet.get("availableEvidenceIds") or [])
        valid_refs = sorted(set(refs) & valid_ids)
        invalid_refs = sorted(set(refs) - valid_ids)
        valid_rate = round(100 * len(valid_refs) / len(set(refs)), 2) if refs else 0.0
        assistance = packet.get("codeAtlasAssistance") or {}
        ca_unknowns = [str(x) for x in assistance.get("unknowns") or []]
        ca_decision = assistance.get("preparedDecision") if packet["condition"] == "ASSISTED" else "NOT_APPLICABLE"
        fake_green = bool(
            packet["condition"] == "ASSISTED"
            and ca_decision in {"BLOCKED", "UNKNOWN"}
            and response.get("decision") == "READY"
        )
        unknown_omission = bool(packet["condition"] == "ASSISTED" and ca_unknowns and not unknowns)
        scored.append(
            {
                "sessionId": session_id,
                "pairedTaskId": pair,
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
                "validEvidenceReferenceRatePct": valid_rate,
                "invalidEvidenceReferences": invalid_refs,
                "unknownCount": len(unknowns),
                "assistedUnknownOmission": unknown_omission,
                "assistedFakeGreen": fake_green,
                "codeAtlasPreparedDecision": ca_decision,
                "sessionIsolation": record["evaluator"].get("sessionIsolation"),
                "modelIdentity": record["evaluator"].get("modelIdentity", "NOT_MEASURED"),
                "historyAuthorizes": False,
            }
        )

    def avg(rows: list[dict[str, Any]], fn) -> float | str:
        vals = [fn(row) for row in rows]
        nums = [float(v) for v in vals if isinstance(v, (int, float))]
        return round(sum(nums) / len(nums), 2) if nums else "NOT_APPLICABLE"

    summaries: dict[str, Any] = {}
    for condition in CONDITIONS:
        rows = [row for row in scored if row["condition"] == condition]
        summaries[condition] = {
            "taskCount": len(rows),
            "authorizationWideningRatePct": round(
                100 * sum(1 for row in rows if row["authorizationWidened"]) / max(1, len(rows)), 2
            ),
            "targetIncludedEditableRatePct": round(
                100 * sum(1 for row in rows if row["targetIncludedEditable"]) / max(1, len(rows)), 2
            ),
            "meanHistoricalCompanionInspectionRecallPct": avg(
                rows, lambda row: row["historicalCompanionInspection"]["recallPct"]
            ),
            "meanHistoricalChangedTestRecallPct": avg(
                rows, lambda row: row["historicalChangedTestSelection"]["recallPct"]
            ),
            "meanValidEvidenceReferenceRatePct": avg(rows, lambda row: row["validEvidenceReferenceRatePct"]),
            "assistedUnknownOmissionCount": sum(1 for row in rows if row["assistedUnknownOmission"]),
            "assistedFakeGreenCount": sum(1 for row in rows if row["assistedFakeGreen"]),
        }

    pairs: list[dict[str, Any]] = []
    for pair in sorted(truths):
        baseline = next(row for row in scored if row["pairedTaskId"] == pair and row["condition"] == "BASELINE")
        assisted = next(row for row in scored if row["pairedTaskId"] == pair and row["condition"] == "ASSISTED")
        def delta(metric_path: tuple[str, str]) -> float | str:
            b = numeric(baseline[metric_path[0]][metric_path[1]])
            a = numeric(assisted[metric_path[0]][metric_path[1]])
            return round(a - b, 2) if a is not None and b is not None else "NOT_APPLICABLE"
        pairs.append(
            {
                "pairedTaskId": pair,
                "repository": baseline["repository"],
                "baselineSessionId": baseline["sessionId"],
                "assistedSessionId": assisted["sessionId"],
                "changedTestRecallDeltaPctPoints": delta(("historicalChangedTestSelection", "recallPct")),
                "companionRecallDeltaPctPoints": delta(("historicalCompanionInspection", "recallPct")),
                "authorizationWideningDelta": int(assisted["authorizationWidened"])
                - int(baseline["authorizationWidened"]),
                "targetEditableDelta": int(assisted["targetIncludedEditable"])
                - int(baseline["targetIncludedEditable"]),
            }
        )

    all_edit_entries = 0
    all_violations = 0
    evidence_rates = []
    for row in scored:
        response = records[row["sessionId"]]["response"]
        all_edit_entries += len(response.get("editableScope") or [])
        all_violations += row["editableScopeViolationCount"]
        evidence_rates.append(row["validEvidenceReferenceRatePct"])

    observed_roi = [
        ref.build_roi_event(
            metric="outOfScopeChangeRate",
            value=round(all_violations / max(1, all_edit_entries), 6),
            unit="ratio",
            repository_identity="caext-multiagent-v1-six-task-paired",
            source="caext.independent_copilot_session_replication.v1",
            context={"taskCount": 6, "sessionCount": 12, "claimCeiling": CLAIM},
        ),
        ref.build_roi_event(
            metric="evidenceCompletenessRate",
            value=round(sum(evidence_rates) / max(1, len(evidence_rates)) / 100, 6),
            unit="ratio",
            repository_identity="caext-multiagent-v1-six-task-paired",
            source="caext.independent_copilot_session_replication.v1",
            context={"taskCount": 6, "sessionCount": 12, "claimCeiling": CLAIM},
        ),
    ]

    state = {
        "schemaVersion": "caext_multiagent_replication_result.v1",
        "classification": "VERIFY / EXTERNAL EVIDENCE",
        "agentUsefulness": "INDEPENDENT_COPILOT_SESSION_REPLICATION_MEASURED_NO_CAUSAL_CLAIM",
        "humanUsefulness": "NOT_MEASURED",
        "design": "WITHIN_TASK_PAIRED_BASELINE_ASSISTED",
        "independentEvaluatorSystem": "GitHub Copilot CLI via isolated GitHub Actions jobs",
        "sessionCount": 12,
        "taskCount": 6,
        "conditionSummary": summaries,
        "pairedTaskResults": pairs,
        "sessions": scored,
        "observedRawRoiEvents": observed_roi,
        "modelIdentity": "NOT_MEASURED",
        "multiModelClaimAllowed": False,
        "causalUpliftClaimAllowed": False,
        "historyAuthorizes": False,
        "certifiable": False,
        "productionCertified": False,
        "limitations": [
            "Copilot sessions are independent runner/session executions but are not proven to use distinct underlying models.",
            "The six historical task identities were used in the prior single-agent pilot, so prior-task contamination risk cannot be reduced to zero.",
            "Evaluator jobs receive no repository checkout and are instructed to use only the packet, but model-side network/tool behavior is not independently audited.",
            "No human evaluator participated.",
            "Historical diffs are bounded evaluation ground truth, not edit authorization.",
        ],
        "notMeasured": [
            "humanUsefulness",
            "humanSupervisionTime",
            "modelIdentity",
            "contextDiscoveryTime",
            "changeScopeIdentificationTime",
            "financialOutcome",
            "workerPeak",
        ],
    }
    state["resultDigest"] = sha_json(state)
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "USEFULNESS_MULTIAGENT_RESULT.json", state)
    dump(out / "SCORED_SESSIONS.json", scored)
    dump(out / "PAIRED_TASKS.json", pairs)
    return state


def blocked(reason: str, out: Path) -> dict[str, Any]:
    state = {
        "schemaVersion": "caext_multiagent_replication_result.v1",
        "classification": "VERIFY / EXTERNAL EVIDENCE",
        "status": "BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR",
        "reason": reason,
        "humanUsefulness": "NOT_MEASURED",
        "agentUsefulness": "NOT_MEASURED",
        "causalUpliftClaimAllowed": False,
        "multiModelClaimAllowed": False,
        "certifiable": False,
        "productionCertified": False,
        "historyAuthorizes": False,
        "financialEstimate": None,
    }
    state["resultDigest"] = sha_json(state)
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "USEFULNESS_MULTIAGENT_RESULT.json", state)
    return state


def selftest() -> None:
    ref = load_reference()
    sample = {
        "taskId": "U0_BASELINE",
        "pairedTaskId": "U0",
        "condition": "BASELINE",
        "responseSchema": {
            "requiredFields": [
                "taskId",
                "packetDigest",
                "decision",
                "editableScope",
                "inspectValidateScope",
                "testPathsToValidate",
                "unknowns",
                "evidenceReferences",
            ],
            "decisionValues": ["READY", "BLOCKED", "UNKNOWN"],
        },
        "generatedAt": "one",
    }
    digest_one = ref.packet_digest(sample)
    sample["generatedAt"] = "two"
    assert ref.packet_digest(sample) == digest_one
    sample["condition"] = "ASSISTED"
    assert ref.packet_digest(sample) != digest_one
    parsed = extract_first_json('noise\\n```json\\n{"taskId":"U0_BASELINE"}\\n```')
    assert parsed["taskId"] == "U0_BASELINE"
    assert len(EXPECTED_SESSIONS) == 12
    print("PASS_CAEXT_MULTIAGENT_REPLICATION_SELFTEST")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--out", required=True)
    p_parse = sub.add_parser("parse-response")
    p_parse.add_argument("--packet", required=True)
    p_parse.add_argument("--raw", required=True)
    p_parse.add_argument("--meta", required=True)
    p_parse.add_argument("--out", required=True)
    p_collect = sub.add_parser("collect")
    p_collect.add_argument("--responses-root", required=True)
    p_collect.add_argument("--out", required=True)
    p_score = sub.add_parser("score")
    p_score.add_argument("--responses", required=True)
    p_score.add_argument("--prepared-root", required=True)
    p_score.add_argument("--out", required=True)
    p_blocked = sub.add_parser("blocked")
    p_blocked.add_argument("--reason", required=True)
    p_blocked.add_argument("--out", required=True)
    args = parser.parse_args()

    if args.cmd == "selftest":
        selftest()
    elif args.cmd == "prepare":
        prepare(Path(args.out))
    elif args.cmd == "parse-response":
        parse_response(Path(args.packet), Path(args.raw), Path(args.meta), Path(args.out))
    elif args.cmd == "collect":
        collect(Path(args.responses_root), Path(args.out))
    elif args.cmd == "score":
        score(Path(args.responses), Path(args.prepared_root), Path(args.out))
    elif args.cmd == "blocked":
        blocked(args.reason, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
