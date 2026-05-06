export type LicenseRefreshConfig = {
  enabled: boolean;
  serverUrl: string | null;
  deviceId: string | null;
  timeoutMs: number;
};

export function getLicenseRefreshConfig(): LicenseRefreshConfig {
  const enabled = process.env.PRISMA_LICENSE_REFRESH_ENABLED === "1" || process.env.PRISMA_LICENSE_REFRESH_ENABLED === "true";
  const serverUrl = process.env.PRISMA_LICENSE_SERVER_URL?.replace(/\/+$/, "") || null;
  const deviceId = process.env.PRISMA_LICENSE_DEVICE_ID || null;
  const timeoutMs = Number(process.env.PRISMA_LICENSE_REFRESH_TIMEOUT_MS || 8000);
  return { enabled, serverUrl, deviceId, timeoutMs: Number.isFinite(timeoutMs) ? timeoutMs : 8000 };
}
