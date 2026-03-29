import type { PitchScreen02 } from "@hitech/contracts";
import { Screen02IndustrialFlowCinematic } from "./screens/screen-02-industrial-flow-cinematic";

export interface ScreenIndustrialFlowProps {
  readonly screen: PitchScreen02;
}

export function ScreenIndustrialFlow({ screen: _screen }: ScreenIndustrialFlowProps) {
  return <Screen02IndustrialFlowCinematic />;
}
