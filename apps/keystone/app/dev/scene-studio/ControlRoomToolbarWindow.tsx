"use client";

import { FloatingWindow } from "./FloatingWindow";
import { ControlRoomToolbar } from "./ControlRoomToolbar";

interface ControlRoomToolbarWindowProps {
  readonly frameStyle?: "LIQUID_GLASS" | "GOLD_NOIR_TERMINAL" | "GRAPHITE_PRISM_ISO";
  readonly framePerfProfile?: "quality" | "perf";
}

export function ControlRoomToolbarWindow({
  frameStyle = "GRAPHITE_PRISM_ISO",
  framePerfProfile = "quality"
}: ControlRoomToolbarWindowProps) {
  return (
    <FloatingWindow
      id="control-room-toolbar"
      title="Control Room"
      defaultPos={{ x: 16, y: 16 }}
      defaultSize={{ w: 360, h: 280 }}
    >
      <ControlRoomToolbar />
    </FloatingWindow>
  );
}
