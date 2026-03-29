import { mutationFlowMap } from "../mutation-flow-map";
if (mutationFlowMap[0] !== "selection") throw new Error("unexpected flow head");
if (mutationFlowMap[mutationFlowMap.length - 1] !== "runtime-facing-effect") throw new Error("unexpected flow tail");
