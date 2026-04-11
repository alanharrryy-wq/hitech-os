# Engine Admission

Admission checks:
1. manifest satisfies `engine_manifest`
2. `engine_id == engine_type` for canonical engines
3. declared stage matches root manifest
4. kernel compatibility matches same major
5. registry writes belong to the sovereign writer only
6. permissions expose `reads` and `writes`
7. entrypoint is importable

Rejection is loud and blocks pipeline startup.
