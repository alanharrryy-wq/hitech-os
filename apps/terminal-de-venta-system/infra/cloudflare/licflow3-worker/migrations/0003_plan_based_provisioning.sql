CREATE TABLE IF NOT EXISTS license_plans (
  plan_id TEXT PRIMARY KEY,
  plan_name TEXT NOT NULL,
  max_tablet_devices INTEGER NOT NULL DEFAULT 0,
  max_pc_devices INTEGER NOT NULL DEFAULT 0,
  max_mobile_devices INTEGER NOT NULL DEFAULT 0,
  max_total_devices INTEGER NOT NULL DEFAULT 0,
  allowed_surfaces_json TEXT NOT NULL,
  features_json TEXT NOT NULL,
  setup_mode TEXT NOT NULL,
  claim_mode TEXT NOT NULL,
  requires_manual_approval INTEGER NOT NULL DEFAULT 0,
  expiration_policy TEXT NOT NULL,
  grace_policy TEXT NOT NULL,
  renewal_policy TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS license_assignments (
  license_assignment_id TEXT PRIMARY KEY,
  license_id TEXT NOT NULL,
  setup_bundle_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  tenant_slug TEXT NOT NULL,
  business_id TEXT NOT NULL,
  plan_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'assigned',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_setup_bundles (
  setup_bundle_id TEXT PRIMARY KEY,
  setup_id TEXT NOT NULL UNIQUE,
  setup_code TEXT NOT NULL UNIQUE,
  setup_link TEXT NOT NULL,
  setup_qr_payload TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  tenant_slug TEXT NOT NULL,
  business_id TEXT NOT NULL,
  business_name TEXT NOT NULL,
  license_id TEXT NOT NULL,
  license_assignment_id TEXT NOT NULL,
  plan_id TEXT NOT NULL,
  operator_action_count INTEGER NOT NULL DEFAULT 1,
  manual_device_claim_required INTEGER NOT NULL DEFAULT 0,
  audit_event_id TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  expires_at TEXT,
  created_by TEXT NOT NULL DEFAULT 'licflow3-worker',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_device_claim_slots (
  slot_id TEXT PRIMARY KEY,
  setup_bundle_id TEXT NOT NULL,
  setup_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  license_id TEXT NOT NULL,
  plan_id TEXT NOT NULL,
  surface TEXT NOT NULL,
  slot_index INTEGER NOT NULL,
  claim_code TEXT NOT NULL UNIQUE,
  device_id TEXT,
  claimed_at TEXT,
  expires_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'AVAILABLE',
  audit_event_id TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (setup_bundle_id, surface, slot_index)
);

CREATE INDEX IF NOT EXISTS idx_customer_setup_bundles_setup_code ON customer_setup_bundles(setup_code);
CREATE INDEX IF NOT EXISTS idx_customer_setup_bundles_customer_plan ON customer_setup_bundles(customer_id, plan_id);
CREATE INDEX IF NOT EXISTS idx_license_assignments_customer_plan ON license_assignments(customer_id, plan_id);
CREATE INDEX IF NOT EXISTS idx_customer_device_claim_slots_bundle_surface ON customer_device_claim_slots(setup_bundle_id, surface, status);
CREATE INDEX IF NOT EXISTS idx_customer_device_claim_slots_license_plan ON customer_device_claim_slots(license_id, plan_id);
