from dataclasses import dataclass, field


@dataclass(slots=True)
class AppSettings:
    theme_id: str = "deltaforge_steel"
    recent_roots: list[str] = field(default_factory=list)
    last_session_root: str = ""
    window_width: int = 1680
    window_height: int = 980
