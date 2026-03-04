"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  SCENE_STUDIO_REQUEST_DIAGNOSTICS,
  isAllowedSceneStudioOrigin,
  isDiagnosticsResponseMessage,
  type SceneDiagnosticsPayload,
  type SceneRecord
} from "../../lib/scene-studio";
import styles from "./scene-studio.module.css";

const cls = (name: string): string => styles[name] ?? "";

function resolveViewportFrameSize(scene: SceneRecord): { width: string; minHeight: number } {
  if (scene.viewport.preset === "mobile") {
    return { width: "430px", minHeight: 760 };
  }

  if (scene.viewport.preset === "tablet") {
    return { width: "1024px", minHeight: 900 };
  }

  if (scene.viewport.preset === "custom") {
    return {
      width: `${scene.viewport.width ?? 1280}px`,
      minHeight: scene.viewport.height ?? 720
    };
  }

  return { width: "100%", minHeight: 760 };
}

export interface SceneStudioPreviewProps {
  readonly scene: SceneRecord | undefined;
  readonly compareScene: SceneRecord | undefined;
  readonly canonicalUrl: string;
  readonly compareCanonicalUrl: string | undefined;
  readonly onCopyCanonicalUrl: () => Promise<boolean>;
  readonly onDiagnostics: (payload: SceneDiagnosticsPayload | null) => void;
  readonly onRunVisual: () => Promise<void>;
}

export function SceneStudioPreview({
  scene,
  compareScene,
  canonicalUrl,
  compareCanonicalUrl,
  onCopyCanonicalUrl,
  onDiagnostics,
  onRunVisual
}: SceneStudioPreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement | null>(null);
  const [copyStatus, setCopyStatus] = useState<"idle" | "copied" | "failed">("idle");
  const [diagnosticsStatus, setDiagnosticsStatus] = useState<"idle" | "loading" | "ready" | "failed">("idle");

  const viewportFrame = useMemo(() => (scene ? resolveViewportFrameSize(scene) : null), [scene]);

  const requestDiagnostics = useCallback(() => {
    const iframeWindow = iframeRef.current?.contentWindow;
    if (!iframeWindow || !scene) {
      return;
    }

    const requestId = `${scene.id}:${Date.now()}`;
    setDiagnosticsStatus("loading");

    iframeWindow.postMessage(
      {
        type: SCENE_STUDIO_REQUEST_DIAGNOSTICS,
        requestId
      },
      window.location.origin
    );

    window.setTimeout(() => {
      setDiagnosticsStatus((previous) => (previous === "loading" ? "failed" : previous));
    }, 2500);
  }, [scene]);

  useEffect(() => {
    onDiagnostics(null);
    setDiagnosticsStatus("idle");
  }, [canonicalUrl, onDiagnostics]);

  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      if (!isAllowedSceneStudioOrigin(event.origin)) {
        return;
      }

      if (!isDiagnosticsResponseMessage(event.data)) {
        return;
      }

      setDiagnosticsStatus("ready");
      onDiagnostics(event.data.payload);
    };

    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [onDiagnostics]);

  if (!scene) {
    return <p className={cls("subtle")}>Select a scene to preview.</p>;
  }

  return (
    <div className={cls("previewWrap")}>
      <div className={cls("previewToolbar")}>
        <button type="button" className={cls("button")} onClick={() => window.open(canonicalUrl, "_blank")?.focus()}>
          Open Tab
        </button>
        <button
          type="button"
          className={cls("button")}
          onClick={async () => {
            const copied = await onCopyCanonicalUrl();
            setCopyStatus(copied ? "copied" : "failed");
            window.setTimeout(() => setCopyStatus("idle"), 1200);
          }}
        >
          {copyStatus === "copied" ? "Copied" : "Copy Canonical URL"}
        </button>
        <button type="button" className={cls("button")} onClick={requestDiagnostics}>
          Validate Scene
        </button>
        <button
          type="button"
          className={cls("button")}
          onClick={async () => {
            await onRunVisual();
          }}
        >
          Run Visual Test
        </button>
        <p className={cls("subtle")}>diagnostics={diagnosticsStatus}</p>
      </div>

      <div className={cls("compareGrid")}>
        <article className={cls("compareCard")}>
          <header className={cls("panelHeader")}>
            <h3 className={cls("panelTitle")}>Primary Scene</h3>
            <p className={cls("subtle")}>{scene.viewport.preset}</p>
          </header>
          <iframe
            ref={iframeRef}
            title="Scene preview"
            src={canonicalUrl}
            className={cls("compareFrame")}
            style={{ width: viewportFrame?.width ?? "100%", minHeight: viewportFrame?.minHeight ?? 760 }}
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          />
        </article>

        {compareScene && compareCanonicalUrl ? (
          <article className={cls("compareCard")}>
            <header className={cls("panelHeader")}>
              <h3 className={cls("panelTitle")}>Compare Scene</h3>
              <p className={cls("subtle")}>{compareScene.viewport.preset}</p>
            </header>
            <iframe
              title="Scene compare preview"
              src={compareCanonicalUrl}
              className={cls("compareFrame")}
              style={{ width: resolveViewportFrameSize(compareScene).width, minHeight: resolveViewportFrameSize(compareScene).minHeight }}
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            />
          </article>
        ) : (
          <article className={cls("compareCard")}>
            <header className={cls("panelHeader")}>
              <h3 className={cls("panelTitle")}>Compare Scene</h3>
            </header>
            <div className={cls("panelBody")}>
              <p className={cls("subtle")}>Select a second scene to compare side-by-side.</p>
            </div>
          </article>
        )}
      </div>
    </div>
  );
}




