import type { PitchScreen04 } from "@hitech/contracts";
import { Screen04ValuationCinematic } from "./screens/screen-04-valuation-cinematic";

export interface ScreenValuationProps {
  readonly screen: PitchScreen04;
}

export function ScreenValuation({ screen }: ScreenValuationProps) {
  return <Screen04ValuationCinematic screen={screen} />;
}
