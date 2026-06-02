from __future__ import annotations
import re
SEVERE=[("CONFLICT_MARKER",re.compile(r"^(<<<<<<<|=======|>>>>>>>)",re.M)),("PRIVATE_KEY",re.compile(r"BEGIN\s+(RSA|OPENSSH|DSA|EC|PGP)?\s*PRIVATE\s+KEY",re.I)),("OPENAI_OR_SIMILAR_KEY",re.compile(r"\bsk-(proj-)?[A-Za-z0-9_\-]{20,}\b")),("AWS_ACCESS_KEY",re.compile(r"\bAKIA[0-9A-Z]{16}\b"))]
SECRET_ASSIGN_RE=re.compile(
    r"(?ix)"
    r"(?P<prefix>\b(?:password|passwd|pwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token)\b\s*[:=]\s*)"
    r"(?P<quote>[\"\']?)"
    r"(?P<value>[^\"\'\r\n,}\]]{6,})"
    r"(?P=quote)"
    r"(?P<suffix>[;)]?)"
)
