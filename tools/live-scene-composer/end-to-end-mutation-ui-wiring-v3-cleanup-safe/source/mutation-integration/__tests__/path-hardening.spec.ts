import { normalizePathLike } from "../path-hardening";
if (normalizePathLike({ Path: "C:/demo" }) !== "C:/demo") throw new Error("path normalization failed");
