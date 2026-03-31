from PySide6.QtWidgets import QFrame


class HairlineSeparator(QFrame):
    def __init__(self, *, vertical: bool = False) -> None:
        super().__init__()
        self.setProperty("card", "section_alt")
        if vertical:
            self.setFrameShape(QFrame.VLine)
            self.setLineWidth(1)
        else:
            self.setFrameShape(QFrame.HLine)
            self.setLineWidth(1)
