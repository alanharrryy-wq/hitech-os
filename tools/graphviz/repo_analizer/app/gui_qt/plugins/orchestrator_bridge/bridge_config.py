from __future__ import annotations

import json
import ntpath
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT_PATH = _THIS_FILE.parents[7]
_PLUGIN_HOST_ROOT_PATH = _THIS_FILE.parents[4]
_ORCHESTRATOR_ROOT_PATH = _REPO_ROOT_PATH / "tools" / "orchestrator_factory"
_DEFAULT_ONE_BUTTON_PATH = _ORCHESTRATOR_ROOT_PATH / "tools" / "one_button.ps1"
_DEFAULT_RUNTIME_ROOT_PATH = _REPO_ROOT_PATH / "tools" / "_local" / "orchestrator_bridge"
_DEFAULT_HANDOFF_DIR_PATH = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Downloads"


def _as_windows_path(path_value: Path) -> str:
    return str(path_value).replace("/", "\\")


REPO_ROOT = _as_windows_path(_REPO_ROOT_PATH)
PLUGIN_HOST_ROOT = _as_windows_path(_PLUGIN_HOST_ROOT_PATH)
ORCHESTRATOR_ROOT = _as_windows_path(_ORCHESTRATOR_ROOT_PATH)
DEFAULT_ONE_BUTTON_PATH = _as_windows_path(_DEFAULT_ONE_BUTTON_PATH)
DEFAULT_HANDOFF_DIR = _as_windows_path(_DEFAULT_HANDOFF_DIR_PATH)
DEFAULT_RUNTIME_ROOT = _as_windows_path(_DEFAULT_RUNTIME_ROOT_PATH)
PLUGIN_CONFIG_FILENAME = "bridge_config.json"
HISTORY_FILENAME = "last_runs.json"

WINDOWS_ABS_RE = re.compile(r"^[A-Za-z]:\\")

DEFAULT_CONFIG: Dict[str, Any] = {
    "one_button_path": DEFAULT_ONE_BUTTON_PATH,
    "default_handoff_dir": DEFAULT_HANDOFF_DIR,
    "runtime_root": DEFAULT_RUNTIME_ROOT,
    "timeouts": {
        "startup_ms": 15000,
        "run_ms": 1800000,
        "kill_after_timeout_ms": 3000,
    },
    "history": {
        "max_runs": 25,
    },
}


def normalize_windows_path(path_value: str) -> str:
    return ntpath.normcase(ntpath.normpath((path_value or "").strip().strip('"')))


def is_windows_abs(path_value: str) -> bool:
    return bool(path_value and WINDOWS_ABS_RE.match(path_value.strip().strip('"')))


def is_under_any_root(path_value: str, roots: Iterable[str]) -> bool:
    normalized_path = normalize_windows_path(path_value)
    for root in roots:
        normalized_root = normalize_windows_path(root)
        if not normalized_root:
            continue
        if normalized_path == normalized_root:
            return True
        if normalized_path.startswith(normalized_root + "\\"):
            return True
    return False


def safe_json_load(path_value: str) -> Dict[str, Any]:
    payload, _error = safe_json_load_with_error(path_value)
    return payload


