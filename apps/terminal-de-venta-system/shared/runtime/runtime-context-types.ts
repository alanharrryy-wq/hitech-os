export type PrismaRuntimeMode = "dev" | "customer" | "test" | "release";

export type PrismaRuntimeProfile =
  | "dev"
  | "standalone"
  | "pro"
  | "pc_backoffice"
  | "managed"
  | "degraded_managed";

export type PrismaVertical = "commerce" | "industrial" | "field" | "control";

export type PrismaRuntimeRole = "tablet" | "pc" | "mobile" | "control" | "shared";

export type RuntimeProvenanceSource =
  | "explicit"
  | "env"
  | "runtime_config"
  | "programdata"
  | "legacy_programdata"
  | "device_identity"
  | "dev_fallback"
  | "default";

export type RuntimeProvenance = {
  source: RuntimeProvenanceSource;
  path: string | null;
  detail: string;
};

export type RuntimeIssue = {
  code: string;
  message: string;
  path?: string | null;
};

export type RuntimeContextPaths = {
  runtimeRoot: string;
  configRoot: string;
  businessRoot: string;
  tabletDataRoot: string;
  pcDataRoot: string;
  syncRoot: string;
  supportRoot: string;
  updatesRoot: string;
  rollbackRoot: string;
  logsRoot: string;
  exportsRoot: string;
  backupsRoot: string;
  licenseFile: string;
  deviceIdentityFile: string;
};

export type DeviceIdentity = {
  schemaVersion: string;
  deviceId: string;
  terminalId: string;
  businessId: string;
  storeId: string;
  vertical: PrismaVertical;
  role: PrismaRuntimeRole;
  createdAt: string;
  updatedAt?: string;
};

export type RuntimeContextConfig = {
  schemaVersion?: string;
  runtimeMode?: PrismaRuntimeMode | PrismaRuntimeProfile;
  runtimeProfile?: PrismaRuntimeProfile;
  vertical?: PrismaVertical;
  role?: PrismaRuntimeRole;
  runtimeRoot?: string;
  configRoot?: string;
  businessId?: string;
  storeId?: string;
  branchId?: string;
  terminalId?: string;
  deviceId?: string;
  clientId?: string;
  packageType?: string;
  paths?: Partial<RuntimeContextPaths>;
  license?: {
    file?: string;
    mode?: string;
    serverUrl?: string;
  };
  sync?: Record<string, unknown>;
  features?: Record<string, unknown>;
  support?: Record<string, unknown>;
  updates?: Record<string, unknown>;
};

export type RuntimeContext = {
  schemaVersion: string;
  runtimeMode: PrismaRuntimeMode;
  runtimeProfile: PrismaRuntimeProfile;
  vertical: PrismaVertical;
  role: PrismaRuntimeRole;
  runtimeRoot: string;
  configRoot: string;
  licenseFile: string;
  deviceIdentityFile: string;
  businessId: string | null;
  storeId: string | null;
  terminalId: string | null;
  deviceId: string | null;
  clientId: string | null;
  packageType: string | null;
  paths: RuntimeContextPaths;
  deviceIdentity: DeviceIdentity | null;
  config: RuntimeContextConfig | null;
  configPath: string | null;
  provenance: Record<string, RuntimeProvenance>;
  warnings: RuntimeIssue[];
  blockingIssues: RuntimeIssue[];
};

export type RuntimeContextResolverOptions = {
  explicitRuntimeConfigPath?: string | null;
  runtimeMode?: PrismaRuntimeMode | PrismaRuntimeProfile | null;
  runtimeProfile?: PrismaRuntimeProfile | null;
  vertical?: PrismaVertical | null;
  role?: PrismaRuntimeRole | null;
  systemRoot?: string | null;
  programDataRoot?: string | null;
  licenseFile?: string | null;
  deviceIdentityFile?: string | null;
};
