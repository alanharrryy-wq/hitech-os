#!/usr/bin/env node
import fs from "node:fs";
import net from "node:net";
import path from "node:path";
import process from "node:process";
import { DatabaseSync } from "node:sqlite";
import { fileURLToPath } from "node:url";

const terminalRoot = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const checkedAt = new Date().toISOString();
const outPath = process.argv.find((arg) => arg.startsWith("--out="))?.slice("--out=".length) || "";

const services = {
  chartLab: { port: 3000, route: "/" },
  prismaWeb: { port: 3110, route: "/api/health" },
  tablet: { port: 3120, route: "/api/health" },
  pc: { port: 3130, route: "/api/health" },
  mobile: { port: 3140, route: "/" },
  controlCenter: { port: 3150, route: "/" },
  cloudCenter: { port: 3160, route: "/api/health" }
};

function rel(file) {
  return path.isAbsolute(file) ? file : path.join(terminalRoot, file);
}

function openDb(file) {
  return new DatabaseSync(rel(file), { readOnly: true });
}

function sqliteIso(value) {
  return value.toISOString().replace(".000Z", "Z");
}

function startOfLocalDay(day) {
  return new Date(`${day}T00:00:00`);
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function moneyLabelToCents(value) {
  const parsed = Number(String(value ?? "").replace(/[^\d.-]/g, ""));
  return Number.isFinite(parsed) ? Math.round(parsed * 100) : 0;
}

function numberLabel(value) {
  const parsed = Number(String(value ?? "").replace(/[^\d.-]/g, ""));
  return Number.isFinite(parsed) ? Math.trunc(parsed) : 0;
}

function check(condition, name, evidence) {
  return { name, status: condition ? "PASS" : "FAIL", evidence };
}

function cloudCenterHealthy(result) {
  const body = result.health.json ?? {};
  const cloudModule = Array.isArray(body.modules)
    ? body.modules.find((module) => module?.id === "cloud-saas")
    : null;
  return result.open
    && result.health.status === 200
    && Number(body.blockers ?? 0) === 0
    && (body.overall === "OK" || body.overall === "PARTIAL")
    && (!cloudModule || cloudModule.status === "CLOUD_LIVE" || cloudModule.http?.ok === true);
}

function jsonAt(value, pathSegments, fallback = null) {
  let current = value;
  for (const segment of pathSegments) {
    if (current == null || typeof current !== "object") return fallback;
    current = current[segment];
  }
  return current ?? fallback;
}

function sanitizeJson(json) {
  if (!json || typeof json !== "object") return json;
  if (Array.isArray(json.modules)) {
    return {
      ...json,
      modules: json.modules.map((module) => ({
        id: module?.id ?? null,
        name: module?.name ?? null,
        role: module?.role ?? null,
        port: module?.port ?? null,
        status: module?.status ?? null,
        directUrl: module?.directUrl ?? null,
        http: module?.http
          ? {
              ok: module.http.ok ?? null,
              statusCode: module.http.statusCode ?? null,
              service: module.http.service ?? null,
              version: module.http.version ?? null,
              error: module.http.error ?? null
            }
          : null
      }))
    };
  }
  return json;
}

async function portOpen(port) {
  return await new Promise((resolve) => {
    const socket = net.createConnection({ host: "127.0.0.1", port });
    const done = (ok) => {
      socket.removeAllListeners();
      socket.destroy();
      resolve(ok);
    };
    socket.setTimeout(1500);
    socket.once("connect", () => done(true));
    socket.once("timeout", () => done(false));
    socket.once("error", () => done(false));
  });
}

async function fetchJson(port, route, timeoutMs = 15000) {
  const url = `http://127.0.0.1:${port}${route}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { signal: controller.signal });
    const text = await response.text();
    let json = null;
    try {
      json = text ? JSON.parse(text) : null;
    } catch {
      json = { rawText: text.slice(0, 300) };
    }
    return { url, status: response.status, ok: response.ok, json: sanitizeJson(json) };
  } catch (error) {
    return { url, status: 0, ok: false, json: null, error: String(error?.message || error) };
  } finally {
    clearTimeout(timer);
  }
}

function salesScope(db) {
  const row = db.prepare(`
    SELECT businessId, substr(createdAt, 1, 10) AS day, COUNT(*) AS tickets, COALESCE(SUM(totalCents), 0) AS totalCents
      FROM Sale
     WHERE status IN ('PAID', 'COMPLETED')
     GROUP BY businessId, substr(createdAt, 1, 10)
     ORDER BY tickets DESC, day DESC
     LIMIT 1
  `).get();
  if (!row?.businessId || !row?.day) throw new Error("No operational sale scope found in local DB");
  const terminal = db.prepare(`
    SELECT terminalId, COUNT(*) AS tickets, COALESCE(SUM(totalCents), 0) AS totalCents
      FROM Sale
     WHERE businessId = ? AND substr(createdAt, 1, 10) = ? AND status IN ('PAID', 'COMPLETED')
     GROUP BY terminalId
     ORDER BY terminalId ASC
     LIMIT 1
  `).get(row.businessId, row.day);
  const store = db.prepare("SELECT id FROM Store WHERE businessId = ? ORDER BY id ASC LIMIT 1").get(row.businessId);
  return {
    businessId: String(row.businessId),
    date: String(row.day),
    terminalId: String(terminal?.terminalId ?? ""),
    storeId: String(store?.id ?? ""),
    tickets: Number(row.tickets ?? 0),
    totalCents: Number(row.totalCents ?? 0)
  };
}

function salesStats(db, input) {
  const from = startOfLocalDay(input.date);
  const toExclusive = addDays(from, 1);
  const terminalClause = input.terminalId ? " AND terminalId = ?" : "";
  const params = [input.businessId, sqliteIso(from), sqliteIso(toExclusive)];
  if (input.terminalId) params.push(input.terminalId);
  const row = db.prepare(`
    SELECT COUNT(*) AS tickets, COALESCE(SUM(totalCents), 0) AS totalCents
      FROM Sale
     WHERE businessId = ?
       AND status IN ('PAID', 'COMPLETED')
       AND createdAt >= ?
       AND createdAt < ?
       ${terminalClause}
  `).get(...params);
  return {
    tickets: Number(row?.tickets ?? 0),
    totalCents: Number(row?.totalCents ?? 0)
  };
}

function outboxCount(db, businessId) {
  return Number(db.prepare("SELECT COUNT(*) AS count FROM OutboxEvent WHERE businessId = ?").get(businessId)?.count ?? 0);
}

function businessIds(db) {
  return db.prepare("SELECT id FROM Business ORDER BY id").all().map((row) => String(row.id));
}

async function main() {
  const pcDb = openDb("products/pc/app/data/canonical.db");
  const tabletDb = openDb("products/tablet/app/data/tablet-pos.db");
  try {
    const scope = salesScope(pcDb);
    const tabletScope = salesScope(tabletDb);
    const allScope = { businessId: scope.businessId, date: scope.date };
    const terminalScope = { ...allScope, terminalId: scope.terminalId };
    const pcAll = salesStats(pcDb, allScope);
    const tabletAll = salesStats(tabletDb, allScope);
    const pcTerminal = salesStats(pcDb, terminalScope);
    const tabletTerminal = salesStats(tabletDb, terminalScope);
    const pcOutbox = outboxCount(pcDb, scope.businessId);
    const tabletOutbox = outboxCount(tabletDb, scope.businessId);

    const portChecks = {};
    for (const [name, service] of Object.entries(services)) {
      portChecks[name] = {
        port: service.port,
        open: await portOpen(service.port),
        health: await fetchJson(service.port, service.route)
      };
    }

    const query = new URLSearchParams({
      businessId: scope.businessId,
      date: scope.date
    });
    const terminalQuery = new URLSearchParams({
      businessId: scope.businessId,
      terminalId: scope.terminalId,
      date: scope.date
    });
    const outboxQuery = new URLSearchParams({
      businessId: scope.businessId,
      limit: "200"
    });
    const pcSalesQuery = new URLSearchParams({
      businessId: scope.businessId,
      preset: "custom",
      from: scope.date,
      to: scope.date
    });
    const catalogQuery = new URLSearchParams({
      businessId: scope.businessId,
      terminalId: scope.terminalId,
      storeId: scope.storeId,
      target: "tablet",
      mode: "bootstrap",
      limit: "20"
    });

    const tabletSalesAll = await fetchJson(3120, `/api/pos/sales/today?${query}`);
    const tabletSalesTerminal = await fetchJson(3120, `/api/pos/sales/today?${terminalQuery}`);
    const tabletOutboxRuntime = await fetchJson(3120, `/api/pos/events/outbox?${outboxQuery}`);
    const pcSalesControl = await fetchJson(3130, `/api/backoffice/sales-control?${pcSalesQuery}`);
    const pcCatalogDelta = await fetchJson(3130, `/api/sync/export/catalog-delta?${catalogQuery}`);
    const mobileSnapshot = await fetchJson(3140, `/api/mobile/snapshot?${terminalQuery}`);

    const tabletRuntimeAll = {
      tickets: Number(jsonAt(tabletSalesAll.json, ["data", "summary", "salesCount"], 0)),
      totalCents: Number(jsonAt(tabletSalesAll.json, ["data", "summary", "totalCents"], 0))
    };
    const tabletRuntimeTerminal = {
      tickets: Number(jsonAt(tabletSalesTerminal.json, ["data", "summary", "salesCount"], 0)),
      totalCents: Number(jsonAt(tabletSalesTerminal.json, ["data", "summary", "totalCents"], 0))
    };
    const pcRuntimeAll = {
      tickets: numberLabel(jsonAt(pcSalesControl.json, ["data", "salesControl", "ticketsLabel"], "0")),
      totalCents: moneyLabelToCents(jsonAt(pcSalesControl.json, ["data", "salesControl", "totalLabel"], "$0"))
    };
    const mobileRuntimeTerminal = {
      tickets: Number(jsonAt(mobileSnapshot.json, ["data", "salesToday", "tickets"], 0)),
      totalCents: Number(jsonAt(mobileSnapshot.json, ["data", "salesToday", "totalSalesCents"], 0)),
      runtimeMode: jsonAt(mobileSnapshot.json, ["meta", "runtimeMode"], null),
      source: jsonAt(mobileSnapshot.json, ["meta", "source"], null),
      pcProbeOk: Boolean((jsonAt(mobileSnapshot.json, ["meta", "upstreams"], []) || []).some((probe) => probe?.id === "pc" && probe?.ok === true)),
      tabletProbeOk: Boolean((jsonAt(mobileSnapshot.json, ["meta", "upstreams"], []) || []).some((probe) => probe?.id === "tablet" && probe?.ok === true))
    };

    const checks = [
      check(JSON.stringify(businessIds(pcDb)) === JSON.stringify(businessIds(tabletDb)), "PC and Tablet expose the same business ids", { pc: businessIds(pcDb), tablet: businessIds(tabletDb) }),
      check(scope.businessId === tabletScope.businessId && scope.date === tabletScope.date, "PC and Tablet resolve the same operational business/date scope", { pc: scope, tablet: tabletScope }),
      check(pcAll.tickets === tabletAll.tickets && pcAll.totalCents === tabletAll.totalCents, "PC and Tablet DB sales match for operational date", { pcAll, tabletAll }),
      check(pcTerminal.tickets === tabletTerminal.tickets && pcTerminal.totalCents === tabletTerminal.totalCents, "PC and Tablet DB sales match for registered terminal", { pcTerminal, tabletTerminal }),
      check(pcOutbox === tabletOutbox, "PC and Tablet outbox rows match for business", { pcOutbox, tabletOutbox }),
      check(portChecks.prismaWeb.open && portChecks.prismaWeb.health.status === 200, "PRISMA Web 3110 health is reachable", portChecks.prismaWeb),
      check(portChecks.tablet.open && portChecks.tablet.health.status === 200, "Tablet 3120 health is reachable", portChecks.tablet),
      check(portChecks.pc.open && portChecks.pc.health.status === 200, "PC 3130 health is reachable", portChecks.pc),
      check(portChecks.mobile.open && portChecks.mobile.health.status === 200, "Mobile 3140 app is reachable", portChecks.mobile),
      check(cloudCenterHealthy(portChecks.cloudCenter), "Cloud Center 3160 local health has no blockers and Cloud module is live", portChecks.cloudCenter),
      check(tabletRuntimeAll.tickets === tabletAll.tickets && tabletRuntimeAll.totalCents === tabletAll.totalCents, "Tablet runtime reads the same all-terminal sales as Tablet DB", { tabletRuntimeAll, tabletAll, route: tabletSalesAll.url }),
      check(tabletRuntimeTerminal.tickets === tabletTerminal.tickets && tabletRuntimeTerminal.totalCents === tabletTerminal.totalCents, "Tablet runtime reads the same terminal sales as Tablet DB", { tabletRuntimeTerminal, tabletTerminal, route: tabletSalesTerminal.url }),
      check(Number(jsonAt(tabletOutboxRuntime.json, ["data", "count"], 0)) === tabletOutbox, "Tablet runtime outbox count matches Tablet DB", { routeCount: jsonAt(tabletOutboxRuntime.json, ["data", "count"], 0), tabletOutbox }),
      check(pcRuntimeAll.tickets === pcAll.tickets && pcRuntimeAll.totalCents === pcAll.totalCents, "PC runtime sales-control reads the same sales as PC DB", { pcRuntimeAll, pcAll, route: pcSalesControl.url }),
      check(pcCatalogDelta.status === 200 && pcCatalogDelta.json?.ok === true && pcCatalogDelta.json?.data?.businessId === scope.businessId, "PC catalog delta export is reachable for the same business", { status: pcCatalogDelta.status, count: pcCatalogDelta.json?.data?.counts?.total ?? null, businessId: pcCatalogDelta.json?.data?.businessId ?? null }),
      check(mobileRuntimeTerminal.tickets === tabletRuntimeTerminal.tickets && mobileRuntimeTerminal.totalCents === tabletRuntimeTerminal.totalCents, "Mobile snapshot reads the same terminal sales as Tablet runtime", { mobileRuntimeTerminal, tabletRuntimeTerminal, route: mobileSnapshot.url }),
      check(mobileRuntimeTerminal.tabletProbeOk && mobileRuntimeTerminal.pcProbeOk, "Mobile snapshot reaches Tablet and PC upstreams", mobileRuntimeTerminal)
    ];

    const payload = {
      ok: checks.every((item) => item.status === "PASS"),
      status: checks.every((item) => item.status === "PASS") ? "PASS_LOCAL_RUNTIME_READONLY" : "FAIL",
      checkedAt,
      scope,
      readOnly: true,
      mutationsPerformed: false,
      db: {
        pc: "products/pc/app/data/canonical.db",
        tablet: "products/tablet/app/data/tablet-pos.db",
        pcAll,
        tabletAll,
        pcTerminal,
        tabletTerminal,
        pcOutbox,
        tabletOutbox
      },
      runtime: {
        ports: portChecks,
        tabletRuntimeAll,
        tabletRuntimeTerminal,
        pcRuntimeAll,
        mobileRuntimeTerminal
      },
      checks,
      failures: checks.filter((item) => item.status === "FAIL")
    };

    if (outPath) {
      const absoluteOut = rel(outPath);
      fs.mkdirSync(path.dirname(absoluteOut), { recursive: true });
      fs.writeFileSync(absoluteOut, `${JSON.stringify(payload, null, 2)}\n`);
    }

    console.log(JSON.stringify(payload, null, 2));
    if (!payload.ok) process.exit(1);
  } finally {
    pcDb.close();
    tabletDb.close();
  }
}

main().catch((error) => {
  console.error(JSON.stringify({
    ok: false,
    status: "FAIL",
    checkedAt,
    readOnly: true,
    mutationsPerformed: false,
    error: String(error?.message || error)
  }, null, 2));
  process.exit(1);
});
