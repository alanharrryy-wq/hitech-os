const path = require("path");

const pcRoot = process.env.PRISMA_SURF_PC_ROOT || process.cwd();
const playwrightTestPath = process.env.PRISMA_SURF_PLAYWRIGHT_TEST_MODULE || path.join(pcRoot, "node_modules", "@playwright", "test");
const { test, expect } = require(playwrightTestPath);
const { registerSurf8VisualQaTests } = require("./surf8.visualqa.engine.cjs");

registerSurf8VisualQaTests(test, expect);
