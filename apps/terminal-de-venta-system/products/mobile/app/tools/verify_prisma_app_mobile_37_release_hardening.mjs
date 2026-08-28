#!/usr/bin/env node
// Historical compatibility entrypoint. Product-interface authority lives in verify_prisma_mobile_interface_canon.mjs.
process.argv.push("--compat=release-hardening");
await import("./verify_prisma_mobile_interface_canon.mjs");
