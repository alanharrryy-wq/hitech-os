from .flags import ENABLE_SERVICE
from .repository import Repository


class Service:
    def __init__(self) -> None:
        self.repository = Repository()

    def status(self) -> str:
        return "enabled" if ENABLE_SERVICE else "disabled"
