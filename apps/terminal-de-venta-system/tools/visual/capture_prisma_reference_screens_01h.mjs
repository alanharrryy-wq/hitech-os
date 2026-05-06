#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function argValue(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1) return fallback;
  return process.argv[index + 1] ?? fallback;
}

const outDir = path.resolve(argValue("--out", "F:/descargasf/prisma_reference_visual_01h_screenshots"));
const prismaAppUrl = argValue("--prisma-app-url", "http://127.0.0.1:3140/prisma-app");
const tabletUrl = argValue("--tablet-url", "http://127.0.0.1:3120/prisma-dark-pos-reference");
const pcUrl = argValue("--pc-url", "http://127.0.0.1:3130/dashboard");

async function main() {
  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch (error) {
    console.error("FAIL Playwright is not installed in this app workspace.");
    console.error("Install deps first, then run this script from the repo/tooling context.");
    process.exit(1);
  }

  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  try {
    const targets = [
      { name: "prisma-app", url: prismaAppUrl, viewport: { width: 430, height: 932 } },
      { name: "tablet", url: tabletUrl, viewport: { width: 1536, height: 1024 } },
      { name: "pc", url: pcUrl, viewport: { width: 1536, height: 1024 } }
    ];

    for (const target of targets) {
      const page = await browser.newPage({ viewport: target.viewport });
      await page.goto(target.url, { waitUntil: "networkidle", timeout: 45000 });
      await page.screenshot({ path: path.join(outDir, `${target.name}.png`), fullPage: true });
      await page.close();
      console.log(`OK captured ${target.name}: ${target.url}`);
    }
  } finally {
    await browser.close();
  }

  console.log(`OK screenshots saved to ${outDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
