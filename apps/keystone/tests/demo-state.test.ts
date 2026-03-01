import {
  canPerformReceivingAction,
  parseDemoStateFromSearchParams,
  resolveReceiveTransition
} from "../lib/pitch/demo-state";

describe("demo-state receiving guards", () => {
  it("role gating blocks auditor from performing receive action", () => {
    expect(canPerformReceivingAction("auditor")).toBe(false);

    const result = resolveReceiveTransition({
      role: "auditor",
      docsComplete: true,
      tempExcursion: false,
      supplierStatus: "APPROVED",
      currentState: "ARRIVED"
    });

    expect(result.allowed).toBe(false);
    expect(result.reason).toBe("ROLE_FORBIDDEN");
    expect(result.nextState).toBe("ARRIVED");
  });

  it("docsComplete=false forces DOCS_HOLD", () => {
    const result = resolveReceiveTransition({
      role: "operator",
      docsComplete: false,
      tempExcursion: false,
      supplierStatus: "APPROVED",
      currentState: "ARRIVED"
    });

    expect(result.allowed).toBe(false);
    expect(result.reason).toBe("DOCS_INCOMPLETE");
    expect(result.nextState).toBe("DOCS_HOLD");
  });

  it("docsComplete=true allows progression to RECEIVED when no other guards fail", () => {
    const result = resolveReceiveTransition({
      role: "operator",
      docsComplete: true,
      tempExcursion: false,
      supplierStatus: "APPROVED",
      currentState: "ARRIVED"
    });

    expect(result.allowed).toBe(true);
    expect(result.reason).toBe("OK");
    expect(result.nextState).toBe("RECEIVED");
  });

  it("tempExcursion=true forces QUARANTINE", () => {
    const result = resolveReceiveTransition({
      role: "operator",
      docsComplete: true,
      tempExcursion: true,
      supplierStatus: "APPROVED",
      currentState: "ARRIVED"
    });

    expect(result.allowed).toBe(false);
    expect(result.reason).toBe("TEMP_EXCURSION");
    expect(result.nextState).toBe("QUARANTINE");
  });

  it("supplierStatus=BLOCKED disables receiving", () => {
    const result = resolveReceiveTransition({
      role: "operator",
      docsComplete: true,
      tempExcursion: false,
      supplierStatus: "BLOCKED",
      currentState: "ARRIVED"
    });

    expect(result.allowed).toBe(false);
    expect(result.reason).toBe("SUPPLIER_BLOCKED");
    expect(result.nextState).toBe("DOCS_HOLD");
  });

  it("query param parsing normalizes demo state values", () => {
    const parsed = parseDemoStateFromSearchParams({
      role: "supervisor",
      docsComplete: "1",
      tempExcursion: "0",
      supplierStatus: "blocked"
    });

    expect(parsed).toEqual({
      role: "operator",
      docsComplete: true,
      tempExcursion: false,
      supplierStatus: "BLOCKED"
    });
  });
});
