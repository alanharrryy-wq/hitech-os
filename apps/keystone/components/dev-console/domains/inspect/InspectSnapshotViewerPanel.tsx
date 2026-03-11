"use client";

import { useMemo } from "react";
import { useDevConsole } from "../../DevConsoleContext";
import styles from "../../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

export function InspectSnapshotViewerPanel() {
  const { diagnostics, runtime, bridgeStatus, bridgeMeta, refreshDiagnostics } = useDevConsole();

  const digest = useMemo(
    () => ({
      bridgeStatus,
      bridgeMeta,
      runtime,
      diagnostics
    }),
    [bridgeMeta, bridgeStatus, diagnostics, runtime]
  );

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Snapshot viewer</div>
        <div className={cls("cardHint")}>
          Immutable view of the latest runtime snapshot payload and diagnostics metadata.
        </div>
        <div className={cls("topBarActions")}>
          <button type="button" className={cls("button")} onClick={() => refreshDiagnostics()}>
            Refresh diagnostics
          </button>
        </div>
      </section>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Snapshot payload</div>
        <pre className={cls("codeBox")}>{JSON.stringify(digest, null, 2)}</pre>
      </section>
    </div>
  );
}
