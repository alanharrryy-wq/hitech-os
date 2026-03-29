"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  buildCanonicalSceneUrl,
  buildCanonicalSceneQuery,
  parseSceneQueryToObject,
  type SceneRecord
} from "../../lib/scene-studio";
import { DevConsoleSceneStudioBinding } from "../dev-console/DevConsoleContext";
import styles from "./scene-studio.module.css";
import { SceneStudioPreview } from "./scene-studio-preview";
import { useSceneStudioHotkeys } from "./use-scene-studio-hotkeys";
import { useSceneStudioState } from "./use-scene-studio-state";

const cls = (name: string): string => styles[name] ?? "";

function syncSceneQuery(scene: SceneRecord): SceneRecord {
  const query = buildCanonicalSceneQuery({
    route: scene.route,
    query: scene.query,
    layerProfile: scene.layerProfile,
    layersMode: scene.layers.mode,
    layerIds: scene.layers.layerIds,
    motion: scene.motion,
    debug: true
  });

  return {
    ...scene,
    query,
    updatedAt: new Date().toISOString()
  };
}

async function copyTextToClipboard(text: string): Promise<boolean> {
  if (typeof navigator !== "undefined" && navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  }

  if (typeof document === "undefined") {
    return false;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();

  const copied = document.execCommand("copy");
  textarea.remove();
  return copied;
}

function BackdropCard({
  title,
  value,
  wide = false
}: {
  title: string;
  value: string;
  wide?: boolean;
}) {
  return (
    <div
      style={{
        minWidth: wide ? "min(420px, 100%)" : "180px",
        flex: wide ? "1 1 420px" : "0 1 auto",
        borderRadius: 18,
        border: "1px solid rgba(2, 167, 202, 0.22)",
        background: "linear-gradient(180deg, rgba(6, 14, 22, 0.82), rgba(6, 14, 22, 0.62))",
        boxShadow: "0 12px 40px rgba(0, 0, 0, 0.22)",
        padding: "14px 16px"
      }}
    >
      <div
        style={{
          color: "rgba(171, 123, 38, 0.95)",
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: "0.16em",
          marginBottom: 8,
          textTransform: "uppercase"
        }}
      >
        {title}
      </div>

      <div
        style={{
          color: "rgba(226, 247, 255, 0.95)",
          fontSize: wide ? 14 : 13,
          lineHeight: 1.45,
          wordBreak: "break-word"
        }}
      >
        {value}
      </div>
    </div>
  );
}

function BrandedBackdrop({
  sceneTitle,
  canonicalUrl,
  statusLine
}: {
  sceneTitle: string;
  canonicalUrl: string;
  statusLine: string;
}) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "grid",
        placeItems: "center",
        padding: "32px"
      }}
    >
      <div
        style={{
          width: "min(1200px, 94vw)",
          borderRadius: 32,
          overflow: "hidden",
          border: "1px solid rgba(2, 167, 202, 0.18)",
          background: [
            "radial-gradient(circle at top left, rgba(171, 123, 38, 0.16), transparent 28%)",
            "radial-gradient(circle at top right, rgba(2, 167, 202, 0.16), transparent 30%)",
            "linear-gradient(160deg, rgba(3, 9, 15, 0.92), rgba(9, 20, 29, 0.82))"
          ].join(", "),
          boxShadow: "0 28px 120px rgba(0, 0, 0, 0.42)"
        }}
      >
        <div
          style={{
            padding: "56px 56px 28px",
            borderBottom: "1px solid rgba(2, 167, 202, 0.12)"
          }}
        >
          <div
            style={{
              color: "rgba(171, 123, 38, 0.95)",
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: "0.28em",
              marginBottom: 14,
              textTransform: "uppercase"
            }}
          >
            Hitech · Scene Studio
          </div>

          <h1
            style={{
              color: "#f3fbff",
              fontSize: "clamp(34px, 5vw, 64px)",
              lineHeight: 1.04,
              margin: 0,
              maxWidth: "12ch"
            }}
          >
            Floating-only mode with a live stage behind the console.
          </h1>

          <p
            style={{
              color: "rgba(206, 235, 244, 0.82)",
              fontSize: 16,
              lineHeight: 1.65,
              margin: "18px 0 0",
              maxWidth: "72ch"
            }}
          >
            La consola flotante se queda con el volante. El escenario vive atrás como stage pasivo,
            sin shell incrustado y sin doble HUD.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 16,
            padding: "28px 32px 32px"
          }}
        >
          <BackdropCard title="Current scene" value={sceneTitle} />
          <BackdropCard title="Workspace mode" value="Floating console only" />
          <BackdropCard title="Status" value={statusLine} />
          <BackdropCard
            title="Canonical URL"
            value={canonicalUrl || "Waiting for a selected scene to generate a canonical URL."}
            wide
          />
        </div>
      </div>
    </div>
  );
}

