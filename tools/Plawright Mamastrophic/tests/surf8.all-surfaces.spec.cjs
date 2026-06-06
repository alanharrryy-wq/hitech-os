// Optional central spec wrapper. The actual Playwright entrypoint lives in products/pc/app/tests/prisma-surfaces.
const { test, expect } = require("@playwright/test");
const { registerSurf8Tests } = require("./surf8.all-surfaces.engine.cjs");
registerSurf8Tests(test, expect);
