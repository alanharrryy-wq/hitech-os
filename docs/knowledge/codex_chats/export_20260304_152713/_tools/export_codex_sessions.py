import json, re, hashlib, datetime
from pathlib import Path

def safe_name(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"[\\/:*?\"<>|]+", "-", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-._")
    return s[:140] if s else "chat"

def _parts_to_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for p in content:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict):
                out.append(str(p.get("text") or p.get("value") or p.get("content") or p.get("data") or ""))
        return "\n".join([x for x in out if x]).strip()
    if isinstance(content, dict):
        return str(content.get("text") or content.get("value") or content.get("content") or "").strip()
    return ""

def extract_messages(obj):
    msgs = []

    if not isinstance(obj, dict):
        return msgs

    # Common shapes
    role = obj.get("role") or obj.get("author") or obj.get("speaker") or obj.get("type")
    content = obj.get("content")

    # Nested message
    if content is None and isinstance(obj.get("message"), dict):
        m = obj["message"]
        role = role or m.get("role") or m.get("author")
        content = m.get("content") or m.get("text") or m.get("message")

    # Other common keys
    if content is None:
        content = obj.get("text") or obj.get("output_text") or obj.get("input_text") or obj.get("prompt")

    content_text = _parts_to_text(content)

    # Normalize role
    role_map = {
        "human": "user",
        "assistant_message": "assistant",
        "user_message": "user",
        "system_message": "system",
    }
    role_norm = role_map.get(str(role).lower(), str(role).lower() if role else None)

    if role_norm in ("user", "assistant", "system") and content_text:
        msgs.append({"role": role_norm, "content": content_text})
        return msgs

    # Tool-ish payloads that contain useful text
    for k in ("tool_output","result","output","data","stdout","stderr"):
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            msgs.append({"role":"tool", "content": v.strip()})
            return msgs

    # Sometimes the record contains an array of events/messages
    for k in ("events","messages","items","steps","turns"):
        v = obj.get(k)
        if isinstance(v, list):
            for it in v:
                msgs.extend(extract_messages(it))

    return msgs

def parse_jsonl(path: Path):
    records = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return records

def pick_title(messages, fallback):
    for m in messages:
        if m["role"] == "user" and len(m["content"]) > 6:
            first = m["content"].splitlines()[0][:120]
            return safe_name(first)
    return safe_name(fallback)

def to_md(messages, header):
    out = []
    out.append(f"# {header}")
    out.append("")
    for m in messages:
        role = m["role"]
        out.append("## " + role.capitalize())
        out.append("")
        out.append(m["content"])
        out.append("")
    return "\n".join(out).rstrip() + "\n"

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def main():
    import sys
    if len(sys.argv) < 3:
        print("usage: export_codex_sessions.py <sessions_root> <out_dir>")
        sys.exit(2)

    sessions_root = Path(sys.argv[1]).expanduser().resolve()
    out_dir = Path(sys.argv[2]).resolve()

    md_dir = out_dir / "md"
    js_dir = out_dir / "json"
    md_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(sessions_root.rglob("rollout-*.jsonl"))

    index = []
    for i, src in enumerate(files, start=1):
        records = parse_jsonl(src)
        messages = []
        for r in records:
            messages.extend(extract_messages(r))

        base = src.name
        title = pick_title(messages, base)
        stem = safe_name(src.stem) + "__" + title
        md_path = md_dir / (stem + ".md")
        js_path = js_dir / (stem + ".summary.json")

        md_path.write_text(to_md(messages, base), encoding="utf-8")

        summary = {
            "source": str(src),
            "file": base,
            "message_count": len(messages),
            "roles": {
                "user": sum(1 for m in messages if m["role"]=="user"),
                "assistant": sum(1 for m in messages if m["role"]=="assistant"),
                "system": sum(1 for m in messages if m["role"]=="system"),
                "tool": sum(1 for m in messages if m["role"]=="tool"),
            },
            "title": title,
            "md": str(md_path.relative_to(out_dir)).replace("\\","/"),
        }
        js_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

        index.append({
            "file": base,
            "title": title,
            "message_count": summary["message_count"],
            "md": summary["md"],
            "summary": str(js_path.relative_to(out_dir)).replace("\\","/"),
        })

        if i % 25 == 0:
            print(f"[progress] {i}/{len(files)}")

    # Write INDEX.md + INDEX.json
    nowz = datetime.datetime.utcnow().isoformat() + "Z"
    idx_md = []
    idx_md.append("# Codex Rollouts Export Index")
    idx_md.append("")
    idx_md.append(f"Generated: {nowz}")
    idx_md.append(f"SessionsRoot: {sessions_root}")
    idx_md.append("")
    idx_md.append("| Chat | Messages | Markdown | Summary |")
    idx_md.append("|---|---:|---|---|")
    for it in sorted(index, key=lambda x: x["file"]):
        idx_md.append(f"| {it['title']} | {it['message_count']} | [{it['md']}]({it['md']}) | [{it['summary']}]({it['summary']}) |")

    (out_dir / "INDEX.md").write_text("\n".join(idx_md) + "\n", encoding="utf-8")
    (out_dir / "INDEX.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[done] files={len(files)} out={out_dir}")

if __name__ == "__main__":
    main()
