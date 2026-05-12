#!/usr/bin/env node
import { runCli } from '../core/kernel.mjs';

runCli(process.argv.slice(2)).then((code) => {
  process.exitCode = code;
}).catch((error) => {
  console.error('[PQOS:FATAL]', error?.stack || error?.message || String(error));
  process.exitCode = 2;
});
