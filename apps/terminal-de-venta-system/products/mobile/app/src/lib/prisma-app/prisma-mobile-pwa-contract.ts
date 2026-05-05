import { z } from "zod";

export const PRISMA_MOBILE_PWA_CONTRACT_ID = "PRISMA_APP_MOBILE_09_PWA_DOMAIN_INSTALL_READY";
export const PRISMA_MOBILE_PWA_CONFIG_PATH = "/prisma-mobile-pwa.config.json";

export const PrismaMobilePwaConfigSchema = z.object({
  contractId: z.literal(PRISMA_MOBILE_PWA_CONTRACT_ID),
  mode: z.literal("pwa-domain"),
  domain: z.string().min(3),
  origin: z.string().url(),
  appPath: z.literal("/prisma-app"),
  installPath: z.literal("/prisma-app/install"),
  offlinePath: z.literal("/prisma-offline.html"),
  manifestPath: z.literal("/manifest.webmanifest"),
  serviceWorkerPath: z.literal("/prisma-mobile-sw.js"),
  supportContact: z.string().min(3),
  lastConfiguredAt: z.string().datetime().nullable(),
  notes: z.array(z.string()).min(1)
});

export type PrismaMobilePwaConfig = z.infer<typeof PrismaMobilePwaConfigSchema>;

export type PrismaMobilePwaInstallStatus = "checking" | "installable" | "installed" | "browser-menu" | "unsupported";

export function isPlaceholderDomain(domain: string): boolean {
  return domain.includes("REPLACE_WITH") || domain === "localhost" || domain.endsWith(".local");
}

export function buildPrismaMobilePublicUrl(config: PrismaMobilePwaConfig, path = config.appPath): string {
  return `${config.origin.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
}
