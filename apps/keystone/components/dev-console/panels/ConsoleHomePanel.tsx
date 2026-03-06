"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

type CopyTarget = "" | "route" | "url";

type LocationSnapshot = {
  route: string;
  href: string;
  origin: string;
  protocol: string;
  host: string;
  hostname: string;
  port: string;
  search: string;
  hash: string;
  segmentCount: number;
  queryParamCount: number;
  isSecure: boolean;
  lastUpdated: string;
};

const DEFAULT_SNAPSHOT: Readonly<LocationSnapshot> = Object.freeze({
  route: "/",
  href: "",
  origin: "",
  protocol: "",
  host: "",
  hostname: "",
  port: "",
  search: "",
  hash: "",
  segmentCount: 0,
  queryParamCount: 0,
  isSecure: false,
  lastUpdated: "server",
});

function normalizePathname(pathname: string | null | undefined): string {
  if (!pathname || pathname.trim() === "") return "/";

  const withLeadingSlash = pathname.startsWith("/") ? pathname : `/${pathname}`;
  const collapsed = withLeadingSlash.replace(/\/{2,}/g, "/");

  return collapsed || "/";
}

function buildLocationSnapshot(): LocationSnapshot {
  if (typeof window === "undefined") {
    return { ...DEFAULT_SNAPSHOT };
  }

  const { location } = window;
  const route = normalizePathname(location.pathname);
  const search = location.search ?? "";
  const hash = location.hash ?? "";
  const queryParamCount = search ? new URLSearchParams(search).size : 0;

  return {
    route,
    href: location.href ?? "",
    origin: location.origin ?? "",
    protocol: location.protocol ?? "",
    host: location.host ?? "",
    hostname: location.hostname ?? "",
    port: location.port ?? "",
    search,
    hash,
    segmentCount: route.split("/").filter(Boolean).length,
    queryParamCount,
    isSecure: location.protocol === "https:",
    lastUpdated: new Date().toLocaleTimeString("en-US", {
      hour12: false,
    }),
  };
}

async function copyToClipboard(value: string): Promise<boolean> {
  if (!value || typeof navigator === "undefined" || !navigator.clipboard) {
    return false;
  }

  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch {
    return false;
  }
}

const actionButtonStyle: React.CSSProperties = {
  appearance: "none",
  border: "1px solid rgba(255,255,255,0.14)",
  background: "rgba(255,255,255,0.04)",
  color: "inherit",
  borderRadius: 10,
  padding: "8px 10px",
  fontSize: 12,
  lineHeight: 1.2,
  cursor: "pointer",
};

const mutedButtonStyle: React.CSSProperties = {
  ...actionButtonStyle,
  opacity: 0.72,
};

