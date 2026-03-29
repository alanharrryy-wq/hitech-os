import { describeProbe } from "../repo-probes";
const value = describeProbe({ status: "unique", selected: "x", candidates: ["x"] });
if (!value.startsWith("unique:")) throw new Error("probe description mismatch");
