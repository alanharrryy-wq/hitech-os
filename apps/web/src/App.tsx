import { useEffect, useMemo, useState } from "react";
import type { FeatureFlags, HealthReport } from "@hitech/contracts";
import { FEATURE_FLAGS_DEFAULTS } from "@hitech/contracts";
import {
  BrandPresenceLayer,
  HitechLogo,
  brandPresenceConfig,
  createBrandPresenceRootStyle
} from "@hitech/ui-kit";
import { getApiBaseUrl, getFeatureFlags, getHealth } from "./lib/api";
import { HealthPage } from "./pages/HealthPage";
import { HomePage } from "./pages/HomePage";

type RouteKey = "home" | "health";

function routeFromHash(hash: string): RouteKey {
  if (hash === "#health") {
    return "health";
  }

  return "home";
}

export function App() {
  const [route, setRoute] = useState<RouteKey>(() => routeFromHash(window.location.hash));
  const [flags, setFlags] = useState<FeatureFlags>(FEATURE_FLAGS_DEFAULTS);
  const [health, setHealth] = useState<HealthReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);
  const brandStyle = useMemo(() => createBrandPresenceRootStyle("neutral", "subtle"), []);

  useEffect(() => {
    const onHashChange = () => {
      setRoute(routeFromHash(window.location.hash));
    };

    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    let canceled = false;
    getFeatureFlags().then((resolvedFlags) => {
      if (!canceled) {
        setFlags(resolvedFlags);
      }
    });

    return () => {
      canceled = true;
    };
  }, []);

  const refreshHealth = async () => {
    setLoading(true);
    setError(null);

    try {
      const report = await getHealth();
      setHealth(report);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (route === "health") {
      void refreshHealth();
    }
  }, [route]);

  const page =
    route === "health" ? (
      <HealthPage
        flags={flags}
        health={health}
        loading={loading}
        error={error}
        onRefresh={() => void refreshHealth()}
        onBack={() => {
          window.location.hash = "#home";
        }}
      />
    ) : (
      <HomePage
        apiBaseUrl={apiBaseUrl}
        onOpenHealth={() => {
          window.location.hash = "#health";
        }}
      />
    );

  return (
    <div className="web-app-shell hitech-brand-shell-depth" style={brandStyle}>
      {brandPresenceConfig.enableGlobalWatermark ? (
        <BrandPresenceLayer
          mode="watermark"
          intensity="subtle"
          profile="neutral"
          repeatPattern
          className="web-brand-watermark"
        />
      ) : null}
      <header className="web-app-header">
        <div className="web-app-logo-wrap">
          {brandPresenceConfig.enableHeaderMark ? (
            <BrandPresenceLayer
              mode="header-mark"
              intensity="subtle"
              profile="neutral"
              className="web-header-mark"
            />
          ) : null}
          <HitechLogo className="web-app-logo" />
        </div>
      </header>
      <main className="web-app-main">{page}</main>
      {brandPresenceConfig.enableFooterSignature ? (
        <footer className="hitech-brand-signature web-app-signature">HITech - Deterministic Systems</footer>
      ) : null}
    </div>
  );
}
