/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    externalDir: true
  },
  transpilePackages: ["@hitech/ui-kit", "@hitech/contracts"]
};

export default nextConfig;
