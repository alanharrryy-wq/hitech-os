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
      hideCloseButton
      frameStyle={frameStyle}
      framePerfProfile={framePerfProfile}
      minWidth={300}
      minHeight={220}
      defaultState={{
        x: 16,
        y: 16,
        w: 360,
        h: 280,
        z: 1100,
        visible: true,
        collapsed: false
      }}
    >
      <ControlRoomToolbar />
    </FloatingWindow>
  );
}
