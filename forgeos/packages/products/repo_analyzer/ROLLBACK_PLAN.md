# ROLLBACK PLAN

1. Stop runtime activation for package $(System.Collections.Specialized.OrderedDictionary.package_id).
2. Reinstall previous known-good package manifest and artifacts.
3. Re-run compatibility and integrity checks before reactivation.
4. Emit rollback evidence into release logs.