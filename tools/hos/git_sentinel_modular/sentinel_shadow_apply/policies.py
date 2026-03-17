from dataclasses import dataclass, field

@dataclass
class ApplyPolicy:
    forbidden_parts: set = field(default_factory=lambda: {
        "_local",
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
    })
    forbidden_suffixes: set = field(default_factory=lambda: {
        ".tmp",
        ".bak",
        ".pyc",
        ".pyo",
    })
    excluded_file_names: set = field(default_factory=lambda: {
        ".DS_Store",
        "Thumbs.db",
    })
    allow_overwrite: bool = True

def default_policy() -> ApplyPolicy:
    return ApplyPolicy()
