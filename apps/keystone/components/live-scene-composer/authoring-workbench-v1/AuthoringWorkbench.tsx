import { LiveSceneComposerProvider, useLiveSceneComposer } from "./LiveSceneComposerProvider";
import { CanvasSurface } from "./canvas/CanvasSurface";
import { DraftControlSurface } from "./draft/DraftControlSurface";
import { getSelectionLabel } from "./model/scene-graph";
import { InspectorPanel } from "./inspector/InspectorPanel";
import { StructureTree } from "./structure/StructureTree";
import type { ReactElement } from "react";
import type { SceneDocument } from "./authoring-workbench-contracts";

function AuthoringWorkbenchShell(): ReactElement {
  const composer = useLiveSceneComposer();
  return (
    <main style={{ display: "grid", gridTemplateColumns: "280px 1fr 320px", gap: 16, color: "#0f172a" }}>
      <aside style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <section style={{ padding: 12, borderRadius: 16, border: "1px solid rgba(148,163,184,0.3)" }}>
          <h2>Authoring Workbench v1</h2>
          <p>{getSelectionLabel(composer.state.documents.preview, composer.state.selection.primaryTarget)}</p>
          <small>Safe Mode default authority posture.</small>
        </section>
        <StructureTree />
      </aside>
      <section style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <CanvasSurface />
        <DraftControlSurface />
      </section>
      <aside>
        <InspectorPanel />
      </aside>
    </main>
  );
}

export interface AuthoringWorkbenchProps {
  readonly initialDocument?: SceneDocument;
}

export function AuthoringWorkbench(props: AuthoringWorkbenchProps): ReactElement {
  const providerProps = props.initialDocument
    ? { initialDocument: props.initialDocument }
    : {};

  return (
    <LiveSceneComposerProvider {...providerProps}>
      <AuthoringWorkbenchShell />
    </LiveSceneComposerProvider>
  );
}
