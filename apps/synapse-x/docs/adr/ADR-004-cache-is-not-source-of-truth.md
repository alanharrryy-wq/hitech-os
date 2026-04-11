# ADR-004 Cache Is Not Source Of Truth

## Status
Accepted

## Context
Cache improves speed, but can drift after partial failures or schema evolution.

## Decision
JSON cache is a derived optimization layer only. SQLite remains authoritative.

## Consequences
Positive:
- clearer repair path
- simpler conflict resolution
- avoids spooky cache-driven bugs

Tradeoffs:
- some reads may require DB-first logic
- cache rebuild routines must exist
