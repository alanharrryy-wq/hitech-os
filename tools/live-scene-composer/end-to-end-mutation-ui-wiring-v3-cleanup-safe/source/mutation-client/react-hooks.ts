import * as React from "react";
import { type PreviewSession } from "./contracts";

export function usePreviewSessionState(initial: PreviewSession | null) {
  const [session, setSession] = React.useState<PreviewSession | null>(initial);
  const [lastAction, setLastAction] = React.useState<string>("idle");

  const updateSession = React.useCallback((next: PreviewSession | null, action: string) => {
    setSession(next);
    setLastAction(action);
  }, []);

  return {
    session,
    lastAction,
    updateSession
  };
}
