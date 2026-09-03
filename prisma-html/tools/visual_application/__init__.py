"""PRISMA Generic Visual Application Engine V1.

Source/static application machinery only. Runtime visual certification is deliberately outside this package.
"""
from .engine import preview, apply, verify, rollback_transaction
__all__=["preview","apply","verify","rollback_transaction"]
