#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const read = (relativePath) => readFileSync(join(root, relativePath), "utf8");
const fail = (message) => {
  console.error(`[PRISMA APP MOBILE 26 FAIL] ${message}`);
  process.exit(1);
};
const mustInclude = (text, token, label) => {
  if (!text.includes(token)) fail(`${label} missing token: ${token}`);
};
const mustNotInclude = (text, token, label) => {
  if (text.includes(token)) fail(`${label} still contains unsafe token: ${token}`);
};

const runtime = read("src/components/prisma-app/PrismaMobilePwaRuntime.tsx");
const sw = read("public/prisma-mobile-sw.js");
const pwaCard = read("src/components/prisma-app/PrismaMobilePwaInstallCard.tsx");
const errorHelper = read("src/lib/prisma-app/prisma-mobile-error.ts");
const apiClient = read("src/lib/prisma-app/prisma-mobile-api-client.ts");
const httpClient = read("src/lib/prisma-app/mobile-data-plane/http.ts");

mustInclude(runtime, "process.env.NODE_ENV !== \"production\"", "PWA runtime dev guard");
mustInclude(runtime, "NEXT_PUBLIC_PRISMA_ENABLE_SW_DEV", "PWA runtime dev override");
mustInclude(runtime, "unregisterPrismaMobileServiceWorkersInDev", "PWA runtime unregister guard");
mustInclude(runtime, "silencePromise(registration.update())", "PWA runtime update catch");
mustInclude(runtime, "removeEventListener(\"controllerchange\"", "PWA runtime cleanup");

mustInclude(sw, "safeCachePut", "service worker cache guard");
mustInclude(sw, "offlineResponseFor", "service worker offline fallback");
mustInclude(sw, "v26-runtime-error-guard", "service worker version");
mustInclude(sw, "Promise.allSettled", "service worker install tolerance");
const unsafeCachePutMatches = [...sw.matchAll(/(?<!function safeCachePut[\s\S]{0,120})cache\.put\(/g)];
if (unsafeCachePutMatches.length > 0) fail(`service worker has raw cache.put calls: ${unsafeCachePutMatches.length}`);

mustInclude(pwaCard, "prismaMobileErrorMessage", "PWA install card error normalization");
mustInclude(pwaCard, "try {", "PWA install card guarded prompt");
mustInclude(pwaCard, "catch (error)", "PWA install card catch");

mustInclude(errorHelper, "JSON.stringify(error)", "error helper object stringify");
mustInclude(apiClient, "prismaMobileErrorMessage", "API client error normalization");
mustInclude(httpClient, "prismaMobileErrorMessage", "data-plane HTTP error normalization");
mustNotInclude(apiClient, "String(result.reason)", "API client object rejection guard");
mustNotInclude(httpClient, "String(error)", "data-plane HTTP object rejection guard");

console.log("OK PRISMA_APP_MOBILE_26_RUNTIME_ERROR_GUARD service worker/dev overlay guards verified");
