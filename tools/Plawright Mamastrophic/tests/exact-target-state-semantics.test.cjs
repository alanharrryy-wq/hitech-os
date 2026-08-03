#!/usr/bin/env node
const assert = require('assert');
const { REAL_RUNTIME_DISABLED_BASELINE, classifyBaseline, classifyHover } = require('../core/exact-target-state-semantics.cjs');

const disabled = { disabled: true, attributes: { disabled: '' } };
const disabledBaseline = classifyBaseline(disabled, {});
assert.equal(disabledBaseline.state, 'disabled');
assert.equal(disabledBaseline.status, REAL_RUNTIME_DISABLED_BASELINE);
assert.equal(disabledBaseline.certifiesEnabledNormal, false);
assert.notEqual(disabledBaseline.state, 'normal');

const disabledHover = classifyHover(disabled, { disabled: true }, {});
assert.equal(disabledHover.status, REAL_RUNTIME_DISABLED_BASELINE);
assert.equal(disabledHover.certifiesEnabledHover, false);
assert.notEqual(disabledHover.state, 'hover');

const enabled = { disabled: false, attributes: {} };
const enabledBaseline = classifyBaseline(enabled, {});
assert.equal(enabledBaseline.state, 'normal');
assert.equal(enabledBaseline.status, 'PASS_ENABLED_NORMAL');
assert.equal(enabledBaseline.certifiesEnabledNormal, true);

const enabledHover = classifyHover(enabled, { disabled: false }, {});
assert.equal(enabledHover.state, 'hover');
assert.equal(enabledHover.status, 'PASS_ENABLED_HOVER');
assert.equal(enabledHover.certifiesEnabledHover, true);

console.log('PASS_EXACT_TARGET_STATE_SEMANTICS');
