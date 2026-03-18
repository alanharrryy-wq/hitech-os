import { buildPreviewEnvelope, buildCommitEnvelope } from "./mutation-intents";
import { openPreviewSession, stageEnvelope } from "./preview-session";
import { createDefaultClock } from "./contracts";

export function createSceneLookScenario() {
  const clock = createDefaultClock(1000);
  const session = openPreviewSession({
    sceneId: "scene-home",
    baselineRevision: "baseline-001",
    draftRevision: "draft-001",
    clock
  });
  const envelope = buildPreviewEnvelope({
    source: "inspector",
    type: "scene-look-update",
    mode: "safe",
    target: { kind: "scene", sceneId: "scene-home" },
    payload: { "theme.primaryColor": "#0A84FF", "theme.background": "#101317" },
    clock
  });
  return {
    session: stageEnvelope(session, envelope, { "theme.primaryColor": "#0A84FF" }),
    previewEnvelope: envelope,
    commitEnvelope: buildCommitEnvelope({
      source: "inspector",
      type: "scene-look-update",
      mode: "safe",
      target: { kind: "scene", sceneId: "scene-home" },
      payload: { "theme.primaryColor": "#0A84FF", "theme.background": "#101317" },
      previewSessionId: session.sessionId,
      clock
    })
  };
}

export function createWidgetStyleScenario() {
  const clock = createDefaultClock(2000);
  const session = openPreviewSession({
    sceneId: "scene-dashboard",
    baselineRevision: "baseline-002",
    draftRevision: "draft-002",
    clock
  });
  const previewEnvelope = buildPreviewEnvelope({
    source: "canvas",
    type: "widget-style-update",
    mode: "safe",
    target: { kind: "widget", sceneId: "scene-dashboard", widgetId: "widget-kpi-1", slotId: "slot-kpi-main" },
    payload: { "style.fontSize": 42, "style.color": "#00CC88" },
    clock
  });
  return {
    session: stageEnvelope(session, previewEnvelope, { "style.fontSize": 42, "style.color": "#00CC88" }),
    previewEnvelope
  };
}
