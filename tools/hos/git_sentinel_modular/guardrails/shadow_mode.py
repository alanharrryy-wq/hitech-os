import os

def shadow_mode_enabled():
    return os.getenv("HOS_SENTINEL_SHADOW") == "1"

def require_shadow_if_enabled():
    if shadow_mode_enabled():
        print("Sentinel running in SHADOW mode")
