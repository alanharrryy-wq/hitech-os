from pathlib import Path
import os

def runtime_root() -> Path:
    return Path(
        os.getenv(
            "HITECH_SENTINEL_RUNTIME",
            r"C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime",
        )
    )

def modular_root() -> Path:
    return Path(
        os.getenv(
            "HITECH_SENTINEL_MODULAR_ROOT",
            r"F:\repos\hitech-os\tools\hos\git_sentinel_modular",
        )
    )

def shadow_root() -> Path:
    return runtime_root() / "shadow_mode"
