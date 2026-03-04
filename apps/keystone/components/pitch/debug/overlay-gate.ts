export function isPitchDebugOverlayEnabled(): boolean {
  return process.env["NEXT_PUBLIC_PITCH_DEBUG"] === "1";
}
