import type { PitchScreen03 } from "@hitech/contracts";
import { Screen03HiTechOsCinematic } from "./screens/screen-03-hitech-os-cinematic";

export interface ScreenHiTechOsProps {
  readonly screen: PitchScreen03;
}

export function ScreenHiTechOs({ screen: _screen }: ScreenHiTechOsProps) {
  return <Screen03HiTechOsCinematic />;
}
