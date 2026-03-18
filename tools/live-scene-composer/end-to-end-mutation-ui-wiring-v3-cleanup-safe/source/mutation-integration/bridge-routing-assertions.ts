export interface BridgeRoutingAssertion {
  readonly mutationType: string;
  readonly mustRouteThroughBridge: true;
}

export const bridgeRoutingAssertions: readonly BridgeRoutingAssertion[] = [
  { mutationType: "scene-look-update", mustRouteThroughBridge: true },
  { mutationType: "layout-move", mustRouteThroughBridge: true },
  { mutationType: "widget-props-update", mustRouteThroughBridge: true },
  { mutationType: "draft-commit", mustRouteThroughBridge: true }
];
