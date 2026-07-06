from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
@dataclass
class RunContext:
    project_root: Path
    output_dir: Path
    max_sample_rows: int=5
    strict_production: bool=False
    include_placeholders: bool=True
