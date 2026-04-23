export const CLIENT_PERMISSION_KEYS = [
  "workspace.read",
  "records.read",
  "records.write",
  "sync.read",
  "sync.retry",
  "schemas.read",
  "flows.start",
  "utilities.open",
  "support.read"
] as const;

export type ClientPermissionKey = (typeof CLIENT_PERMISSION_KEYS)[number];

export const CLIENT_DEFAULT_PERMISSIONS: ClientPermissionKey[] = [
  "workspace.read",
  "records.read",
  "records.write",
  "sync.read",
  "sync.retry",
  "schemas.read",
  "flows.start",
  "utilities.open",
  "support.read"
];

