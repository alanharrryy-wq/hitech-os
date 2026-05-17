#!/usr/bin/env node
import { runCli } from '../core/kernel.mjs';

let settled = false;

const keepAlive = setInterval(() => {}, 1000);

const watchdog = setTimeout(() => {
  if (!settled) {
    console.error('[PQOS:WATCHDOG] runCli() did not settle within 5 minutes.');
    clearInterval(keepAlive);
    process.exit(2);
  }
}, 300000);

Promise.resolve()
  .then(() => runCli(process.argv.slice(2)))
  .then((exitCode) => {
    settled = true;
    clearInterval(keepAlive);
    clearTimeout(watchdog);
    process.exit(Number.isInteger(exitCode) ? exitCode : 0);
  })
  .catch((error) => {
    settled = true;
    clearInterval(keepAlive);
    clearTimeout(watchdog);
    console.error('[PQOS:FATAL]', error?.stack || error?.message || String(error));
    process.exit(2);
  });
