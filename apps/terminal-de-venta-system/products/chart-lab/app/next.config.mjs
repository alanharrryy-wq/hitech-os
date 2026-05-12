import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const systemRoot = path.resolve(__dirname, "..", "..", "..");
const staticExport = process.env.PRISMA_CHART_LAB_STATIC_EXPORT === "true";

/** @type {import('next').NextConfig} */
const nextConfig = {
  ...(staticExport ? { output: "export", trailingSlash: true, images: { unoptimized: true } } : {}),
  outputFileTracingRoot: systemRoot,
  env: {
    NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE:
      process.env.NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE ?? process.env.PRISMA_CHART_LAB_PUBLIC_SAFE ?? "false",
    NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE:
      process.env.NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE ?? (staticExport ? "cloudflare-pages" : "local")
  },
  experimental: {
    externalDir: true
  },
  reactStrictMode: true,
  turbopack: {
    root: systemRoot
  },
  typedRoutes: false
};

export default nextConfig;
