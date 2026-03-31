from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class SectionCard(QFrame):
    def __init__(self, title: str, subtitle: str = "", *, alt: bool = False) -> None:
        super().__init__()
        self.setProperty("card", "section_alt" if alt else "section")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setProperty("role", "title")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setProperty("role", "subtitle")

        layout.addWidget(self.title_label)
        if subtitle:
            layout.addWidget(self.subtitle_label)

        self.content_host = QWidget()
        self.content_layout = QVBoxLayout(self.content_host)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        layout.addWidget(self.content_host, 1)

    def set_content_widget(self, widget: QWidget) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().setParent(None)
        self.content_layout.addWidget(widget)
