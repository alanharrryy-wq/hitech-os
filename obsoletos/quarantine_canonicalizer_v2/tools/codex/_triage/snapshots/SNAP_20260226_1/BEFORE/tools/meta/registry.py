from __future__ import annotations

import pathlib
from dataclasses import dataclass

from .constants import DEFAULT_REGISTRY, DOCS_DOCTOR_REL
from .io_ops import atomic_write_text


@dataclass(frozen=True)
class RepoEntry:
    name: str
    path: str
    docs_doctor: str


@dataclass(frozen=True)
class Registry:
    version: int
    timezone: str
    feature_flags: dict[str, str]
    repos: list[RepoEntry]


def ensure_default_registry(path: pathlib.Path) -> None:
    if path.exists():
        return
    lines: list[str] = []
    lines.append("version: 1")
    lines.append("timezone: America/Mexico_City")
    lines.append("feature_flags:")
    lines.append("  convergence_actions: OFF")
    lines.append("  forced_repo_changes: OFF")
    lines.append("repos:")
    for repo in DEFAULT_REGISTRY["repos"]:
        lines.append(f"  - name: {repo['name']}")
        lines.append(f"    path: {repo['path']}")
        lines.append(f"    docs_doctor: {repo['docs_doctor']}")
    atomic_write_text(path, "\n".join(lines))


def load_registry(path: pathlib.Path) -> Registry:
    text = path.read_text(encoding="utf-8")
    raw = _parse_simple_yaml(text)
    version = int(raw.get("version", 1))
    timezone = str(raw.get("timezone", "America/Mexico_City"))
    feature_flags = dict(raw.get("feature_flags", {"convergence_actions": "OFF", "forced_repo_changes": "OFF"}))
    repos_raw = raw.get("repos", [])
    repos: list[RepoEntry] = []
    for item in repos_raw:
        name = str(item.get("name", "")).strip()
        repo_path = str(item.get("path", "")).strip()
        doctor = str(item.get("docs_doctor", DOCS_DOCTOR_REL)).strip() or DOCS_DOCTOR_REL
        if not name or not repo_path:
            continue
        repos.append(RepoEntry(name=name, path=repo_path, docs_doctor=doctor))

    repos = sorted(repos, key=lambda r: r.name.lower())
    return Registry(version=version, timezone=timezone, feature_flags=feature_flags, repos=repos)


def _parse_simple_yaml(text: str) -> dict:
    """
    Minimal deterministic parser for the registry shape:
      version: 1
      timezone: America/Mexico_City
      feature_flags:
        key: value
      repos:
        - name: ...
          path: ...
          docs_doctor: ...
    """
    data: dict = {"feature_flags": {}, "repos": []}
    lines = text.splitlines()
    i = 0
    mode = ""
    current_repo: dict | None = None
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        if line.startswith("version:"):
            data["version"] = line.split(":", 1)[1].strip()
            mode = ""
            continue
        if line.startswith("timezone:"):
            data["timezone"] = line.split(":", 1)[1].strip()
            mode = ""
            continue
        if line == "feature_flags:":
            mode = "flags"
            continue
        if line == "repos:":
            mode = "repos"
            continue
        if mode == "flags" and ":" in line:
            k, v = line.split(":", 1)
            data["feature_flags"][k.strip()] = v.strip()
            continue
        if mode == "repos":
            if line.startswith("- "):
                if current_repo:
                    data["repos"].append(current_repo)
                current_repo = {}
                payload = line[2:]
                if ":" in payload:
                    k, v = payload.split(":", 1)
                    current_repo[k.strip()] = v.strip()
                continue
            if ":" in line and current_repo is not None:
                k, v = line.split(":", 1)
                current_repo[k.strip()] = v.strip()
                continue
    if current_repo:
        data["repos"].append(current_repo)
    return data
