import { InternalToolClientOnlyBoundary } from "../internal-tooling/internal-tool-client-only-boundary";
import { SceneStudioPage } from "./scene-studio-page";

const SCENE_STUDIO_PANEL_NAME = "SceneStudioPage";

export function SceneStudioPageClientOnly() {
  return (
    <InternalToolClientOnlyBoundary
      componentName={SCENE_STUDIO_PANEL_NAME}
      fallback={
        <section
          aria-live="polite"
          style={{
            padding: "1.25rem",
            fontSize: "0.88rem",
            color: "hsl(var(--ui-text-3))"
          }}
        >
          Loading Scene Studio client workspace...
        </section>
      }
    >
      <SceneStudioPage />
    </InternalToolClientOnlyBoundary>
  );
}

