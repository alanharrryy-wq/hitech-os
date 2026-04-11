# scanner

Purpose: Discover files, imports, exports, and emit non-canonical signals.

Stage: `scan`
Reads: `none`
Writes: `signals`

Forbidden moves:
- do not write outside declared ownership
- do not invent new states
- do not alter system or kernel without explicit review
