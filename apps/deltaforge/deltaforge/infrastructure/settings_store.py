from __future__ import annotations

import json
from pathlib import Path

from deltaforge.domain.models import AppSettings


class SettingsStore:
    def __init__(self, settings_path: Path | None = None) -> None:
        default_dir = Path.home() / ".deltaforge"
        self._path = settings_path or (default_dir / "settings.json")

    def load(self) -> AppSettings:
        if not self._path.exists():
            return AppSettings()

        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return AppSettings()

        return AppSettings(
            theme_id=str(raw.get("theme_id") or "deltaforge_steel"),
            recent_roots=list(raw.get("recent_roots") or []),
            last_session_root=str(raw.get("last_session_root") or ""),
            window_width=int(raw.get("window_width") or 1680),
            window_height=int(raw.get("window_height") or 980),
        )

    def save(self, settings: AppSettings) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "theme_id": settings.theme_id,
            "recent_roots": settings.recent_roots,
            "last_session_root": settings.last_session_root,
            "window_width": settings.window_width,
            "window_height": settings.window_height,
        }
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