export function ConsoleHomePanel() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [snapshot, setSnapshot] = useState<LocationSnapshot>(DEFAULT_SNAPSHOT);
  const [isMounted, setIsMounted] = useState(false);
  const [copied, setCopied] = useState<CopyTarget>("");

  const refreshLocation = useCallback(() => {
    if (typeof window === "undefined") return;

    setSnapshot(buildLocationSnapshot());
    setIsMounted(true);
  }, []);

  useEffect(() => {
    refreshLocation();
  }, [refreshLocation, pathname, searchParams]);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleHashChange = () => refreshLocation();
    const handleFocus = () => refreshLocation();
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        refreshLocation();
      }
    };

    window.addEventListener("hashchange", handleHashChange);
    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.removeEventListener("hashchange", handleHashChange);
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [refreshLocation]);

  useEffect(() => {
    if (!copied || typeof window === "undefined") return;

    const timer = window.setTimeout(() => {
      setCopied("");
    }, 1400);

    return () => {
      window.clearTimeout(timer);
    };
  }, [copied]);

  const routeSegments = useMemo(() => {
    return snapshot.route.split("/").filter(Boolean);
  }, [snapshot.route]);

  const mountedRoute = isMounted ? snapshot.route : "/";
  const mountedHref = isMounted ? snapshot.href || "hydrating..." : "hydrating...";
  const mountedSearch = isMounted ? snapshot.search || "none" : "pending";
  const mountedHash = isMounted ? snapshot.hash || "none" : "pending";
  const mountedProtocol = isMounted ? snapshot.protocol || "unknown" : "pending";
  const mountedHost = isMounted ? snapshot.host || "unknown" : "pending";

  const syncLabel = isMounted
    ? `Live browser state synced at ${snapshot.lastUpdated}`
    : "Stable SSR shell loaded. Waiting for browser state...";

  const securityLabel = isMounted
    ? snapshot.isSecure
      ? "Secure"
      : "Insecure"
    : "Pending";

  const segmentLabel = routeSegments.length > 0 ? routeSegments.join(" / ") : "(root)";

  const handleCopy = useCallback(async (target: CopyTarget, value: string) => {
    if (!value) return;

    const ok = await copyToClipboard(value);
    setCopied(ok ? target : "");
  }, []);

  return (
    <div className={cls("card")} aria-live="polite">
      <div className={cls("cardTitle")}>Control Room</div>

      <div className={cls("cardHint")}>
        Single floating console, modular slots, persistent layout, and debug actions for every dev slide.{" "}
        {syncLabel}
      </div>

      <div className={cls("kvGrid")}>
        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Current Route</div>
          <div className={cls("kvValue")} title={mountedRoute}>
            {mountedRoute}
          </div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Current URL</div>
          <div className={cls("kvValue")} title={mountedHref}>
            {mountedHref}
          </div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Query String</div>
          <div className={cls("kvValue")} title={mountedSearch}>
            {mountedSearch}
          </div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Hash</div>
          <div className={cls("kvValue")} title={mountedHash}>
            {mountedHash}
          </div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Protocol</div>
          <div className={cls("kvValue")}>{mountedProtocol}</div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Host</div>
          <div className={cls("kvValue")} title={mountedHost}>
            {mountedHost}
          </div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Security</div>
          <div className={cls("kvValue")}>{securityLabel}</div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Hydration State</div>
          <div className={cls("kvValue")}>{isMounted ? "Client-synced" : "SSR shell"}</div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Path Segments</div>
          <div className={cls("kvValue")}>{snapshot.segmentCount}</div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Query Params</div>
          <div className={cls("kvValue")}>{snapshot.queryParamCount}</div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Floating Persistence</div>
          <div className={cls("kvValue")}>Enabled</div>
        </div>

        <div className={cls("kvItem")}>
          <div className={cls("kvLabel")}>Module Architecture</div>
          <div className={cls("kvValue")}>Registry-driven</div>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
          marginTop: 12,
          marginBottom: 12,
        }}
      >
        <button
          type="button"
          style={isMounted ? actionButtonStyle : mutedButtonStyle}
          onClick={() => void handleCopy("route", snapshot.route)}
          disabled={!isMounted}
          aria-label="Copy current route"
          title="Copy current route"
        >
          {copied === "route" ? "Route copied" : "Copy route"}
        </button>

        <button
          type="button"
          style={isMounted ? actionButtonStyle : mutedButtonStyle}
          onClick={() => void handleCopy("url", snapshot.href)}
          disabled={!isMounted}
          aria-label="Copy current url"
          title="Copy current url"
        >
          {copied === "url" ? "URL copied" : "Copy URL"}
        </button>

        <button
          type="button"
          style={isMounted ? actionButtonStyle : mutedButtonStyle}
          onClick={refreshLocation}
          disabled={!isMounted}
          aria-label="Refresh browser snapshot"
          title="Refresh browser snapshot"
        >
          Refresh snapshot
        </button>
      </div>

      <div className={cls("codeBox")}>
        {[
          "Slots ready for extension:",
          "- scene binding",
          "- runtime bridge",
          "- overlay tools",
          "- flags and actions",
          "- perf meter",
          "- layout profiles",
          "",
          "Live snapshot:",
          `- route: ${mountedRoute}`,
          `- segments: ${segmentLabel}`,
          `- query params: ${snapshot.queryParamCount}`,
          `- search: ${mountedSearch}`,
          `- hash: ${mountedHash}`,
          `- protocol: ${mountedProtocol}`,
          `- host: ${mountedHost}`,
          `- secure: ${securityLabel}`,
        ].join("\n")}
      </div>
    </div>
  );
}