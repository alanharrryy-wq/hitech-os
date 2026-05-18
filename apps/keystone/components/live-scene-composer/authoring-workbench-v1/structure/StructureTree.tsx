import type { ReactElement } from "react";
import { listStructureEntries } from "../model/scene-graph";
import { useLiveSceneComposer } from "../LiveSceneComposerProvider";

export function StructureTree(): ReactElement {
  const composer = useLiveSceneComposer();
  const entries = listStructureEntries(composer.state.documents.preview);
  const selectedId = composer.state.selection.primaryTarget?.id ?? null;
  return (
    <section style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <header>
        <h3>Structure</h3>
        <small>Scene → Layout → Slots → Widgets</small>
      </header>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {entries.map((entry) => (
          <div key={`${entry.kind}-${entry.id}`} style={{ display: "flex", alignItems: "center", gap: 6, marginLeft: entry.depth * 14 }}>
            <button
              onClick={() => composer.select(entry.selectionTarget, "structure")}
              style={{
                flex: 1,
                textAlign: "left",
                padding: "6px 10px",
                borderRadius: 12,
                border: selectedId === entry.id ? "1px solid #38bdf8" : "1px solid rgba(148,163,184,0.3)",
                background: selectedId === entry.id ? "rgba(56,189,248,0.14)" : "rgba(15,23,42,0.03)",
              }}
            >
              {entry.kind} · {entry.title}
            </button>
            {entry.kind === "layout-node" && entry.parentId ? (
              <>
                <button onClick={() => composer.reorderLayoutNode(entry.selectionTarget, Math.max(0, (composer.state.documents.preview.layoutNodes[entry.id]?.orderIndex ?? 0) - 1))}>↑</button>
                <button onClick={() => composer.reorderLayoutNode(entry.selectionTarget, (composer.state.documents.preview.layoutNodes[entry.id]?.orderIndex ?? 0) + 1)}>↓</button>
              </>
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}
