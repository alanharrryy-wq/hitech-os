import { PRISMA_MOBILE_PWA_CONFIG_PATH, PrismaMobilePwaConfigSchema, type PrismaMobilePwaConfig } from "./prisma-mobile-pwa-contract";

export async function loadPrismaMobilePwaConfig(): Promise<PrismaMobilePwaConfig> {
  const response = await fetch(PRISMA_MOBILE_PWA_CONFIG_PATH, { cache: "no-store", headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`No se pudo leer ${PRISMA_MOBILE_PWA_CONFIG_PATH}: HTTP ${response.status}`);
  return PrismaMobilePwaConfigSchema.parse(await response.json());
}

export function isStandaloneDisplay(): boolean {
  if (typeof window === "undefined") return false;
  const displayModes = ["standalone", "fullscreen", "minimal-ui", "window-controls-overlay"];
  return displayModes.some((mode) => window.matchMedia?.(`(display-mode: ${mode})`).matches) || Boolean((window.navigator as Navigator & { standalone?: boolean }).standalone);
}

export function isSecurePwaContext(): boolean {
  if (typeof window === "undefined") return false;
  return window.isSecureContext || window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
}

export function getUserAgent(): string {
  if (typeof navigator === "undefined") return "";
  return navigator.userAgent || "";
}

export function isAndroidChrome(): boolean {
  const ua = getUserAgent();
  return /Android/i.test(ua) && /Chrome\//i.test(ua) && !/EdgA|OPR|SamsungBrowser|wv/i.test(ua);
}

export function isAndroidDevice(): boolean {
  return /Android/i.test(getUserAgent());
}

export function isIOSDevice(): boolean {
  const ua = getUserAgent();
  return /iPhone|iPad|iPod/i.test(ua) || (typeof navigator !== "undefined" && navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

export function isIOSSafari(): boolean {
  const ua = getUserAgent();
  return isIOSDevice() && /Safari/i.test(ua) && !/CriOS|FxiOS|EdgiOS|OPiOS|Instagram|FBAN|FBAV|WhatsApp/i.test(ua);
}

export function isWhatsAppWebView(): boolean {
  return /WhatsApp/i.test(getUserAgent());
}

export function isChromiumInstallCapable(): boolean {
  return isAndroidChrome() && isSecurePwaContext();
}

export function currentInstallUrl(): string {
  if (typeof window === "undefined") return "/prisma-app/install?from=whatsapp";
  const url = new URL("/prisma-app/install?from=whatsapp", window.location.origin);
  return url.toString();
}

export function currentAppUrl(): string {
  if (typeof window === "undefined") return "/prisma-app";
  return new URL("/prisma-app", window.location.origin).toString();
}

export function androidChromeIntentUrl(targetUrl: string): string {
  const url = new URL(targetUrl);
  const path = `${url.host}${url.pathname}${url.search}`;
  return `intent://${path}#Intent;scheme=${url.protocol.replace(":", "")};package=com.android.chrome;S.browser_fallback_url=${encodeURIComponent(targetUrl)};end`;
}

export function tryOpenAndroidChrome(targetUrl: string): void {
  if (typeof window === "undefined") return;
  window.location.href = androidChromeIntentUrl(targetUrl);
}

export async function copyText(value: string): Promise<boolean> {
  if (typeof navigator === "undefined" || !navigator.clipboard) return false;
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch (_error) {
    return false;
  }
}

export async function readServiceWorkerState(): Promise<string> {
  if (typeof navigator === "undefined" || !("serviceWorker" in navigator)) return "service-worker no soportado";
  const registration = await navigator.serviceWorker.getRegistration("/");
  if (!registration) return "sin service-worker activo";
  if (registration.active) return "service-worker activo";
  if (registration.installing) return "service-worker instalando";
  if (registration.waiting) return "service-worker en espera";
  return "service-worker registrado";
}
