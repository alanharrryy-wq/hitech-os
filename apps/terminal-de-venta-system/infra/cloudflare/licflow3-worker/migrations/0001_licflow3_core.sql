CREATE TABLE IF NOT EXISTS tenants (
  slug TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'prepared',
  plan TEXT NOT NULL DEFAULT 'TABLET_PC_MANAGED',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS licenses (
  license_id TEXT PRIMARY KEY,
  tenant_slug TEXT NOT NULL,
  status TEXT NOT NULL,
  plan TEXT NOT NULL,
  activation_status TEXT,
  valid_until TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
  device_id TEXT PRIMARY KEY,
  tenant_slug TEXT NOT NULL,
  device_name TEXT,
  role TEXT,
  platform TEXT,
  status TEXT NOT NULL DEFAULT 'registered',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS integration_receipts (
  receipt_id TEXT PRIMARY KEY,
  tenant_slug TEXT NOT NULL,
  kind TEXT NOT NULL,
  ok INTEGER NOT NULL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS support_notes (
  note_id TEXT PRIMARY KEY,
  tenant_slug TEXT NOT NULL,
  text TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
  event_id TEXT PRIMARY KEY,
  tenant_slug TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_licenses_tenant_slug ON licenses (tenant_slug);
CREATE INDEX IF NOT EXISTS idx_devices_tenant_slug ON devices (tenant_slug);
CREATE INDEX IF NOT EXISTS idx_receipts_tenant_slug ON integration_receipts (tenant_slug);
CREATE INDEX IF NOT EXISTS idx_support_notes_tenant_slug ON support_notes (tenant_slug);
CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_slug ON audit_events (tenant_slug);
