/** @type {import('next').NextConfig} */
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const systemRoot = path.resolve(__dirname, "..", "..", "..");
const zeroIdleShadowDistDir = process.env.PRISMA_ZERO_IDLE_SHADOW_DIST_DIR?.trim();

const nextConfig = {
  isolatedDevBuild: true,
  ...(zeroIdleShadowDistDir ? { distDir: zeroIdleShadowDistDir } : {}),
  allowedDevOrigins: ["tablet.hitechrts.com", "127.0.0.1", "localhost"],
  outputFileTracingRoot: systemRoot,
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
