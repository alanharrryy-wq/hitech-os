export function validateAnalysisModel(model){
  const errors = [];
  if(!model || typeof model !== 'object') errors.push('model is missing');
  if(!Array.isArray(model.records)) errors.push('records must be an array');
  if(!Array.isArray(model.cssRules)) errors.push('cssRules must be an array');
  if(!Array.isArray(model.panels)) errors.push('panels must be an array');
  if(!model.summary) errors.push('summary is required');
  if(model.policy){
    const requiredFalse = ['modifiedRepo','startedServers','killedProcesses','freedPorts','regeneratedPrisma','gitWrite'];
    for(const key of requiredFalse){ if(model.policy[key] !== false) errors.push(`policy.${key} must be false`); }
  }
  return { ok: errors.length === 0, errors };
}
export function assertValidAnalysisModel(model){
  const result = validateAnalysisModel(model);
  if(!result.ok) throw new Error(`Invalid Panel Locator model:\n${result.errors.join('\n')}`);
  return model;
}
