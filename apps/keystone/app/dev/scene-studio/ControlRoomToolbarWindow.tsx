"use client";

import { FloatingWindow } from "./FloatingWindow";
import { ControlRoomToolbar } from "./ControlRoomToolbar";

export function ControlRoomToolbarWindow() {
  return (
    <FloatingWindow
      id="control-room-toolbar"
      title="Control Room"
      hideCloseButton
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
