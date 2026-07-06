-- LICFLOW3 revoke compatibility fix for the live D1 legacy licenses schema.
-- Migration 0004 added license client-context triggers that reference
-- NEW.license_id, but the live licenses table can still be legacy-shaped with
-- id / tenant_id columns. Keep client-context enforcement in the Worker, where
-- it can inspect schema shape safely.

DROP TRIGGER IF EXISTS trg_licenses_require_client_assignment_insert;
DROP TRIGGER IF EXISTS trg_licenses_require_client_assignment_update;

CREATE INDEX IF NOT EXISTS idx_license_assignments_license_client
ON license_assignments(license_id, customer_id, business_id, status);
