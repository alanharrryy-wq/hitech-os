import { PitchLayerDevToolsClientOnly } from "./pitch-layer-dev-tools-client-only";

export interface PitchDevConsoleMountProps {
  readonly visible: boolean;
}

export function PitchDevConsoleMount({ visible }: PitchDevConsoleMountProps) {
  return <PitchLayerDevToolsClientOnly visible={visible} />;
}
