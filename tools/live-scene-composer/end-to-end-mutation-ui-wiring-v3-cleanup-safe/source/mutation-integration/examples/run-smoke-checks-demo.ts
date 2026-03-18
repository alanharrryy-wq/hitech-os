import { evaluateSmokeChecks } from "../smoke-checks";

const result = evaluateSmokeChecks({
  docs: true,
  staging: true,
  mutationClientIndex: true,
  mutationIntegrationIndex: true
});

console.log(JSON.stringify(result, null, 2));
