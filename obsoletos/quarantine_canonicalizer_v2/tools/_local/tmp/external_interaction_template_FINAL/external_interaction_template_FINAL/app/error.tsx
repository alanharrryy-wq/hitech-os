"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { useEffect } from "react";

import { Button } from "@components/ui/button";
import { StatusPanel } from "@components/ui/status-panel";

export default function GlobalError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="grid min-h-[60vh] place-items-center px-4 py-10">
      <StatusPanel
        tone="danger"
        size="lg"
        icon={<AlertTriangle className="h-6 w-6" />}
        eyebrow="Runtime interruption"
        title="Something drifted off the happy path"
        description="The shell is still alive, but this route hit an unexpected error. You can retry safely without losing the whole workspace." 
        meta={error.digest ? `digest: ${error.digest}` : undefined}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button variant="primary" onClick={reset}>
              <RefreshCw className="mr-1.5 h-4 w-4" />
              Retry route
            </Button>
            <Button variant="ghost" onClick={() => window.location.assign("/")}>
              Go to launcher
            </Button>
          </div>
        }
      />
    </div>
  );
}
