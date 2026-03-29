import { type VerificationReport } from "../contracts";
const report: VerificationReport | null = null;
if (report !== null) throw new Error("expected null in placeholder test");
