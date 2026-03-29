"use client";

import { useEffect } from "react";
import { useOptionalDevConsole } from "../../dev-console/DevConsoleContext";
import { applySceneLookModelToElement } from "../../dev-console/look/scene-look-model";
import { dispatchConsoleEvent } from "../../dev-console/console-core/console-core-events";
import { DEV_CONSOLE_SCENE_LOOK_MODEL_EVENT } from "../../dev-console/dev-console-events";

function applyToPitchRoots() {
  return Array.from(document.querySelectorAll<HTMLElement>(".pitch-shell-root"));
}

export function PitchSceneLookRuntime() {
  const devConsole = useOptionalDevConsole();
  const sceneLookModel = devConsole?.sceneLookModel;

  useEffect(() => {
    if (!sceneLookModel) {
      return;
    }
    if (typeof document === "undefined") {
      return;
    }

    applySceneLookModelToElement(document.documentElement, sceneLookModel);
    for (const root of applyToPitchRoots()) {
      applySceneLookModelToElement(root, sceneLookModel);
    }

    dispatchConsoleEvent(DEV_CONSOLE_SCENE_LOOK_MODEL_EVENT, {
      model: sceneLookModel,
      timestamp: new Date().toISOString()
    });
  }, [sceneLookModel]);

  return null;
}
