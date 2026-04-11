/** @type {import('next').NextConfig} */
// Next 16 expects hostnames (not full URLs) in allowedDevOrigins.
const allowedDevOrigins = [
  "localhost",
  "127.0.0.1",
  "192.168.1.13"
];

const nextConfig = {
  experimental: {
    externalDir: true
  },
  allowedDevOrigins
};

export default nextConfig;