export function SceneStudioPage() {
  const {
    draftScene,
    updateDraft,
    saveDraft,
    createScene,
    resetSelectedSceneToDefaults
  } = useSceneStudioState();

  const [statusLine, setStatusLine] = useState<string>("ready");
  const backgroundRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const node = backgroundRef.current;
    if (!node) {
      return;
    }

    node.setAttribute("inert", "");

    return () => {
      node.removeAttribute("inert");
    };
  }, []);

  const normalizedDraft = useMemo(() => (draftScene ? syncSceneQuery(draftScene) : undefined), [draftScene]);

  const canonicalUrl = useMemo(() => {
    if (!normalizedDraft) {
      return "";
    }

    return buildCanonicalSceneUrl({
      route: normalizedDraft.route,
      query: normalizedDraft.query,
      layerProfile: normalizedDraft.layerProfile,
      layersMode: normalizedDraft.layers.mode,
      layerIds: normalizedDraft.layers.layerIds,
      motion: normalizedDraft.motion,
      debug: true
    });
  }, [normalizedDraft]);

  const runVisualForSelection = async (): Promise<void> => {
    if (!normalizedDraft) {
      setStatusLine("no scene selected");
      return;
    }

    setStatusLine(`running visual test for ${normalizedDraft.id}...`);

    try {
      const response = await fetch("/api/scene-studio/run?debug=1", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          sceneIds: [normalizedDraft.id],
          mode: "smoke"
        })
      });

      if (!response.ok) {
        const details = await response.text();
        setStatusLine(`visual run failed: ${details.slice(0, 140)}`);
        return;
      }

      const payload = (await response.json()) as {
        command: string;
        exitCode: number;
        artifactRoot?: string;
      };

      if (payload.exitCode === 0) {
        setStatusLine(`visual run complete: ${payload.artifactRoot ?? "artifacts generated"}`);
      } else {
        setStatusLine(`visual run exited with code ${payload.exitCode}`);
      }
    } catch (error) {
      setStatusLine(error instanceof Error ? error.message : "visual run request failed");
    }
  };

  const handlePassiveCopyCanonicalUrl = async (): Promise<boolean> => {
    if (!canonicalUrl) {
      setStatusLine("no scene selected");
      return false;
    }

    const copied = await copyTextToClipboard(canonicalUrl);
    setStatusLine(copied ? "canonical URL copied" : "copy failed");
    return copied;
  };

  useSceneStudioHotkeys({
    onFocusSearch: () => {},
    onNewScene: () => {
      createScene();
      setStatusLine("new scene created");
    },
    onSaveScene: () => {
      const saved = saveDraft();
      setStatusLine(saved ? `saved ${saved.id}` : "nothing to save");
    },
    onCopyUrl: () => {
      void handlePassiveCopyCanonicalUrl();
    },
    onRunVisual: () => {
      void runVisualForSelection();
    }
  });

  const handleSceneChange = (next: SceneRecord) => {
    const queryObject = parseSceneQueryToObject(next.query);
    const refreshed = syncSceneQuery({
      ...next,
      query: buildCanonicalSceneQuery({
        route: next.route,
        query: queryObject,
        layerProfile: next.layerProfile,
        layersMode: next.layers.mode,
        layerIds: next.layers.layerIds,
        motion: next.motion,
        debug: true
      })
    });

    updateDraft(refreshed);
  };

  return (
    <section
      className={cls("root")}
      style={{
        position: "relative",
        minHeight: "calc(100dvh - 4.5rem)",
        overflow: "hidden",
        isolation: "isolate"
      }}
    >
      <DevConsoleSceneStudioBinding
        scene={normalizedDraft}
        onChange={handleSceneChange}
        onResetToDefaults={resetSelectedSceneToDefaults}
      />

      <div
        ref={backgroundRef}
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 0,
          pointerEvents: "none",
          userSelect: "none"
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(180deg, rgba(4, 10, 16, 0.08), rgba(4, 10, 16, 0.34))"
          }}
        />

        {normalizedDraft ? (
          <>
            <div
              style={{
                position: "absolute",
                inset: "clamp(20px, 4vw, 48px)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }}
            >
              <div
                style={{
                  width: "min(1480px, 94vw)",
                  maxWidth: "100%",
                  borderRadius: 28,
                  overflow: "hidden",
                  border: "1px solid rgba(2, 167, 202, 0.16)",
                  background: "rgba(2, 7, 11, 0.72)",
                  boxShadow: "0 36px 120px rgba(0, 0, 0, 0.46)",
                  opacity: 0.9,
                  filter: "saturate(0.92) contrast(0.94) brightness(0.92)"
                }}
              >
                <SceneStudioPreview
                  scene={normalizedDraft}
                  compareScene={undefined}
                  canonicalUrl={canonicalUrl}
                  compareCanonicalUrl={undefined}
                  onCopyCanonicalUrl={handlePassiveCopyCanonicalUrl}
                  onDiagnostics={() => {}}
                  onRunVisual={runVisualForSelection}
                  passive
                />
              </div>
            </div>

            <div
              style={{
                position: "absolute",
                inset: 0,
                background: [
                  "linear-gradient(180deg, rgba(5, 8, 12, 0.18) 0%, rgba(5, 8, 12, 0.08) 16%, rgba(5, 8, 12, 0.34) 100%)",
                  "radial-gradient(circle at 50% 50%, transparent 0%, rgba(5, 8, 12, 0.08) 52%, rgba(5, 8, 12, 0.42) 100%)"
                ].join(", ")
              }}
            />
          </>
        ) : (
          <BrandedBackdrop
            sceneTitle="No scene selected"
            canonicalUrl={canonicalUrl}
            statusLine={statusLine}
          />
        )}
      </div>

      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          left: 20,
          right: 20,
          bottom: 18,
          zIndex: 1,
          display: "flex",
          flexWrap: "wrap",
          gap: 10,
          pointerEvents: "none"
        }}
      >
        {[
          "floating-only",
          normalizedDraft ? "live passive stage" : "branded backdrop",
          normalizedDraft ? normalizedDraft.title : "no scene selected",
          statusLine
        ].map((label) => (
          <span
            key={label}
            style={{
              borderRadius: 999,
              border: "1px solid rgba(2, 167, 202, 0.18)",
              background: "rgba(5, 11, 17, 0.58)",
              boxShadow: "0 8px 30px rgba(0, 0, 0, 0.18)",
              color: "rgba(228, 247, 255, 0.88)",
              fontSize: 12,
              lineHeight: 1,
              padding: "10px 12px",
              backdropFilter: "blur(10px)"
            }}
          >
            {label}
          </span>
        ))}
      </div>
    </section>
  );
}