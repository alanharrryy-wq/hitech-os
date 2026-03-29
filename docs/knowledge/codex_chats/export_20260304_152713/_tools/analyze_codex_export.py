import json, re, hashlib
from pathlib import Path

PROMPT_MARKERS = [
    r"YOU ARE CODEX WORKER:",
    r"===\s*[A-Z_]+\s+PROMPT\s*===",
    r"PROMPTS_PACK",
    r"RUN_ID:",
    r"CODEX_ID:",
    r"BEGIN PROMPT",
    r"^#\s*SYSTEM",
]
PROMPT_RE = re.compile("|".join(PROMPT_MARKERS), re.IGNORECASE | re.MULTILINE)

SCENE_MARKERS = [
    r"Scene Engine",
    r"Pitch OS",
    r"scene_engine",
    r"pitch_os",
    r"renderer",
    r"kernel",
    r"timeline",
    r"shot",
    r"scene",
    r"composition",
    r"layout",
    r"orchestrator",
    r"factory",
    r"FACTORY_RUNTIME_EXPLAINED\.md",
    r"KERNEL_CONTEXT\.md",
]
SCENE_RE = re.compile("|".join(SCENE_MARKERS), re.IGNORECASE)

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def read_md_blocks(md_text: str):
    # Split by headings "## User/Assistant/System/Tool"
    parts = re.split(r"^##\s+", md_text, flags=re.MULTILINE)
    blocks = []
    for p in parts[1:]:
        # first line is role
        lines = p.splitlines()
        role = (lines[0] or "").strip().lower()
        content = "\n".join(lines[1:]).strip()
        if role and content:
            blocks.append((role, content))
    return blocks

def extract_prompt_candidates(blocks):
    hits = []
    for role, content in blocks:
        if role != "user":
            continue
        if PROMPT_RE.search(content):
            hits.append(content)
    return hits

def extract_scene_mentions(blocks):
    hits = []
    for role, content in blocks:
        if SCENE_RE.search(content):
            hits.append((role, content))
    return hits

def repo_grep(repo_root: Path, patterns):
    # Best-effort grep in repo without external deps
    hits = []
    exts = {".md",".txt",".py",".ps1",".js",".ts",".tsx",".json",".yaml",".yml"}
    for p in repo_root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in exts:
            continue
        try:
            data = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in patterns:
            if re.search(pat, data, flags=re.IGNORECASE):
                hits.append((str(p), pat))
                break
    return hits

def main():
    import sys
    if len(sys.argv) < 3:
        print("usage: analyze_codex_export.py <export_dir> <repo_root>")
        sys.exit(2)

    export_dir = Path(sys.argv[1]).resolve()
    repo_root = Path(sys.argv[2]).resolve()

    md_dir = export_dir / "md"
    out_dir = export_dir / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(md_dir.glob("*.md"))

    prompt_map = {}
    prompt_items = []
    scene_mentions = []

    for md in md_files:
        text = md.read_text(encoding="utf-8", errors="ignore")
        blocks = read_md_blocks(text)

        prompts = extract_prompt_candidates(blocks)
        for pr in prompts:
            h = sha1(pr.strip())
            if h not in prompt_map:
                prompt_map[h] = {
                    "hash": h,
                    "first_seen_in": md.name,
                    "length": len(pr),
                    "text": pr.strip(),
                }

        scenes = extract_scene_mentions(blocks)
        for role, content in scenes:
            scene_mentions.append({
                "file": md.name,
                "role": role,
                "snippet": content[:800].strip(),
            })

    prompt_items = list(prompt_map.values())
    prompt_items.sort(key=lambda x: (-x["length"], x["first_seen_in"]))

    # Repo scan to ground architecture in real files
    repo_hits = repo_grep(repo_root, [
        r"Scene Engine",
        r"Pitch OS",
        r"scene_engine",
        r"pitch_os",
        r"KERNEL_CONTEXT\.md",
        r"FACTORY_RUNTIME_EXPLAINED\.md",
        r"factory",
        r"orchestrator",
        r"renderer",
        r"timeline",
    ])

    # Write machine outputs
    (out_dir / "KEY_PROMPTS.json").write_text(json.dumps(prompt_items, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "SCENE_PITCH_MENTIONS.json").write_text(json.dumps(scene_mentions, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "REPO_HITS.json").write_text(json.dumps(repo_hits, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write human outputs
    mdp = []
    mdp.append("# Key Prompts (Deduped)")
    mdp.append("")
    mdp.append(f"Total unique prompts: {len(prompt_items)}")
    mdp.append("")
    for i, it in enumerate(prompt_items[:200], start=1):
        mdp.append(f"## Prompt {i}")
        mdp.append(f"- hash: `{it['hash']}`")
        mdp.append(f"- first_seen_in: `{it['first_seen_in']}`")
        mdp.append(f"- length: {it['length']}")
        mdp.append("")
        mdp.append("```")
        mdp.append(it["text"])
        mdp.append("```")
        mdp.append("")

    (out_dir / "KEY_PROMPTS.md").write_text("\n".join(mdp), encoding="utf-8")

    mda = []
    mda.append("# Scene Engine / Pitch OS — Architecture Extraction (Evidence-First)")
    mda.append("")
    mda.append("## Evidence from chats (snippets)")
    mda.append("")
    for i, it in enumerate(scene_mentions[:300], start=1):
        mda.append(f"### Mention {i}")
        mda.append(f"- file: `{it['file']}`")
        mda.append(f"- role: `{it['role']}`")
        mda.append("")
        mda.append("> " + it["snippet"].replace("\n", "\n> "))
        mda.append("")

    mda.append("## Evidence from repo (files containing keywords)")
    mda.append("")
    if repo_hits:
        for fp, pat in sorted(set(tuple(x) for x in repo_hits))[:500]:
            mda.append(f"- `{fp}`  (matched: `{pat}`)")
    else:
        mda.append("- (No hits found — either naming differs or files are elsewhere)")

    (out_dir / "SCENE_PITCH_ARCHITECTURE.md").write_text("\n".join(mda), encoding="utf-8")

    print(f"[done] analyzed md_files={len(md_files)} out={out_dir}")

if __name__ == "__main__":
    main()
