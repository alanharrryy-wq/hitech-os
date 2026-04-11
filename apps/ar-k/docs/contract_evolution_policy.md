# Contract Evolution Policy

Additive change:
- add optional field
- add backward-tolerant enum value
- add declared artifact family without forcing existing engines

Breaking change:
- rename or remove required field
- tighten enum with no adapter
- move write ownership without docs + manifest change

Deprecation:
- document the field as deprecated
- keep it for at least one minor line
- emit validator warning during coexistence

Multiple versions may coexist only with an explicit adapter declared in the contract registry.
