from __future__ import annotations

from dataclasses import dataclass

__version__ = "2.0.0-block-b"


@dataclass(frozen=True)
class VersionInfo:
    major: int
    minor: int
    patch: int
    label: str

    @property
    def text(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.label:
            return f"{base}-{self.label}"
        return base


def parse_version(version: str) -> VersionInfo:
    base = version
    label = ""
    if "-" in version:
        base, label = version.split("-", 1)
    parts = base.split(".")
    padded = (parts + ["0", "0", "0"])[:3]
    major, minor, patch = (int(item) if item.isdigit() else 0 for item in padded)
    return VersionInfo(major=major, minor=minor, patch=patch, label=label)


def get_version() -> str:
    return __version__

