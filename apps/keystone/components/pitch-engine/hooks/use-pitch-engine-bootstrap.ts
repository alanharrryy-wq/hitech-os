"use client";

import { useEffect } from "react";
import {
  fetchArtifactRuns,
  fetchCapabilities,
  fetchOperatorStatus,
  fetchPrograms
} from "../api-client";
import { usePitchEngineStore } from "../state/use-pitch-engine-store";
import type { CapabilityMode } from "../types";

export function usePitchEngineBootstrap(requestedMode: CapabilityMode): void {
  const hydratePrograms = usePitchEngineStore((state) => state.hydratePrograms);
  const setArtifactRuns = usePitchEngineStore((state) => state.setArtifactRuns);
  const setOperatorHud = usePitchEngineStore((state) => state.setOperatorHud);
  const setUiError = usePitchEngineStore((state) => state.setUiError);
  const updateCapabilityMode = usePitchEngineStore((state) => state.updateCapabilityMode);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const [programs, capabilities, hud, runs] = await Promise.all([
          fetchPrograms(),
          fetchCapabilities(requestedMode),
          fetchOperatorStatus(),
          fetchArtifactRuns()
        ]);

        if (!active) {
          return;
        }

        hydratePrograms(programs);
        updateCapabilityMode(capabilities.requestedMode, {
          debug: capabilities.debugTokenPresent
        });
        setOperatorHud(hud);
        setArtifactRuns(runs);
        setUiError(null);
      } catch (error) {
        if (!active) {
          return;
        }

        setUiError(error instanceof Error ? error.message : "Failed to bootstrap pitch engine state");
      }
    };

    void run();

    const interval = window.setInterval(() => {
      void fetchOperatorStatus()
        .then((hud) => {
          if (active) {
            setOperatorHud(hud);
          }
        })
        .catch(() => {
          // Keep stale HUD status in case of fetch failures.
        });
    }, 8000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [
    hydratePrograms,
    requestedMode,
    setArtifactRuns,
    setOperatorHud,
    setUiError,
    updateCapabilityMode
  ]);
}
