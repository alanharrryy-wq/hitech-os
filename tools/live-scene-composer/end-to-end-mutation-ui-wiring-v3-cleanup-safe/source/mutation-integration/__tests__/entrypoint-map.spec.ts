import { getComposerEntrypointMap } from "../composer-entrypoint-map";
const map = getComposerEntrypointMap();
if (!map.canvas || !map["structure-tree"] || !map.inspector) throw new Error("missing entrypoint");
