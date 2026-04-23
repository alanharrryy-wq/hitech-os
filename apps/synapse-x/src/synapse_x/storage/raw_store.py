import shutil
from pathlib import Path


def copy_raw_file(source: str | Path, target: str | Path) -> Path:
    src = Path(source)
    dst = Path(target)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return dst
