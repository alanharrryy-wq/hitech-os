import { evaluateSmokeChecks } from "../smoke-checks";
const checks = evaluateSmokeChecks({ docs: true, staging: false });
if (checks.length !== 2) throw new Error("unexpected check count");
