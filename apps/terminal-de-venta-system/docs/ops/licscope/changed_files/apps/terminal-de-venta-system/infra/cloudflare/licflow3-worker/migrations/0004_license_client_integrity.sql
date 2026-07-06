CREATE TRIGGER IF NOT EXISTS trg_licenses_require_client_assignment_insert
BEFORE INSERT ON licenses
FOR EACH ROW
WHEN NEW.status IN ('active', 'renewed', 'expiring', 'grace_period', 'refreshed')
  AND NOT EXISTS (
    SELECT 1
    FROM license_assignments
    WHERE license_id = NEW.license_id
      AND customer_id IS NOT NULL
      AND business_id IS NOT NULL
      AND status IN ('assigned', 'active', 'renewed')
  )
BEGIN
  SELECT RAISE(ABORT, 'LICENSE_CLIENT_CONTEXT_REQUIRED');
END;

CREATE TRIGGER IF NOT EXISTS trg_licenses_require_client_assignment_update
BEFORE UPDATE OF status ON licenses
FOR EACH ROW
WHEN NEW.status IN ('active', 'renewed', 'expiring', 'grace_period', 'refreshed')
  AND NOT EXISTS (
    SELECT 1
    FROM license_assignments
    WHERE license_id = NEW.license_id
      AND customer_id IS NOT NULL
      AND business_id IS NOT NULL
      AND status IN ('assigned', 'active', 'renewed')
  )
BEGIN
  SELECT RAISE(ABORT, 'LICENSE_CLIENT_CONTEXT_REQUIRED');
END;

CREATE INDEX IF NOT EXISTS idx_license_assignments_license_client
ON license_assignments(license_id, customer_id, business_id, status);
