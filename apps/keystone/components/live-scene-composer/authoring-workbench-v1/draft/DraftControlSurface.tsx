import type { ReactElement } from "react";
import { useLiveSceneComposer } from "../LiveSceneComposerProvider";

export function DraftControlSurface(): ReactElement {
  const composer = useLiveSceneComposer();
  const latestFeedback = composer.state.feedback[0] ?? null;
  return (
    <section style={{ display: "flex", flexDirection: "column", gap: 8, border: "1px solid rgba(148,163,184,0.25)", borderRadius: 16, padding: 12 }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h3>Draft / Preview / Commit</h3>
          <small>Baseline revision {composer.state.documents.baseline.meta.revision} · Draft revision {composer.state.documents.draft.meta.revision}</small>
        </div>
        <strong>{composer.dirty ? "Draft dirty" : "Draft clean"}</strong>
      </header>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button onClick={() => composer.commitDraft()}>commit draft</button>
        <button onClick={() => composer.discardDraft()}>discard draft</button>
        <button onClick={() => composer.resetSelectedElement()}>reset selected</button>
        <button onClick={() => composer.clearFeedback()}>clear feedback</button>
      </div>
      {latestFeedback ? (
        <div style={{ padding: 10, borderRadius: 12, background: latestFeedback.level === "error" ? "rgba(239,68,68,0.10)" : "rgba(14,165,233,0.10)" }}>
          <strong>{latestFeedback.commandType}</strong>
          <div>{latestFeedback.message}</div>
          <small>code: {latestFeedback.code}</small>
        </div>
      ) : (
        <small>No bridge feedback yet.</small>
      )}
    </section>
  );
}
