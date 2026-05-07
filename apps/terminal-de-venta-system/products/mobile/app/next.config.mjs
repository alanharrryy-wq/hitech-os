import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const systemRoot = path.resolve(__dirname, "..", "..", "..");

/** @type {import('next').NextConfig} */
const nextConfig = {
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
