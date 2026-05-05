const PRISMA_MOBILE_SW_VERSION = "prisma-mobile-pwa-v30-install-landing-black-20260503";
const PRISMA_MOBILE_CACHE = `prisma-mobile-cache-${PRISMA_MOBILE_SW_VERSION}`;
const PRISMA_MOBILE_APP_SHELL = "/prisma-app";
const PRISMA_MOBILE_INSTALL = "/prisma-app/install";
const PRISMA_MOBILE_OFFLINE = "/prisma-offline.html";

const PRISMA_MOBILE_PRECACHE = [
  PRISMA_MOBILE_APP_SHELL,
  PRISMA_MOBILE_INSTALL,
  PRISMA_MOBILE_OFFLINE,
  "/manifest.webmanifest",
  "/prisma-mobile-pwa.config.json",
  "/apple-touch-icon.png",
  "/apple-touch-icon-precomposed.png",
  "/icons/prisma_ios_touch_icon_180.png",
  "/icons/prisma_playstore_icon_192.png",
  "/icons/prisma_playstore_icon_512.png",
  "/icons/prisma_whatsapp_install_icon.png",
  "/icons/prisma-app-icon.svg",
  "/icons/prisma-app-maskable.svg",
  "/icons/prisma-app-monochrome.svg",
  "/screenshots/prisma-mobile-pwa-dashboard.png"
];

async function safeCachePut(cache, request, response) {
  try {
    if (response && response.ok) await cache.put(request, response.clone());
  } catch (_error) {
    // CacheStorage can reject dev assets or unavailable optional files. Never let that become an unhandled rejection.
  }
}

function offlineResponseFor(request) {
  const url = new URL(request.url);
  if (url.pathname.startsWith("/api/mobile/")) {
    return new Response(JSON.stringify({ ok: false, error: "PRISMA App sin conexión o caché disponible." }), {
      status: 503,
      headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }
    });
  }
  return new Response("PRISMA App sin conexión.", { status: 503, headers: { "Content-Type": "text/plain; charset=utf-8" } });
}

async function cacheOne(cache, url) {
  try {
    const response = await fetch(url, { cache: "reload" });
    await safeCachePut(cache, url, response);
  } catch (_error) {
    // Optional assets should not block install. One missing screenshot should not sink the whole app.
  }
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(PRISMA_MOBILE_CACHE)
      .then((cache) => Promise.allSettled(PRISMA_MOBILE_PRECACHE.map((url) => cacheOne(cache, url))))
      .then(() => self.skipWaiting())
      .catch(() => undefined)
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key.startsWith("prisma-mobile-cache-") && key !== PRISMA_MOBILE_CACHE).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
      .catch(() => undefined)
  );
});

async function cacheFirst(request) {
  const cache = await caches.open(PRISMA_MOBILE_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  await safeCachePut(cache, request, response);
  return response;
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(PRISMA_MOBILE_CACHE);
  const cached = await cache.match(request);
  const network = fetch(request)
    .then(async (response) => {
      await safeCachePut(cache, request, response);
      return response;
    })
    .catch(() => cached || offlineResponseFor(request));
  return cached || network;
}

async function networkFirstNavigation(request) {
  const cache = await caches.open(PRISMA_MOBILE_CACHE);
  const url = new URL(request.url);
  try {
    const response = await fetch(request);
    await safeCachePut(cache, request, response);
    if (response && response.ok && url.pathname === PRISMA_MOBILE_APP_SHELL) {
      await safeCachePut(cache, PRISMA_MOBILE_APP_SHELL, response);
    }
    if (response && response.ok && url.pathname === PRISMA_MOBILE_INSTALL) {
      await safeCachePut(cache, PRISMA_MOBILE_INSTALL, response);
    }
    return response;
  } catch (_error) {
    return (await cache.match(request)) ||
      (await cache.match(url.pathname)) ||
      (await cache.match(PRISMA_MOBILE_APP_SHELL)) ||
      (await cache.match(PRISMA_MOBILE_OFFLINE)) ||
      offlineResponseFor(request);
  }
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(networkFirstNavigation(request));
    return;
  }

  if (url.pathname.startsWith("/api/mobile/")) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  if (
    url.pathname.startsWith("/_next/") ||
    url.pathname.startsWith("/icons/") ||
    url.pathname === "/apple-touch-icon.png" ||
    url.pathname === "/apple-touch-icon-precomposed.png" ||
    url.pathname.startsWith("/screenshots/") ||
    url.pathname === "/manifest.webmanifest" ||
    url.pathname === "/prisma-mobile-pwa.config.json" ||
    url.pathname === PRISMA_MOBILE_OFFLINE
  ) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  if (url.pathname === PRISMA_MOBILE_APP_SHELL || url.pathname === PRISMA_MOBILE_INSTALL || url.pathname.startsWith("/prisma-app/")) {
    event.respondWith(cacheFirst(request).catch(() => offlineResponseFor(request)));
  }
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "PRISMA_MOBILE_SKIP_WAITING") {
    if (typeof event.waitUntil === "function") {
      event.waitUntil(self.skipWaiting().catch(() => undefined));
    } else {
      void self.skipWaiting().catch(() => undefined);
    }
  }
});
