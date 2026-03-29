import { safeModeAllows } from "../bridge-policy-assertions";
if (!safeModeAllows("draft-commit")) throw new Error("safe mode should allow commit workflow");
