from dataclasses import dataclass, field


@dataclass(slots=True)
class DiffHunk:
    header: str
    before: str
    after: str


@dataclass(slots=True)
class FileDiff:
    path: str
    change_type: str
    hunks: list[DiffHunk] = field(default_factory=list)


@dataclass(slots=True)
class DiffPreview:
    summary: str
    files: list[FileDiff] = field(default_factory=list)
