'use strict';

const REAL_RUNTIME_DISABLED_BASELINE = 'REAL_RUNTIME_DISABLED_BASELINE';

function classifyBaseline(snapshot, beforePseudo) {
  if (snapshot.disabled) {
    return {
      state: 'disabled',
      status: REAL_RUNTIME_DISABLED_BASELINE,
      evidenceRole: 'runtime-baseline',
      certifiesEnabledNormal: false,
      snapshot,
      beforePseudo
    };
  }
  return {
    state: 'normal',
    status: 'PASS_ENABLED_NORMAL',
    evidenceRole: 'runtime-baseline',
    certifiesEnabledNormal: true,
    snapshot,
    beforePseudo
  };
}

function classifyHover(baseline, snapshot, beforePseudo) {
  if (baseline.disabled) {
    return {
      state: 'disabled-hover-observation',
      status: REAL_RUNTIME_DISABLED_BASELINE,
      reason: 'Hover observation on a native disabled target does not certify enabled hover.',
      certifiesEnabledHover: false,
      snapshot,
      beforePseudo
    };
  }
  return {
    state: 'hover',
    status: 'PASS_ENABLED_HOVER',
    certifiesEnabledHover: true,
    snapshot,
    beforePseudo
  };
}

module.exports = { REAL_RUNTIME_DISABLED_BASELINE, classifyBaseline, classifyHover };
