"""
Engine Guardian v3.

Lightweight external adapter-based orchestration layer for:
- origin remediation
- Cloudflare tunnel and service observation
- public engine truth health
- official startup scheduler contract
- Repo Analyzer sibling-domain wrappers

Non-goals:
- owning git_sentinel_modular
- rewriting Repo Analyzer internals
- replacing legacy Cloudflare tooling from the inside
"""

__all__ = ["__version__"]
__version__ = "0.3.0"
