"use client";

import { useEffect } from "react";

const ENABLE_DEV_SERVICE_WORKER = process.env.NEXT_PUBLIC_PRISMA_ENABLE_SW_DEV === "1";

function shouldRegisterPrismaMobileServiceWorker(): boolean {
  if (typeof window === "undefined") return false;
  if (process.env.NODE_ENV !== "production" && !ENABLE_DEV_SERVICE_WORKER) return false;
  if (!("serviceWorker" in navigator)) return false;
  return window.isSecureContext || window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
}

function silencePromise<T>(promise: Promise<T>): void {
  void promise.catch(() => {
    // PWA runtime failures must not trip the Next dev overlay.
  });
}

function unregisterPrismaMobileServiceWorkersInDev(): void {
  if (typeof window === "undefined") return;
  if (!("serviceWorker" in navigator)) return;
  if (process.env.NODE_ENV === "production" || ENABLE_DEV_SERVICE_WORKER) return;
  if (!("getRegistrations" in navigator.serviceWorker)) return;

  silencePromise(
    navigator.serviceWorker.getRegistrations().then((registrations) =>
      Promise.allSettled(
        registrations
          .filter((registration) => registration.active?.scriptURL.includes("/prisma-mobile-sw.js"))
          .map((registration) => registration.unregister())
      )
    )
  );
}

export function PrismaMobilePwaRuntime() {
  useEffect(() => {
    unregisterPrismaMobileServiceWorkersInDev();
    if (!shouldRegisterPrismaMobileServiceWorker()) return;

    let refreshing = false;
    const onControllerChange = () => {
      if (refreshing) return;
      refreshing = true;
      window.location.reload();
    };

    navigator.serviceWorker.addEventListener("controllerchange", onControllerChange);

    silencePromise(
      navigator.serviceWorker.register("/prisma-mobile-sw.js", { scope: "/" }).then((registration) => {
        silencePromise(registration.update());
        if (registration.waiting) {
          try {
            registration.waiting.postMessage({ type: "PRISMA_MOBILE_SKIP_WAITING" });
          } catch {
            // Ignore postMessage drift; installability should not break the dashboard.
          }
        }
      })
    );

    return () => {
      navigator.serviceWorker.removeEventListener("controllerchange", onControllerChange);
    };
  }, []);

  return null;
}
