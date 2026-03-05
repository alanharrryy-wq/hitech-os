"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { SceneRecord } from "../../../lib/scene-studio";
import { FloatingSceneDock } from "../../../src/studio/FloatingSceneDock";
import { SceneStudioEditor } from "./SceneStudioEditor";

const DEFAULT_SCENE: SceneRecord = {
  id: "scene-studio-default",
  title: "Scene Studio Default",
  route: "/pitch/01-double-engine",
  tags: ["studio", "default"],
  mode: "single",
  layers: ["motion.enabled"]
};

export default function SceneStudioPage() {
  const [scene, setScene] = useState<SceneRecord>(DEFAULT_SCENE);

  const previewHref = useMemo(() => {
    const trimmed = scene.route.trim();
    if (!trimmed) return "/pitch";
    if (trimmed.startsWith("/")) return trimmed;
    return `/${trimmed}`;
  }, [scene.route]);

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "2rem 1.25rem",
        background:
          "radial-gradient(1200px 700px at 90% -10%, hsl(var(--ui-accent) / 0.14), transparent 55%), hsl(var(--ui-bg))"
      }}
    >
      <section
        style={{
          margin: "0 auto",
          maxWidth: 980,
          border: "1px solid hsl(var(--ui-border-1))",
          borderRadius: 20,
          padding: "1.25rem",
          background: "hsl(var(--ui-surface-1) / 0.82)",
          boxShadow: "var(--ui-shadow-2)"
        }}
      >
        <p className="keystone-kicker">Keystone</p>
        <h1 style={{ margin: "0.25rem 0 0", fontSize: "clamp(1.4rem, 3vw, 2rem)" }}>
          Scene Studio
        </h1>
        <p style={{ margin: "0.65rem 0 1.1rem", color: "hsl(var(--ui-text-2))" }}>
          Floating editor and quick scene navigation dock for Studio and Pitch routes.
        </p>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link
            href={previewHref}
            style={{
              display: "inline-flex",
              alignItems: "center",
              height: 38,
              padding: "0 12px",
              borderRadius: 12,
              border: "1px solid hsl(var(--ui-border-2))",
              background: "hsl(var(--ui-surface-2) / 0.85)",
              color: "hsl(var(--ui-text-1))",
              fontSize: 13,
              textDecoration: "none"
            }}
          >
            Open Active Route
          </Link>
          <code
            style={{
              border: "1px solid hsl(var(--ui-border-1))",
              borderRadius: 12,
              padding: "0.55rem 0.7rem",
              background: "hsl(var(--ui-surface-0) / 0.5)",
              fontSize: 12
            }}
          >
            {previewHref}
          </code>
        </div>
      </section>

      <SceneStudioEditor
        scene={scene}
        onChange={setScene}
        onResetToDefaults={() => setScene(DEFAULT_SCENE)}
      />
      <FloatingSceneDock />
    </main>
  );
}
