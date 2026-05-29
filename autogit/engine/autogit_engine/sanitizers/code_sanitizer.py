from __future__ import annotations
from ..paths import redact_local_paths
from ..secret_scan import redact_literal_keys
def sanitize_code_text(text:str)->str: return redact_literal_keys(redact_local_paths(text))
