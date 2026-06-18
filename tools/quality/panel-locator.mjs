#!/usr/bin/env node
import { runPanelLocatorCli } from './panel-locator/cli.mjs';

runPanelLocatorCli(process.argv.slice(2)).catch((error) => {
  const message = error && error.stack ? error.stack : String(error);
  console.error(message);
  process.exit(1);
});
