from __future__ import annotations

import json
import tempfile
from pathlib import Path

from pya.kernel.context import RuntimeContext
from pya.kernel.discovery import load_json_file


FIXED_TIME = "2026-04-11T00:00:00Z"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sample_app_root() -> Path:
    return project_root() / "examples" / "sample_app"


def load_manifest(name: str) -> dict[str, object]:
    return load_json_file(project_root() / "pya" / "engines" / name / "manifest.json")


def build_context(*, target: Path | None = None):
    temp_dir = tempfile.TemporaryDirectory()
    out = Path(temp_dir.name) / "out"
    context = RuntimeContext.build(
        root=project_root(),
        target=(target or sample_app_root()),
        out=out,
        execution_time=FIXED_TIME,
    )
    return temp_dir, context


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))



def build_frontend_target(target: Path) -> Path:
    (target / "src" / "components").mkdir(parents=True, exist_ok=True)
    (target / "src" / "pages").mkdir(parents=True, exist_ok=True)
    (target / "src" / "routes").mkdir(parents=True, exist_ok=True)
    (target / "public").mkdir(parents=True, exist_ok=True)
    (target / "src" / "main.tsx").write_text(
        "import { Home } from './pages/Home'\nconst routes = [{ path: '/' }]\n",
        encoding="utf-8",
    )
    (target / "src" / "routes" / "register.ts").write_text(
        "export const routes = [{ path: '/modules' }]\n",
        encoding="utf-8",
    )
    (target / "src" / "modules.registry.ts").write_text(
        "export const ModuleDef = { key: 'home' }\n",
        encoding="utf-8",
    )
    (target / "src" / "hitechBridge.ts").write_text(
        "export function send(){ return window.QWebChannel }\n",
        encoding="utf-8",
    )
    (target / "src" / "pages" / "Home.tsx").write_text(
        "export function Home(){ return null }\n",
        encoding="utf-8",
    )
    (target / "src" / "components" / "NavBar.tsx").write_text(
        "export function NavBar(){ return null }\n",
        encoding="utf-8",
    )
    (target / "public" / "modules.config.json").write_text('{"modules": []}\n', encoding="utf-8")
    return target
