CREATE TABLE IF NOT EXISTS customer_setups (
  setup_id TEXT PRIMARY KEY,
  setup_code TEXT NOT NULL UNIQUE,
  setup_url TEXT NOT NULL,
  qr_payload TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  tenant_slug TEXT NOT NULL,
  business_id TEXT NOT NULL,
  business_name TEXT NOT NULL,
  package_code TEXT NOT NULL,
  plan_code TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  expires_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_setup_slots (
  setup_id TEXT NOT NULL,
  surface TEXT NOT NULL,
  label TEXT NOT NULL,
  allowed INTEGER NOT NULL DEFAULT 1,
  claimed INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (setup_id, surface),
  FOREIGN KEY (setup_id) REFERENCES customer_setups(setup_id)
);

CREATE TABLE IF NOT EXISTS customer_device_claims (
  claim_id TEXT PRIMARY KEY,
  setup_id TEXT NOT NULL,
  setup_code TEXT NOT NULL,
  tenant_slug TEXT NOT NULL,
  surface TEXT NOT NULL,
  device_id TEXT NOT NULL,
  device_name TEXT,
  installation_fingerprint TEXT,
  app_version TEXT,
  operator_label TEXT,
  status TEXT NOT NULL DEFAULT 'claimed',
  claimed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  replaced_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (setup_id, device_id),
  FOREIGN KEY (setup_id) REFERENCES customer_setups(setup_id)
);

CREATE INDEX IF NOT EXISTS idx_customer_setups_code ON customer_setups(setup_code);
CREATE INDEX IF NOT EXISTS idx_customer_device_claims_setup_surface ON customer_device_claims(setup_id, surface);
