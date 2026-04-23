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



def build_noisy_frontend_target(target: Path) -> Path:
    build_frontend_target(target)
    (target / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
    (target / "reports" / "patch_runs").mkdir(parents=True, exist_ok=True)
    (target / "_dependency_graphs").mkdir(parents=True, exist_ok=True)
    (target / "tests").mkdir(parents=True, exist_ok=True)
    (target / "tools").mkdir(parents=True, exist_ok=True)
    (target / "src" / "lib" / "i18n" / "feature_contracts").mkdir(parents=True, exist_ok=True)

    (target / "docs" / "architecture" / "BACKEND_FLOW_MAP.md").write_text(
        '# backend flow\nlocale: es-MX\npath: "/fake-docs-route"\n',
        encoding="utf-8",
    )
    (target / "reports" / "patch_runs" / "patch_20260410_155501.md").write_text(
        '# patch report\ni18n translation summary\n',
        encoding="utf-8",
    )
    (target / "_dependency_graphs" / "visual_control_map_external_interaction_template.md").write_text(
        '# graph\npath: "/graph"\n',
        encoding="utf-8",
    )
    (target / "tests" / "payments.i18n.contract.test.ts").write_text(
        "import { describe } from 'vitest'\nexport const value = 1\n",
        encoding="utf-8",
    )
    (target / "tools" / "enforce_i18n_guardrails.py").write_text(
        "import json\n\ndef main():\n    return json.dumps({'ok': True})\n",
        encoding="utf-8",
    )
    (target / "src" / "lib" / "i18n" / "feature_contracts" / "README.md").write_text(
        '# i18n feature contracts\ntranslate locale contract\n',
        encoding="utf-8",
    )
    return target
