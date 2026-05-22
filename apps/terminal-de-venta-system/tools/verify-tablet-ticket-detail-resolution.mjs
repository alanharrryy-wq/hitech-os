#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

function read(rel) {
  return fs.readFileSync(path.join(terminalRoot, rel), "utf8");
}

const route = read("products/tablet/app/app/api/pos/sales/detail/route.ts");
const resolver = read("products/tablet/app/src/server/pos-api/sales-detail.prisma.ts");
const screen = read("products/tablet/app/components/sales/sales-ticket-detail-screen.tsx");
const css = read("products/tablet/app/components/sales/sales.module.css");

const bannedBrowserTokens = [
  "from \"node:fs\"",
  "from \"fs\"",
  "better-sqlite3",
  "sqlite3",
  "new PrismaClient",
  "C:\\\\ProgramData",
];

const checks = [
  {
    name: "API route returns diagnostic on SALE_NOT_FOUND",
    status: route.includes("getSaleLookupDiagnostic") && route.includes("diagnostic") && route.includes("SALE_NOT_FOUND") ? "PASS" : "FAIL",
  },
  {
    name: "server resolver searches saleId folio clientRequestId aliases",
    status: resolver.includes("ticketNeedleWhere") && resolver.includes("clientRequestId") && resolver.includes("local_alias_fallback") ? "PASS" : "FAIL",
  },
  {
    name: "server diagnostic includes counts latest tickets and outbox",
    status: ["scopedTicketCount", "totalTicketCount", "latestTickets", "matchedOutboxEvents", "latestOutboxEvents"].every((token) => resolver.includes(token)) ? "PASS" : "FAIL",
  },
  {
    name: "diagnostic exposes server boundary paths",
    status: resolver.includes("serverAdapters") && resolver.includes("app/api/pos/sales/detail/route.ts") ? "PASS" : "FAIL",
  },
  {
    name: "UI renders ticket not found diagnostic from API details",
    status: screen.includes("TicketNotFoundDiagnostic") && screen.includes("data-prisma-ticket-resolution") && screen.includes("Últimos tickets locales") ? "PASS" : "FAIL",
  },
  {
    name: "browser component has no direct DB/license imports",
    status: bannedBrowserTokens.some((token) => screen.includes(token)) ? "FAIL" : "PASS",
  },
  {
    name: "diagnostic has responsive premium styles",
    status: css.includes(".diagnosticGrid") && css.includes(".diagnosticSection") && css.includes("data-prisma-skin=\"light\"") ? "PASS" : "FAIL",
  },
];

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, checks };
const files = reportPaths("PRISMA_TABLET_TICKET_DETAIL_RESOLUTION");
writeJson(files.json, report);
writeText(files.md, [
  "# PRISMA Tablet Ticket Detail Resolution Verify",
  "",
  `Overall: ${overall}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name}`)
].join("\n") + "\n");

console.log(`${overall} tablet ticket detail resolution report: ${files.md}`);
if (overall !== "PASS") process.exit(1);
