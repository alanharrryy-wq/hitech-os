"use client";

import { useEffect } from "react";
import { useOptionalDevConsole } from "../DevConsoleContext";
import { DEV_CONSOLE_EVENT_CONTRACTS } from "./console-core-contracts";
import { getConsoleEventListenerCount } from "./console-core-events";
import { createConsoleCoreLogger } from "./console-core-logger";
import { isSceneLookModel } from "../look/scene-look-model";

const logger = createConsoleCoreLogger("RuntimeInvariants");
const RUNTIME_ASSERTION_INTERVAL_MS = 2000;

function assertInvariant(condition: boolean, message: string, metadata?: unknown): void {
  if (condition) {
    return;
  }
  logger.error(message, metadata);
  console.assert(condition, `[DevConsoleInvariant] ${message}`);
}

export function ConsoleCoreRuntimeInvariants() {
  const devConsole = useOptionalDevConsole();

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (!devConsole) {
      return;
    }

    const check = () => {
      const diagnostics = devConsole.diagnostics;
      if (diagnostics) {
        assertInvariant(diagnostics.route.startsWith("/"), "Diagnostics route must be absolute", diagnostics.route);
        assertInvariant(
          !Number.isNaN(Date.parse(diagnostics.timestamp)),
          "Diagnostics timestamp must be parseable",
          diagnostics.timestamp
        );
      }

      assertInvariant(
        isSceneLookModel(devConsole.sceneLookModel),
        "SceneLookModel must satisfy canonical schema",
        devConsole.sceneLookModel
      );

      for (const eventContract of DEV_CONSOLE_EVENT_CONTRACTS) {
        if (!eventContract.mustHaveListener) {
          continue;
        }
        const listeners = getConsoleEventListenerCount(eventContract.eventName);
        assertInvariant(
          listeners > 0,
          `Required event has no active listeners: ${eventContract.symbol}`,
          eventContract.eventName
        );
      }
    };

    const firstCheckTimer = window.setTimeout(check, 0);
    const timer = window.setInterval(check, RUNTIME_ASSERTION_INTERVAL_MS);
    return () => {
      window.clearTimeout(firstCheckTimer);
      window.clearInterval(timer);
    };
  }, [devConsole]);

  return null;
}
