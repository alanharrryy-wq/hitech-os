export interface UiSessionState {
  readonly sessionId: string;
  readonly openedAtUtc: string;
  readonly surfaceVisitOrder: readonly string[];
}

export function openUiSession(surface: string): UiSessionState {
  const at = new Date().toISOString();
  return { sessionId: `ui-session-${Date.now()}`, openedAtUtc: at, surfaceVisitOrder: [surface] };
}

export function recordSurfaceVisit(session: UiSessionState, surface: string): UiSessionState {
  return { ...session, surfaceVisitOrder: [...session.surfaceVisitOrder, surface] };
}
