from PySide6.QtWidgets import QLabel


class ChipLabel(QLabel):
    def __init__(self, text: str, *, tone: str = "neutral") -> None:
        super().__init__(text)
        self.setProperty("role", "hint")
        self.setStyleSheet(self._style_for_tone(tone))

    def _style_for_tone(self, tone: str) -> str:
        palette = {
            "neutral": "#2b3d52",
            "good": "#2e614a",
            "warn": "#6d5530",
            "danger": "#6c3a43",
            "accent": "#2f567a",
        }
        bg = palette.get(tone, palette["neutral"])
        return f"padding: 4px 8px; border-radius: 9px; background: {bg}; color: #dbe7f4;"


class StatusPill(ChipLabel):
    pass
