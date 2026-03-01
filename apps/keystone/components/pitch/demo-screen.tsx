"use client";

import { cn } from "@hitech/ui-kit";
import { useDemoScreens, useDemoState } from "../../lib/pitch/use-demo-state";
import { DemoControls } from "./demo-controls";
import { ScreenInventoryFoundation } from "./screen-inventory-foundation";
import { ScreenShipmentsReceiving } from "./screen-shipments-receiving";

export type PitchDemoScreenSlug = "05-inventory-foundation" | "06-shipments-receiving";

export interface PitchDemoScreenProps {
  readonly slug: PitchDemoScreenSlug;
  readonly className?: string;
}

export function PitchDemoScreen({ slug, className }: PitchDemoScreenProps) {
  const [state, actions] = useDemoState();
  const screens = useDemoScreens(state);

  return (
    <section className={cn("space-y-4", className)} aria-live="polite">
      <DemoControls state={state} actions={actions} />
      {slug === "05-inventory-foundation" ? (
        <ScreenInventoryFoundation screen={screens.inventoryFoundation} />
      ) : (
        <ScreenShipmentsReceiving screen={screens.shipmentsReceiving} />
      )}
    </section>
  );
}
