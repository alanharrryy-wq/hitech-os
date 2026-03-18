import { bridgeRoutingAssertions } from "../bridge-routing-assertions";
if (!bridgeRoutingAssertions.every((item) => item.mustRouteThroughBridge)) throw new Error("bridge routing mismatch");
