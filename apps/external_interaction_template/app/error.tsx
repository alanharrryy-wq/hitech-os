"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { useEffect } from "react";

import { Button } from "@components/ui/button";
import { StatusPanel } from "@components/ui/status-panel";

import { useT } from "@/lib/i18n/use-t";

export default function GlobalError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const t = useT();

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="grid min-h-[60vh] place-items-center px-4 py-10">
      <StatusPanel
        tone="danger"
        size="lg"
        icon={<AlertTriangle className="h-6 w-6" />}
        eyebrow={t("status.error.eyebrow")}
        title={t("status.error.title")}
        description={t("status.error.description")}
        meta={error.digest ? `digest: ${error.digest}` : undefined}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button variant="primary" onClick={reset}>
              <RefreshCw className="mr-1.5 h-4 w-4" />
              {t("status.error.retry")}
            </Button>
            <Button variant="ghost" onClick={() => window.location.assign("/")}>
              {t("status.error.goHome")}
            </Button>
          </div>
        }
      />
    </div>
  );
}
