#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ANCHORS = [
    "rfc",
    "slsa",
    "in-toto",
    "trust root",
    "strictness ladder",
    "verification required",
    "no silent pass",
    "provenance",
    "signing policy",
    "evidence outputs",
]
TEMPLATE_PHRASES = ["status: read-only", "do not modify legacy path", "deterministic output", "additive-only"]
UNIVERSE_SIG = {
    "u1_constitutional_change": ["constitution", "constitutional", "charter", "amendment", "rfc"],
    "u2_evidence_chain": ["evidence", "provenance", "attestation", "slsa", "in-toto", "signing", "sbom"],
    "u3_policy_plane": ["policy", "strictness ladder", "verification required", "no silent pass", "enforcement", "gate"],
    "u4_enterprise_agents": ["agent", "worker", "orchestrator", "handoff", "multi-agent", "multi agent"],
}
ALLOWLIST = ("docs", "documentation", "governance", "policy")
MAX_MOVES = 20
THRESHOLD = 0.95


@dataclasses.dataclass(frozen=True)
class Profile:
    rel: str
    text: str
    lines: int
    doc_id: str
    doc_type: str
    universe: str
    headings: frozenset[str]
    anchors: frozenset[str]
    templates: frozenset[str]
    universe_hits: frozenset[str]


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def atomic_write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = text if text.endswith("\n") else text + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    tmp_path = pathlib.Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        tmp_path.replace(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def frontmatter(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return out
    try:
        end = lines.index("---", 1)
    except ValueError:
        return out
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m:
            out[m.group(1).lower()] = m.group(2).strip()
    return out


def norm_name(path: str) -> str:
    stem = pathlib.Path(path).stem.lower()
    return re.sub(r"\s+", " ", re.sub(r"[_-]+", " ", stem)).strip()


def norm_heading(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", value.lower())).strip()


def headings(text: str) -> frozenset[str]:
    found = set()
    for line in text.splitlines():
        m = re.match(r"^#{1,2}\s+(.+)$", line)
        if m:
            token = norm_heading(m.group(1))
            if token:
                found.add(token)
    return frozenset(sorted(found))


def phrase_hits(text: str, phrases: list[str]) -> frozenset[str]:
    lower = text.lower()
    return frozenset(sorted(p for p in phrases if p in lower))


def universe_hits(text: str) -> frozenset[str]:
    lower = text.lower()
    found = [u for u, words in UNIVERSE_SIG.items() if any(w in lower for w in words)]
    return frozenset(sorted(found))


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def levenshtein(a: str, b: str) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1]


def filename_score(legacy_rel: str, canon_rel: str) -> float:
    la, ca = pathlib.Path(legacy_rel).stem, pathlib.Path(canon_rel).stem
    if la.lower() == ca.lower():
        return 1.0
    ln, cn = norm_name(legacy_rel), norm_name(canon_rel)
    if ln and ln == cn:
        return 0.85
    mx = max(len(ln), len(cn))
    if mx and levenshtein(ln, cn) / mx <= 0.15:
        return 0.70
    return 0.0


def profile(repo_root: pathlib.Path, rel: str) -> Profile:
    path = repo_root / rel
    text = read_text(path)
    fm = frontmatter(text)
    return Profile(
        rel=rel.replace("\\", "/"),
        text=text,
        lines=len(text.splitlines()),
        doc_id=fm.get("doc_id", ""),
        doc_type=fm.get("doc_type", ""),
        universe=fm.get("universe", ""),
        headings=headings(text),
        anchors=phrase_hits(text, ANCHORS),
        templates=phrase_hits(text, TEMPLATE_PHRASES),
        universe_hits=universe_hits(text),
    )


def is_gov_candidate(p: Profile) -> bool:
    name = pathlib.Path(p.rel).stem.lower()
    return any(k in name for k in ("governance", "constitution", "contract", "policy", "audit", "determinism", "security", "protocol")) or bool(p.anchors)


def code_refs(repo_root: pathlib.Path, legacy_rel: str) -> bool:
    needles = [legacy_rel, legacy_rel.replace("/", "\\"), pathlib.Path(legacy_rel).name]
    for root in ("src", "app", "lib", "core"):
        base = repo_root / root
        if not base.is_dir():
            continue
        for n in needles:
            rg = shutil.which("rg")
            if rg:
                cp = subprocess.run([rg, "-n", "--fixed-strings", "--glob", "!README.md", "--", n, str(base)], capture_output=True, text=True)
                if cp.returncode == 0 and cp.stdout.strip():
                    return True
            else:
                for file in base.rglob("*"):
                    if file.is_file() and file.name != "README.md" and n in read_text(file):
                        return True
    return False


def manifest_sorted(path: pathlib.Path) -> bool:
    if not path.is_file():
        return False
    paths = [m.group(1).strip().strip("\"'") for m in re.finditer(r"(?m)^\s*-\s+path:\s*(.+)\s*$", read_text(path))]
    return paths == sorted(paths, key=lambda p: p.lower())


def run(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--repo-root", default="")
    ns = ap.parse_args(argv)
    if ns.check == ns.write:
        ns.check = True
        ns.write = False

    repo_root = pathlib.Path(ns.repo_root).resolve() if ns.repo_root else pathlib.Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()).resolve()
    missing = [p for p in ("KERNEL_CONTEXT.md", "docs/factory/FACTORY_RUNTIME_EXPLAINED.md") if not (repo_root / p).is_file()]
    additive_only = bool(missing)

    legacy_files = sorted(
        str(p.relative_to(repo_root)).replace("\\", "/")
        for root in ALLOWLIST
        for p in ((repo_root / root).rglob("*.md") if (repo_root / root).is_dir() else [])
        if "docs/govos/" not in str(p.relative_to(repo_root)).replace("\\", "/")
    )
    canonical_profiles = [
        profile(repo_root, str(p.relative_to(repo_root)).replace("\\", "/"))
        for p in sorted((repo_root / "docs/govos").rglob("*.md")) if (repo_root / "docs/govos").is_dir()
        if "_reports" not in str(p.relative_to(repo_root)).replace("\\", "/")
    ]
    canonical_profiles = [p for p in canonical_profiles if p.doc_type != "template"]

    rows: list[dict[str, object]] = []
    for rel in legacy_files:
        lp = profile(repo_root, rel)
        if not is_gov_candidate(lp) or not canonical_profiles:
            continue
        best = None
        for cp in canonical_profiles:
            fs = filename_score(lp.rel, cp.rel)
            hs = jaccard(lp.headings, cp.headings)
            ans = jaccard(lp.anchors, cp.anchors)
            ts = jaccard(lp.templates, cp.templates)
            ds = 1.0 if lp.doc_id and cp.doc_id and lp.doc_id.lower() == cp.doc_id.lower() else 0.0
            conf = 0.35 * fs + 0.30 * hs + 0.20 * ans + 0.10 * ts + 0.05 * ds
            cand = (round(conf, 4), cp, fs, hs, ans, ts, ds)
            if best is None or cand[0] > best[0] or (cand[0] == best[0] and cp.rel < best[1].rel):
                best = cand
        assert best is not None
        conf, cp, fs, hs, ans, ts, ds = best
        mixed = len(lp.universe_hits) > 1
        conflict = bool(lp.doc_id and cp.doc_id and lp.doc_id.lower() != cp.doc_id.lower())
        eligible_pre = conf >= THRESHOLD and lp.lines <= 2000 and not mixed and not conflict
        ref_found = code_refs(repo_root, lp.rel) if eligible_pre else False
        rows.append(
            dict(
                legacy=lp.rel,
                canon=cp.rel,
                confidence=conf,
                filename=round(fs, 2),
                headings=round(hs, 2),
                anchors=round(ans, 2),
                templates=round(ts, 2),
                doc_id=round(ds, 2),
                mixed=mixed,
                eligible=eligible_pre and not ref_found,
                disposition="",
            )
        )

    rows.sort(key=lambda x: x["legacy"])  # deterministic
    eligible = [r for r in rows if r["eligible"]]
    planned = eligible[:MAX_MOVES]
    moved = 0
    for r in rows:
        if r["mixed"]:
            r["disposition"] = "CROSS_UNIVERSE_MIXED_PRESERVED"
        elif r["eligible"] and additive_only:
            r["disposition"] = "ADDITIVE_ONLY_NO_MOVE"
        elif r["eligible"] and ns.write and r in planned and not additive_only:
            r["disposition"] = "MOVED_AND_STUBBED"
            moved += 1
        elif r["eligible"]:
            r["disposition"] = "ELIGIBLE_PENDING_WRITE"
        else:
            r["disposition"] = "CANONICAL_CREATED_LEGACY_PRESERVED"

    blockers: list[str] = []
    required = [
        "docs/govos/README.md",
        "docs/govos/MASTER_INDEX.md",
        "docs/govos/MANIFEST.yaml",
        "docs/govos/dependency-map/GOVOS_DEPENDENCIES.dot",
        "docs/govos/schemas/STATUS_SCHEMA.json",
        "docs/govos/schemas/BLOCKERS_SCHEMA.json",
        "docs/govos/schemas/DEBT_SCHEMA.json",
        "docs/govos/u1_constitutional_change/U1_CONSTITUTIONAL_CHANGE.md",
        "docs/govos/u2_evidence_chain/U2_EVIDENCE_CHAIN.md",
        "docs/govos/u3_policy_plane/U3_POLICY_PLANE.md",
        "docs/govos/u4_enterprise_agents/U4_ENTERPRISE_AGENTS.md",
    ]
    blockers.extend(f"missing required canonical file: {p}" for p in required if not (repo_root / p).is_file())
    if not manifest_sorted(repo_root / "docs/govos/MANIFEST.yaml"):
        blockers.append("manifest missing or not sorted: docs/govos/MANIFEST.yaml")
    doc_ids: dict[str, list[str]] = {}
    for p in sorted((repo_root / "docs/govos").rglob("*.md")) if (repo_root / "docs/govos").is_dir() else []:
        rel = str(p.relative_to(repo_root)).replace("\\", "/")
        if rel.startswith("docs/govos/_reports/"):
            continue
        doc_id = frontmatter(read_text(p)).get("doc_id", "").strip()
        if not doc_id:
            blockers.append(f"missing doc_id front matter: {rel}")
            continue
        doc_ids.setdefault(doc_id, []).append(rel)
    blockers.extend(f"duplicate doc_id `{k}` in: {', '.join(sorted(v))}" for k, v in doc_ids.items() if len(v) > 1)

    if ns.write:
        table = ["| legacy_path | best_canonical | confidence | filename | headings | anchors | templates | doc_id | cross_universe | disposition |", "|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
        table.extend(
            f"| {r['legacy']} | {r['canon']} | {r['confidence']:.4f} | {r['filename']:.2f} | {r['headings']:.2f} | {r['anchors']:.2f} | {r['templates']:.2f} | {r['doc_id']:.2f} | {'yes' if r['mixed'] else 'no'} | {r['disposition']} |"
            for r in rows
        )
        atomic_write(repo_root / "docs/govos/_reports/LEGACY_MAP.md", "# LEGACY MAP\n\n- mode: write\n- additive_only: " + str(additive_only).lower() + ("\n- missing_mandatory_reads: " + ", ".join(missing) if missing else "") + "\n\n" + "\n".join(table))
        atomic_write(repo_root / "docs/govos/_reports/CONVERGENCE_LOG.md", "# CONVERGENCE LOG\n\n## Block 1 - Discovery + Convergence Model\n\n- mode: write\n- legacy_governance_docs_detected: " + str(len(rows)) + "\n- auto_move_eligible: " + str(len(eligible)) + "\n- overflow_deferred: " + str(max(0, len(eligible) - MAX_MOVES)) + "\n\n## Block 2 - Canon Creation + Safe Neutralization + Validation\n\n- moved_and_stubbed: " + str(moved) + "\n- preserved_legacy_docs: " + str(len(rows) - moved))
        result = "OK" if not blockers else "BLOCKED"
        atomic_write(repo_root / "docs/govos/_reports/FINAL_REPORT.md", "# FINAL REPORT\n\nRESULT: " + result + "\nREPO_ROOT: " + str(repo_root).replace("\\", "/") + "\nCANONICAL_DOCS_ROOT: docs/govos\n\n## Mandatory First Read\n\n- KERNEL_CONTEXT.md: " + ("present" if (repo_root / "KERNEL_CONTEXT.md").is_file() else "missing") + "\n- docs/factory/FACTORY_RUNTIME_EXPLAINED.md: " + ("present" if (repo_root / "docs/factory/FACTORY_RUNTIME_EXPLAINED.md").is_file() else "missing") + ("\n- additive_only_trigger: true\n- reason: missing mandatory first-read files -> " + ", ".join(missing) if missing else "\n- additive_only_trigger: false"))

    if blockers:
        for b in sorted(blockers):
            print(f"BLOCKER: {b}")
        print("RESULT: BLOCKED")
        return 2
    print("RESULT: OK")
    print(f"REPO_ROOT: {str(repo_root).replace('\\', '/')}")
    print("CANONICAL_DOCS_ROOT: docs/govos")
    return 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
