# Customer Upgrade and Rollback

Customer upgrades must be boring in the best possible way: backup first, apply only the intended folder, verify, and rollback if verification fails.

For this bundle, the install payload is scoped to `quality`. The installer delivered beside the payload backs up the existing target folder before replacement.

Quality itself remains read-only toward the product DB. Migration safety is static unless the operator explicitly runs a migration plan outside PQOS.
