from __future__ import annotations
from ..secret_scan import redact_literal_keys
def sanitize_code_text(text:str)->str: return redact_literal_keys(text, code=True)
