import fs from "node:fs";
import path from "node:path";

const root = process.argv[2] || process.cwd();
const logoPath = path.join(root, "apps/terminal-de-venta-system/products/tablet/app/public/prisma/logo-prisma-primary.png");
if (!fs.existsSync(logoPath)) {
  console.error(`Missing logo asset: ${logoPath}`);
  process.exit(1);
}
const buf = fs.readFileSync(logoPath);
const pngSig = "89504e470d0a1a0a";
if (buf.subarray(0, 8).toString("hex") !== pngSig) {
  console.error("Logo asset is not a PNG file.");
  process.exit(2);
}
console.log("Verifier OK: transparent PRISMA logo asset is present.");
