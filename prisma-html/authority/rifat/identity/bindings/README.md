# IDBIND1

This directory contains governed, read-only binding definitions and coverage evidence.

Use:

```powershell
python tools/identity_binding_resolver.py sources
python tools/identity_binding_resolver.py coverage
python tools/identity_binding_resolver.py example
python tools/validate_identity_bindings.py
```

A binding envelope is an instruction and evidence object. It is never a product patch.
