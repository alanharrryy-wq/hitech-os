import json, os, re, sys, pathlib, datetime

def safe_name(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"[\\/:*?\"<>|]+", "-", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-._")
    return s[:140] if s else "chat"

def extract_messages(obj):
    # Best-effort across variants: {role, content} or nested shapes.
    msgs = []
    if isinstance(obj, dict):
        role = obj.get("role") or obj.get("author") or obj.get("speaker") or obj.get("type")
        content = obj.get("content")

        # Sometimes content is list of parts
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, str):
                    parts.append(p)
                elif isinstance(p, dict):
                    parts.append(str(p.get("text") or p.get("value") or p.get("content") or ""))
            content = "\n".join([x for x in parts if x])

        # Sometimes nested message
        if content is None and "message" in obj and isinstance(obj["message"], dict):
            m = obj["message"]
            role = role or m.get("role")
            content = m.get("content") or m.get("text")

        # Sometimes OpenAI-ish "output_text"/"input_text"
        if content is None:
            content = obj.get("text") or obj.get("output_text") or obj.get("input_text")

        if role in ("user","assistant","system") and isinstance(content, str) and content.strip():
            msgs.append({"role": role, "content": content.strip()})
            return msgs

        # Tool call outputs sometimes contain useful text
        for k in ("tool_output","result","output","data"):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                msgs.append({"role":"tool", "content": v.strip()})
                return msgs

    return msgs

def parse_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            records.append(obj)
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
        if role == "assistant":
            out.append("## Assistant")
        elif role == "user":
            out.append("## User")
        elif role == "system":
            out.append("## System")
        else:
            out.append("## Tool")
        out.append("")
        out.append(m["content"])
        out.append("")
    return "\n".join(out).rstrip() + "\n"

def main():
    if len(sys.argv) < 3:
        print("usage: parse_rollouts.py <out_dir> <file1> [file2...]")
        sys.exit(2)

    out_dir = pathlib.Path(sys.argv[1]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    md_dir = out_dir / "md"
    js_dir = out_dir / "json"
    md_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)

    index = []
    for p in sys.argv[2:]:
        src = pathlib.Path(p).resolve()
        base = src.name
        records = parse_jsonl(str(src))
        messages = []
        for r in records:
            messages.extend(extract_messages(r))

        # Build header using filename timestamp if present
        header = base
        title = pick_title(messages, base)
        stem = safe_name(base.replace(".jsonl","")) + "__" + title

        md_path = md_dir / (stem + ".md")
        js_path = js_dir / (stem + ".summary.json")

        md_path.write_text(to_md(messages, header), encoding="utf-8")

        summary = {
            "source": str(src),
            "file": base,
            "message_count": len(messages),
            "roles": {
                "user": sum(1 for m in messages if m["role"]=="user"),
                "assistant": sum(1 for m in messages if m["role"]=="assistant"),
                "system": sum(1 for m in messages if m["role"]=="system"),
                "tool": sum(1 for m in messages if m["role"]=="tool"),
            }
        }
        js_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

        index.append({
            "file": base,
            "md": str(md_path.relative_to(out_dir)).replace("\\","/"),
            "summary": str(js_path.relative_to(out_dir)).replace("\\","/"),
            "message_count": summary["message_count"],
            "title": title,
        })

    # Write INDEX.md
    idx_md = []
    idx_md.append("# Codex Rollouts Export Index")
    idx_md.append("")
    idx_md.append(f"Generated: {datetime.datetime.utcnow().isoformat()}Z")
    idx_md.append("")
    idx_md.append("| Chat | Messages | Markdown | Summary |")
    idx_md.append("|---|---:|---|---|")
    for it in sorted(index, key=lambda x: x["file"]):
        idx_md.append(f"| {it['title']} | {it['message_count']} | [{it['md']}]({it['md']}) | [{it['summary']}]({it['summary']}) |")
    (out_dir / "INDEX.md").write_text("\n".join(idx_md) + "\n", encoding="utf-8")

    # Machine index
    (out_dir / "INDEX.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    main()