def safe_json_load_with_error(path_value: str) -> Tuple[Dict[str, Any], str]:
    try:
        if not path_value or not os.path.isfile(path_value):
            return {}, ""
        with open(path_value, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            return {}, "json root must be an object"
        return data, ""
    except Exception as exc:
        return {}, str(exc)


def safe_json_dump(path_value: str, payload: Any) -> Tuple[bool, str]:
    directory = os.path.dirname(path_value)
    try:
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path_value, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def coerce_int(value: Any, default_value: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default_value
    return max(minimum, min(maximum, parsed))


def load_plugin_manifest(plugin_dir: str) -> Dict[str, Any]:
    manifest_path = os.path.join(plugin_dir, "plugin.json")
    data = safe_json_load(manifest_path)
    return data if isinstance(data, dict) else {}


@dataclass
class BridgeConfig:
    one_button_path: str
    default_handoff_dir: str
    runtime_root: str
    startup_timeout_ms: int
    run_timeout_ms: int
    kill_after_timeout_ms: int
    max_runs: int
    config_path: str = ""

    @property
    def history_path(self) -> str:
        return ntpath.join(self.runtime_root, HISTORY_FILENAME)

    @property
    def allowed_output_roots(self) -> List[str]:
        roots = [
            REPO_ROOT,
            PLUGIN_HOST_ROOT,
            ORCHESTRATOR_ROOT,
            self.default_handoff_dir,
            self.runtime_root,
        ]
        return [root for root in roots if root]

    def validate(self) -> List[str]:
        problems: List[str] = []
        if not self.one_button_path:
            problems.append("Configuration missing one_button_path.")
        elif not is_windows_abs(self.one_button_path):
            problems.append(
                f"Configured one_button_path must be an absolute Windows path: {self.one_button_path}"
            )
        elif not self.one_button_path.lower().endswith(".ps1"):
            problems.append(
                f"Configured one_button_path must point to a .ps1 file: {self.one_button_path}"
            )
        elif not is_under_any_root(self.one_button_path, [ORCHESTRATOR_ROOT]):
            problems.append(
                f"Configured one_button_path is outside the approved orchestrator root: {self.one_button_path}"
            )

        if not self.default_handoff_dir:
            problems.append("Configuration missing default_handoff_dir.")
        elif not is_windows_abs(self.default_handoff_dir):
            problems.append(
                f"Configured default_handoff_dir must be an absolute Windows path: {self.default_handoff_dir}"
            )

        if not self.runtime_root:
            problems.append("Configuration missing runtime_root.")
        elif not is_windows_abs(self.runtime_root):
            problems.append(
                f"Configured runtime_root must be an absolute Windows path: {self.runtime_root}"
            )
        elif not is_under_any_root(self.runtime_root, [ntpath.join(REPO_ROOT, "tools", "_local")]):
            problems.append(
                f"Configured runtime_root must stay under tools\\_local: {self.runtime_root}"
            )

        if self.startup_timeout_ms <= 0:
            problems.append("Configured startup timeout must be greater than zero.")
        if self.run_timeout_ms <= 0:
            problems.append("Configured run timeout must be greater than zero.")
        if self.kill_after_timeout_ms <= 0:
            problems.append("Configured kill_after_timeout_ms must be greater than zero.")
        if self.max_runs <= 0:
            problems.append("Configured history.max_runs must be greater than zero.")
        return problems


def load_bridge_config(plugin_dir: str) -> Tuple[BridgeConfig, List[str]]:
    config_path = os.path.join(plugin_dir, PLUGIN_CONFIG_FILENAME)
    raw, load_error = safe_json_load_with_error(config_path)
    load_problems: list[str] = []
    if load_error:
        load_problems.append(f"Could not parse bridge_config.json: {load_error}")

    one_button_path = str(raw.get("one_button_path") or DEFAULT_CONFIG["one_button_path"]).strip()
    default_handoff_dir = str(
        raw.get("default_handoff_dir") or DEFAULT_CONFIG["default_handoff_dir"]
    ).strip()
    runtime_root = str(raw.get("runtime_root") or DEFAULT_CONFIG["runtime_root"]).strip()

    timeouts_raw = raw.get("timeouts") if isinstance(raw.get("timeouts"), dict) else {}
    history_raw = raw.get("history") if isinstance(raw.get("history"), dict) else {}

    config = BridgeConfig(
        one_button_path=one_button_path,
        default_handoff_dir=default_handoff_dir,
        runtime_root=runtime_root,
        startup_timeout_ms=coerce_int(
            timeouts_raw.get("startup_ms"),
            int(DEFAULT_CONFIG["timeouts"]["startup_ms"]),
            1000,
            600000,
        ),
        run_timeout_ms=coerce_int(
            timeouts_raw.get("run_ms"),
            int(DEFAULT_CONFIG["timeouts"]["run_ms"]),
            5000,
            28800000,
        ),
        kill_after_timeout_ms=coerce_int(
            timeouts_raw.get("kill_after_timeout_ms"),
            int(DEFAULT_CONFIG["timeouts"]["kill_after_timeout_ms"]),
            1000,
            30000,
        ),
        max_runs=coerce_int(
            history_raw.get("max_runs"),
            int(DEFAULT_CONFIG["history"]["max_runs"]),
            1,
            500,
        ),
        config_path=config_path,
    )
    return config, load_problems + config.validate()


__all__ = [
    "BridgeConfig",
    "DEFAULT_CONFIG",
    "DEFAULT_HANDOFF_DIR",
    "DEFAULT_ONE_BUTTON_PATH",
    "DEFAULT_RUNTIME_ROOT",
    "HISTORY_FILENAME",
    "ORCHESTRATOR_ROOT",
    "PLUGIN_CONFIG_FILENAME",
    "PLUGIN_HOST_ROOT",
    "REPO_ROOT",
    "coerce_int",
    "is_under_any_root",
    "is_windows_abs",
    "load_bridge_config",
    "load_plugin_manifest",
    "normalize_windows_path",
    "safe_json_dump",
    "safe_json_load",
    "safe_json_load_with_error",
]
