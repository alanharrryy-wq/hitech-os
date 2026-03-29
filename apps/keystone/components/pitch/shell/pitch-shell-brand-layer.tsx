"use client";

import {
  BrandPresenceLayer,
  createBrandPresenceRootStyle,
  useLayerFlags
} from "@hitech/ui-kit";

export function PitchShellBrandLayer() {
  const { resolved } = useLayerFlags();

  return (
    <div className="pitch-shell-brand-layer" style={createBrandPresenceRootStyle(resolved.profile, "subtle")}>
      <BrandPresenceLayer
        mode="watermark"
        intensity="subtle"
        profile={resolved.profile}
        repeatPattern
        className="pitch-shell-brand-watermark"
      />
    </div>
  );
}
