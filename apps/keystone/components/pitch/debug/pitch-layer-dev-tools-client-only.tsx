import { InternalToolClientOnlyBoundary } from "../../internal-tooling/internal-tool-client-only-boundary";
import { PitchLayerDevTools, type PitchLayerDevToolsProps } from "./pitch-layer-dev-tools";

const TOOL_PANEL_NAME = "PitchLayerDevTools";

export function PitchLayerDevToolsClientOnly({ visible }: PitchLayerDevToolsProps) {
  return (
    <InternalToolClientOnlyBoundary componentName={TOOL_PANEL_NAME} enabled={visible}>
      <PitchLayerDevTools visible={visible} />
    </InternalToolClientOnlyBoundary>
  );
}
