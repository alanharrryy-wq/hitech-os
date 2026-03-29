import type { PitchScreen01 } from "@hitech/contracts";
import { Screen01DoubleEngineCinematic } from "./screens/screen-01-double-engine-cinematic";

export interface ScreenDoubleEngineProps {
  readonly screen: PitchScreen01;
}

export function ScreenDoubleEngine({ screen: _screen }: ScreenDoubleEngineProps) {
  return <Screen01DoubleEngineCinematic />;
}
