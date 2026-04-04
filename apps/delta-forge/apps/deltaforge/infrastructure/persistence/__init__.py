from infrastructure.persistence.session_layout_store import SessionLayoutStore
from infrastructure.settings_store import SettingsStore

# Legacy alias kept for compatibility. Do not use in new code.
StructuredSettingsStore = SettingsStore

__all__ = ["SessionLayoutStore", "SettingsStore", "StructuredSettingsStore"]
